"""
Punto de entrada del pipeline de ingeniería de datos.

Uso:
    python run_data_pipeline.py
    python run_data_pipeline.py --skip-ingestion   # si ya tienes el parquet intermedio
"""

from src.data_engineering.pipeline import run_full_pipeline

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de ingeniería de datos EPA")
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Omitir ingesta y usar el parquet intermedio existente",
    )
    args = parser.parse_args()

    run_full_pipeline(skip_ingestion=args.skip_ingestion)
