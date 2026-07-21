"""Rutas y configuración común del proyecto de ingeniería de datos."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
META_DIR = DATA_DIR / "meta"
INTERIM_DIR = DATA_DIR / "processed" / "interim"
MODELING_DIR = DATA_DIR / "processed" / "modeling"

DOCS_DIR = PROJECT_ROOT / "docs"

# Periodo de análisis (diseño de registro EPA 2021 en adelante)
ANIO_INICIO = 2021
ANIO_FIN = 2026

# Única fuente de metadatos oficiales a partir de ahora
DISENO_REGISTRO_EPA = META_DIR / "diseno_registro_2021_en_adelante.xlsx"
RUTA_DICCIONARIO_DATOS = DOCS_DIR / "diccionario_datos.md"

# Artefactos del pipeline
INTERIM_EPA = INTERIM_DIR / "epa_2021_en_adelante.parquet"
DATASET_FASE1 = MODELING_DIR / "dataset_fase1_macro.parquet"
DATASET_FASE2 = MODELING_DIR / "dataset_fase2_micro.parquet"

# Plantilla de descarga de microdatos del INE (fallback para trimestres no disponibles localmente)
URL_TEMPLATE = "https://www.ine.es/ftp/microdatos/epa/datos_{trimestre}t{anio}.zip"

for directory in (RAW_DIR, META_DIR, INTERIM_DIR, MODELING_DIR, DOCS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
