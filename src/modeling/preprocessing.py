"""Preparación de features y partición temporal para el modelado de Fase 1.

Filosofía:
- Split TEMPORAL (no aleatorio): se entrena con el pasado y se evalúa con los
  trimestres más recientes, que es como se usaría el modelo en producción.
- Dos familias de preprocesado:
    - "nativo": para LightGBM, que soporta de forma nativa columnas
      categóricas (`dtype=category`) y valores nulos, sin necesidad de
      codificar nada.
    - "sklearn": para LogisticRegression y RandomForest, que necesitan
      variables numéricas sin nulos: imputación + one-hot para categóricas,
      imputación + escalado para numéricas.
- Los nulos NUNCA se imputan a ciegas cuando son estructurales (p.ej. no
  haber nacido en el extranjero): se añade antes un indicador binario
  "_ES_NULO" para que el modelo pueda seguir usando esa información.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CORTE_ANIO, CORTE_TRIMESTRE

# Se excluyen CCAA_NOMBRE/PROV_NOMBRE: son la misma información que
# CCAA/PROV en formato texto, solo aportan redundancia (y explotan la
# dimensionalidad del one-hot de los modelos lineales).
COLUMNAS_EXCLUIDAS = {"CCAA_NOMBRE", "PROV_NOMBRE", "TARGET_MACRO"}

COLUMNAS_NUMERICAS = ["ANIO_REF", "TAM_HOGAR", "ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]

# Numéricas cuyo nulo es estructural (no es un dato perdido, es "no aplica"):
# se conserva la señal con un indicador binario antes de imputar.
COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL = ["ANOS_RESIDENCIA_ESPANA", "EDAD_FIN_ESTUDIOS"]


def obtener_columnas_categoricas(df: pd.DataFrame, columnas_features: list[str]) -> list[str]:
    return [c for c in columnas_features if c not in COLUMNAS_NUMERICAS]


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


def anadir_indicadores_de_nulo(df: pd.DataFrame) -> pd.DataFrame:
    """Añade columnas `<col>_ES_NULO` para las numéricas con nulo estructural, antes de imputar."""
    df = df.copy()
    for col in COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL:
        if col in df.columns:
            df[f"{col}_ES_NULO"] = df[col].isna().astype(int)
    return df


def preparar_features_nativo(df: pd.DataFrame, columnas_features: list[str]) -> pd.DataFrame:
    """Para LightGBM: mantiene categóricas como `category` y nulos tal cual (los soporta nativamente)."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features)
    X = anadir_indicadores_de_nulo(df[columnas_features].copy())
    for col in columnas_categoricas:
        X[col] = X[col].astype("category")
    return X


def construir_preprocesador_sklearn(df: pd.DataFrame, columnas_features: list[str]) -> ColumnTransformer:
    """Para LogisticRegression/RandomForest: imputación + one-hot / escalado."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features)
    columnas_numericas = [c for c in columnas_features if c in COLUMNAS_NUMERICAS]
    columnas_numericas += [f"{c}_ES_NULO" for c in COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL if c in columnas_features]

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
            ("num", pipeline_numerico, columnas_numericas),
        ]
    )


def preparar_features_sklearn(df: pd.DataFrame, columnas_features: list[str]) -> pd.DataFrame:
    """Prepara el X de entrada para el ColumnTransformer (añade indicadores de nulo, castea a str las categóricas)."""
    columnas_categoricas = obtener_columnas_categoricas(df, columnas_features)
    X = anadir_indicadores_de_nulo(df[columnas_features].copy())
    for col in columnas_categoricas:
        X[col] = X[col].astype("object").where(X[col].notna(), None)
    return X


class ModeloEnvuelto:
    """Envuelve un estimador + su preprocesado bajo una interfaz común, para poder
    entrenar/evaluar/explicar LightGBM (categóricas nativas) y modelos sklearn
    (one-hot) exactamente igual desde `fase1.py`.
    """

    def __init__(self, nombre: str, familia: str, estimador, columnas_features: list[str]):
        self.nombre = nombre
        self.familia = familia
        self.estimador = estimador
        self.columnas_features = columnas_features
        self.preprocesador: ColumnTransformer | None = None

    def _X(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.familia == "nativo":
            return preparar_features_nativo(df, self.columnas_features)
        return preparar_features_sklearn(df, self.columnas_features)

    def fit(self, df: pd.DataFrame, y) -> "ModeloEnvuelto":
        X = self._X(df)
        if self.familia == "sklearn":
            self.preprocesador = construir_preprocesador_sklearn(df, self.columnas_features)
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
            f"{c}_ES_NULO" for c in COLUMNAS_NUMERICAS_CON_NULO_ESTRUCTURAL if c in self.columnas_features
        ]
