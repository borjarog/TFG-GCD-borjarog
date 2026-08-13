"""Ingesta + validación + features. `--skip-ingestion` si ya está el parquet."""

from src.data_engineering.pipeline import run_full_pipeline

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de ingeniería de datos EPA")
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Saltar ingesta y usar el parquet intermedio que ya hay",
    )
    args = parser.parse_args()

    run_full_pipeline(skip_ingestion=args.skip_ingestion)
