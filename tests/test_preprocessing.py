"""Split temporal y preparación de X."""

import pandas as pd

from src.modeling.preprocessing import (
    COLUMNAS_EXCLUIDAS,
    COLUMNAS_EXCLUIDAS_FASE2,
    anadir_indicadores_de_nulo,
    split_temporal,
)


def _df_temporal() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ANIO_REF": [2024, 2024, 2025, 2025],
            "TRIMESTRE_REF": [3, 4, 1, 2],
            "valor": [1, 2, 3, 4],
        }
    )


def test_split_temporal_train_es_pasado_test_es_futuro():
    df = _df_temporal()
    train, test = split_temporal(df, corte_anio=2025, corte_trimestre=1)

    assert len(train) == 2
    assert len(test) == 2
    assert train["ANIO_REF"].max() <= 2024
    assert test["ANIO_REF"].min() >= 2025
    assert set(train.index).isdisjoint(set(test.index))


def test_split_temporal_incluye_trimestre_corte_en_test():
    df = pd.DataFrame({"ANIO_REF": [2025], "TRIMESTRE_REF": [1], "valor": [1]})
    train, test = split_temporal(df, corte_anio=2025, corte_trimestre=1)

    assert len(train) == 0
    assert len(test) == 1


def test_anadir_indicadores_de_nulo():
    df = pd.DataFrame({"EDAD_FIN_ESTUDIOS": [20.0, None, 25.0]})
    out = anadir_indicadores_de_nulo(df, columnas_nulo=["EDAD_FIN_ESTUDIOS"])

    assert "EDAD_FIN_ESTUDIOS_ES_NULO" in out.columns
    assert out["EDAD_FIN_ESTUDIOS_ES_NULO"].tolist() == [0, 1, 0]


def test_columnas_excluidas_fase1_no_incluye_target():
    assert "TARGET_MACRO" in COLUMNAS_EXCLUIDAS
    assert "CCAA_NOMBRE" in COLUMNAS_EXCLUIDAS


def test_columnas_excluidas_fase2_no_incluye_target_ni_region_trabajo():
    assert "TARGET_SUBEMPLEO" in COLUMNAS_EXCLUIDAS_FASE2
    assert "REGION_TRABAJO" in COLUMNAS_EXCLUIDAS_FASE2
