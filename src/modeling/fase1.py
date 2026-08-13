"""Fase 1: Activo/Inactivo y, sobre activos, Ocupado/Parado.

Tres modelos por etapa (más un baseline de prevalencia), búsqueda por PR-AUC
y umbral F1. Al final se encadenan A y B sobre el test.
"""

from __future__ import annotations

import time

import joblib
from joblib import parallel_backend
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from .config import (
    CORTE_ANIO,
    CORTE_TRIMESTRE,
    CV_FOLDS,
    DATASET_FASE1,
    FIGURES_FASE1_DIR,
    MODELS_FASE1_DIR,
    N_ITER_BUSQUEDA,
    RANDOM_STATE,
    REPORTS_FASE1_DIR,
    TAMANO_MAX_ENTRENO_LINEAL,
    TAMANO_MUESTRA_BUSQUEDA,
)
from .evaluate import (
    guardar_curva_pr,
    guardar_json,
    guardar_matriz_confusion,
    metricas_baseline_prevalencia,
    metricas_binarias,
    reporte_texto_binario,
    umbral_optimo_f1,
)
from .interpretability import graficar_shap_completo
from .model_specs import construir_candidatos
from .preprocessing import COLUMNAS_EXCLUIDAS, ModeloEnvuelto, construir_preprocesador_sklearn, split_temporal
from .preprocessing import preparar_features_nativo, preparar_features_sklearn


def obtener_columnas_features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in COLUMNAS_EXCLUIDAS]


def _a_tipo_serializable(valor):
    """numpy -> int/float para poder meterlo en JSON."""
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
        X_muestra = preparar_features_nativo(df_muestra, columnas_features)
        estimador = clone(candidato.estimador)
        espacio = dict(candidato.espacio_busqueda)
    else:
        X_muestra = preparar_features_sklearn(df_muestra, columnas_features)
        preprocesador = construir_preprocesador_sklearn(df_muestra, columnas_features)
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
    # Backend threading: en Windows loky se ha colgado de forma reproducible.
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
            f"en vez de {len(df_train):,} — lbfgs no escala bien a millones.)"
        )

    estimador = clone(candidato.estimador).set_params(**params_finales)
    modelo = ModeloEnvuelto(candidato.nombre, candidato.familia_preprocesado, estimador, columnas_features)

    t0 = time.time()
    modelo.fit(df_fit, y_fit)
    duracion = time.time() - t0

    y_proba = modelo.predict_proba(df_test)
    y_pred = (y_proba >= 0.5).astype(int)
    metricas = metricas_binarias(y_test, y_pred, y_proba)
    metricas["segundos_entrenamiento"] = round(duracion, 1)
    metricas["filas_entreno"] = filas_entreno
    return modelo, y_pred, y_proba, metricas


