# Contexto del Proyecto: TFG Ciencia de Datos
**Objetivo:** Análisis predictivo del mercado laboral español usando microdatos de la EPA (Encuesta de Población Activa).

**Fase 1 (Macro):** 
- Modelo de clasificación multiclase.
- Variable objetivo: Estado general (Ocupado, Parado, Inactivo).
- Reto principal: Desbalance de clases.

**Fase 2 (Micro):** 
- Aislar solo a la población "Ocupada".
- Variable objetivo: "Subempleo por insuficiencia de horas" (definición OIT).
- Modelado predictivo (Gradient Boosting, Random Forest).
- Interpretabilidad: Extraer factores de riesgo usando valores SHAP (eXplainable AI).

**Stack Tecnológico:**
Python, pandas, scikit-learn, XGBoost/LightGBM, shap, matplotlib, seaborn.