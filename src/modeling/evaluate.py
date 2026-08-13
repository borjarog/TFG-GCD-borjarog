"""Métricas y figuras de evaluación.

Con desbalance la accuracy engaña; el criterio de selección es PR-AUC.
También se reportan ROC-AUC, F1 y balanced accuracy.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)


def metricas_binarias(y_true, y_pred, y_proba) -> dict:
    return {
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
    }


def umbral_optimo_f1(y_true, y_proba) -> float:
    """Umbral de la rejilla que maximiza F1 de la clase positiva."""
    mejores_f1, mejor_umbral = -1.0, 0.5
    for umbral in np.linspace(0.05, 0.95, 37):
        pred = (y_proba >= umbral).astype(int)
        if pred.sum() == 0:
            continue
        score = f1_score(y_true, pred, zero_division=0)
        if score > mejores_f1:
            mejores_f1, mejor_umbral = score, float(umbral)
    return mejor_umbral


def metricas_baseline_prevalencia(y_train, y_test) -> dict:
    """Baseline: todos los casos con la prevalencia del positivo en train."""
    prevalencia = float(np.asarray(y_train).mean())
    y_proba = np.full(len(y_test), prevalencia, dtype=float)
    y_pred = (y_proba >= 0.5).astype(int)
    metricas = metricas_binarias(y_test, y_pred, y_proba)
    metricas["prevalencia_train"] = prevalencia
    metricas["segundos_entrenamiento"] = 0.0
    metricas["filas_entreno"] = int(len(y_train))
    metricas["mejores_hiperparametros"] = {"strategy": "score_constante_prevalencia"}
    metricas["pr_auc_cv_busqueda"] = None
    return metricas


def reporte_texto_binario(y_true, y_pred, target_names: list[str]) -> str:
    return classification_report(y_true, y_pred, target_names=target_names)


def guardar_matriz_confusion(
    y_true, y_pred, valores_clases: list, etiquetas_visibles: list[str], titulo: str, ruta_salida: Path
) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        labels=valores_clases,
        display_labels=etiquetas_visibles,
        cmap="Blues",
        ax=ax,
        colorbar=False,
    )
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def guardar_curva_pr(y_true, y_proba, titulo: str, ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5))
    PrecisionRecallDisplay.from_predictions(y_true, y_proba, ax=ax)
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def guardar_importancia_variables(importancias: pd.Series, titulo: str, ruta_salida: Path, top_n: int = 20) -> None:
    top = importancias.sort_values(ascending=False).head(top_n).sort_values()
    fig, ax = plt.subplots(figsize=(7, max(4, top_n * 0.3)))
    ax.barh(top.index.astype(str), top.values, color="#2b6cb0")
    ax.set_title(titulo)
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def guardar_json(datos: dict, ruta_salida: Path) -> None:
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
