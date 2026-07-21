"""Rutas y configuración común del modelado."""

from pathlib import Path

from src.data_engineering.config import DATASET_FASE1, DATASET_FASE2, PROJECT_ROOT

RANDOM_STATE = 42

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

MODELS_FASE1_DIR = MODELS_DIR / "fase1"
REPORTS_FASE1_DIR = REPORTS_DIR / "fase1"
FIGURES_FASE1_DIR = FIGURES_DIR / "fase1"

# Corte temporal train/test: se entrena con todo lo anterior al corte y se
# evalúa con el corte en adelante (los trimestres más recientes), simulando
# el uso real del modelo para predecir el futuro a partir del pasado.
CORTE_ANIO = 2025
CORTE_TRIMESTRE = 1

# Tamaño de la submuestra estratificada usada SOLO durante la búsqueda de
# hiperparámetros (RandomizedSearchCV), para que sea viable en tiempo sobre
# ~1.7M filas. El modelo ganador se reentrena siempre con el train completo.
TAMANO_MUESTRA_BUSQUEDA = 120_000
N_ITER_BUSQUEDA = 12
CV_FOLDS = 3

for directorio in (MODELS_FASE1_DIR, REPORTS_FASE1_DIR, FIGURES_FASE1_DIR):
    directorio.mkdir(parents=True, exist_ok=True)

__all__ = [
    "DATASET_FASE1",
    "DATASET_FASE2",
    "RANDOM_STATE",
    "MODELS_FASE1_DIR",
    "REPORTS_FASE1_DIR",
    "FIGURES_FASE1_DIR",
    "CORTE_ANIO",
    "CORTE_TRIMESTRE",
    "TAMANO_MUESTRA_BUSQUEDA",
    "N_ITER_BUSQUEDA",
    "CV_FOLDS",
]