def entrenar_etapa(
    nombre_etapa: str,
    df_train: pd.DataFrame,
    y_train: pd.Series,
    df_test: pd.DataFrame,
    y_test: pd.Series,
    columnas_features: list[str],
    etiquetas: list[str],
) -> dict:
    print(f"\n{'=' * 70}\n ETAPA: {nombre_etapa}\n{'=' * 70}")
    print(f" Train: {len(df_train):,} filas | Test: {len(df_test):,} filas")
    print(
        f" Búsqueda HP: n_iter={N_ITER_BUSQUEDA}, muestra={TAMANO_MUESTRA_BUSQUEDA:,}, "
        f"CV={CV_FOLDS}"
    )

    comparacion: dict[str, dict] = {}
    modelos: dict[str, ModeloEnvuelto] = {}
    predicciones: dict[str, tuple] = {}

    print("\n--- Baseline: prevalencia (score constante) ---")
    baseline = metricas_baseline_prevalencia(y_train, y_test)
    comparacion["baseline_prevalencia"] = baseline
    print(
        f"  Test -> PR-AUC={baseline['pr_auc']:.4f}  ROC-AUC={baseline['roc_auc']:.4f}  "
        f"F1={baseline['f1']:.4f}  (prevalencia train={baseline['prevalencia_train']:.4f})"
    )

    candidatos = construir_candidatos(RANDOM_STATE)
    for candidato in candidatos:
        print(f"\n--- Candidato: {candidato.nombre} ---")
        print("  Buscando hiperparámetros (RandomizedSearchCV sobre muestra estratificada)...")
        t0 = time.time()
        mejores_params, mejor_score_cv = _buscar_mejores_hiperparametros(
            candidato, df_train, y_train, columnas_features
        )
        print(f"  Búsqueda completada en {time.time() - t0:.1f}s. PR-AUC (CV, muestra) = {mejor_score_cv:.4f}")
        print(f"  Mejores hiperparámetros: {mejores_params}")

        print("  Reentrenando con el train completo y evaluando en test...")
        modelo, y_pred, y_proba, metricas = _entrenar_y_evaluar(
            candidato, mejores_params, df_train, y_train, df_test, y_test, columnas_features
        )
        metricas["mejores_hiperparametros"] = {
            k: _a_tipo_serializable(v) for k, v in mejores_params.items()
        }
        metricas["pr_auc_cv_busqueda"] = round(float(mejor_score_cv), 4)
        print(
            f"  Test @0.50 -> PR-AUC={metricas['pr_auc']:.4f}  ROC-AUC={metricas['roc_auc']:.4f}  "
            f"F1={metricas['f1']:.4f}  BalAcc={metricas['balanced_accuracy']:.4f}"
        )

        comparacion[candidato.nombre] = metricas
        modelos[candidato.nombre] = modelo
        predicciones[candidato.nombre] = (y_pred, y_proba)

    ganador = max(
        (n for n in comparacion if n != "baseline_prevalencia"),
        key=lambda n: comparacion[n]["pr_auc"],
    )
    print(f"\n>>> Modelo ganador de '{nombre_etapa}': {ganador} (PR-AUC={comparacion[ganador]['pr_auc']:.4f})")

    modelo_ganador = modelos[ganador]
    y_pred_05, y_proba_ganador = predicciones[ganador]
    slug = "".join(c for c in nombre_etapa.lower() if c.isalnum() or c == " ").replace(" ", "_")

    # Umbral óptimo F1 calibrado en muestra del train (como Fase 2)
    print("\nCalibrando umbral de decisión (máx. F1) sobre muestra del train...")
    df_cal, y_cal = _submuestra_estratificada(
        df_train, y_train, min(TAMANO_MUESTRA_BUSQUEDA, len(df_train)), RANDOM_STATE + 1
    )
    umbral = umbral_optimo_f1(y_cal, modelo_ganador.predict_proba(df_cal))
    y_pred_opt = (y_proba_ganador >= umbral).astype(int)
    metricas_opt = metricas_binarias(y_test, y_pred_opt, y_proba_ganador)
    print(f"  Umbral óptimo (F1 en train) = {umbral:.3f}")
    print(
        f"  Test @{umbral:.3f} -> F1={metricas_opt['f1']:.4f}  "
        f"BalAcc={metricas_opt['balanced_accuracy']:.4f}  "
        f"(F1@0.50={comparacion[ganador]['f1']:.4f})"
    )

    joblib.dump(modelo_ganador, MODELS_FASE1_DIR / f"{slug}_{ganador}.joblib")
    guardar_json(
        {"umbral_f1_train": umbral, "ganador": ganador, "etapa": nombre_etapa},
        MODELS_FASE1_DIR / f"{slug}_umbral_decision.json",
    )

    guardar_matriz_confusion(
        y_test,
        y_pred_05,
        [0, 1],
        etiquetas,
        f"Matriz de confusión @0.50 — {nombre_etapa} ({ganador})",
        FIGURES_FASE1_DIR / f"{slug}_matriz_confusion.png",
    )
    guardar_matriz_confusion(
        y_test,
        y_pred_opt,
        [0, 1],
        etiquetas,
        f"Matriz de confusión @{umbral:.2f} — {nombre_etapa} ({ganador})",
        FIGURES_FASE1_DIR / f"{slug}_matriz_confusion_umbral_optimo.png",
    )
    guardar_curva_pr(
        y_test,
        y_proba_ganador,
        f"Curva Precision-Recall — {nombre_etapa} ({ganador})",
        FIGURES_FASE1_DIR / f"{slug}_curva_pr.png",
    )
    try:
        graficar_shap_completo(
            modelo_ganador,
            df_test,
            f"{nombre_etapa} ({ganador})",
            FIGURES_FASE1_DIR / f"{slug}_shap_summary.png",
            FIGURES_FASE1_DIR / f"{slug}_shap_importancia_barras.png",
        )
    except Exception as exc:
        print(f"  (Aviso: no se pudo generar el gráfico SHAP de {ganador}: {exc})")

    informe_05 = reporte_texto_binario(y_test, y_pred_05, etiquetas)
    informe_opt = reporte_texto_binario(y_test, y_pred_opt, etiquetas)
    print(f"\n[Informe @ umbral 0.50 — {nombre_etapa}]\n{informe_05}")
    print(f"[Informe @ umbral {umbral:.3f} — {nombre_etapa}]\n{informe_opt}")

    return {
        "ganador": ganador,
        "comparacion": comparacion,
        "umbral": umbral,
        "metricas_umbral_optimo": metricas_opt,
        "informe_texto_05": informe_05,
        "informe_texto_opt": informe_opt,
        "modelo": modelo_ganador,
    }


