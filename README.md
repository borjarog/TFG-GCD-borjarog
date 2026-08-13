# TFG: mercado laboral español (EPA)

Modelos de clasificación sobre microdatos de la EPA (INE). Fase 1: ocupado / parado / inactivo (16-64, solo demografía). Fase 2: subempleo por insuficiencia de horas (AOI=03) en ocupados. Evaluación con split temporal (train hasta 2024T4, test desde 2025T1) e interpretabilidad con SHAP.

## Entorno

```cmd
pip install -r requirements.txt
```

Datos crudos, parquet procesado y `.joblib` no van en git (pesan ~1.2 GB). El Excel de diseño de registro del INE sí está: `data/meta/diseno_registro_2021_en_adelante.xlsx`.

## Cómo ejecutarlo

```cmd
python run_data_pipeline.py
python run_model_fase1.py
python run_model_fase2.py
python run_fase2_cierre.py
```

Si el parquet intermedio ya existe: `python run_data_pipeline.py --skip-ingestion`.

Si faltan CSV en `data/raw/CSV/`, la ingesta los descarga del INE. Diccionario de variables: `python -m src.data_engineering.diccionario_datos`. Figuras EDA: `python scripts/generar_eda.py`. Tests: `pytest`.

Salidas: `data/processed/`, `models/`, `reports/`.

## Estructura

```
data/            raw, meta, processed (interim + modeling)
docs/            diccionario de datos
src/data_engineering/
src/modeling/
notebooks/       EDA y resultados
scripts/         generar_eda.py
reports/         métricas, figuras, textos para la memoria
models/          joblib (no versionados)
tests/
run_*.py         puntos de entrada
```

Notebooks: `notebooks/ingenieria_datos/01_eda.ipynb`, `notebooks/modelado/01_resultados_fase1.ipynb`, `notebooks/modelado/02_resultados_fase2.ipynb`. Cargan lo ya generado; no hace falta reentrenar.

Textos y cifras para la memoria: `reports/memoria/`.
