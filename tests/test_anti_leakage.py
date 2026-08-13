"""Comprobar que el target no se cuela en las predictoras."""

import pandas as pd

from src.data_engineering.features import COLUMNAS_FASE2
from src.modeling.fase1 import obtener_columnas_features as columnas_fase1
from src.modeling.fase2 import obtener_columnas_features as columnas_fase2

# AOI=03 se define con estas; no están en el parquet de Fase 2.
VARIABLES_FUGA_AOI = {"MASHOR", "DISMAS", "RZNDISH", "HORDES", "BUSOTR", "AOI"}


def test_dataset_fase2_no_contiene_variables_fuga():
    assert VARIABLES_FUGA_AOI.isdisjoint(set(COLUMNAS_FASE2))


def test_obtener_columnas_fase2_excluye_target_y_redundantes():
    df = pd.DataFrame({col: [1] for col in COLUMNAS_FASE2})
    features = columnas_fase2(df)

    assert "TARGET_SUBEMPLEO" not in features
    assert "CCAA_NOMBRE" not in features
    assert "PROV_NOMBRE" not in features
    assert "REGION_TRABAJO" not in features
    assert "HORAS_HABITUALES" in features


def test_obtener_columnas_fase1_solo_demografia_sin_target():
    columnas = ["ANIO_REF", "SEXO", "TARGET_MACRO", "CCAA_NOMBRE"]
    df = pd.DataFrame({c: [1] for c in columnas})
    features = columnas_fase1(df)

    assert "TARGET_MACRO" not in features
    assert "CCAA_NOMBRE" not in features
    assert "SEXO" in features
