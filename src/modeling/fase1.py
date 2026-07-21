"""Modelado de Fase 1: Ocupado / Parado / Inactivo, en dos etapas jerárquicas.

Etapa A — Activo vs. Inactivo (filtro inicial, sobre toda la población 16+)
Etapa B — Ocupado vs. Parado (solo dentro de los Activos)

Para cada etapa se comparan 3 algoritmos (Regresión Logística, Random
Forest, LightGBM), cada uno con su propia búsqueda aleatoria de
hiperparámetros (validada por PR-AUC, la métrica más informativa bajo
desbalance de clases). El ganador de cada etapa se reentrena con TODO el
train, se evalúa en el test temporal y se explica con SHAP.

Al final se encadenan las dos etapas sobre el test para obtener la
evaluación real de Fase 1: Inactivo / Ocupado / Parado.

Uso:
    python -m src.modeling.fase1
"""

from __future__ import annotations

import time

import joblib
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
    TAMANO_MUESTRA_BUSQUEDA,
)
from .evaluate import (
    guardar_curva_pr,
    guardar_json,
    guardar_matriz_confusion,
    metricas_binarias,
    reporte_texto_binario,
)
from .interpretability import graficar_shap_summary
from .model_specs import construir_candidatos
from .preprocessing import COLUMNAS_EXCLUIDAS, ModeloEnvuelto, construir_preprocesador_sklearn, split_temporal
from .preprocessing import preparar_features_nativo, preparar_features_sklearn


def obtener_columnas_features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in COLUMNAS_EXCLUIDAS]


def _a_tipo_serializable(valor):
    """Convierte escalares numpy (int64, float64...) a tipos nativos de Python para poder guardarlos en JSON."""
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
    df_muestra, y_muestra = _submuestra_estratificada(df_train, y_train, TAMANO_MUESTRA_BUSQUEDA, RANDOM_STATE)
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
    busqueda.fit(X_muestra, y_muestra)

    mejores_params = busqueda.best_params_
    if candidato.familia_preprocesado == "sklearn":
        mejores_params = {k.replace("modelo__", "", 1): v for k, v in mejores_params.items()}
    return mejores_params, busqueda.best_score_


def _entrenar_y_evaluar(candidato, mejores_params, df_train, y_train, df_test, y_test, columnas_features):
    estimador = clone(candidato.estimador).set_params(**mejores_params)
    modelo = ModeloEnvuelto(candidato.nombre, candidato.familia_preprocesado, estimador, columnas_features)

    t0 = time.time()
    modelo.fit(df_train, y_train)
    duracion = time.time() - t0

    y_proba = modelo.predict_proba(df_test)
    y_pred = (y_proba >= 0.5).astype(int)
    metricas = metricas_binarias(y_test, y_pred, y_proba)
    metricas["segundos_entrenamiento_train_completo"] = round(duracion, 1)
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

    candidatos = construir_candidatos(RANDOM_STATE)
    comparacion: dict[str, dict] = {}
    modelos: dict[str, ModeloEnvuelto] = {}
    predicciones: dict[str, tuple] = {}

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
        metricas["mejores_hiperparametros"] = {k: _a_tipo_serializable(v) for k, v in mejores_params.items()}
        metricas["pr_auc_cv_busqueda"] = round(float(mejor_score_cv), 4)
        print(
            f"  Test -> PR-AUC={metricas['pr_auc']:.4f}  ROC-AUC={metricas['roc_auc']:.4f}  "
            f"F1={metricas['f1']:.4f}  BalAcc={metricas['balanced_accuracy']:.4f}"
        )

        comparacion[candidato.nombre] = metricas
        modelos[candidato.nombre] = modelo
        predicciones[candidato.nombre] = (y_pred, y_proba)

    ganador = max(comparacion, key=lambda n: comparacion[n]["pr_auc"])
    print(f"\n>>> Modelo ganador de '{nombre_etapa}': {ganador} (PR-AUC={comparacion[ganador]['pr_auc']:.4f})")

    modelo_ganador = modelos[ganador]
    y_pred_ganador, y_proba_ganador = predicciones[ganador]
    slug = "".join(c for c in nombre_etapa.lower() if c.isalnum() or c == " ").replace(" ", "_")

    joblib.dump(modelo_ganador, MODELS_FASE1_DIR / f"{slug}_{ganador}.joblib")
    guardar_matriz_confusion(
        y_test,
        y_pred_ganador,
        [0, 1],
        etiquetas,
        f"Matriz de confusión — {nombre_etapa} ({ganador})",
        FIGURES_FASE1_DIR / f"{slug}_matriz_confusion.png",
    )
    guardar_curva_pr(
        y_test, y_proba_ganador, f"Curva Precision-Recall — {nombre_etapa} ({ganador})",
        FIGURES_FASE1_DIR / f"{slug}_curva_pr.png",
    )
    try:
        graficar_shap_summary(
            modelo_ganador, df_test, f"SHAP — {nombre_etapa} ({ganador})",
            FIGURES_FASE1_DIR / f"{slug}_shap_summary.png",
        )
    except Exception as exc:  # SHAP puede fallar por memoria/compatibilidad; no debe tumbar el pipeline
        print(f"  (Aviso: no se pudo generar el gráfico SHAP de {ganador}: {exc})")

    informe_texto = reporte_texto_binario(y_test, y_pred_ganador, etiquetas)
    print(f"\n[Informe de clasificación — {nombre_etapa}]\n{informe_texto}")

    return {
        "ganador": ganador,
        "comparacion": comparacion,
        "informe_texto": informe_texto,
        "modelo": modelo_ganador,
    }


