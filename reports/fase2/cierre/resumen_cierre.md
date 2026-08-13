# Cierre Fase 2 — Prioridad 1

## Ablación
- Baseline PR-AUC: **0.0690**
- Solo demografía (LightGBM, 14 vars): **PR-AUC=0.1632**
- Modelo completo (+ laborales, 28 vars): **PR-AUC=0.4794**
- Salto demografía → completo: **+0.3162** PR-AUC

## Umbrales F1 (train)
- Completo: 0.825 → F1 test=0.5158
- Ablación: 0.625 → F1 test=0.2354

## Figuras
- `ablacion_demografia_vs_laboral.png`
- `errores_por_jornada.png` / sector / ocupación / CCAA
- Waterfalls SHAP locales

## Lectura
Las variables laborales aportan la mayor parte del poder predictivo del subempleo;
la demografía sola apenas supera el baseline en PR-AUC relativo al modelo completo.
