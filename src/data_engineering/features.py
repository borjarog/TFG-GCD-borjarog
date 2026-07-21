"""
Feature engineering EPA: variables demográficas y datasets de modelado para
Fase 1 (macro: Ocupado/Parado/Inactivo) y Fase 2 (micro: subempleo).

Uso:
    python -m src.data_engineering.features
"""

from __future__ import annotations

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from .config import DATASET_FASE1, DATASET_FASE2, INTERIM_EPA
from .diccionario_datos import codigo_en, mapear_variable

# Columnas mínimas necesarias del parquet intermedio (reduce memoria)
COLUMNAS_NECESARIAS = [
    "NIVEL",
    "AOI",
    "SEXO1",
    "EDAD1",
    "NFORMA",
    "ECIV1",
    "NAC1",
    "RELPP1",
    "CURSR",
    "CCAA",
    "PROV",
    "NVIVI",
    "NPERS",
    "ANIO_REF",
    "TRIMESTRE_REF",
    # Origen geográfico y residencia (Fase 1)
    "PRONA1",
    "REGNA1",
    "EXREGNA1",
    "ANORE1",
    # Formación (Fase 1)
    "EDADEST",
    "CURSNR",
    "NCURSR",
    # Estructura del hogar (Fase 1, derivadas)
    "NCONY",
    "NPADRE",
    "NMADRE",
    # Empleo principal (Fase 2)
    "DUCON1",
    "DUCON2",
    "DUCON3",
    "PARCO1",
    "SITU",
    "SP",
    "ACT1",
    "OCUP1",
    "PROEST",
    "REGEST",
    "TRAPLU",
    "HORASH",
    "HORASE",
    "EXTRA",
    "DCOM",
]

# Agrupación del TFG (no es 1:1 con el xlsx, pero usa los códigos oficiales de AOI)
MAPEO_AOI_MACRO = {
    "03": "Ocupado",
    "04": "Ocupado",
    "05": "Parado",
    "06": "Parado",
    "07": "Inactivo",
    "08": "Inactivo",
    "09": "Inactivo",
}

# Tramos de edad joven (EDAD1) y niveles educativos bajos (NFORMA), para la
# variable derivada VULNERABILIDAD_JOVEN. No son mapeos oficiales del INE.
EDAD1_JOVEN = {"16", "20"}
NFORMA_BAJA = {"AN", "P1", "P2"}


def filtrar_poblacion_adulta(df: pd.DataFrame) -> pd.DataFrame:
    """NIVEL=1 -> personas de 16 o más años (población de análisis del TFG)."""
    adultos = df[codigo_en(df["NIVEL"], {"1"})].copy()
    print(f"  -> Filtrado 16+: {len(adultos):,} registros (de {len(df):,} totales).")
    return adultos


def _calcular_tam_hogar(df: pd.DataFrame) -> pd.Series:
    """Tamaño real del hogar: nº de personas que comparten hogar.

    `NPERS` es el número de orden de la persona DENTRO del hogar, no el tamaño
    del hogar; usarlo directamente (como hacía la versión anterior del
    pipeline) era un error. El tamaño real se obtiene contando personas por
    hogar, identificado por trimestre + provincia + número de vivienda.
    """
    clave_hogar = ["ANIO_REF", "TRIMESTRE_REF", "PROV", "NVIVI"]
    return df.groupby(clave_hogar)["NPERS"].transform("count")


