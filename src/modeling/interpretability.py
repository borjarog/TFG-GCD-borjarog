"""Interpretabilidad con SHAP para el modelo ganador de cada etapa de Fase 1."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import shap

from .config import RANDOM_STATE
from .preprocessing import ModeloEnvuelto

TAMANO_MUESTRA_SHAP = 3_000


def _explicador_para(modelo: ModeloEnvuelto, X_fondo):
    if modelo.nombre == "regresion_logistica":
        # LinearExplainer necesita un fondo (background) para calcular el valor esperado.
        return shap.LinearExplainer(modelo.estimador, X_fondo)
    # LightGBM y Random Forest son ambos basados en árboles: TreeExplainer es exacto y rápido.
    return shap.TreeExplainer(modelo.estimador)


def graficar_shap_summary(modelo: ModeloEnvuelto, df_test: pd.DataFrame, titulo: str, ruta_salida: Path) -> None:
    """Genera y guarda un summary plot de SHAP sobre una muestra del test."""
    muestra = df_test.sample(
        n=min(TAMANO_MUESTRA_SHAP, len(df_test)), random_state=RANDOM_STATE
    )
    X = modelo.transformar(muestra)
    if hasattr(X, "toarray"):
        X = X.toarray()
    nombres = modelo.nombres_features()

    explicador = _explicador_para(modelo, X)
    valores_shap = explicador.shap_values(X)
    # Para clasificación binaria algunos explainers devuelven una lista [clase0, clase1].
    if isinstance(valores_shap, list):
        valores_shap = valores_shap[1]
    # TreeExplainer en modo multiclase-shape (n, features, clases): nos quedamos con la clase positiva.
    if hasattr(valores_shap, "ndim") and valores_shap.ndim == 3:
        valores_shap = valores_shap[:, :, 1]

    fig = plt.figure(figsize=(8, 6))
    shap.summary_plot(valores_shap, X, feature_names=nombres, show=False, max_display=15)
    plt.title(titulo)
    plt.tight_layout()
    fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(fig)