def _predecir_con_umbral(modelo: ModeloEnvuelto, df: pd.DataFrame, umbral: float) -> np.ndarray:
    return (modelo.predict_proba(df) >= umbral).astype(int)


def _persistir_resultados_fase1(resultado_a: dict, resultado_b: dict, test_df: pd.DataFrame, informe_combinado: str) -> None:
    pred_activo = _predecir_con_umbral(resultado_a["modelo"], test_df, resultado_a["umbral"])
    pred_final = np.where(pred_activo == 0, "Inactivo", "Ocupado").astype(object)
    idx_activos = np.where(pred_activo == 1)[0]
    if len(idx_activos) > 0:
        pred_parado = _predecir_con_umbral(
            resultado_b["modelo"], test_df.iloc[idx_activos], resultado_b["umbral"]
        )
        pred_final[idx_activos] = np.where(pred_parado == 1, "Parado", "Ocupado")

    y_true_final = test_df["TARGET_MACRO"].astype(str).to_numpy()
    etiquetas_finales = ["Inactivo", "Ocupado", "Parado"]
    if informe_combinado is None:
        informe_combinado = classification_report(y_true_final, pred_final, labels=etiquetas_finales)
        print(informe_combinado)

    guardar_matriz_confusion(
        y_true_final,
        pred_final,
        etiquetas_finales,
        etiquetas_finales,
        "Matriz de confusión combinada (3 clases) — Fase 1",
        FIGURES_FASE1_DIR / "combinado_matriz_confusion.png",
    )

    guardar_json(
        {
            "config_busqueda": {
                "n_iter": N_ITER_BUSQUEDA,
                "tamano_muestra": TAMANO_MUESTRA_BUSQUEDA,
                "cv_folds": CV_FOLDS,
            },
            "etapa_a": {
                "ganador": resultado_a["ganador"],
                "umbral_optimo_f1_train": resultado_a["umbral"],
                "comparacion": resultado_a["comparacion"],
                "metricas_test_umbral_optimo": resultado_a["metricas_umbral_optimo"],
            },
            "etapa_b": {
                "ganador": resultado_b["ganador"],
                "umbral_optimo_f1_train": resultado_b["umbral"],
                "comparacion": resultado_b["comparacion"],
                "metricas_test_umbral_optimo": resultado_b["metricas_umbral_optimo"],
            },
        },
        REPORTS_FASE1_DIR / "comparacion_modelos.json",
    )
    with open(REPORTS_FASE1_DIR / "informe_final.txt", "w", encoding="utf-8") as f:
        f.write(
            f"MODELADO FASE 1 — Ganador Etapa A: {resultado_a['ganador']} | "
            f"Ganador Etapa B: {resultado_b['ganador']}\n"
        )
        f.write(
            f"Búsqueda HP: n_iter={N_ITER_BUSQUEDA}, muestra={TAMANO_MUESTRA_BUSQUEDA}, "
            f"CV={CV_FOLDS}\n"
        )
        f.write(
            f"Umbrales calibrados (máx. F1 en train): "
            f"A={resultado_a['umbral']:.3f} | B={resultado_b['umbral']:.3f}\n\n"
        )
        f.write("=== Etapa A: Activo vs Inactivo @0.50 ===\n")
        f.write(resultado_a["informe_texto_05"] + "\n")
        f.write(f"=== Etapa A @ umbral {resultado_a['umbral']:.3f} ===\n")
        f.write(resultado_a["informe_texto_opt"] + "\n\n")
        f.write("=== Etapa B: Ocupado vs Parado @0.50 ===\n")
        f.write(resultado_b["informe_texto_05"] + "\n")
        f.write(f"=== Etapa B @ umbral {resultado_b['umbral']:.3f} ===\n")
        f.write(resultado_b["informe_texto_opt"] + "\n\n")
        f.write("=== Combinado (3 clases), A -> B con umbrales calibrados ===\n")
        f.write(informe_combinado + "\n")

    print(f"\nArtefactos guardados en {MODELS_FASE1_DIR}, {REPORTS_FASE1_DIR} y {FIGURES_FASE1_DIR}.")


