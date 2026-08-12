"""Interpretabilidad con SHAP para los modelos ganadores de Fase 1 y Fase 2."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from .config import RANDOM_STATE
from .preprocessing import ModeloEnvuelto

TAMANO_MUESTRA_SHAP = 3_000


def _explicador_para(modelo: ModeloEnvuelto, X_fondo):
    if modelo.nombre == "regresion_logistica":
        return shap.LinearExplainer(modelo.estimador, X_fondo)
    return shap.TreeExplainer(modelo.estimador)


def _valores_shap_clase_positiva(explicador, X):
    valores_shap = explicador.shap_values(X)
    if isinstance(valores_shap, list):
        valores_shap = valores_shap[1]
    if hasattr(valores_shap, "ndim") and valores_shap.ndim == 3:
        valores_shap = valores_shap[:, :, 1]
    return np.asarray(valores_shap)


def _preparar_matriz_shap(modelo: ModeloEnvuelto, df_test: pd.DataFrame):
    muestra = df_test.sample(
        n=min(TAMANO_MUESTRA_SHAP, len(df_test)), random_state=RANDOM_STATE
    )
    X = modelo.transformar(muestra)
    if hasattr(X, "toarray"):
        X = X.toarray()
    nombres = modelo.nombres_features()
    explicador = _explicador_para(modelo, X)
    valores_shap = _valores_shap_clase_positiva(explicador, X)
    return valores_shap, X, nombres


def graficar_shap_summary(modelo: ModeloEnvuelto, df_test: pd.DataFrame, titulo: str, ruta_salida: Path) -> None:
    """Summary beeswarm de SHAP sobre una muestra del test."""
    valores_shap, X, nombres = _preparar_matriz_shap(modelo, df_test)

    fig = plt.figure(figsize=(8, 6))
    shap.summary_plot(valores_shap, X, feature_names=nombres, show=False, max_display=15)
    plt.title(titulo)
    plt.tight_layout()
    fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close("all")


def graficar_shap_importancia_barras(
    modelo: ModeloEnvuelto, df_test: pd.DataFrame, titulo: str, ruta_salida: Path, top_n: int = 20
) -> None:
    """Importancia media |SHAP|: útil cuando el beeswarm no colorea bien las categóricas nativas."""
    valores_shap, _, nombres = _preparar_matriz_shap(modelo, df_test)
    importancia = pd.Series(np.abs(valores_shap).mean(axis=0), index=nombres)
    top = importancia.sort_values(ascending=False).head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.32)))
    ax.barh(top.index.astype(str), top.values, color="#2b6cb0")
    ax.set_xlabel("Importancia media |SHAP|")
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(fig)