def crear_features_demograficas(df: pd.DataFrame) -> pd.DataFrame:
    """Features demográficas comunes a Fase 1 y Fase 2, con etiquetas oficiales del diccionario."""
    print("Creando features demográficas...")

    features = pd.DataFrame(index=df.index)
    features["SEXO"] = mapear_variable(df["SEXO1"], "SEXO1")
    features["TRAMO_EDAD"] = mapear_variable(df["EDAD1"], "EDAD1")
    features["NIVEL_EDUC"] = mapear_variable(
        df["NFORMA"], "NFORMA", default="Desconocido"
    )
    features["ESTADO_CIVIL"] = mapear_variable(df["ECIV1"], "ECIV1")
    features["NACIONALIDAD"] = mapear_variable(df["NAC1"], "NAC1")
    features["ROL_HOGAR"] = mapear_variable(df["RELPP1"], "RELPP1")
    features["ESTUDIANDO_AHORA"] = mapear_variable(df["CURSR"], "CURSR")
    features["CCAA_NOMBRE"] = mapear_variable(df["CCAA"], "CCAA", default=pd.NA)
    features["PROV_NOMBRE"] = mapear_variable(df["PROV"], "PROV", default=pd.NA)
    features["TAM_HOGAR"] = _calcular_tam_hogar(df)

    # Origen geográfico: PROVINCIA_NACIMIENTO y REGION_NACIMIENTO_EXTRANJERO son
    # mutuamente excluyentes por diseño (nacido en España vs. en el extranjero);
    # el patrón de nulos complementario es esperado, no un problema de calidad.
    features["PROVINCIA_NACIMIENTO"] = mapear_variable(
        df["PRONA1"], "PRONA1", default=pd.NA
    )
    features["REGION_NACIMIENTO_EXTRANJERO"] = mapear_variable(
        df["REGNA1"], "REGNA1", default=pd.NA
    )
    features["REGION_NACIONALIDAD_EXTRANJERA"] = mapear_variable(
        df["EXREGNA1"], "EXREGNA1", default=pd.NA
    )
    features["ANOS_RESIDENCIA_ESPANA"] = pd.to_numeric(df["ANORE1"], errors="coerce")

    # Formación adicional
    features["EDAD_FIN_ESTUDIOS"] = pd.to_numeric(df["EDADEST"], errors="coerce")
    features["FORMACION_NO_REGLADA"] = mapear_variable(df["CURSNR"], "CURSNR")
    # NIVEL_ESTUDIOS_ACTUALES solo aplica a quien estudia ahora (NaN estructural para el resto)
    features["NIVEL_ESTUDIOS_ACTUALES"] = mapear_variable(
        df["NCURSR"], "NCURSR", default=pd.NA
    )

    # Estructura del hogar (derivadas: presencia de convivientes, no identificadores)
    features["TIENE_CONYUGE_HOGAR"] = np.where(
        codigo_en(df["NCONY"], {"00"}), "No", "Si"
    )
    vive_con_padre = ~codigo_en(df["NPADRE"], {"00"})
    vive_con_madre = ~codigo_en(df["NMADRE"], {"00"})
    features["VIVE_CON_PADRES"] = np.where(vive_con_padre | vive_con_madre, "Si", "No")

    es_referencia = codigo_en(df["RELPP1"], {"1"})
    features["CARGA_FAMILIAR"] = np.where(
        es_referencia & (features["TAM_HOGAR"] >= 3), "Alta", "Baja_o_Nula"
    )

    es_joven = codigo_en(df["EDAD1"], EDAD1_JOVEN)
    educ_baja = (
        df["NFORMA"]
        .where(df["NFORMA"].notna(), None)
        .astype(str)
        .str.strip()
        .isin(NFORMA_BAJA)
    )
    features["VULNERABILIDAD_JOVEN"] = np.where(es_joven & educ_baja, "Alta", "Baja")

    return pd.concat([df, features], axis=1)


def _mapear_aoi_macro(serie: pd.Series) -> pd.Series:
    def _lookup(valor):
        if pd.isna(valor):
            return pd.NA
        codigo = str(valor).strip().zfill(2)
        return MAPEO_AOI_MACRO.get(codigo, pd.NA)

    return serie.map(_lookup)


COLUMNAS_FASE1 = [
    "ANIO_REF",
    "TRIMESTRE_REF",
    "CCAA",
    "CCAA_NOMBRE",
    "PROV",
    "PROV_NOMBRE",
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
    "PROVINCIA_NACIMIENTO",
    "REGION_NACIMIENTO_EXTRANJERO",
    "REGION_NACIONALIDAD_EXTRANJERA",
    "ANOS_RESIDENCIA_ESPANA",
    "EDAD_FIN_ESTUDIOS",
    "FORMACION_NO_REGLADA",
    "NIVEL_ESTUDIOS_ACTUALES",
    "TIENE_CONYUGE_HOGAR",
    "VIVE_CON_PADRES",
    "TARGET_MACRO",
]