def _cargar_resultado_etapa_a_guardado(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """Reconstruye el resultado de A desde el modelo/umbral ya guardados (sin reentrenar)."""
    import json

    ruta_modelo = MODELS_FASE1_DIR / "etapa_a__activo_vs_inactivo_random_forest.joblib"
    ruta_umbral = MODELS_FASE1_DIR / "etapa_a__activo_vs_inactivo_umbral_decision.json"
    if not ruta_modelo.exists() or not ruta_umbral.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo/umbral de Etapa A en {MODELS_FASE1_DIR}. "
            "Ejecuta primero el pipeline completo o al menos la Etapa A."
        )

    modelo_a = joblib.load(ruta_modelo)
    with open(ruta_umbral, encoding="utf-8") as f:
        meta = json.load(f)
    umbral = float(meta["umbral_f1_train"])

    y_train = (train_df["TARGET_MACRO"] != "Inactivo").astype(int)
    y_test = (test_df["TARGET_MACRO"] != "Inactivo").astype(int)
    y_proba = modelo_a.predict_proba(test_df)
    y_pred_05 = (y_proba >= 0.5).astype(int)
    y_pred_opt = (y_proba >= umbral).astype(int)

    metricas_05 = metricas_binarias(y_test, y_pred_05, y_proba)
    metricas_opt = metricas_binarias(y_test, y_pred_opt, y_proba)
    baseline = metricas_baseline_prevalencia(y_train, y_test)

    # Métricas de los otros candidatos del reentrenamiento (log 12/08/2026); el ganador se reevalúa arriba.
    comparacion = {
        "baseline_prevalencia": baseline,
        "regresion_logistica": {
            "roc_auc": 0.8355,
            "pr_auc": 0.9264,
            "f1": 0.8527,
            "balanced_accuracy": 0.7538,
            "nota": "métricas del retrain (modelo no persistido)",
        },
        "random_forest": {
            **metricas_05,
            "mejores_hiperparametros": {
                "max_depth": 19,
                "max_features": 0.47857853816408474,
                "min_samples_leaf": 14,
                "min_samples_split": 9,
                "n_estimators": 332,
            },
            "pr_auc_cv_busqueda": 0.9306,
        },
        "lightgbm": {
            "roc_auc": 0.8567,
            "pr_auc": 0.9377,
            "f1": 0.8528,
            "balanced_accuracy": 0.7750,
            "nota": "métricas del retrain (modelo no persistido)",
        },
    }

    return {
        "ganador": "random_forest",
        "comparacion": comparacion,
        "umbral": umbral,
        "metricas_umbral_optimo": metricas_opt,
        "informe_texto_05": reporte_texto_binario(y_test, y_pred_05, ["Inactivo", "Activo"]),
        "informe_texto_opt": reporte_texto_binario(y_test, y_pred_opt, ["Inactivo", "Activo"]),
        "modelo": modelo_a,
    }


def ejecutar_pipeline_fase1_solo_b() -> dict:
    """Continúa Fase 1: usa Etapa A ya entrenada y reentrena solo Etapa B + combinado."""
    print("=" * 70)
    print(" MODELADO FASE 1 — SOLO ETAPA B (+ combinado con A guardada)")
    print("=" * 70)
    print(f"\nCargando {DATASET_FASE1}...")
    df = pd.read_parquet(DATASET_FASE1)
    columnas_features = obtener_columnas_features(df)
    train_df, test_df = split_temporal(df, CORTE_ANIO, CORTE_TRIMESTRE)

    print("\nCargando Etapa A guardada (sin reentrenar)...")
    resultado_a = _cargar_resultado_etapa_a_guardado(train_df, test_df)
    print(
        f"  -> ganador={resultado_a['ganador']} | umbral={resultado_a['umbral']:.3f} | "
        f"PR-AUC={resultado_a['comparacion']['random_forest']['pr_auc']:.4f}"
    )

    train_activos = train_df[train_df["TARGET_MACRO"] != "Inactivo"].copy()
    test_activos = test_df[test_df["TARGET_MACRO"] != "Inactivo"].copy()
    y_train_b = (train_activos["TARGET_MACRO"] == "Parado").astype(int)
    y_test_b = (test_activos["TARGET_MACRO"] == "Parado").astype(int)
    resultado_b = entrenar_etapa(
        "Etapa B - Ocupado vs Parado",
        train_activos,
        y_train_b,
        test_activos,
        y_test_b,
        columnas_features,
        ["Ocupado", "Parado"],
    )

    print(f"\n{'=' * 70}\n EVALUACIÓN COMBINADA (3 CLASES) SOBRE EL TEST TEMPORAL\n{'=' * 70}")
    print(
        f" Umbrales calibrados: A={resultado_a['umbral']:.3f} | B={resultado_b['umbral']:.3f}"
    )
    pred_activo = _predecir_con_umbral(resultado_a["modelo"], test_df, resultado_a["umbral"])
    pred_final = np.where(pred_activo == 0, "Inactivo", "Ocupado").astype(object)
    idx_activos = np.where(pred_activo == 1)[0]
    if len(idx_activos) > 0:
        pred_parado = _predecir_con_umbral(
            resultado_b["modelo"], test_df.iloc[idx_activos], resultado_b["umbral"]
        )
        pred_final[idx_activos] = np.where(pred_parado == 1, "Parado", "Ocupado")
    y_true_final = test_df["TARGET_MACRO"].astype(str).to_numpy()
    informe_combinado = classification_report(
        y_true_final, pred_final, labels=["Inactivo", "Ocupado", "Parado"]
    )
    print(informe_combinado)

    _persistir_resultados_fase1(resultado_a, resultado_b, test_df, informe_combinado)
    print("Etapa B + combinado completados.")
    return {"etapa_a": resultado_a, "etapa_b": resultado_b, "informe_combinado": informe_combinado}


