# TFG Ciencia de Datos: Análisis del Mercado Laboral (EPA)

Análisis predictivo del mercado laboral español usando microdatos de la EPA (Encuesta de Población Activa), con énfasis en **machine learning explicable** (SHAP), evaluación temporal y diseño anti-leakage por fases.

## Estructura del proyecto

```
TFG-GCF-borjarog/
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
├── reports/
│   ├── fase1/                    # comparacion_modelos.json, informe_final.txt
│   ├── fase2/                    # comparacion_modelos.json, informe_final.txt, cierre/
│   ├── figures/
│   │   ├── fase1/
│   │   └── fase2/                # incluye subcarpeta cierre/ (ablación, errores, waterfalls)
│   └── memoria/                  # Materiales listos para la memoria y la defensa
│       ├── 01_hilo_cientifico.md
│       ├── 02_hilo_fase2.md
│       ├── metricas_maestras.json
│       └── eda/                  # Figuras EDA exportadas
│
├── scripts/
│   └── generar_eda.py            # Generación de figuras EDA para la memoria
│
├── src/
│   ├── data_engineering/         ← INGENIERÍA DE DATOS
│   │   ├── config.py
│   │   ├── diccionario_datos.py
│   │   ├── ingestion.py
│   │   ├── validation.py
│   │   ├── features.py
│   │   └── pipeline.py
│   │
│   └── modeling/                 ← MODELADO
│       ├── config.py
│       ├── preprocessing.py
│       ├── model_specs.py
│       ├── evaluate.py           # Métricas, baseline, umbral F1 óptimo
│       ├── interpretability.py   # SHAP (beeswarm, barras, waterfalls)
│       ├── fase1.py
│       ├── fase2.py
│       └── fase2_cierre.py       # Ablación, análisis de errores, XAI local
│
├── notebooks/
│   ├── ingenieria_datos/
│   │   └── 01_eda.ipynb          # EDA + galería de figuras para memoria
│   └── modelado/
│       ├── 01_resultados_fase1.ipynb
│       └── 02_resultados_fase2.ipynb
│
├── run_data_pipeline.py          # Ingesta + validación + feature engineering
├── run_model_fase1.py            # Modelado Fase 1 (etapas A y B)
├── run_model_fase1_etapa_b.py    # Solo etapa B (si A ya está entrenada)
├── run_model_fase2.py            # Modelado Fase 2 (subempleo)
├── run_fase2_cierre.py           # Cierre académico Fase 2 (ablación, errores, waterfalls)
├── tests/                        # Tests mínimos (pytest)
├── contexto.md
└── requirements.txt
```

## Fases del TFG

- **Fase 0 — Ingeniería de datos:** EPA unificada → datasets Fase 1 (16–64, macro) y Fase 2 (ocupados, subempleo AOI=03). EDA documentado en notebook y `reports/memoria/eda/`.
- **Fase 1 (Macro):** Clasificación jerárquica anti-leakage (solo demografía): Activo/Inactivo → Ocupado/Parado. Comparación LogReg / Random Forest / LightGBM, baseline de prevalencia, umbral F1 calibrado, SHAP global. Split temporal train ≤ 2024T4 · test ≥ 2025T1.
- **Fase 2 (Micro):** Subempleo por insuficiencia de horas en ocupados. Demografía + variables laborales (sin fugas MASHOR/DISMAS/HORDES/BUSOTR). Cierre con ablación demográfica vs completa, waterfalls SHAP y análisis de errores por jornada, sector, ocupación y CCAA.

**Hilo científico:** la demografía explica la participación laboral, no basta para el paro; las variables del puesto aportan para el subempleo. Ver [`reports/memoria/01_hilo_cientifico.md`](reports/memoria/01_hilo_cientifico.md).

## Puesta en marcha en una máquina nueva (tras `git clone`)

Los datos (`data/raw`, `data/processed`) y los modelos entrenados (`models/`) **no están en git** por su tamaño (~1.2 GB); se regeneran localmente:

```cmd
pip install -r requirements.txt

REM 1. Ingesta + validación + feature engineering
python run_data_pipeline.py

REM 2. Modelado Fase 1 (tarda: búsqueda HP, 3 algoritmos x 2 etapas)
python run_model_fase1.py

REM 3. Modelado Fase 2
python run_model_fase2.py

REM 4. Cierre académico Fase 2 (ablación, errores, waterfalls SHAP)
python run_fase2_cierre.py
```

El único dato que SÍ viaja con el repo es `data/meta/diseno_registro_2021_en_adelante.xlsx` (diseño de registro INE, necesario para el diccionario y el parseo de ancho fijo).

## Notebooks (memoria y defensa)

Ejecutar **Run All** en cada notebook; cargan artefactos ya generados (no reentrenan salvo que lo indiques).

| Notebook | Contenido |
|---|---|
| [`notebooks/ingenieria_datos/01_eda.ipynb`](notebooks/ingenieria_datos/01_eda.ipynb) | Regenera/visualiza EDA → `reports/memoria/eda/` |
| [`notebooks/modelado/01_resultados_fase1.ipynb`](notebooks/modelado/01_resultados_fase1.ipynb) | Métricas, tabla de modelos, informe y figuras Fase 1 |
| [`notebooks/modelado/02_resultados_fase2.ipynb`](notebooks/modelado/02_resultados_fase2.ipynb) | Ablación, métricas, figuras y cierre Fase 2 |

## Ingeniería de datos (detalle)

1. Excel de diseño INE en `data/meta/diseno_registro_2021_en_adelante.xlsx` (incluido en el repo). Microdatos opcionales en `data/raw/CSV/` (si faltan, se descargan del INE).
2. Regenerar diccionario de datos:

```cmd
python -m src.data_engineering.diccionario_datos
```

3. Pipeline completo:

```cmd
python run_data_pipeline.py
python run_data_pipeline.py --skip-ingestion   # si ya tienes el parquet intermedio
```

Salida: `data/processed/interim/epa_2021_en_adelante.parquet`, `dataset_fase1_macro.parquet` y `dataset_fase2_micro.parquet`.

4. EDA para la memoria:

```cmd
python scripts/generar_eda.py
```

## Modelado de Fase 1 (detalle)

```cmd
python run_model_fase1.py
python run_model_fase1_etapa_b.py   # solo etapa B, reutilizando modelos A guardados
```

Artefactos:
- `models/fase1/*.joblib` — ganadores por etapa (RF en A, LightGBM en B)
- `reports/fase1/comparacion_modelos.json`, `informe_final.txt`
- `reports/figures/fase1/*.png` — curvas PR, matrices (@0.50 y umbral F1), SHAP, combinado 3 clases

## Modelado de Fase 2 (detalle)

```cmd
python run_model_fase2.py
python run_fase2_cierre.py
```

Sobre ~1,08 M ocupados (~7,6 % subempleo). Ganador por PR-AUC; umbral F1 calibrado en train.

Artefactos:
- `models/fase2/subempleo_*.joblib`, `umbral_decision.json`
- `reports/fase2/comparacion_modelos.json`, `informe_final.txt`
- `reports/fase2/cierre/` — JSON/CSV/Markdown de ablación y errores
- `reports/figures/fase2/` y `reports/figures/fase2/cierre/`

## Materiales para la memoria

| Documento | Uso |
|---|---|
| [`reports/memoria/01_hilo_cientifico.md`](reports/memoria/01_hilo_cientifico.md) | Intro, metodología, conclusiones, limitaciones |
| [`reports/memoria/02_hilo_fase2.md`](reports/memoria/02_hilo_fase2.md) | Capítulo subempleo / calidad del empleo |
| [`reports/memoria/metricas_maestras.json`](reports/memoria/metricas_maestras.json) | Cifras clave para tablas |
| [`reports/memoria/eda/`](reports/memoria/eda/) | Figuras exploratorias |

## Configuración del entorno

```cmd
conda activate base
pip install -r requirements.txt
```

## Tests

Tests mínimos de reproducibilidad (split temporal, umbrales, anti-fuga Fase 2):

```cmd
pytest
```

Archivos en `tests/`: `test_evaluate.py`, `test_preprocessing.py`, `test_anti_leakage.py`.

## Stack

Python, pandas, scikit-learn, LightGBM, SHAP, matplotlib, seaborn, pytest.