def procesar_fase1_macro(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Dataset Fase 1: Ocupado / Parado / Inactivo, a partir de AOI.

    Los predictores son puramente demográficos (disponibles para cualquier
    persona de 16+, sin depender de si tiene o busca empleo) para evitar fuga
    de información hacia el target: se excluyen a propósito variables como
    OCUP1, ACT1, SITU, DUCON1, PARCO1, horas trabajadas, BUSCA, MASHOR..., que
    solo existen para quien ya tiene o busca empleo.
    """
    print("Procesando Fase 1 (Mercado Macro)...")

    df_adultos = df.dropna(subset=["AOI"]).copy()
    df_adultos["TARGET_MACRO"] = _mapear_aoi_macro(df_adultos["AOI"])
    df_adultos = df_adultos.dropna(subset=["TARGET_MACRO"])

    df_fase1 = df_adultos[COLUMNAS_FASE1].copy()
    for col in df_fase1.select_dtypes(include=["object"]).columns:
        df_fase1[col] = df_fase1[col].astype("category")

    return df_fase1, df_adultos


COLUMNAS_FASE2 = [
    "ANIO_REF",
    "TRIMESTRE_REF",
    "CCAA",
    "CCAA_NOMBRE",
    "PROV",
    "PROV_NOMBRE",
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
    "TIPO_CONTRATO",
    "TIPO_JORNADA",
    "SITUACION_PROF",
    "SECTOR_ACTIVIDAD",
    "SEGUNDO_EMPLEO",
    "HORAS_HABITUALES",
    "ANTIGUEDAD_MESES",
    "OCUPACION",
    "TIPO_ADMINISTRACION",
    "CONTRATO_PERMANENTE_DISCONTINUO",
    "TIPO_CONTRATO_TEMPORAL",
    "PROVINCIA_TRABAJO",
    "REGION_TRABAJO",
    "HORAS_EFECTIVAS",
    "HIZO_HORAS_EXTRA",
    "TARGET_SUBEMPLEO",
]


def procesar_fase2_micro(df_adultos: pd.DataFrame) -> pd.DataFrame:
    """Dataset Fase 2: subempleo por insuficiencia de horas, solo para Ocupados.

    TARGET_SUBEMPLEO se toma directamente del código oficial AOI=03
    ("Ocupados subempleados por insuficiencia de horas", la misma definición
    OIT que ya aplica el INE), en vez de reconstruirlo a mano con
    MASHOR+DISMAS. Por eso MASHOR, DISMAS, RZNDISH y HORDES (y BUSOTR, por ser
    un síntoma casi equivalente) no se usan como predictores: son la fuente
    directa de esa clasificación y causarían fuga de información.
    """
    print("Procesando Fase 2 (Subempleo Micro)...")

    df_ocupados = df_adultos[df_adultos["TARGET_MACRO"] == "Ocupado"].copy()
    df_ocupados["TARGET_SUBEMPLEO"] = codigo_en(df_ocupados["AOI"], {"03"}).astype(int)

    df_ocupados["TIPO_CONTRATO"] = mapear_variable(
        df_ocupados["DUCON1"], "DUCON1"
    ).fillna("No_asalariado")
    df_ocupados["TIPO_JORNADA"] = mapear_variable(
        df_ocupados["PARCO1"], "PARCO1", default="Desconocido"
    )
    df_ocupados["SITUACION_PROF"] = mapear_variable(
        df_ocupados["SITU"], "SITU", default="Desconocido"
    )
    df_ocupados["SECTOR_ACTIVIDAD"] = mapear_variable(
        df_ocupados["ACT1"], "ACT1", default="Desconocido"
    )
    df_ocupados["SEGUNDO_EMPLEO"] = mapear_variable(
        df_ocupados["TRAPLU"], "TRAPLU", default="No"
    )
    df_ocupados["HORAS_HABITUALES"] = pd.to_numeric(
        df_ocupados["HORASH"], errors="coerce"
    )
    df_ocupados["ANTIGUEDAD_MESES"] = pd.to_numeric(
        df_ocupados["DCOM"], errors="coerce"
    )

    df_ocupados["OCUPACION"] = mapear_variable(
        df_ocupados["OCUP1"], "OCUP1", default="Desconocido"
    )
    df_ocupados["TIPO_ADMINISTRACION"] = mapear_variable(
        df_ocupados["SP"], "SP", default=pd.NA
    ).fillna("No_aplica")
    # DUCON2/DUCON3 son mutuamente excluyentes por diseño (indefinido vs.
    # temporal), igual que PRONA1/REGNA1 en Fase 1: el NaN complementario es
    # esperado, no un problema de calidad.
    df_ocupados["CONTRATO_PERMANENTE_DISCONTINUO"] = mapear_variable(
        df_ocupados["DUCON2"], "DUCON2", default=pd.NA
    )
    df_ocupados["TIPO_CONTRATO_TEMPORAL"] = mapear_variable(
        df_ocupados["DUCON3"], "DUCON3", default=pd.NA
    )
    df_ocupados["PROVINCIA_TRABAJO"] = mapear_variable(
        df_ocupados["PROEST"], "PROEST", default=pd.NA
    )
    df_ocupados["REGION_TRABAJO"] = mapear_variable(
        df_ocupados["REGEST"], "REGEST", default=pd.NA
    )
    df_ocupados["HORAS_EFECTIVAS"] = pd.to_numeric(
        df_ocupados["HORASE"], errors="coerce"
    )
    df_ocupados["HIZO_HORAS_EXTRA"] = mapear_variable(
        df_ocupados["EXTRA"], "EXTRA", default=pd.NA
    ).fillna("No_asalariado")

    df_fase2 = df_ocupados[COLUMNAS_FASE2].copy()
    for col in df_fase2.select_dtypes(include=["object", "category"]).columns:
        if col != "TARGET_SUBEMPLEO":
            df_fase2[col] = df_fase2[col].astype("category")

    return df_fase2


def ejecutar_pipeline(
    input_file=INTERIM_EPA,
    output_fase1=DATASET_FASE1,
    output_fase2=DATASET_FASE2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Transforma el parquet intermedio en los datasets listos para Machine Learning."""
    print(f"Cargando datos intermedios de {input_file}...")

    import pyarrow.parquet as pq  # type: ignore

    columnas_disponibles = pq.read_schema(input_file).names
    columnas_leer = [c for c in COLUMNAS_NECESARIAS if c in columnas_disponibles]
    df_raw = pd.read_parquet(input_file, columns=columnas_leer)

    df_adultos = filtrar_poblacion_adulta(df_raw)
    del df_raw

    df_base = crear_features_demograficas(df_adultos)
    del df_adultos

    df_fase1, df_adultos_target = procesar_fase1_macro(df_base)
    print(
        f"  -> Dataset Fase 1 creado: {df_fase1.shape[0]:,} filas x {df_fase1.shape[1]} columnas."
    )

    df_fase2 = procesar_fase2_micro(df_adultos_target)
    subempleados = int(df_fase2["TARGET_SUBEMPLEO"].sum())
    print(
        f"  -> Dataset Fase 2 creado: {df_fase2.shape[0]:,} filas x {df_fase2.shape[1]} columnas."
    )
    print(
        f"  -> Tasa de subempleo (AOI=03): {(subempleados / len(df_fase2)) * 100:.2f}% "
        f"({subempleados:,} personas)"
    )

    print("\nGuardando datasets listos para Machine Learning...")
    output_fase1.parent.mkdir(parents=True, exist_ok=True)
    df_fase1.to_parquet(output_fase1, index=False)
    df_fase2.to_parquet(output_fase2, index=False)
    print("Feature engineering completado.")

    return df_fase1, df_fase2


if __name__ == "__main__":
    ejecutar_pipeline()