def ejecutar_pipeline_fase1() -> dict:
    print("=" * 70)
    print(" MODELADO FASE 1 — Ocupado / Parado / Inactivo (edad activa 16-64)")
    print("=" * 70)
    print(f"\nCargando {DATASET_FASE1}...")
    df = pd.read_parquet(DATASET_FASE1)
    columnas_features = obtener_columnas_features(df)
    print(f"  -> {len(df):,} filas, {len(columnas_features)} variables predictoras.")

    train_df, test_df = split_temporal(df, CORTE_ANIO, CORTE_TRIMESTRE)

    y_train_a = (train_df["TARGET_MACRO"] != "Inactivo").astype(int)
    y_test_a = (test_df["TARGET_MACRO"] != "Inactivo").astype(int)
    resultado_a = entrenar_etapa(
        "Etapa A - Activo vs Inactivo",
        train_df,
        y_train_a,
        test_df,
        y_test_a,
        columnas_features,
        ["Inactivo", "Activo"],
    )

    train_activos = train_df[train_df["TARGET_MACRO"] != "Inactivo"].copy()
    test_activos = test_df[test_df["TARGET_MACRO"] != "Inactivo"].copy()
    y_train_b = (train_activos["TARGET_MACRO"] == "Parado").astype(int)
    y_test_b = (test_activos["TARGET_MACRO"] == "Parado").astype(int)
    resultado_b = entrenar_etapa(
        "Etapa B - Ocupado vs Parado",
        train_activos,
        y_train_b,
        test_activos,
        y_test_b,
        columnas_features,
        ["Ocupado", "Parado"],
    )

    print(f"\n{'=' * 70}\n EVALUACIÓN COMBINADA (3 CLASES) SOBRE EL TEST TEMPORAL\n{'=' * 70}")
    print(
        f" Umbrales calibrados: A={resultado_a['umbral']:.3f} | B={resultado_b['umbral']:.3f}"
    )
    pred_activo = _predecir_con_umbral(resultado_a["modelo"], test_df, resultado_a["umbral"])
    pred_final = np.where(pred_activo == 0, "Inactivo", "Ocupado").astype(object)
    idx_activos = np.where(pred_activo == 1)[0]
    if len(idx_activos) > 0:
        pred_parado = _predecir_con_umbral(
            resultado_b["modelo"], test_df.iloc[idx_activos], resultado_b["umbral"]
        )
        pred_final[idx_activos] = np.where(pred_parado == 1, "Parado", "Ocupado")

    y_true_final = test_df["TARGET_MACRO"].astype(str).to_numpy()
    informe_combinado = classification_report(
        y_true_final, pred_final, labels=["Inactivo", "Ocupado", "Parado"]
    )
    print(informe_combinado)

    _persistir_resultados_fase1(resultado_a, resultado_b, test_df, informe_combinado)
    print("Modelado de Fase 1 completado.")
    return {"etapa_a": resultado_a, "etapa_b": resultado_b, "informe_combinado": informe_combinado}


if __name__ == "__main__":
    import sys

    if "--solo-b" in sys.argv:
        ejecutar_pipeline_fase1_solo_b()
    else:
        ejecutar_pipeline_fase1()
