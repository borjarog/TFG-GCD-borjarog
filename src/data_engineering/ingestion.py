"""Lee los microdatos EPA (2021+). Si falta un trimestre, lo baja del INE."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from .config import ANIO_FIN, ANIO_INICIO, INTERIM_EPA, RAW_DIR, URL_TEMPLATE
from .diccionario_datos import cargar_diccionario_variables, colspecs_ancho_fijo

CSV_DIR = RAW_DIR / "CSV"
DESCARGAS_DIR = RAW_DIR / "_descargas"


def _ruta_local(anio: int, trimestre: int) -> Path | None:
    stem = f"EPA_{anio}T{trimestre}"
    for ext in (".csv", ".tab"):
        ruta = CSV_DIR / f"{stem}{ext}"
        if ruta.exists():
            return ruta
    return None


def _leer_delimitado(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, sep="\t", dtype=str, encoding="latin1", low_memory=False)


def _leer_ancho_fijo(ruta: Path) -> pd.DataFrame:
    colspecs, nombres = colspecs_ancho_fijo(cargar_diccionario_variables())
    return pd.read_fwf(ruta, colspecs=colspecs, names=nombres, dtype=str, encoding="latin1")


def _descargar_trimestre(anio: int, trimestre: int) -> Path | None:
    """ZIP de microdatos del INE cuando el trimestre no está en local."""
    anio_str = str(anio)[-2:]
    url = URL_TEMPLATE.format(anio=anio_str, trimestre=trimestre)
    print(f"  -> Sin archivo local, descargando desde el INE: {url}")

    try:
        respuesta = requests.get(url, timeout=60)
        respuesta.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(respuesta.content)) as z:
            archivos = [
                n
                for n in z.namelist()
                if n.lower().endswith((".csv", ".tab")) and "leeme" not in n.lower()
            ]
            if not archivos:
                return None
            DESCARGAS_DIR.mkdir(parents=True, exist_ok=True)
            z.extractall(DESCARGAS_DIR)
            return DESCARGAS_DIR / archivos[0]
    except requests.exceptions.RequestException as e:
        print(f"  -> Error descargando {anio}-T{trimestre}: {e}")
    except zipfile.BadZipFile:
        print(f"  -> El archivo descargado para {anio}-T{trimestre} no es un ZIP válido.")

    return None


def _cargar_archivo(ruta: Path) -> pd.DataFrame:
    if ruta.suffix.lower() in {".csv", ".tab"}:
        return _leer_delimitado(ruta)
    return _leer_ancho_fijo(ruta)


def cargar_trimestre(anio: int, trimestre: int) -> pd.DataFrame | None:
    """Carga un trimestre desde `data/raw/CSV/`, o lo descarga del INE si no existe localmente."""
    ruta = _ruta_local(anio, trimestre)
    origen = "local"

    if ruta is None:
        ruta = _descargar_trimestre(anio, trimestre)
        origen = "INE"

    if ruta is None or not ruta.exists():
        print(f"  -> Omitido {anio}-T{trimestre}: no hay datos disponibles.")
        return None

    df = _cargar_archivo(ruta)
    df.columns = [str(c).strip().strip('"') for c in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "NA": pd.NA})

    df["ANIO_REF"] = anio
    df["TRIMESTRE_REF"] = trimestre
    print(f"  -> {len(df):,} registros cargados ({origen}: {ruta.name}).")
    return df


def ingerir_historico(anio_inicio: int = ANIO_INICIO, anio_fin: int = ANIO_FIN) -> pd.DataFrame:
    """Consolida todos los trimestres disponibles (2021+) en un único DataFrame."""
    dataframes = []

    for anio in range(anio_inicio, anio_fin + 1):
        print(f"\nAño {anio}")
        for trimestre in range(1, 5):
            df_trimestre = cargar_trimestre(anio, trimestre)
            if df_trimestre is not None:
                dataframes.append(df_trimestre)

    if not dataframes:
        raise RuntimeError(
            "No se procesó ningún trimestre. Coloca archivos EPA_YYYYTQ.csv|.tab en data/raw/CSV/."
        )

    df_completo = pd.concat(dataframes, ignore_index=True, sort=False)
    print(f"\nTotal consolidado: {len(df_completo):,} registros, {len(df_completo.columns)} columnas.")
    return df_completo


def ejecutar_ingesta(anio_inicio: int = ANIO_INICIO, anio_fin: int = ANIO_FIN) -> Path:
    """Ejecuta la ingesta completa y guarda el parquet intermedio."""
    df = ingerir_historico(anio_inicio, anio_fin)

    INTERIM_EPA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(INTERIM_EPA, engine="pyarrow", compression="snappy", index=False)
    print(f"\nGuardado: {INTERIM_EPA} ({len(df):,} registros, {len(df.columns)} columnas)")
    return INTERIM_EPA


if __name__ == "__main__":
    ejecutar_ingesta()
