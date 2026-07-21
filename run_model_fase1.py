"""
Punto de entrada del modelado de Fase 1 (Ocupado / Parado / Inactivo).

Compara Regresión Logística, Random Forest y LightGBM en un esquema
jerárquico de dos etapas (Activo/Inactivo -> Ocupado/Parado), con búsqueda
de hiperparámetros, evaluación en un test temporal (los trimestres más
recientes) e interpretabilidad con SHAP.

Uso:
    python run_model_fase1.py
"""

from src.modeling.fase1 import ejecutar_pipeline_fase1

if __name__ == "__main__":
    ejecutar_pipeline_fase1()
