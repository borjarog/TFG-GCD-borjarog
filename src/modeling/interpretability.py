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

# RF one-hot + muchos árboles: 3000 muestras × 2 pasadas era inabordable.
TAMANO_MUESTRA_SHAP = 1_500
TAMANO_MUESTRA_SHAP_RF = 600


def _tamano_muestra_shap(modelo: ModeloEnvuelto) -> int:
    if modelo.nombre == "random_forest":
        return TAMANO_MUESTRA_SHAP_RF
    return TAMANO_MUESTRA_SHAP


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
    n = min(_tamano_muestra_shap(modelo), len(df_test))
    print(f"  SHAP: calculando sobre {n:,} filas ({modelo.nombre})...")
    muestra = df_test.sample(n=n, random_state=RANDOM_STATE)
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
    modelo: ModeloEnvuelto,
    df_test: pd.DataFrame,
    titulo: str,
    ruta_salida: Path,
    top_n: int = 20,
    valores_shap=None,
    nombres=None,
) -> None:
    """Importancia media |SHAP|. Si se pasan valores ya calculados, no recomputa."""
    if valores_shap is None or nombres is None:
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


def graficar_shap_completo(
    modelo: ModeloEnvuelto,
    df_test: pd.DataFrame,
    titulo_base: str,
    ruta_summary: Path,
    ruta_barras: Path,
    top_n: int = 20,
) -> None:
    """Beeswarm + barras con un único cálculo SHAP (evita duplicar horas en RF)."""
    valores_shap, X, nombres = _preparar_matriz_shap(modelo, df_test)

    fig = plt.figure(figsize=(8, 6))
    shap.summary_plot(valores_shap, X, feature_names=nombres, show=False, max_display=15)
    plt.title(titulo_base)
    plt.tight_layout()
    fig.savefig(ruta_summary, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  SHAP beeswarm -> {ruta_summary.name}")

    graficar_shap_importancia_barras(
        modelo,
        df_test,
        f"Importancia media |SHAP| — {titulo_base}",
        ruta_barras,
        top_n=top_n,
        valores_shap=valores_shap,
        nombres=nombres,
    )
    print(f"  SHAP barras -> {ruta_barras.name}")


def graficar_shap_waterfalls(
    modelo: ModeloEnvuelto,
    df_test: pd.DataFrame,
    y_true: pd.Series,
    y_proba: np.ndarray,
    umbral: float,
    dir_salida: Path,
    max_display: int = 12,
) -> list[Path]:
    """Genera 3 waterfalls: TP subempleo, TN no-subempleo, y un error (FP o FN)."""
    dir_salida.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    y_pred = (y_proba >= umbral).astype(int)

    def _pick(mask: np.ndarray, prefer_high_proba: bool) -> int | None:
        idx = np.where(mask)[0]
        if len(idx) == 0:
            return None
        orden = np.argsort(y_proba[idx])
        elegido = idx[orden[-1]] if prefer_high_proba else idx[orden[0]]
        return int(elegido)

    casos = [
        (
            "tp_subempleo",
            "Caso TP — subempleo real y predicho",
            _pick((y_true_arr == 1) & (y_pred == 1), prefer_high_proba=True),
        ),
        (
            "tn_no_subempleo",
            "Caso TN — no subempleo real y predicho",
            _pick((y_true_arr == 0) & (y_pred == 0), prefer_high_proba=False),
        ),
    ]
    # Preferir un FN (subempleo perdido); si no hay, un FP
    idx_fn = _pick((y_true_arr == 1) & (y_pred == 0), prefer_high_proba=True)
    idx_fp = _pick((y_true_arr == 0) & (y_pred == 1), prefer_high_proba=True)
    if idx_fn is not None:
        casos.append(("fn_subempleo", "Caso FN — subempleo real no detectado", idx_fn))
    elif idx_fp is not None:
        casos.append(("fp_subempleo", "Caso FP — falso subempleo", idx_fp))

    rutas: list[Path] = []
    # Fondo pequeño para TreeExplainer (nativo LightGBM no lo necesita, pero ayuda estabilidad)
    fondo = df_test.sample(n=min(200, len(df_test)), random_state=RANDOM_STATE)
    X_fondo = modelo.transformar(fondo)
    explicador = _explicador_para(modelo, X_fondo)

    for slug, titulo, idx in casos:
        if idx is None:
            print(f"  (Aviso: no hay filas para {slug})")
            continue
        fila = df_test.iloc[[idx]]
        X = modelo.transformar(fila)
        if hasattr(X, "toarray"):
            X = X.toarray()

        valores = explicador.shap_values(X)
        if isinstance(valores, list):
            valores = valores[1]
        if hasattr(valores, "ndim") and valores.ndim == 3:
            valores = valores[:, :, 1]
        valores = np.asarray(valores)
        if valores.ndim == 2:
            valores = valores[0]

        expected = explicador.expected_value
        if isinstance(expected, (list, np.ndarray)):
            expected = expected[1] if len(np.atleast_1d(expected)) > 1 else float(np.ravel(expected)[0])
        expected = float(expected)

        nombres = modelo.nombres_features()
        # Datos de display: para nativo usar la fila de features; para sklearn, valores numéricos
        if modelo.familia == "nativo":
            data_row = X.iloc[0] if hasattr(X, "iloc") else X[0]
            if hasattr(X, "iloc"):
                data_vals = []
                for c in nombres:
                    if c in X.columns:
                        data_vals.append(X.iloc[0][c])
                    else:
                        data_vals.append(np.nan)
                data_vals = np.array(data_vals, dtype=object)
            else:
                data_vals = np.asarray(data_row)
        else:
            data_vals = np.asarray(X[0] if np.ndim(X) > 1 else X)

        explanation = shap.Explanation(
            values=valores,
            base_values=expected,
            data=data_vals,
            feature_names=list(nombres),
        )

        plt.figure(figsize=(9, 6))
        shap.plots.waterfall(explanation, max_display=max_display, show=False)
        plt.title(
            f"{titulo}\nP(subempleo)={y_proba[idx]:.3f} | umbral={umbral:.3f} | y={y_true_arr[idx]}",
            fontsize=11,
        )
        ruta = dir_salida / f"shap_waterfall_{slug}.png"
        plt.tight_layout()
        plt.savefig(ruta, dpi=160, bbox_inches="tight", facecolor="#f4f6f8")
        plt.close("all")
        rutas.append(ruta)
        print(f"  -> {ruta.name} (idx={idx}, proba={y_proba[idx]:.3f})")

    return rutas
