"""Split temporal y preprocesado (LightGBM nativo vs sklearn).

Train = pasado, test = trimestres del corte en adelante. LightGBM se queda
con categóricas y nulos; logística y RF van con imputación + one-hot.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CORTE_ANIO, CORTE_TRIMESTRE

# --- Fase 1 -----------------------------------------------------------------
# CCAA_NOMBRE / PROV_NOMBRE son el mismo dato que CCAA / PROV.
COLUMNAS_EXCLUIDAS = {"CCAA_NOMBRE", "PROV_NOMBRE", "TARGET_MACRO"}
COLUMNAS_NUMERICAS = ["ANIO_REF", "TAM_HOGAR", "ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]
COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL = ["ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]

# --- Fase 2 -----------------------------------------------------------------
# REGION_TRABAJO está casi siempre vacío (trabajan en España).
# MASHOR/DISMAS/HORDES no están en el parquet: definen el target AOI=03.
COLUMNAS_EXCLUIDAS_FASE2 = {
    "CCAA_NOMBRE",
    "PROV_NOMBRE",
    "TARGET_SUBEMPLEO",
    "REGION_TRABAJO",
}
COLUMNAS_NUMERICAS_FASE2 = [
    "ANIO_REF",
    "TRIMESTRE_REF",
    "TAM_HOGAR",
    "ANOS_RESIDENCIA_ESPANA",
    "EDAD_FIN_ESTUDIOS",
    "HORAS_HABITUALES",
    "HORAS_EFECTIVAS",
    "ANTIGUEDAD_MESES",
]
COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL_FASE2 = [
    "ANOS_RESIDENCIA_ESPANA",
    "EDAD_FIN_ESTUDIOS",
]


def obtener_columnas_categoricas(
    df: pd.DataFrame,
    columnas_features: list[str],
    columnas_numericas: list[str] | None = None,
) -> list[str]:
    numericas = set(columnas_numericas if columnas_numericas is not None else COLUMNAS_NUMERICAS)
    return [c for c in columnas_features if c not in numericas]


def split_temporal(
    df: pd.DataFrame, corte_anio: int = CORTE_ANIO, corte_trimestre: int = CORTE_TRIMESTRE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train antes del corte; el trimestre de corte entra en test."""
    es_test = (df["ANIO_REF"] > corte_anio) | (
        (df["ANIO_REF"] == corte_anio) & (df["TRIMESTRE_REF"] >= corte_trimestre)
    )
    train_df, test_df = df[~es_test].copy(), df[es_test].copy()
    print(
        f"  -> Split temporal: train hasta {corte_anio - 1}T4 ({len(train_df):,} filas), "
        f"test desde {corte_anio}T{corte_trimestre} ({len(test_df):,} filas)."
    )
    return train_df, test_df


def anadir_indicadores_de_nulo(
    df: pd.DataFrame, columnas_nulo: list[str] | None = None
) -> pd.DataFrame:
    """Flag de nulo estructural (`<col>_ES_NULO`)."""
    df = df.copy()
    for col in columnas_nulo if columnas_nulo is not None else COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL:
        if col in df.columns:
            df[f"{col}_ES_NULO"] = df[col].isna().astype(int)
    return df


def preparar_features_nativo(
    df: pd.DataFrame,
    columnas_features: list[str],
    columnas_numericas: list[str] | None = None,
    columnas_nulo: list[str] | None = None,
) -> pd.DataFrame:
    """X para LightGBM: category + nulos sin imputar."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features, columnas_numericas)
    X = anadir_indicadores_de_nulo(df[columnas_features].copy(), columnas_nulo)
    for col in columnas_categoricas:
        X[col] = X[col].astype("category")
    return X


def construir_preprocesador_sklearn(
    df: pd.DataFrame,
    columnas_features: list[str],
    columnas_numericas: list[str] | None = None,
    columnas_nulo: list[str] | None = None,
) -> ColumnTransformer:
    """ColumnTransformer: imputación, one-hot y escalado."""
    numericas_base = list(columnas_numericas if columnas_numericas is not None else COLUMNAS_NUMERICAS)
    nulos = list(columnas_nulo if columnas_nulo is not None else COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL)
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features, numericas_base)
    columnas_numericas_final = [c for c in columnas_features if c in numericas_base]
    columnas_numericas_final += [f"{c}_ES_NULO" for c in nulos if c in columnas_features]

    pipeline_categorico = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="constant", fill_value="Sin_dato")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    pipeline_numerico = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("cat", pipeline_categorico, columnas_categoricas),
            ("num", pipeline_numerico, columnas_numericas_final),
        ]
    )


def preparar_features_sklearn(
    df: pd.DataFrame,
    columnas_features: list[str],
    columnas_numericas: list[str] | None = None,
    columnas_nulo: list[str] | None = None,
) -> pd.DataFrame:
    """X de entrada al ColumnTransformer de sklearn."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features, columnas_numericas)
    X = anadir_indicadores_de_nulo(df[columnas_features].copy(), columnas_nulo)
    for col in columnas_categoricas:
        X[col] = X[col].astype("object").where(X[col].notna(), None)
    return X


class ModeloEnvuelto:
    """Estimador + preprocesado con la misma interfaz (fit / predict / SHAP)."""

    def __init__(
        self,
        nombre: str,
        familia: str,
        estimador,
        columnas_features: list[str],
        columnas_numericas: list[str] | None = None,
        columnas_nulo: list[str] | None = None,
    ):
        self.nombre = nombre
        self.familia = familia
        self.estimador = estimador
        self.columnas_features = columnas_features
        self.columnas_numericas = list(
            columnas_numericas if columnas_numericas is not None else COLUMNAS_NUMERICAS
        )
        self.columnas_nulo = list(
            columnas_nulo if columnas_nulo is not None else COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL
        )
        self.preprocesador: ColumnTransformer | None = None

    def _X(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.familia == "nativo":
            return preparar_features_nativo(
                df, self.columnas_features, self.columnas_numericas, self.columnas_nulo
            )
        return preparar_features_sklearn(
            df, self.columnas_features, self.columnas_numericas, self.columnas_nulo
        )

    def fit(self, df: pd.DataFrame, y) -> "ModeloEnvuelto":
        X = self._X(df)
        if self.familia == "sklearn":
            self.preprocesador = construir_preprocesador_sklearn(
                df, self.columnas_features, self.columnas_numericas, self.columnas_nulo
            )
            X = self.preprocesador.fit_transform(X)
        self.estimador.fit(X, y)
        return self

    def transformar(self, df: pd.DataFrame):
        """Matriz lista para el estimador (y para SHAP)."""
        X = self._X(df)
        if self.familia == "sklearn":
            X = self.preprocesador.transform(X)
        return X

    def predict(self, df: pd.DataFrame):
        return self.estimador.predict(self.transformar(df))

    def predict_proba(self, df: pd.DataFrame):
        return self.estimador.predict_proba(self.transformar(df))[:, 1]

    def nombres_features(self) -> list[str]:
        if self.familia == "sklearn":
            return list(self.preprocesador.get_feature_names_out())
        return list(self.columnas_features) + [
            f"{c}_ES_NULO" for c in self.columnas_nulo if c in self.columnas_features
        ]
