"""Figuras EDA para la memoria (`reports/memoria/eda/`)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_engineering.config import (  # noqa: E402
    DATASET_FASE1,
    DATASET_FASE2,
    INTERIM_EPA,
)

# Colores de estado laboral y de dataset van aparte (si no se mezclan en las leyendas).
COLORES = {
    "fondo": "#f4f6f8",
    "texto": "#1a2332",
    "gris": "#8b9aab",
    # Semántica — estado laboral / subempleo
    "ocupado": "#0d5c63",
    "parado": "#c45c26",
    "inactivo": "#5b6b7c",
    "subempleo": "#b45309",
    "no_subempleo": "#94a3b8",
    # Semántica — sexo (distinto de targets)
    "hombre": "#334155",
    "mujer": "#be185d",
    # Meta — etapas del pipeline / datasets
    # (azul + dorado: lejos del teal Ocupado y del terracota Parado/Subempleo)
    "dataset_interim": "#64748b",
    "dataset_f1": "#1d4ed8",
    "dataset_f2": "#eab308",
}

EDA_DIR = PROJECT_ROOT / "reports" / "memoria" / "eda"
RESUMEN_MD = EDA_DIR / "resumen_eda.md"
RESUMEN_JSON = EDA_DIR / "resumen_eda.json"


def _aplicar_estilo() -> None:
    sns.set_theme(style="whitegrid", font="DejaVu Sans")
    plt.rcParams.update(
        {
            "figure.facecolor": COLORES["fondo"],
            "axes.facecolor": COLORES["fondo"],
            "axes.edgecolor": COLORES["gris"],
            "axes.labelcolor": COLORES["texto"],
            "text.color": COLORES["texto"],
            "xtick.color": COLORES["texto"],
            "ytick.color": COLORES["texto"],
            "grid.color": "#dde3ea",
            "grid.linewidth": 0.6,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "savefig.facecolor": COLORES["fondo"],
        }
    )


def _guardar(fig: plt.Figure, nombre: str) -> Path:
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    ruta = EDA_DIR / nombre
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  -> {ruta.relative_to(PROJECT_ROOT)}")
    return ruta


def fig_volumenes(n_interim: int, n_fase1: int, n_fase2: int) -> Path:
    """Comparativa de tamaños a lo largo del pipeline."""
    labels = [
        "Interim\n(todos los registros)",
        "Fase 1 ML\n(edad activa 16–64)",
        "Fase 2 ML\n(ocupados)",
    ]
    valores = [n_interim, n_fase1, n_fase2]
    colores = [COLORES["dataset_interim"], COLORES["dataset_f1"], COLORES["dataset_f2"]]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bars = ax.bar(labels, valores, color=colores, width=0.62, edgecolor="none")
    ax.set_ylabel("Número de registros (personas-trimestre)")
    ax.set_title("Volumen de datos a lo largo del pipeline")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.2f}M"))
    for bar, v in zip(bars, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.01,
            f"{v:,}".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=COLORES["texto"],
        )
    ax.set_ylim(0, max(valores) * 1.15)
    sns.despine(ax=ax, left=False)
    return _guardar(fig, "01_volumenes_pipeline.png")


def fig_cobertura_temporal(interim: pd.DataFrame) -> Path:
    conteo = (
        interim.groupby(["ANIO_REF", "TRIMESTRE_REF"], observed=True)
        .size()
        .reset_index(name="n")
    )
    conteo["periodo"] = (
        conteo["ANIO_REF"].astype(int).astype(str)
        + "T"
        + conteo["TRIMESTRE_REF"].astype(int).astype(str)
    )
    conteo = conteo.sort_values(["ANIO_REF", "TRIMESTRE_REF"])

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.fill_between(range(len(conteo)), conteo["n"], color=COLORES["dataset_interim"], alpha=0.25)
    ax.plot(range(len(conteo)), conteo["n"], color=COLORES["dataset_interim"], lw=2.2, marker="o", ms=4)
    ax.set_xticks(range(len(conteo)))
    ax.set_xticklabels(conteo["periodo"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Registros por trimestre")
    ax.set_title("Cobertura temporal de la EPA (interim 2021+)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
    sns.despine(ax=ax)
    return _guardar(fig, "02_cobertura_temporal.png")


def fig_target_fase1(f1: pd.DataFrame) -> Path:
    orden = ["Ocupado", "Parado", "Inactivo"]
    colores = [COLORES["ocupado"], COLORES["parado"], COLORES["inactivo"]]
    counts = f1["TARGET_MACRO"].value_counts().reindex(orden)
    pct = (counts / counts.sum() * 100).round(1)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [1.1, 1]})
    axes[0].pie(
        counts,
        labels=[f"{o}\n{pct[o]}%" for o in orden],
        colors=colores,
        startangle=90,
        wedgeprops={"width": 0.55, "edgecolor": COLORES["fondo"], "linewidth": 2},
        textprops={"fontsize": 10, "color": COLORES["texto"]},
    )
    axes[0].set_title("Distribución TARGET_MACRO\n(Fase 1 · 16–64)")

    axes[1].barh(orden[::-1], counts[::-1], color=colores[::-1], height=0.55)
    for y, (lab, v) in enumerate(zip(orden[::-1], counts[::-1])):
        axes[1].text(v * 1.01, y, f"{v:,.0f}".replace(",", "."), va="center", fontsize=9)
    axes[1].set_xlabel("Registros")
    axes[1].set_title("Conteos absolutos")
    axes[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"))
    sns.despine(ax=axes[1])
    fig.tight_layout()
    return _guardar(fig, "03_target_fase1_macro.png")


def fig_edad_sexo_fase1(f1: pd.DataFrame) -> Path:
    # Orden natural de tramos
    orden_edad = [
        "16 a 19 años",
        "20 a 24 años",
        "25 a 29 años",
        "30 a 34 años",
        "35 a 39 años",
        "40 a 44 años",
        "45 a 49 años",
        "50 a 54 años",
        "55 a 59 años",
        "60 a 64 años",
    ]
    ct = pd.crosstab(f1["TRAMO_EDAD"], f1["SEXO"])
    # etiquetas pueden variar ligeramente; reindex flexible
    idx = [i for i in orden_edad if i in ct.index]
    ct = ct.reindex(idx)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(ct))
    w = 0.38
    c_h = ct.get("Hombre", ct.iloc[:, 0] if "Hombre" not in ct.columns else ct["Hombre"])
    c_m = ct.get("Mujer", ct.iloc[:, 1] if len(ct.columns) > 1 else 0)
    if "Hombre" in ct.columns:
        c_h = ct["Hombre"]
    if "Mujer" in ct.columns:
        c_m = ct["Mujer"]
    ax.bar(x - w / 2, c_h, w, label="Hombre", color=COLORES["hombre"])
    ax.bar(x + w / 2, c_m, w, label="Mujer", color=COLORES["mujer"])
    ax.set_xticks(x)
    ax.set_xticklabels([t.replace(" años", "") for t in ct.index], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Registros")
    ax.set_title("Pirámide simplificada: tramo de edad × sexo (Fase 1)")
    ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1e3:.0f}k"))
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "04_edad_sexo_fase1.png")


def fig_educacion_vs_estado(f1: pd.DataFrame) -> Path:
    # Agrupar niveles largos del INE en etiquetas cortas
    def _corto(nivel: str) -> str:
        s = str(nivel)
        if "superior" in s.lower():
            return "Superior"
        if "secundaria" in s.lower() or "segunda" in s.lower():
            return "Secundaria"
        if "primaria" in s.lower():
            return "Primaria"
        if "analfabet" in s.lower() or s.startswith("AN") or "sin estudios" in s.lower():
            return "Sin / muy bajo"
        if "Desconocido" in s:
            return "Desconocido"
        return "Otros"

    tmp = f1.copy()
    tmp["EDUC_CORTO"] = tmp["NIVEL_EDUC"].astype(str).map(_corto)
    orden_e = ["Sin / muy bajo", "Primaria", "Secundaria", "Superior", "Otros", "Desconocido"]
    orden_e = [e for e in orden_e if e in set(tmp["EDUC_CORTO"])]
    ct = pd.crosstab(tmp["EDUC_CORTO"], tmp["TARGET_MACRO"], normalize="index") * 100
    ct = ct.reindex(orden_e)
    cols = [c for c in ["Ocupado", "Parado", "Inactivo"] if c in ct.columns]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ct[cols].plot(
        kind="bar",
        stacked=True,
        ax=ax,
        color=[COLORES["ocupado"], COLORES["parado"], COLORES["inactivo"]][: len(cols)],
        width=0.7,
        edgecolor=COLORES["fondo"],
    )
    ax.set_ylabel("% dentro del nivel educativo")
    ax.set_xlabel("")
    ax.set_title("Estado laboral según nivel educativo (Fase 1 · 16–64)")
    ax.legend(title="", frameon=False, loc="upper right")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_ylim(0, 100)
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "05_educacion_vs_estado.png")


def fig_subempleo_fase2(f2: pd.DataFrame) -> Path:
    tasa = f2["TARGET_SUBEMPLEO"].mean() * 100
    counts = f2["TARGET_SUBEMPLEO"].value_counts().sort_index()

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(
        ["No subempleo", "Subempleo\n(AOI=03)"],
        [counts.get(0, 0), counts.get(1, 0)],
        color=[COLORES["no_subempleo"], COLORES["subempleo"]],
        width=0.55,
    )
    axes[0].set_title("Conteo absoluto (ocupados)")
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"))
    for i, v in enumerate([counts.get(0, 0), counts.get(1, 0)]):
        axes[0].text(i, v * 1.01, f"{v:,}".replace(",", "."), ha="center", fontsize=9, fontweight="bold")
    sns.despine(ax=axes[0])

    # Gauge simple de tasa
    axes[1].barh([0], [100], color="#e2e8f0", height=0.35)
    axes[1].barh([0], [tasa], color=COLORES["subempleo"], height=0.35)
    axes[1].set_xlim(0, 100)
    axes[1].set_yticks([])
    axes[1].set_xlabel("% de ocupados en subempleo")
    axes[1].set_title(f"Tasa de subempleo: {tasa:.2f}%")
    axes[1].axvline(tasa, color=COLORES["texto"], lw=0.8, ls="--", alpha=0.5)
    axes[1].text(tasa + 1.5, 0, f"{tasa:.2f}%", va="center", fontweight="bold")
    sns.despine(ax=axes[1], left=True)
    fig.tight_layout()
    return _guardar(fig, "06_subempleo_fase2.png")


def fig_horas_vs_subempleo(f2: pd.DataFrame) -> Path:
    # EPA suele guardar horas×100 (p.ej. 4000 = 40,00 h)
    tmp = f2[["HORAS_HABITUALES", "HORAS_EFECTIVAS", "TARGET_SUBEMPLEO"]].copy()
    for c in ["HORAS_HABITUALES", "HORAS_EFECTIVAS"]:
        tmp[c] = pd.to_numeric(tmp[c], errors="coerce") / 100.0

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
    for ax, col, titulo in zip(
        axes,
        ["HORAS_HABITUALES", "HORAS_EFECTIVAS"],
        ["Horas habituales / semana", "Horas efectivas / semana"],
    ):
        data = [
            tmp.loc[tmp["TARGET_SUBEMPLEO"] == 0, col].dropna(),
            tmp.loc[tmp["TARGET_SUBEMPLEO"] == 1, col].dropna(),
        ]
        bp = ax.boxplot(
            data,
            tick_labels=["No subempleo", "Subempleo"],
            patch_artist=True,
            widths=0.55,
            showfliers=False,
        )
        for patch, color in zip(bp["boxes"], [COLORES["no_subempleo"], COLORES["subempleo"]]):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
        for median in bp["medians"]:
            median.set_color("white")
            median.set_linewidth(2)
        ax.set_title(titulo)
        ax.set_ylabel("Horas" if ax is axes[0] else "")
        sns.despine(ax=ax)
    fig.suptitle("Horas trabajadas según subempleo (Fase 2)", fontweight="bold", y=1.02)
    fig.tight_layout()
    return _guardar(fig, "07_horas_vs_subempleo.png")


def fig_jornada_vs_subempleo(f2: pd.DataFrame) -> Path:
    ct = pd.crosstab(f2["TIPO_JORNADA"], f2["TARGET_SUBEMPLEO"], normalize="index") * 100
    # Ordenar por tasa de subempleo
    if 1 in ct.columns:
        ct = ct.sort_values(1, ascending=True)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    left = np.zeros(len(ct))
    for col, color, lab in [
        (0, COLORES["no_subempleo"], "No subempleo"),
        (1, COLORES["subempleo"], "Subempleo"),
    ]:
        if col not in ct.columns:
            continue
        ax.barh(ct.index.astype(str), ct[col], left=left, color=color, label=lab, height=0.55)
        left = left + ct[col].values
    ax.set_xlabel("% dentro del tipo de jornada")
    ax.set_title("Subempleo según tipo de jornada (Fase 2)")
    ax.set_xlim(0, 100)
    ax.legend(frameon=False, loc="lower right")
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "08_jornada_vs_subempleo.png")


def fig_nulos_estructurales(f1: pd.DataFrame, f2: pd.DataFrame) -> Path:
    cols_f1 = [
        "PROVINCIA_NACIMIENTO",
        "REGION_NACIMIENTO_EXTRANJERO",
        "ANOS_RESIDENCIA_ESPANA",
        "NIVEL_ESTUDIOS_ACTUALES",
        "EDAD_FIN_ESTUDIOS",
    ]
    cols_f2 = [
        "REGION_TRABAJO",
        "TIPO_CONTRATO_TEMPORAL",
        "CONTRATO_PERMANENTE_DISCONTINUO",
        "PROVINCIA_TRABAJO",
    ]
    rows = []
    for c in cols_f1:
        if c in f1.columns:
            rows.append({"dataset": "Fase 1", "variable": c, "pct_nulo": f1[c].isna().mean() * 100})
    for c in cols_f2:
        if c in f2.columns:
            rows.append({"dataset": "Fase 2", "variable": c, "pct_nulo": f2[c].isna().mean() * 100})
    df = pd.DataFrame(rows).sort_values("pct_nulo")

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [
        COLORES["dataset_f1"] if d == "Fase 1" else COLORES["dataset_f2"] for d in df["dataset"]
    ]
    ax.barh(df["variable"], df["pct_nulo"], color=colors, height=0.6)
    ax.set_xlabel("% de valores nulos")
    ax.set_title("Nulos estructurales (no son errores de calidad)")
    ax.set_xlim(0, 105)
    for y, (_, r) in enumerate(df.iterrows()):
        ax.text(r["pct_nulo"] + 1, y, f"{r['pct_nulo']:.1f}%", va="center", fontsize=8)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(color=COLORES["dataset_f1"], label="Dataset Fase 1"),
            Patch(color=COLORES["dataset_f2"], label="Dataset Fase 2"),
        ],
        frameon=False,
        loc="lower right",
    )
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "09_nulos_estructurales.png")


def _periodo_label(df: pd.DataFrame) -> pd.Series:
    return (
        df["ANIO_REF"].astype(int).astype(str)
        + "T"
        + df["TRIMESTRE_REF"].astype(int).astype(str)
    )


def fig_evolucion_estado_fase1(f1: pd.DataFrame) -> Path:
    """Evolución trimestral del mix Ocupado/Parado/Inactivo — útil en memoria."""
    tmp = f1.copy()
    tmp["periodo"] = _periodo_label(tmp)
    ct = (
        pd.crosstab(tmp["periodo"], tmp["TARGET_MACRO"], normalize="index") * 100
    )
    # orden temporal
    orden = sorted(
        ct.index,
        key=lambda p: (int(p.split("T")[0]), int(p.split("T")[1])),
    )
    ct = ct.reindex(orden)
    cols = [c for c in ["Ocupado", "Parado", "Inactivo"] if c in ct.columns]

    fig, ax = plt.subplots(figsize=(11, 4.6))
    x = np.arange(len(ct))
    ax.stackplot(
        x,
        *[ct[c].values for c in cols],
        labels=cols,
        colors=[COLORES["ocupado"], COLORES["parado"], COLORES["inactivo"]][: len(cols)],
        alpha=0.9,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(ct.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("% de registros (Fase 1 · 16–64)")
    ax.set_ylim(0, 100)
    ax.set_title("Evolución del estado laboral en el tiempo")
    ax.legend(frameon=False, loc="lower left", ncol=3)
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "10_evolucion_estado_fase1.png")


def fig_evolucion_subempleo_fase2(f2: pd.DataFrame) -> Path:
    tmp = f2.copy()
    tmp["periodo"] = _periodo_label(tmp)
    serie = (
        tmp.groupby("periodo", observed=True)["TARGET_SUBEMPLEO"].mean() * 100
    )
    orden = sorted(
        serie.index,
        key=lambda p: (int(p.split("T")[0]), int(p.split("T")[1])),
    )
    serie = serie.reindex(orden)

    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = np.arange(len(serie))
    ax.fill_between(x, serie.values, color=COLORES["subempleo"], alpha=0.2)
    ax.plot(x, serie.values, color=COLORES["subempleo"], lw=2.3, marker="o", ms=4)
    ax.set_xticks(x)
    ax.set_xticklabels(serie.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Tasa de subempleo (%)")
    ax.set_title("Evolución de la tasa de subempleo (ocupados · AOI=03)")
    media = float(serie.mean())
    ax.axhline(media, color=COLORES["texto"], ls="--", lw=0.9, alpha=0.55)
    ax.text(len(serie) - 1, media + 0.15, f"media {media:.2f}%", ha="right", fontsize=8)
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "11_evolucion_subempleo_fase2.png")


def fig_top_ccaa_parado_fase1(f1: pd.DataFrame, top_n: int = 10) -> Path:
    """CCAA con mayor % de Parado dentro de Fase 1 — lectura territorial."""
    nombre = "CCAA_NOMBRE" if "CCAA_NOMBRE" in f1.columns else "CCAA"
    tmp = f1[[nombre, "TARGET_MACRO"]].copy()
    tasas = (
        tmp.assign(es_parado=(tmp["TARGET_MACRO"] == "Parado").astype(int))
        .groupby(nombre, observed=True)["es_parado"]
        .agg(["mean", "count"])
    )
    tasas = tasas[tasas["count"] >= 5000]  # evitar CCAA con muy poca muestra
    tasas["pct"] = tasas["mean"] * 100
    top = tasas.sort_values("pct", ascending=True).tail(top_n)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top.index.astype(str), top["pct"], color=COLORES["parado"], height=0.62)
    ax.set_xlabel("% Parado dentro de la CCAA (Fase 1 · 16–64)")
    ax.set_title(f"Top {top_n} CCAA por proporción de paro (muestra EPA)")
    for y, (_, r) in enumerate(top.iterrows()):
        ax.text(r["pct"] + 0.05, y, f"{r['pct']:.1f}%", va="center", fontsize=8)
    sns.despine(ax=ax)
    fig.tight_layout()
    return _guardar(fig, "12_top_ccaa_parado_fase1.png")


def _resumen_numerico(interim: pd.DataFrame, f1: pd.DataFrame, f2: pd.DataFrame) -> dict:
    dist_f1 = f1["TARGET_MACRO"].value_counts(normalize=True).to_dict()
    return {
        "interim_filas": int(len(interim)),
        "interim_columnas": int(len(interim.columns)),
        "fase1_filas": int(len(f1)),
        "fase1_columnas": int(len(f1.columns)),
        "fase2_filas": int(len(f2)),
        "fase2_columnas": int(len(f2.columns)),
        "fase1_pct_ocupado": round(float(dist_f1.get("Ocupado", 0)) * 100, 2),
        "fase1_pct_parado": round(float(dist_f1.get("Parado", 0)) * 100, 2),
        "fase1_pct_inactivo": round(float(dist_f1.get("Inactivo", 0)) * 100, 2),
        "fase2_tasa_subempleo": round(float(f2["TARGET_SUBEMPLEO"].mean()) * 100, 2),
        "periodos": sorted(
            {
                f"{int(a)}T{int(t)}"
                for a, t in zip(interim["ANIO_REF"], interim["TRIMESTRE_REF"])
            }
        ),
    }


def escribir_resumen_md(resumen: dict, figuras: list[Path]) -> None:
    lineas = [
        "# Resumen EDA — Ingeniería de datos (EPA)",
        "",
        "## Volúmenes",
        f"- Interim: **{resumen['interim_filas']:,}** filas × {resumen['interim_columnas']} columnas".replace(",", "."),
        f"- Fase 1 (16–64): **{resumen['fase1_filas']:,}** filas × {resumen['fase1_columnas']} columnas".replace(",", "."),
        f"- Fase 2 (ocupados): **{resumen['fase2_filas']:,}** filas × {resumen['fase2_columnas']} columnas".replace(",", "."),
        "",
        "## Targets",
        f"- Fase 1 — Ocupado {resumen['fase1_pct_ocupado']}% · Parado {resumen['fase1_pct_parado']}% · Inactivo {resumen['fase1_pct_inactivo']}%",
        f"- Fase 2 — Tasa de subempleo (AOI=03): **{resumen['fase2_tasa_subempleo']}%**",
        "",
        "## Periodo",
        f"- Trimestres: {', '.join(resumen['periodos'])}",
        "",
        "## Figuras generadas",
    ]
    for f in figuras:
        lineas.append(f"- `{f.name}`")
    lineas += [
        "",
        "## Notas para la memoria",
        "- Los nulos altos en origen/formación/contrato son **estructurales** (no aplica), no fallos de calidad.",
        "- Fase 1 excluye 65+ para no reducir el problema a detectar jubilación.",
        "- Fase 2 se centra en ocupados; las horas diferencian con claridad el subempleo.",
        "- Colores: verde petróleo/naranja = estados laborales; azul/ámbar = datasets Fase 1/2.",
        "",
    ]
    RESUMEN_MD.write_text("\n".join(lineas), encoding="utf-8")
    RESUMEN_JSON.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {RESUMEN_MD.relative_to(PROJECT_ROOT)}")
    print(f"  -> {RESUMEN_JSON.relative_to(PROJECT_ROOT)}")


def generar_eda_completo() -> dict:
    _aplicar_estilo()
    print("Cargando datasets...")
    import pyarrow.parquet as pq

    n_interim = pq.ParquetFile(INTERIM_EPA).metadata.num_rows
    n_cols_interim = len(pq.read_schema(INTERIM_EPA).names)
    interim = pd.read_parquet(INTERIM_EPA, columns=["ANIO_REF", "TRIMESTRE_REF"])
    f1 = pd.read_parquet(DATASET_FASE1)
    f2 = pd.read_parquet(DATASET_FASE2)
    print(f"  Interim: {n_interim:,} | Fase1: {len(f1):,} | Fase2: {len(f2):,}")

    print("Generando figuras...")
    figuras = [
        fig_volumenes(n_interim, len(f1), len(f2)),
        fig_cobertura_temporal(interim),
        fig_target_fase1(f1),
        fig_edad_sexo_fase1(f1),
        fig_educacion_vs_estado(f1),
        fig_evolucion_estado_fase1(f1),
        fig_top_ccaa_parado_fase1(f1),
        fig_subempleo_fase2(f2),
        fig_horas_vs_subempleo(f2),
        fig_jornada_vs_subempleo(f2),
        fig_evolucion_subempleo_fase2(f2),
        fig_nulos_estructurales(f1, f2),
    ]
    resumen = _resumen_numerico(interim, f1, f2)
    resumen["interim_filas"] = int(n_interim)
    resumen["interim_columnas"] = int(n_cols_interim)
    escribir_resumen_md(resumen, figuras)
    print("EDA completado.")
    return resumen


if __name__ == "__main__":
    generar_eda_completo()
