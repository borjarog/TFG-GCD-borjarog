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

# Corte temporal train/test: se entrena con todo lo anterior al corte y se
# evalúa con el corte en adelante (los trimestres más recientes), simulando
# el uso real del modelo para predecir el futuro a partir del pasado.
CORTE_ANIO = 2025
CORTE_TRIMESTRE = 1

# Tamaño de la submuestra estratificada usada SOLO durante la búsqueda de
# hiperparámetros (RandomizedSearchCV), para que sea viable en tiempo sobre
# ~1.7M filas. Los árboles (RF/LightGBM) se reentrenan con el train completo;
# la logística se limita a TAMANO_MAX_ENTRENO_LINEAL (lbfgs no escala bien
# a millones de filas con one-hot).
# Búsqueda más amplia que la primera pasada (8 iters / 80k): mejor exploración
# del espacio HP sin llegar a grid search inabordable sobre ~1M filas.
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
