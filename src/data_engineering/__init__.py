"""Pipeline de ingeniería de datos EPA.

Import ligero: no arrastra ingestion/validation/features al importar el paquete
(p. ej. `from src.data_engineering.config import ...` desde notebooks).
"""

from __future__ import annotations

__all__ = ["run_full_pipeline"]


def __getattr__(name: str):
    if name == "run_full_pipeline":
        from .pipeline import run_full_pipeline

        return run_full_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
