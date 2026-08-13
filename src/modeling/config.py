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

MODELS_FASE2_DIR = MODELS_DIR / "fase2"
REPORTS_FASE2_DIR = REPORTS_DIR / "fase2"
FIGURES_FASE2_DIR = FIGURES_DIR / "fase2"

# Train: todo lo anterior a este corte. Test: este trimestre en adelante.
CORTE_ANIO = 2025
CORTE_TRIMESTRE = 1

# RandomizedSearchCV sobre una submuestra; RF/LGBM se reentrenan con el train
# entero. La logística se recorta porque lbfgs + one-hot no escala a ~1M filas.
TAMANO_MUESTRA_BUSQUEDA = 120_000
TAMANO_MAX_ENTRENO_LINEAL = 300_000
N_ITER_BUSQUEDA = 20
CV_FOLDS = 3

for directorio in (
    MODELS_FASE1_DIR,
    REPORTS_FASE1_DIR,
    FIGURES_FASE1_DIR,
    MODELS_FASE2_DIR,
    REPORTS_FASE2_DIR,
    FIGURES_FASE2_DIR,
):
    directorio.mkdir(parents=True, exist_ok=True)

__all__ = [
    "DATASET_FASE1",
    "DATASET_FASE2",
    "RANDOM_STATE",
    "MODELS_FASE1_DIR",
    "REPORTS_FASE1_DIR",
    "FIGURES_FASE1_DIR",
    "MODELS_FASE2_DIR",
    "REPORTS_FASE2_DIR",
    "FIGURES_FASE2_DIR",
    "CORTE_ANIO",
    "CORTE_TRIMESTRE",
    "TAMANO_MUESTRA_BUSQUEDA",
    "TAMANO_MAX_ENTRENO_LINEAL",
    "N_ITER_BUSQUEDA",
    "CV_FOLDS",
]
