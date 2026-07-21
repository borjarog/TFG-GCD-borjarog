# TFG Ciencia de Datos: Análisis del Mercado Laboral (EPA)

Análisis predictivo del mercado laboral español usando microdatos de la EPA (Encuesta de Población Activa).

## Estructura del proyecto

```
TFG-GCD-borjarog/
│
├── data/                         ← DATOS
│   ├── raw/                      # Microdatos crudos del INE (CSV/TAB por trimestre)
│   ├── meta/                     # Excel "Diseño de Registro" oficial del INE (2021+)
│   └── processed/
│       ├── interim/              # Parquet parseado (post-ingesta)
│       └── modeling/             # Datasets finales para ML
│
├── docs/
│   └── diccionario_datos.md      # Diccionario de datos completo (todas las variables y códigos)
│
├── src/
│   ├── data_engineering/         ← INGENIERÍA DE DATOS
│   │   ├── config.py             # Rutas y configuración
│   │   ├── diccionario_datos.py  # Diccionario de datos + utilidades de mapeo de códigos
│   │   ├── ingestion.py          # Lectura local (data/raw/CSV) + descarga INE de trimestres nuevos
│   │   ├── validation.py         # Sanity checks del dataset intermedio
│   │   ├── features.py           # Feature engineering: datasets Fase 1 y Fase 2
│   │   └── pipeline.py           # Orquestador de los 3 pasos
│   │
│   └── modeling/                 ← MODELADO
│       ├── model_fase1_baseline.py
│       ├── models.py
│       └── visualization.py
│
├── notebooks/
│   ├── ingenieria_datos/         ← Notebooks de datos (a rellenar)
│   └── modelado/                 ← Notebooks de modelos (a rellenar)
│
├── contexto.md                   # Contexto y objetivos del TFG
└── requirements.txt
```

## Fases del TFG

- **Fase 1 (Macro):** Clasificación Ocupado / Parado / Inactivo. Reto: desbalance de clases.
- **Fase 2 (Micro):** Subempleo por insuficiencia de horas en ocupados. Interpretabilidad con SHAP.

## Ingeniería de datos (empezar aquí)

1. Asegúrate de tener el Excel de diseño de registro del INE en `data/meta/diseno_registro_2021_en_adelante.xlsx` y los microdatos trimestrales en `data/raw/CSV/`.
2. (Re)genera el diccionario de datos completo, fuente de verdad para todo el pipeline:

```cmd
python -m src.data_engineering.diccionario_datos
```

Esto crea [`docs/diccionario_datos.md`](docs/diccionario_datos.md): las 91 variables del cuestionario EPA, con su posición/longitud en el fichero y, si son categóricas, todos sus códigos oficiales con su significado.

3. Ejecuta el pipeline completo (ingesta → validación → feature engineering):

```cmd
python run_data_pipeline.py
python run_data_pipeline.py --skip-ingestion   # si ya tienes el parquet intermedio
```

Esto genera `data/processed/interim/epa_2021_en_adelante.parquet` y, en `data/processed/modeling/`, `dataset_fase1_macro.parquet` (Ocupado/Parado/Inactivo) y `dataset_fase2_micro.parquet` (subempleo por insuficiencia de horas, `AOI = 03`).

## Configuración del entorno

```cmd
conda activate base
pip install -r requirements.txt
```

## Stack

Python, pandas, scikit-learn, XGBoost/LightGBM, SHAP, matplotlib, seaborn.
