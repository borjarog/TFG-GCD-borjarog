"""Modelado de Fase 2: subempleo por insuficiencia de horas (ocupados).

Target binario TARGET_SUBEMPLEO = 1 si AOI=03 (definición OIT/INE).
Se comparan Regresión Logística, Random Forest y LightGBM con búsqueda
de hiperparámetros (PR-AUC), evaluación en test temporal e interpretabilidad
SHAP (beeswarm + barras de importancia media |SHAP|).

Variables EXCLUIDAS por fuga (definición del target): MASHOR, DISMAS,
RZNDISH, HORDES, BUSOTR. Las horas habituales/efectivas SÍ se usan como
factores de riesgo laborales (no son la fuente directa de AOI=03).

Uso:
    python -m src.modeling.fase2
    python run_model_fase2.py
"""

from __future__ import annotations

import time

import joblib
from joblib import parallel_backend
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from .config import (
    CORTE_ANIO,
    CORTE_TRIMESTRE,
    CV_FOLDS,
    DATASET_FASE2,
    FIGURES_FASE2_DIR,
    MODELS_FASE2_DIR,
    N_ITER_BUSQUEDA,
    RANDOM_STATE,
    REPORTS_FASE2_DIR,
    TAMANO_MAX_ENTRENO_LINEAL,
    TAMANO_MUESTRA_BUSQUEDA,
)
from .evaluate import (
    guardar_curva_pr,
    guardar_json,
    guardar_matriz_confusion,
    metricas_binarias,
    reporte_texto_binario,
    umbral_optimo_f1,
)
from .interpretability import graficar_shap_completo
from .model_specs import construir_candidatos
from .preprocessing import (
    COLUMNAS_EXCLUIDAS_FASE2,
    COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
    COLUMNAS_NUMERICAS_FASE2,
    ModeloEnvuelto,
    construir_preprocesador_sklearn,
    preparar_features_nativo,
    preparar_features_sklearn,
    split_temporal,
)


def obtener_columnas_features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in COLUMNAS_EXCLUIDAS_FASE2]


def _a_tipo_serializable(valor):
    if isinstance(valor, np.integer):
        return int(valor)
    if isinstance(valor, np.floating):
        return float(valor)
    return valor


def _submuestra_estratificada(df: pd.DataFrame, y: pd.Series, n: int, random_state: int):
    if len(df) <= n:
        return df, y
    df_muestra, _, y_muestra, _ = train_test_split(
        df, y, train_size=n, stratify=y, random_state=random_state
    )
    return df_muestra, y_muestra


