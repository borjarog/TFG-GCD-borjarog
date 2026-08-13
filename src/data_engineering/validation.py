"""Checks del parquet intermedio (EPA 2021+)."""

from __future__ import annotations

import io
import sys

import pandas as pd  # type: ignore

from .config import INTERIM_EPA
from .diccionario_datos import codigo_en, mapear_variable


def _configurar_stdout_utf8() -> None:
    """UTF-8 en consola Windows; en Jupyter no se toca stdout."""
    if sys.platform != "win32":
        return
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is None:
        return
    try:
        sys.stdout = io.TextIOWrapper(buffer, encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass


_configurar_stdout_utf8()

def cargar_datos(archivo=INTERIM_EPA) -> pd.DataFrame | None:
    """Carga el parquet intermedio."""
    if not archivo.exists():
        print(f"Error: no se encuentra el archivo {archivo}")
        return None

    print(f"Cargando dataset: {archivo.name}...")
    return pd.read_parquet(archivo)


def _check_estructura(df: pd.DataFrame) -> None:
    print("\n[1. ESTRUCTURA BÁSICA]")
    print(f"Total de registros (personas encuestadas): {len(df):,}")
    print(f"Número de variables: {len(df.columns)}")
    anios = sorted(df["ANIO_REF"].dropna().unique())
    print(f"Años contenidos: {anios}")


def _check_poblacion(df: pd.DataFrame) -> None:
    print("\n[2. POBLACIÓN ESTIMADA (FACTOREL)]")
    if "FACTOREL" not in df.columns:
        print(" -> No se encontró la columna FACTOREL.")
        return

    factor = pd.to_numeric(df["FACTOREL"], errors="coerce")
    poblacion_trimestre = (
        df.assign(FACTOREL_NUM=factor)
        .groupby(["ANIO_REF", "TRIMESTRE_REF"])["FACTOREL_NUM"]
        .sum()
    )
    # La suma de FACTOREL ya da personas directamente. Su descripción oficial
    # (ver docs/diccionario_datos.md) dice que hay que dividir entre 1000 para
    # reproducir las tablas de INEbase, que se publican en MILES de personas
    # -- es decir, la división es para pasar a "miles", no para obtener personas.
    poblacion_media = poblacion_trimestre.mean()

    print(f"Población media estimada por trimestre: {poblacion_media:,.0f} personas")
    if 35_000_000 < poblacion_media < 52_000_000:
        print(" -> OK: la poblacion cuadra con la escala esperada (~40-48M).")
    else:
        print(" -> AVISO: el cálculo de población no cuadra. Revisar FACTOREL.")


def _check_sexo(df: pd.DataFrame) -> None:
    print("\n[3. DISTRIBUCIÓN POR SEXO]")
    if "SEXO1" not in df.columns:
        print(" -> No se encontró la columna SEXO1.")
        return

    etiquetas = mapear_variable(df["SEXO1"], "SEXO1")
    distribucion = etiquetas.value_counts(normalize=True, dropna=False) * 100
    print(distribucion.to_string(float_format="%.1f%%"))

    porcentaje_mujeres = distribucion.get("Mujer", 0.0)
    if 49.0 < porcentaje_mujeres < 53.0:
        print(" -> OK: la proporcion de mujeres esta en torno al 51%.")
    else:
        print(
            f" -> AVISO: porcentaje de mujeres detectado: {porcentaje_mujeres:.1f}%. Revisar."
        )


def _check_actividad(df: pd.DataFrame) -> None:
    print("\n[4. MERCADO LABORAL (AOI)]")
    if "AOI" not in df.columns:
        print(" -> No se encontró la columna AOI.")
        return

    etiquetas = mapear_variable(df["AOI"], "AOI", default="Desconocido")
    distribucion = etiquetas.value_counts(normalize=True, dropna=False) * 100
    print(distribucion.to_string(float_format="%.1f%%"))

    nulos_aoi = df["AOI"].isna()
    if nulos_aoi.any() and "NIVEL" in df.columns:
        menores = codigo_en(df.loc[nulos_aoi, "NIVEL"], {"2"})
        pct_menores = menores.mean() * 100
        print(
            f"\n   -> De los {nulos_aoi.sum():,} registros sin AOI, "
            f"{pct_menores:.1f}% son menores de 16 años (NIVEL=2)."
        )
        if pct_menores > 99.0:
            print(
                "   -> OK: los nulos en AOI corresponden a menores de 16 anos."
            )
        else:
            print(
                "   -> AVISO: hay nulos en AOI que no corresponden a menores de 16 años."
            )

    ocupados = codigo_en(df["AOI"], {"03", "04"}).mean() * 100
    print(
        f"\nProporción de ocupados (sobre el total, incl. menores de 16): {ocupados:.1f}%"
    )
    if ocupados > 40.0:
        print(" -> OK: la proporcion de ocupados tiene sentido.")
    else:
        print(" -> AVISO: proporción inusual de ocupados.")


def _check_nulos(df: pd.DataFrame) -> None:
    print("\n[5. SANIDAD DE DATOS (nulos)]")
    for col in ("PROV", "EDAD1", "NIVEL"):
        if col in df.columns:
            pct_nulos = df[col].isna().mean() * 100
            print(f"{col}: {pct_nulos:.2f}% valores nulos")
            if pct_nulos > 5:
                print(f" -> AVISO: demasiados nulos en {col}.")


def realizar_sanity_check(df: pd.DataFrame) -> None:
    """Comprobaciones de cordura sobre el dataset intermedio EPA 2021+."""
    print("\n" + "=" * 50)
    print(" SANITY CHECK: EPA 2021+")
    print("=" * 50)

    _check_estructura(df)
    _check_poblacion(df)
    _check_sexo(df)
    _check_actividad(df)
    _check_nulos(df)

    print("\n" + "=" * 50)
    print(" FIN DEL SANITY CHECK")
    print("=" * 50)


if __name__ == "__main__":
    dataframe = cargar_datos()
    if dataframe is not None:
        realizar_sanity_check(dataframe)
