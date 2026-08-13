"""Ingeniería de datos EPA. El import del paquete no carga ingestion/features."""

from __future__ import annotations

__all__ = ["run_full_pipeline"]


def __getattr__(name: str):
    if name == "run_full_pipeline":
        from .pipeline import run_full_pipeline

        return run_full_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