def _buscar_mejores_hiperparametros(candidato, df_train, y_train, columnas_features):
    df_muestra, y_muestra = _submuestra_estratificada(
        df_train, y_train, TAMANO_MUESTRA_BUSQUEDA, RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    if candidato.familia_preprocesado == "nativo":
        X_muestra = preparar_features_nativo(
            df_muestra,
            columnas_features,
            COLUMNAS_NUMERICAS_FASE2,
            COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
        )
        estimador = clone(candidato.estimador)
        espacio = dict(candidato.espacio_busqueda)
    else:
        X_muestra = preparar_features_sklearn(
            df_muestra,
            columnas_features,
            COLUMNAS_NUMERICAS_FASE2,
            COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
        )
        preprocesador = construir_preprocesador_sklearn(
            df_muestra,
            columnas_features,
            COLUMNAS_NUMERICAS_FASE2,
            COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
        )
        estimador = Pipeline([("prep", preprocesador), ("modelo", clone(candidato.estimador))])
        espacio = {f"modelo__{k}": v for k, v in candidato.espacio_busqueda.items()}

    busqueda = RandomizedSearchCV(
        estimator=estimador,
        param_distributions=espacio,
        n_iter=N_ITER_BUSQUEDA,
        scoring="average_precision",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=False,
    )
    with parallel_backend("threading"):
        busqueda.fit(X_muestra, y_muestra)

    mejores_params = busqueda.best_params_
    if candidato.familia_preprocesado == "sklearn":
        mejores_params = {k.replace("modelo__", "", 1): v for k, v in mejores_params.items()}
    return mejores_params, busqueda.best_score_


def _entrenar_y_evaluar(candidato, mejores_params, df_train, y_train, df_test, y_test, columnas_features):
    params_finales = dict(mejores_params)
    if candidato.nombre in {"random_forest", "lightgbm"}:
        params_finales["n_jobs"] = -1

    df_fit, y_fit = df_train, y_train
    filas_entreno = len(df_train)
    if candidato.nombre == "regresion_logistica" and len(df_train) > TAMANO_MAX_ENTRENO_LINEAL:
        df_fit, y_fit = _submuestra_estratificada(
            df_train, y_train, TAMANO_MAX_ENTRENO_LINEAL, RANDOM_STATE
        )
        filas_entreno = len(df_fit)
        print(
            f"  (Logística: reentreno sobre {filas_entreno:,} filas estratificadas "
            f"en vez de {len(df_train):,}.)"
        )

    estimador = clone(candidato.estimador).set_params(**params_finales)
    modelo = ModeloEnvuelto(
        candidato.nombre,
        candidato.familia_preprocesado,
        estimador,
        columnas_features,
        COLUMNAS_NUMERICAS_FASE2,
        COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
    )

    t0 = time.time()
    modelo.fit(df_fit, y_fit)
    duracion = time.time() - t0

    y_proba = modelo.predict_proba(df_test)
    y_pred = (y_proba >= 0.5).astype(int)
    metricas = metricas_binarias(y_test, y_pred, y_proba)
    metricas["segundos_entrenamiento"] = round(duracion, 1)
    metricas["filas_entreno"] = filas_entreno
    return modelo, y_pred, y_proba, metricas


def ejecutar_pipeline_fase2() -> dict:
    print("=" * 70)
    print(" MODELADO FASE 2 — Subempleo por insuficiencia de horas (ocupados)")
    print("=" * 70)
    print(f"\nCargando {DATASET_FASE2}...")
    df = pd.read_parquet(DATASET_FASE2)
    columnas_features = obtener_columnas_features(df)
    tasa = float(df["TARGET_SUBEMPLEO"].mean())
    print(
        f"  -> {len(df):,} filas, {len(columnas_features)} predictoras, "
        f"tasa de subempleo = {tasa * 100:.2f}%."
    )
    print(f"  -> Predictoras: {', '.join(columnas_features)}")

    train_df, test_df = split_temporal(df, CORTE_ANIO, CORTE_TRIMESTRE)
    y_train = train_df["TARGET_SUBEMPLEO"].astype(int)
    y_test = test_df["TARGET_SUBEMPLEO"].astype(int)
    print(
        f"  -> Subempleo train: {y_train.mean() * 100:.2f}% | "
        f"test: {y_test.mean() * 100:.2f}%"
    )

    candidatos = construir_candidatos(RANDOM_STATE)
    comparacion: dict[str, dict] = {}
    modelos: dict[str, ModeloEnvuelto] = {}
    predicciones: dict[str, tuple] = {}

    print(f"\n{'=' * 70}\n COMPARACIÓN DE CANDIDATOS\n{'=' * 70}")
    for candidato in candidatos:
        print(f"\n--- Candidato: {candidato.nombre} ---")
        print("  Buscando hiperparámetros (RandomizedSearchCV sobre muestra estratificada)...")
        t0 = time.time()
        mejores_params, mejor_score_cv = _buscar_mejores_hiperparametros(
            candidato, train_df, y_train, columnas_features
        )
        print(
            f"  Búsqueda completada en {time.time() - t0:.1f}s. "
            f"PR-AUC (CV, muestra) = {mejor_score_cv:.4f}"
        )
        print(f"  Mejores hiperparámetros: {mejores_params}")

        print("  Reentrenando y evaluando en test...")
        modelo, y_pred, y_proba, metricas = _entrenar_y_evaluar(
            candidato, mejores_params, train_df, y_train, test_df, y_test, columnas_features
        )
        metricas["mejores_hiperparametros"] = {
            k: _a_tipo_serializable(v) for k, v in mejores_params.items()
        }
        metricas["pr_auc_cv_busqueda"] = round(float(mejor_score_cv), 4)
        print(
            f"  Test @0.5 -> PR-AUC={metricas['pr_auc']:.4f}  ROC-AUC={metricas['roc_auc']:.4f}  "
            f"F1={metricas['f1']:.4f}  BalAcc={metricas['balanced_accuracy']:.4f}"
        )

        comparacion[candidato.nombre] = metricas
        modelos[candidato.nombre] = modelo
        predicciones[candidato.nombre] = (y_pred, y_proba)

    ganador = max(comparacion, key=lambda n: comparacion[n]["pr_auc"])
    print(f"\n>>> Modelo ganador Fase 2: {ganador} (PR-AUC={comparacion[ganador]['pr_auc']:.4f})")

    modelo_ganador = modelos[ganador]
    y_pred_05, y_proba_ganador = predicciones[ganador]

    # Umbral calibrado en una muestra del TRAIN (no del test) para no sobreajustar el informe.
    print("\nCalibrando umbral de decisión (máx. F1) sobre muestra del train...")
    df_cal, y_cal = _submuestra_estratificada(train_df, y_train, 120_000, RANDOM_STATE)
    umbral = umbral_optimo_f1(y_cal, modelo_ganador.predict_proba(df_cal))
    y_pred_opt = (y_proba_ganador >= umbral).astype(int)
    metricas_opt = metricas_binarias(y_test, y_pred_opt, y_proba_ganador)
    print(f"  Umbral óptimo (F1 en train) = {umbral:.3f}")
    print(
        f"  Test @{umbral:.3f} -> F1={metricas_opt['f1']:.4f}  "
        f"BalAcc={metricas_opt['balanced_accuracy']:.4f}"
    )

    joblib.dump(modelo_ganador, MODELS_FASE2_DIR / f"subempleo_{ganador}.joblib")
    guardar_json(
        {"umbral_f1_train": umbral, "ganador": ganador},
        MODELS_FASE2_DIR / "umbral_decision.json",
    )

    guardar_matriz_confusion(
        y_test,
        y_pred_05,
        [0, 1],
        ["No subempleo", "Subempleo"],
        f"Matriz de confusión — Fase 2 @0.5 ({ganador})",
        FIGURES_FASE2_DIR / "matriz_confusion_umbral_05.png",
    )
    guardar_matriz_confusion(
        y_test,
        y_pred_opt,
        [0, 1],
        ["No subempleo", "Subempleo"],
        f"Matriz de confusión — Fase 2 @{umbral:.2f} ({ganador})",
        FIGURES_FASE2_DIR / "matriz_confusion_umbral_optimo.png",
    )
    guardar_curva_pr(
        y_test,
        y_proba_ganador,
        f"Curva Precision-Recall — Fase 2 ({ganador})",
        FIGURES_FASE2_DIR / "curva_pr.png",
    )

    try:
        graficar_shap_completo(
            modelo_ganador,
            test_df,
            f"Fase 2 ({ganador})",
            FIGURES_FASE2_DIR / "shap_summary.png",
            FIGURES_FASE2_DIR / "shap_importancia_barras.png",
        )
    except Exception as exc:
        print(f"  (Aviso: no se pudo generar SHAP de {ganador}: {exc})")

    informe_05 = reporte_texto_binario(y_test, y_pred_05, ["No subempleo", "Subempleo"])
    informe_opt = reporte_texto_binario(y_test, y_pred_opt, ["No subempleo", "Subempleo"])
    print(f"\n[Informe @ umbral 0.5]\n{informe_05}")
    print(f"[Informe @ umbral {umbral:.3f}]\n{informe_opt}")

    guardar_json(
        {
            "comparacion": comparacion,
            "ganador": ganador,
            "umbral_optimo_f1_train": umbral,
            "metricas_test_umbral_05": comparacion[ganador],
            "metricas_test_umbral_optimo": metricas_opt,
            "tasa_subempleo_global": round(tasa, 4),
            "columnas_features": columnas_features,
        },
        REPORTS_FASE2_DIR / "comparacion_modelos.json",
    )

    with open(REPORTS_FASE2_DIR / "informe_final.txt", "w", encoding="utf-8") as f:
        f.write(f"MODELADO FASE 2 — Subempleo (AOI=03) | Ganador: {ganador}\n")
        f.write(f"Tasa de subempleo (dataset): {tasa * 100:.2f}%\n")
        f.write(f"Umbral calibrado (máx. F1 en train): {umbral:.3f}\n\n")
        f.write("=== Test @ umbral 0.50 ===\n")
        f.write(informe_05 + "\n\n")
        f.write(f"=== Test @ umbral {umbral:.3f} ===\n")
        f.write(informe_opt + "\n\n")
        f.write("=== Métricas de comparación (PR-AUC es el criterio de ganador) ===\n")
        for nombre, mets in comparacion.items():
            f.write(
                f"- {nombre}: PR-AUC={mets['pr_auc']:.4f} ROC-AUC={mets['roc_auc']:.4f} "
                f"F1@0.5={mets['f1']:.4f}\n"
            )

    print(f"\nArtefactos en {MODELS_FASE2_DIR}, {REPORTS_FASE2_DIR} y {FIGURES_FASE2_DIR}.")
    print("Modelado de Fase 2 completado.")

    return {
        "ganador": ganador,
        "comparacion": comparacion,
        "umbral": umbral,
        "modelo": modelo_ganador,
    }


if __name__ == "__main__":
    ejecutar_pipeline_fase2()
