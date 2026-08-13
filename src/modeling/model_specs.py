"""Catálogo de algoritmos a comparar para Fase 1 y sus espacios de búsqueda de hiperparámetros.

Se comparan tres familias con lógicas de generalización muy distintas:
- Regresión Logística: baseline lineal, rápida e interpretable por coeficientes.
- Random Forest: ensemble de árboles por bagging, robusto a outliers/escala.
- LightGBM: gradient boosting, suele ser el más preciso en datos tabulares
  y soporta categóricas nativas + valores nulos sin preprocesado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lightgbm import LGBMClassifier
from scipy.stats import loguniform, randint, uniform
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


@dataclass
class ModeloCandidato:
    nombre: str
    familia_preprocesado: str  # "nativo" (LightGBM) | "sklearn" (LogReg, RandomForest)
    estimador: BaseEstimator
    espacio_busqueda: dict[str, Any]


def construir_candidatos(random_state: int) -> list[ModeloCandidato]:
    return [
        # lbfgs + L2: baseline lineal rápido. Evitamos saga (L1/L2) porque
        # sobre ~1M+ filas con one-hot se queda horas en un solo núcleo.
        ModeloCandidato(
            nombre="regresion_logistica",
            familia_preprocesado="sklearn",
            estimador=LogisticRegression(
                class_weight="balanced",
                max_iter=300,
                solver="lbfgs",
                random_state=random_state,
            ),
            espacio_busqueda={
                "C": loguniform(1e-3, 1e2),
            },
        ),
        ModeloCandidato(
            nombre="random_forest",
            familia_preprocesado="sklearn",
            estimador=RandomForestClassifier(
                class_weight="balanced",
                n_jobs=1,
                random_state=random_state,
            ),
            espacio_busqueda={
                "n_estimators": randint(120, 350),
                "max_depth": randint(4, 22),
                "min_samples_leaf": randint(1, 50),
                "max_features": uniform(0.25, 0.7),
                "min_samples_split": randint(2, 20),
            },
        ),
        ModeloCandidato(
            nombre="lightgbm",
            familia_preprocesado="nativo",
            estimador=LGBMClassifier(
                class_weight="balanced",
                n_jobs=1,
                random_state=random_state,
                verbose=-1,
            ),
            espacio_busqueda={
                "n_estimators": randint(100, 500),
                "learning_rate": loguniform(5e-3, 3e-1),
                "num_leaves": randint(15, 128),
                "max_depth": randint(3, 14),
                "min_child_samples": randint(5, 200),
                "subsample": uniform(0.55, 0.45),
                "colsample_bytree": uniform(0.55, 0.45),
                "reg_lambda": loguniform(1e-2, 10.0),
            },
        ),
    ]
