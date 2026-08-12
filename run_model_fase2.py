"""
Punto de entrada del modelado de Fase 2 (subempleo por insuficiencia de horas).

Compara Regresión Logística, Random Forest y LightGBM sobre ocupados,
con búsqueda de hiperparámetros (PR-AUC), test temporal, umbral calibrado
e interpretabilidad SHAP.

Uso:
    python run_model_fase2.py
"""

from src.modeling.fase2 import ejecutar_pipeline_fase2

if __name__ == "__main__":
    ejecutar_pipeline_fase2()
