"""Cierre académico Fase 2 — prioridad 1.

Incluye:
1. Ablación demografía vs modelo laboral completo (LightGBM)
2. Baseline de prevalencia
3. Waterfalls SHAP locales (3 casos)
4. Análisis de errores por jornada / sector / ocupación / CCAA

Uso:
    python run_fase2_cierre.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from joblib import parallel_backend

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
    TAMANO_MUESTRA_BUSQUEDA,
)
from .evaluate import (
    guardar_json,
    metricas_baseline_prevalencia,
    metricas_binarias,
    umbral_optimo_f1,
)
from .fase2 import _submuestra_estratificada, obtener_columnas_features
from .interpretability import graficar_shap_waterfalls
from .model_specs import construir_candidatos
from .preprocessing import (
    COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2,
    COLUMNAS_NUMERICAS_FASE2,
    ModeloEnvuelto,
    preparar_features_nativo,
    split_temporal,
)

# Predictoras demográficas presentes en el dataset Fase 2 (sin variables del puesto).
FEATURES_DEMOGRAFICAS_FASE2 = [
    "ANIO_REF",
    "TRIMESTRE_REF",
    "CCAA",
    "PROV",
    "SEXO",
    "TRAMO_EDAD",
    "NIVEL_EDUC",
    "ESTADO_CIVIL",
    "NACIONALIDAD",
    "ROL_HOGAR",
    "ESTUDIANDO_AHORA",
    "TAM_HOGAR",
    "CARGA_FAMILIAR",
    "VULNERABILIDAD_JOVEN",
]

FIGURES_CIERRE = FIGURES_FASE2_DIR / "cierre"
REPORTS_CIERRE = REPORTS_FASE2_DIR / "cierre"


def _candidato_lightgbm():
    return next(c for c in construir_candidatos(RANDOM_STATE) if c.nombre == "lightgbm")


def _numericas_para(features: list[str]) -> tuple[list[str], list[str]]:
    nums = [c for c in COLUMNAS_NUMERICAS_FASE2 if c in features]
    nulos = [c for c in COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2 if c in features]
    return nums, nulos


def entrenar_ablacion_demografica(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict:
    """LightGBM solo con demografía — contraste con el modelo laboral completo."""
    features = [c for c in FEATURES_DEMOGRAFICAS_FASE2 if c in train_df.columns]
    print(f"\n{'=' * 70}\n ABLACIÓN: solo demografía ({len(features)} features)\n{'=' * 70}")
    print(f"  Features: {', '.join(features)}")

    candidato = _candidato_lightgbm()
    df_muestra, y_muestra = _submuestra_estratificada(
        train_df, y_train, TAMANO_MUESTRA_BUSQUEDA, RANDOM_STATE
    )
    nums, nulos = _numericas_para(features)
    X_muestra = preparar_features_nativo(df_muestra, features, nums, nulos)
    estimador = clone(candidato.estimador)
    busqueda = RandomizedSearchCV(
        estimator=estimador,
        param_distributions=dict(candidato.espacio_busqueda),
        n_iter=min(12, N_ITER_BUSQUEDA),
        scoring="average_precision",
        cv=StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE),
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=False,
    )
    print("  Buscando hiperparámetros (LightGBM demográfico)...")
    t0 = time.time()
    with parallel_backend("threading"):
        busqueda.fit(X_muestra, y_muestra)
    print(f"  Búsqueda en {time.time() - t0:.1f}s. PR-AUC CV={busqueda.best_score_:.4f}")

    params = dict(busqueda.best_params_)
    params["n_jobs"] = -1
    modelo = ModeloEnvuelto(
        "lightgbm",
        "nativo",
        clone(candidato.estimador).set_params(**params),
        features,
        nums,
        nulos,
    )
    t0 = time.time()
    modelo.fit(train_df, y_train)
    dur = time.time() - t0
    y_proba = modelo.predict_proba(test_df)
    y_pred = (y_proba >= 0.5).astype(int)
    metricas = metricas_binarias(y_test, y_pred, y_proba)
    metricas["segundos_entrenamiento"] = round(dur, 1)
    metricas["filas_entreno"] = len(train_df)
    metricas["mejores_hiperparametros"] = {
        k: (float(v) if hasattr(v, "item") else v) for k, v in params.items() if k != "n_jobs"
    }
    metricas["pr_auc_cv_busqueda"] = round(float(busqueda.best_score_), 4)
    metricas["n_features"] = len(features)
    metricas["features"] = features

    df_cal, y_cal = _submuestra_estratificada(train_df, y_train, 80_000, RANDOM_STATE + 3)
    umbral = umbral_optimo_f1(y_cal, modelo.predict_proba(df_cal))
    metricas_opt = metricas_binarias(y_test, (y_proba >= umbral).astype(int), y_proba)

    print(
        f"  Test @0.50 -> PR-AUC={metricas['pr_auc']:.4f}  ROC-AUC={metricas['roc_auc']:.4f}  "
        f"F1={metricas['f1']:.4f}"
    )
    print(f"  Umbral F1={umbral:.3f} -> F1={metricas_opt['f1']:.4f}")

    joblib.dump(modelo, MODELS_FASE2_DIR / "subempleo_ablacion_demografica_lightgbm.joblib")
    return {
        "modelo": modelo,
        "metricas_05": metricas,
        "metricas_umbral_optimo": metricas_opt,
        "umbral": umbral,
        "y_proba": y_proba,
    }


def graficar_ablacion(comparacion: dict, ruta: Path) -> None:
    """Barras PR-AUC / ROC-AUC: baseline vs demografía vs laboral completo."""
    orden = ["baseline_prevalencia", "solo_demografia", "modelo_completo"]
    etiquetas = {
        "baseline_prevalencia": "Baseline\n(prevalencia)",
        "solo_demografia": "Solo\ndemografía",
        "modelo_completo": "Modelo completo\n(+ laborales)",
    }
    colores = ["#94a3b8", "#1d4ed8", "#0d5c63"]

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2))
    for ax, metrica, titulo in zip(
        axes,
        ["pr_auc", "roc_auc"],
        ["PR-AUC (test)", "ROC-AUC (test)"],
    ):
        vals = [comparacion[k][metrica] for k in orden]
        bars = ax.bar(
            [etiquetas[k] for k in orden],
            vals,
            color=colores,
            width=0.65,
        )
        ax.set_ylim(0, 1.05)
        ax.set_title(titulo, fontweight="bold")
        for b, v in zip(bars, vals):
            ax.text(
                b.get_x() + b.get_width() / 2,
                v + 0.02,
                f"{v:.3f}",
                ha="center",
                fontsize=10,
                fontweight="bold",
            )
        sns.despine(ax=ax)
    fig.suptitle(
        "Ablación Fase 2: valor añadido de las variables laborales",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=160, bbox_inches="tight", facecolor="#f4f6f8")
    plt.close(fig)
    print(f"  -> {ruta}")


def analizar_errores(
    test_df: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
) -> dict:
    """Tasas de subempleo real/predicho y errores por variables clave."""
    tmp = test_df.copy()
    tmp["y_true"] = y_true.to_numpy()
    tmp["y_pred"] = y_pred
    tmp["y_proba"] = y_proba
    tmp["acierto"] = (tmp["y_true"] == tmp["y_pred"]).astype(int)
    tmp["fp"] = ((tmp["y_true"] == 0) & (tmp["y_pred"] == 1)).astype(int)
    tmp["fn"] = ((tmp["y_true"] == 1) & (tmp["y_pred"] == 0)).astype(int)

    grupos = {}
    for col, top_n, titulo, fname in [
        ("TIPO_JORNADA", 10, "Tipo de jornada", "errores_por_jornada.png"),
        ("SECTOR_ACTIVIDAD", 12, "Sector de actividad", "errores_por_sector.png"),
        ("OCUPACION", 12, "Ocupación", "errores_por_ocupacion.png"),
        ("CCAA_NOMBRE" if "CCAA_NOMBRE" in tmp.columns else "CCAA", 20, "CCAA", "errores_por_ccaa.png"),
    ]:
        if col not in tmp.columns:
            continue
        g = (
            tmp.groupby(col, observed=True)
            .agg(
                n=("y_true", "size"),
                tasa_real=("y_true", "mean"),
                tasa_pred=("y_pred", "mean"),
                pct_fp=("fp", "mean"),
                pct_fn=("fn", "mean"),
                accuracy=("acierto", "mean"),
            )
            .reset_index()
        )
        g = g[g["n"] >= 500].sort_values("tasa_real", ascending=False).head(top_n)
        g["tasa_real"] *= 100
        g["tasa_pred"] *= 100
        g["pct_fp"] *= 100
        g["pct_fn"] *= 100
        g["accuracy"] *= 100
        grupos[col] = g

        fig, ax = plt.subplots(figsize=(9, max(3.5, len(g) * 0.38)))
        y = np.arange(len(g))
        labels = g[col].astype(str).str.slice(0, 42)
        ax.barh(y - 0.18, g["tasa_real"], height=0.35, color="#b45309", label="% subempleo real")
        ax.barh(y + 0.18, g["tasa_pred"], height=0.35, color="#0d5c63", label="% predicho (umbral)")
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("%")
        ax.set_title(f"Subempleo real vs predicho — {titulo}")
        ax.legend(frameon=False, loc="lower right")
        sns.despine(ax=ax)
        fig.tight_layout()
        ruta = FIGURES_CIERRE / fname
        fig.savefig(ruta, dpi=160, bbox_inches="tight", facecolor="#f4f6f8")
        plt.close(fig)
        print(f"  -> {ruta}")

        g.to_csv(REPORTS_CIERRE / fname.replace(".png", ".csv"), index=False, encoding="utf-8")

    return {k: v.to_dict(orient="records") for k, v in grupos.items()}


def ejecutar_cierre_fase2() -> dict:
    FIGURES_CIERRE.mkdir(parents=True, exist_ok=True)
    REPORTS_CIERRE.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" FASE 2 — CIERRE PRIORIDAD 1 (ablación, XAI local, errores, baseline)")
    print("=" * 70)

    df = pd.read_parquet(DATASET_FASE2)
    features_full = obtener_columnas_features(df)
    train_df, test_df = split_temporal(df, CORTE_ANIO, CORTE_TRIMESTRE)
    y_train = train_df["TARGET_SUBEMPLEO"].astype(int)
    y_test = test_df["TARGET_SUBEMPLEO"].astype(int)

    # --- Baseline ---
    print("\n--- Baseline prevalencia ---")
    baseline = metricas_baseline_prevalencia(y_train, y_test)
    print(f"  PR-AUC={baseline['pr_auc']:.4f}  (prevalencia={baseline['prevalencia_train']:.4f})")

    # --- Modelo completo ya entrenado ---
    ruta_modelo = MODELS_FASE2_DIR / "subempleo_lightgbm.joblib"
    ruta_umbral = MODELS_FASE2_DIR / "umbral_decision.json"
    if not ruta_modelo.exists():
        raise FileNotFoundError(f"No está el modelo completo en {ruta_modelo}. Ejecuta run_model_fase2.py primero.")

    print("\n--- Cargando modelo laboral completo ---")
    modelo_full = joblib.load(ruta_modelo)
    with open(ruta_umbral, encoding="utf-8") as f:
        meta = json.load(f)
    umbral_full = float(meta["umbral_f1_train"])
    y_proba_full = modelo_full.predict_proba(test_df)
    y_pred_full = (y_proba_full >= umbral_full).astype(int)
    metricas_full_05 = metricas_binarias(y_test, (y_proba_full >= 0.5).astype(int), y_proba_full)
    metricas_full_opt = metricas_binarias(y_test, y_pred_full, y_proba_full)
    print(
        f"  Completo @0.50 PR-AUC={metricas_full_05['pr_auc']:.4f} | "
        f"@{umbral_full:.3f} F1={metricas_full_opt['f1']:.4f}"
    )

    # --- Ablación demográfica ---
    ablacion = entrenar_ablacion_demografica(train_df, test_df, y_train, y_test)

    comparacion_ablacion = {
        "baseline_prevalencia": {
            "pr_auc": baseline["pr_auc"],
            "roc_auc": baseline["roc_auc"],
            "f1": baseline["f1"],
        },
        "solo_demografia": {
            "pr_auc": ablacion["metricas_05"]["pr_auc"],
            "roc_auc": ablacion["metricas_05"]["roc_auc"],
            "f1": ablacion["metricas_05"]["f1"],
            "f1_umbral_optimo": ablacion["metricas_umbral_optimo"]["f1"],
            "umbral": ablacion["umbral"],
            "n_features": ablacion["metricas_05"]["n_features"],
        },
        "modelo_completo": {
            "pr_auc": metricas_full_05["pr_auc"],
            "roc_auc": metricas_full_05["roc_auc"],
            "f1": metricas_full_05["f1"],
            "f1_umbral_optimo": metricas_full_opt["f1"],
            "umbral": umbral_full,
            "n_features": len(features_full),
        },
    }
    graficar_ablacion(comparacion_ablacion, FIGURES_CIERRE / "ablacion_demografia_vs_laboral.png")

    # --- Errores ---
    print(f"\n{'=' * 70}\n ANÁLISIS DE ERRORES\n{'=' * 70}")
    errores = analizar_errores(test_df, y_test, y_pred_full, y_proba_full)

    # --- Waterfalls ---
    print(f"\n{'=' * 70}\n SHAP LOCAL (waterfalls)\n{'=' * 70}")
    rutas_wf = graficar_shap_waterfalls(
        modelo_full,
        test_df,
        y_test,
        y_proba_full,
        umbral_full,
        FIGURES_CIERRE,
    )

    # --- Resumen markdown ---
    salto_pr = metricas_full_05["pr_auc"] - ablacion["metricas_05"]["pr_auc"]
    md = [
        "# Cierre Fase 2 — Prioridad 1",
        "",
        "## Ablación",
        f"- Baseline PR-AUC: **{baseline['pr_auc']:.4f}**",
        f"- Solo demografía (LightGBM, {ablacion['metricas_05']['n_features']} vars): "
        f"**PR-AUC={ablacion['metricas_05']['pr_auc']:.4f}**",
        f"- Modelo completo (+ laborales, {len(features_full)} vars): "
        f"**PR-AUC={metricas_full_05['pr_auc']:.4f}**",
        f"- Salto demografía → completo: **+{salto_pr:.4f}** PR-AUC",
        "",
        "## Umbrales F1 (train)",
        f"- Completo: {umbral_full:.3f} → F1 test={metricas_full_opt['f1']:.4f}",
        f"- Ablación: {ablacion['umbral']:.3f} → F1 test={ablacion['metricas_umbral_optimo']['f1']:.4f}",
        "",
        "## Figuras",
        "- `ablacion_demografia_vs_laboral.png`",
        "- `errores_por_jornada.png` / sector / ocupación / CCAA",
        "- Waterfalls SHAP locales",
        "",
        "## Lectura",
        "Las variables laborales aportan la mayor parte del poder predictivo del subempleo;",
        "la demografía sola apenas supera el baseline en PR-AUC relativo al modelo completo.",
        "",
    ]
    (REPORTS_CIERRE / "resumen_cierre.md").write_text("\n".join(md), encoding="utf-8")

    payload = {
        "ablacion": comparacion_ablacion,
        "errores_resumen_keys": list(errores.keys()),
        "waterfalls": [str(p.name) for p in rutas_wf],
        "umbral_modelo_completo": umbral_full,
    }
    guardar_json(payload, REPORTS_CIERRE / "cierre_prioridad1.json")
    print(f"\nResumen: {REPORTS_CIERRE / 'resumen_cierre.md'}")
    print("Cierre prioridad 1 completado.")
    return payload


if __name__ == "__main__":
    ejecutar_cierre_fase2()
