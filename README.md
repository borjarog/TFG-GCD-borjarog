# TFG Ciencia de Datos: Análisis del Mercado Laboral (EPA)

Análisis predictivo del mercado laboral español usando microdatos de la EPA (Encuesta de Población Activa).

## Estructura del proyecto

```
TFG-GCD-borjarog/
│
├── data/                         ← DATOS (no versionados en git, ver más abajo)
│   ├── raw/                      # Microdatos crudos del INE (CSV/TAB por trimestre)
│   ├── meta/                     # Excel "Diseño de Registro" oficial del INE (2021+) — SÍ está en git
│   └── processed/
│       ├── interim/              # Parquet parseado (post-ingesta)
│       └── modeling/             # Datasets finales para ML
│
├── docs/
│   └── diccionario_datos.md      # Diccionario de datos completo (todas las variables y códigos)
│
├── models/                       # Modelos entrenados (.joblib), no versionados en git
│   ├── fase1/
│   └── fase2/
│
├── reports/                      # Métricas, informes y gráficas del modelado
│   └── figures/
│       ├── fase1/
│       └── fase2/
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
│       ├── config.py             # Rutas de modelos/informes y parámetros de entrenamiento
│       ├── preprocessing.py      # Split temporal + preprocesado (nativo LightGBM / one-hot sklearn)
│       ├── model_specs.py        # Algoritmos candidatos y espacios de búsqueda de hiperparámetros
│       ├── evaluate.py           # Métricas y gráficas (matriz de confusión, curva PR)
│       ├── interpretability.py   # SHAP (beeswarm + barras |SHAP|)
│       ├── fase1.py              # Orquestador Fase 1 (Ocupado/Parado/Inactivo)
│       └── fase2.py              # Orquestador Fase 2 (subempleo en ocupados)
│
├── notebooks/
│   ├── ingenieria_datos/         ← Notebooks de datos (a rellenar)
│   └── modelado/                 ← Notebooks de modelos (a rellenar)
│
├── run_data_pipeline.py          # Entry point: ingesta + validación + feature engineering
├── run_model_fase1.py            # Entry point: modelado Fase 1
├── run_model_fase2.py            # Entry point: modelado Fase 2
├── contexto.md                   # Contexto y objetivos del TFG
└── requirements.txt
```

## Fases del TFG

- **Fase 1 (Macro):** Clasificación Ocupado / Parado / Inactivo, en dos etapas jerárquicas (Activo/Inactivo → Ocupado/Parado), población en edad activa 16–64. Se comparan Regresión Logística, Random Forest y LightGBM con búsqueda de hiperparámetros, evaluación en un test temporal e interpretabilidad con SHAP. Reto principal: desbalance de clases.
- **Fase 2 (Micro):** Subempleo por insuficiencia de horas (`AOI = 03`) solo en ocupados. Misma comparación de algoritmos + umbral calibrado (F1) + SHAP (factores de riesgo).

## Puesta en marcha en una máquina nueva (tras `git clone`)

Los datos (`data/raw`, `data/processed`) y los modelos entrenados (`models/`) **no están en git** por su tamaño (~1.2 GB); se regeneran localmente:

```cmd
pip install -r requirements.txt

REM 1. Ingesta + validación + feature engineering.
REM    Si data/raw/CSV está vacío, descarga automáticamente cada trimestre desde el INE.
python run_data_pipeline.py

REM 2. Modelado de Fase 1 (tarda: búsqueda de hiperparámetros con 3 algoritmos x 2 etapas)
python run_model_fase1.py

REM 3. Modelado de Fase 2 (subempleo en ocupados)
python run_model_fase2.py
```

El único dato que SÍ viaja con el repo es `data/meta/diseno_registro_2021_en_adelante.xlsx` (el diseño de registro oficial del INE, pesa poco y es necesario para poder generar el diccionario de datos y parsear ficheros de ancho fijo).

## Ingeniería de datos (detalle)

1. Asegúrate de tener el Excel de diseño de registro del INE en `data/meta/diseno_registro_2021_en_adelante.xlsx` (ya viene en el repo) y, opcionalmente, los microdatos trimestrales ya descargados en `data/raw/CSV/` (si no están, se descargan solos).
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

## Modelado de Fase 1 (detalle)

```cmd
python run_model_fase1.py
```

Artefactos generados:
- `models/fase1/*.joblib`: modelo ganador de cada etapa (Activo/Inactivo y Ocupado/Parado).
- `reports/fase1/comparacion_modelos.json` y `informe_final.txt`: métricas de los 3 algoritmos comparados y el informe de clasificación final (3 clases).
- `reports/figures/fase1/*.png`: matrices de confusión, curvas Precision-Recall y resúmenes SHAP.

## Modelado de Fase 2 (detalle)

```cmd
python run_model_fase2.py
```

Sobre `dataset_fase2_micro.parquet` (~1,08M ocupados, ~7,6% subempleo). Criterio de ganador: PR-AUC. Además se calibra un umbral de decisión (máx. F1 en train) y se generan SHAP beeswarm + barras de importancia.

Artefactos:
- `models/fase2/subempleo_*.joblib` y `umbral_decision.json`
- `reports/fase2/comparacion_modelos.json` e `informe_final.txt`
- `reports/figures/fase2/*.png`

## Configuración del entorno

```cmd
conda activate base
pip install -r requirements.txt
```

## Stack

Python, pandas, scikit-learn, XGBoost/LightGBM, SHAP, matplotlib, seaborn.