def ejecutar_pipeline_fase1() -> dict:
    print("=" * 70)
    print(" MODELADO FASE 1 — Ocupado / Parado / Inactivo")
    print("=" * 70)
    print(f"\nCargando {DATASET_FASE1}...")
    df = pd.read_parquet(DATASET_FASE1)
    columnas_features = obtener_columnas_features(df)
    print(f"  -> {len(df):,} filas, {len(columnas_features)} variables predictoras.")

    train_df, test_df = split_temporal(df, CORTE_ANIO, CORTE_TRIMESTRE)

    # --- ETAPA A: Activo (Ocupado o Parado) vs. Inactivo ---
    y_train_a = (train_df["TARGET_MACRO"] != "Inactivo").astype(int)
    y_test_a = (test_df["TARGET_MACRO"] != "Inactivo").astype(int)
    resultado_a = entrenar_etapa(
        "Etapa A - Activo vs Inactivo", train_df, y_train_a, test_df, y_test_a, columnas_features,
        ["Inactivo", "Activo"],
    )

    # --- ETAPA B: Ocupado vs. Parado, solo dentro de los Activos ---
    train_activos = train_df[train_df["TARGET_MACRO"] != "Inactivo"].copy()
    test_activos = test_df[test_df["TARGET_MACRO"] != "Inactivo"].copy()
    y_train_b = (train_activos["TARGET_MACRO"] == "Parado").astype(int)
    y_test_b = (test_activos["TARGET_MACRO"] == "Parado").astype(int)
    resultado_b = entrenar_etapa(
        "Etapa B - Ocupado vs Parado", train_activos, y_train_b, test_activos, y_test_b, columnas_features,
        ["Ocupado", "Parado"],
    )

    # --- Evaluación combinada: encadenar A -> B sobre TODO el test, 3 clases ---
    print(f"\n{'=' * 70}\n EVALUACIÓN COMBINADA (3 CLASES) SOBRE EL TEST TEMPORAL\n{'=' * 70}")
    pred_activo = resultado_a["modelo"].predict(test_df)
    pred_final = np.where(pred_activo == 0, "Inactivo", "Ocupado").astype(object)
    idx_activos = np.where(pred_activo == 1)[0]
    if len(idx_activos) > 0:
        pred_parado = resultado_b["modelo"].predict(test_df.iloc[idx_activos])
        pred_final[idx_activos] = np.where(pred_parado == 1, "Parado", "Ocupado")

    y_true_final = test_df["TARGET_MACRO"].astype(str).to_numpy()
    etiquetas_finales = ["Inactivo", "Ocupado", "Parado"]
    informe_combinado = classification_report(y_true_final, pred_final, labels=etiquetas_finales)
    print(informe_combinado)

    guardar_matriz_confusion(
        y_true_final, pred_final, etiquetas_finales, etiquetas_finales,
        "Matriz de confusión combinada (3 clases) — Fase 1", FIGURES_FASE1_DIR / "combinado_matriz_confusion.png",
    )

    # --- Persistir informe y comparación de candidatos ---
    guardar_json(
        {"etapa_a": resultado_a["comparacion"], "etapa_b": resultado_b["comparacion"]},
        REPORTS_FASE1_DIR / "comparacion_modelos.json",
    )
    with open(REPORTS_FASE1_DIR / "informe_final.txt", "w", encoding="utf-8") as f:
        f.write(f"MODELADO FASE 1 — Ganador Etapa A: {resultado_a['ganador']} | Ganador Etapa B: {resultado_b['ganador']}\n\n")
        f.write("=== Etapa A: Activo vs Inactivo ===\n")
        f.write(resultado_a["informe_texto"] + "\n\n")
        f.write("=== Etapa B: Ocupado vs Parado ===\n")
        f.write(resultado_b["informe_texto"] + "\n\n")
        f.write("=== Combinado (3 clases), encadenando A -> B en el test temporal ===\n")
        f.write(informe_combinado + "\n")

    print(f"\nArtefactos guardados en {MODELS_FASE1_DIR}, {REPORTS_FASE1_DIR} y {FIGURES_FASE1_DIR}.")
    print("Modelado de Fase 1 completado.")

    return {"etapa_a": resultado_a, "etapa_b": resultado_b, "informe_combinado": informe_combinado}


if __name__ == "__main__":
    ejecutar_pipeline_fase1()
