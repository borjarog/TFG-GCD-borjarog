# Resumen EDA — Ingeniería de datos (EPA)

## Volúmenes
- Interim: **2.627.372** filas × 97 columnas
- Fase 1 (16–64): **1.626.199** filas × 26 columnas
- Fase 2 (ocupados): **1.079.939** filas × 32 columnas

## Targets
- Fase 1 — Ocupado 65.17% · Parado 8.76% · Inactivo 26.07%
- Fase 2 — Tasa de subempleo (AOI=03): **7.59%**

## Periodo
- Trimestres: 2021T1, 2021T2, 2021T3, 2021T4, 2022T1, 2022T2, 2022T3, 2022T4, 2023T1, 2023T2, 2023T3, 2023T4, 2024T1, 2024T2, 2024T3, 2024T4, 2025T1, 2025T2, 2025T3, 2025T4, 2026T1

## Figuras generadas
- `01_volumenes_pipeline.png`
- `02_cobertura_temporal.png`
- `03_target_fase1_macro.png`
- `04_edad_sexo_fase1.png`
- `05_educacion_vs_estado.png`
- `10_evolucion_estado_fase1.png`
- `12_top_ccaa_parado_fase1.png`
- `06_subempleo_fase2.png`
- `07_horas_vs_subempleo.png`
- `08_jornada_vs_subempleo.png`
- `11_evolucion_subempleo_fase2.png`
- `09_nulos_estructurales.png`

## Notas para la memoria
- Los nulos altos en origen/formación/contrato son **estructurales** (no aplica), no fallos de calidad.
- Fase 1 excluye 65+ para no reducir el problema a detectar jubilación.
- Fase 2 se centra en ocupados; las horas diferencian con claridad el subempleo.
- Colores: verde petróleo/naranja = estados laborales; azul/ámbar = datasets Fase 1/2.
