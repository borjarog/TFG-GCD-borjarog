"""Preparación de features y partición temporal para el modelado.

Filosofía:
- Split TEMPORAL (no aleatorio): se entrena con el pasado y se evalúa con los
  trimestres más recientes, que es como se usaría el modelo en producción.
- Dos familias de preprocesado:
    - "nativo": para LightGBM (categóricas `dtype=category` + nulos nativos).
    - "sklearn": para LogisticRegression y RandomForest (imputación + one-hot /
      escalado).
- Los nulos estructurales se conservan con un indicador `<col>_ES_NULO`.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CORTE_ANIO, CORTE_TRIMESTRE

# --- Fase 1 -----------------------------------------------------------------
# Se excluyen CCAA_NOMBRE/PROV_NOMBRE: redundantes respecto a CCAA/PROV.
COLUMNAS_EXCLUIDAS = {"CCAA_NOMBRE", "PROV_NOMBRE", "TARGET_MACRO"}
COLUMNAS_NUMERICAS = ["ANIO_REF", "TAM_HOGAR", "ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]
COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL = ["ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]

# --- Fase 2 -----------------------------------------------------------------
# REGION_TRABAJO ~99.6% nulo (casi todo el trabajo es en España); PROVINCIA_TRABAJO basta.
# No se incluyen MASHOR/DISMAS/HORDES/... : son la definición del target AOI=03.
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
    """Divide en train (pasado) / test (futuro) según un corte (año, trimestre) incluido en el test."""
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
    """Añade columnas `<col>_ES_NULO` para numéricas con nulo estructural."""
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
    """Para LightGBM: mantiene categóricas como `category` y nulos tal cual."""
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
    """Para LogisticRegression/RandomForest: imputación + one-hot / escalado."""
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
    """Prepara el X de entrada para el ColumnTransformer."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features, columnas_numericas)
    X = anadir_indicadores_de_nulo(df[columnas_features].copy(), columnas_nulo)
    for col in columnas_categoricas:
        X[col] = X[col].astype("object").where(X[col].notna(), None)
    return X


class ModeloEnvuelto:
    """Envuelve un estimador + su preprocesado bajo una interfaz común."""

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
        """Devuelve la matriz ya lista para entrar al estimador (útil también para SHAP)."""
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
