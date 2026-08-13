"""Orquestador del pipeline de ingeniería de datos EPA."""

from .config import ANIO_FIN, ANIO_INICIO, INTERIM_EPA
from .features import ejecutar_pipeline
from .ingestion import ejecutar_ingesta
from .validation import cargar_datos, realizar_sanity_check


def run_full_pipeline(
    anio_inicio: int = ANIO_INICIO,
    anio_fin: int = ANIO_FIN,
    skip_ingestion: bool = False,
):
    """Ingesta, validación y feature engineering."""
    print("\n" + "=" * 60)
    print(" PIPELINE DE INGENIERÍA DE DATOS — EPA")
    print("=" * 60)

    if not skip_ingestion:
        print("\n>>> PASO 1/3: Ingesta")
        ejecutar_ingesta(anio_inicio, anio_fin)
    else:
        print("\n>>> PASO 1/3: Ingesta (omitida)")

    print("\n>>> PASO 2/3: Validación")
    df = cargar_datos()
    if df is None:
        raise FileNotFoundError(
            f"No se encontró el dataset intermedio esperado en:\n  {INTERIM_EPA}\n"
            "Ejecuta primero la ingesta o coloca el parquet intermedio manualmente."
        )
    realizar_sanity_check(df)

    print("\n>>> PASO 3/3: Feature engineering")
    ejecutar_pipeline()

    print("\n" + "=" * 60)
    print(" PIPELINE COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    run_full_pipeline()
