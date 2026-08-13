# Hilo científico, métricas maestras y limitaciones

**TFG:** Machine Learning explicable para analizar el estado laboral y la calidad del empleo en España  
**Fuente:** microdatos EPA (INE), 2021T1–2026T1  
**Evaluación:** split temporal — train ≤ 2024T4 · test ≥ 2025T1  

Este documento concentra el relato científico del trabajo, la tabla de métricas y las limitaciones. Los informes detallados están en `reports/fase1/` y `reports/fase2/`.

---

## 1. Tesis en una frase

> Con variables **demográficas** se puede anticipar razonablemente la **participación** en el mercado de trabajo (activo vs inactivo), pero **no** diagnosticar bien el **paro** frente a la ocupación; cuando se incorporan variables del **puesto** (horas, jornada, ocupación, contrato…), el modelo **sí** aporta poder predictivo y explicación sobre el **subempleo** por insuficiencia de horas.

Ese es el hilo que debe atravesar introducción, resultados y conclusiones.

---

## 2. Hilo narrativo por fases

### Fase 0 — Ingeniería de datos (EPA)

Se unifica la EPA en un dataset intermedio (~2,63 M registros) y se construyen dos vistas de modelado:

| Dataset | Filas | Rol |
|---|---:|---|
| Interim (EPA unificada) | 2.627.372 | Base limpia previa al ML |
| Fase 1 (16–64) | 1.626.199 | Estado laboral macro |
| Fase 2 (ocupados) | 1.079.939 | Subempleo AOI=03 (~7,59 %) |

**Mensaje:** el problema no es “falta de datos”, sino **qué información se permite usar** en cada fase.

### Fase 1 — Techo predictivo demográfico

Diseño jerárquico anti-leakage (solo demografía):

1. **Etapa A:** Activo vs Inactivo → **Random Forest** (PR-AUC ≈ 0,938)  
2. **Etapa B:** Ocupado vs Parado (sobre activos) → **LightGBM** (PR-AUC ≈ 0,273)  
3. **Combinado A→B** con umbrales F1 calibrados (A=0,275 · B=0,625) → accuracy ≈ **0,72**

**Mensaje:** la demografía **estructura la participación**; **no basta** para separar paro y ocupación. El accuracy combinado ~72 % se interpreta como **límite informativo**, no como fallo del algoritmo (los tres candidatos de B quedan cercanos).

### Fase 2 — Calidad del empleo (subempleo)

Universo: ocupados. Target oficial **AOI=03**. Predictoras demográficas + laborales (sin MASHOR/DISMAS/HORDES/BUSOTR por fuga).

- Ganador: **LightGBM** (PR-AUC ≈ 0,479 · ROC-AUC ≈ 0,896)  
- Umbral F1 (train) = **0,825** → F1 test ≈ **0,52**

**Ablación (prueba estrella):**

| Modelo | PR-AUC test |
|---|---:|
| Baseline (prevalencia) | 0,069 |
| Solo demografía (14 vars) | 0,163 |
| Completo + laborales (28 vars) | **0,479** |
| Salto demografía → completo | **+0,316** |

**Mensaje:** el subempleo “vive” en el **empleo**, no solo en el perfil personal. Fase 2 no es “más de lo mismo” que Fase 1.

> Desarrollo completo de Fase 2 (ablación, errores, XAI, variables, limitaciones propias): ver [`02_hilo_fase2.md`](02_hilo_fase2.md).

### Síntesis (Fase 3 narrativa)

EPA → techo demográfico (F1) → valor añadido laboral + XAI (F2) → lectura de calidad del empleo (parcialidad, horas, ocupación elemental) con sesgos explícitos (sobrepredicción en jornada parcial).

---

## 3. Afirmación ↔ evidencia (para memoria y defensa)

| Afirmación | Evidencia principal | Dónde está |
|---|---|---|
| La EPA se puede operacionalizar en un pipeline reproducible | Volúmenes interim / F1 / F2; cobertura 2021–2026 | `reports/memoria/eda/` |
| Filtrar 16–64 evita trivializar el problema | Exclusión de EDAD1=65+; caída esperada de accuracy vs incluir jubilados | `features.py`, EDA volúmenes |
| Fase 1 no usa variables laborales (anti-leakage) | 23 predictoras demográficas; exclusión explícita de OCUP/ACT/horas/BUSCA… | `features.py`, `preprocessing.py` |
| La participación laboral es predecible con demografía | Etapa A: PR-AUC 0,938 · ROC 0,86 | `reports/fase1/` |
| El paro no se diagnostica bien solo con demografía | Etapa B: PR-AUC ~0,27; F1 parado ~0,31–0,33 | `reports/fase1/` |
| El sistema cascada es el resultado operativo de Fase 1 | Combinado 3 clases: accuracy 0,72; F1 parado 0,25 | `informe_final.txt` Fase 1 |
| El desbalance se trata sin SMOTE | `class_weight=balanced` + selección por PR-AUC + umbral F1 | `model_specs.py`, evaluate |
| Las variables laborales aportan de verdad en subempleo | Ablación: 0,163 → 0,479 PR-AUC (+0,316) | `reports/fase2/cierre/` |
| El mecanismo del subempleo es horas/jornada | SHAP global + waterfalls TP/TN/FN | `reports/figures/fase2/` |
| El modelo exagera el proxy “jornada parcial” | Real 33 % vs predicho 58 % en parcial | `errores_por_jornada.*` |
| No hay leakage en el target de Fase 2 | Target AOI=03; excluidos MASHOR/DISMAS/HORDES/BUSOTR | `fase2.py`, docstring features |

---

## 4. Decisiones de diseño (página para la memoria)

| Decisión | Por qué | Alternativa descartada |
|---|---|---|
| **EPA como única fuente** | Microdatos oficiales, definición OIT de subempleo, volumen y reproducibilidad | Cambiar de dataset a mitad de TFG |
| **Split temporal (corte 2025T1)** | Simula uso real: entrenar con pasado, evaluar futuro | Split aleatorio (fuga temporal / optimismo) |
| **Fase 1 solo demografía** | Medir techo predictivo sin filtrar el estado laboral | Meter ocupación/horas (leakage) |
| **Población 16–64 en Fase 1** | Evitar que el modelo sea un detector de jubilación | Incluir 65+ (métricas artificialmente altas) |
| **Clasificación jerárquica A→B** | Respeta la estructura Activo⊃{Ocupado,Parado}; facilita umbrales y XAI por etapa | Un solo multiclass sin cascada |
| **Selección por PR-AUC** | Clases raras (paro ~9 %, subempleo ~7,6 %); la accuracy engaña | Optimizar accuracy |
| **`class_weight=balanced`** | No ignorar la clase positiva en el entrenamiento | SMOTE (irreal con categóricas EPA a escala millón) |
| **Umbral F1 calibrado en train** | Traducir ranking a etiqueta operativa sin mirar el test | Umbral fijo 0,5 |
| **Target Fase 2 = AOI=03** | Definición oficial INE/OIT | Construir subempleo “casero” con MASHOR |
| **Excluir MASHOR/DISMAS/HORDES/BUSOTR** | Son (casi) la definición del target | Incluirlas “para subir métricas” |
| **Comparar LogReg / RF / LightGBM** | Familias distintas (lineal, bagging, boosting) | Un solo algoritmo |
| **SHAP (global + local)** | Exigencia de explicabilidad del título del TFG | Solo importancia de impureza |

---

## 5. Tabla maestra de métricas (test temporal)

Criterio de ganador en binarios: **PR-AUC**. Umbrales: maximizan **F1** de la clase positiva en **train**.

### 5.1. Fase 1 — por etapa

| Bloque | Modelo | PR-AUC | ROC-AUC | F1 @0,50 | Umbral F1 | F1 @umbral | Notas |
|---|---|---:|---:|---:|---:|---:|---|
| A Activo/Inactivo | Baseline prevalencia | 0,749 | 0,500 | — | — | — | Prevalencia activo train ≈ 0,74 |
| A | Logística | 0,926 | 0,836 | 0,853 | — | — | |
| A | **Random Forest** | **0,938** | **0,858** | 0,857 | **0,275** | **0,896** | Ganador A |
| A | LightGBM | 0,938 | 0,857 | 0,853 | — | — | Empate técnico |
| B Ocupado/Parado | Baseline prevalencia | 0,102 | 0,500 | 0,000 | — | — | Parado ≈ 10–12 % de activos |
| B | Logística | 0,242 | 0,734 | 0,313 | — | — | |
| B | Random Forest | 0,272 | 0,751 | 0,323 | — | — | |
| B | **LightGBM** | **0,273** | **0,753** | 0,314 | **0,625** | **0,334** | Ganador B |

### 5.2. Fase 1 — combinado A→B (umbrales calibrados)

| Clase | Precision | Recall | F1 | Support (test) |
|---|---:|---:|---:|---:|
| Inactivo | 0,76 | 0,50 | 0,61 | 88.825 |
| Ocupado | 0,81 | 0,84 | 0,83 | 238.460 |
| Parado | 0,19 | 0,34 | 0,25 | 27.023 |
| **Accuracy** | | | **0,72** | 354.308 |
| Macro avg F1 | | | ≈ 0,56 | |

### 5.3. Fase 2 — subempleo

| Modelo | PR-AUC | ROC-AUC | F1 @0,50 | Umbral F1 | F1 @umbral |
|---|---:|---:|---:|---:|---:|
| Baseline prevalencia | 0,069 | 0,500 | 0,000 | — | — |
| Logística | 0,422 | 0,868 | 0,420 | — | — |
| Random Forest | 0,468 | 0,892 | 0,425 | — | — |
| **LightGBM (completo)** | **0,479** | **0,896** | 0,422 | **0,825** | **0,516** |
| LightGBM solo demografía (ablación) | 0,163 | 0,714 | 0,214 | 0,625 | 0,235 |

### 5.4. Números “de diapositiva” (defensa)

Llevar solo estos en una slide:

1. **A:** PR-AUC **0,94** — la participación se predice con demografía.  
2. **B:** PR-AUC **0,27** — el paro no.  
3. **Combinado:** accuracy **0,72** — techo del sistema Fase 1.  
4. **Ablación F2:** 0,16 → **0,48** (+0,32) — aportan las variables laborales.  
5. **F2 operativo:** F1 subempleo **0,52** @ umbral 0,825 · ROC **0,90**.

---

## 6. Tratamiento del desbalance (párrafo listo)

Las clases positivas son minoritarias (parado ≈ 9 % en Fase 1; subempleo ≈ 7,6 % en Fase 2). No se recurre a SMOTE ni a undersampling agresivo: a esta escala, con muchas categóricas EPA, el muestreo sintético inventaría perfiles poco defendibles y destruiría información útil. El desbalance se aborda en tres capas: (i) `class_weight="balanced"` en logística, Random Forest y LightGBM; (ii) selección de modelos por **PR-AUC**, métrica sensible al ranking de la clase rara; (iii) umbral de decisión calibrado maximizando **F1 en train**, no el 0,5 por defecto. Se reportan además balanced accuracy y precision/recall por clase, junto a un baseline de prevalencia.

---

## 7. Limitaciones (sección para la memoria)

1. **EPA es encuesta, no censo.** Los modelos estiman patrones en microdatos ponderables por diseño muestral; no constituyen un sistema de scoring individual para políticas públicas sin validación adicional.  
2. **Fase 1 mide un techo informativo.** El PR-AUC bajo de Ocupado vs Parado refleja solapamiento demográfico, no necesariamente un mal algoritmo: LogReg, RF y LightGBM quedan cercanos.  
3. **La cascada A→B propaga errores.** Un parado etiquetado como inactivo en A no llega a B; las métricas de B (sobre activos reales) son algo más optimistas que el sistema combinado.  
4. **El umbral F1 es una elección de coste.** Otra política (p. ej. maximizar recall a precisión fija) cambiaría precision/recall sin alterar el PR-AUC.  
5. **Variables temporales (`ANIO_REF`, `TRIMESTRE_REF`)** pueden capturar coyuntura; se mantienen por cobertura longitudinal y se discuten en XAI (impacto relativo menor frente a demografía/laborales clave).  
6. **Fase 2 sobrepredice en jornada parcial** (real ~33 % vs predicho ~58 %). El modelo identifica el canal correcto (parcialidad/horas) y lo exagera al umbral 0,825; infraestima subempleo en perfiles industriales/cualificados menos “prototípicos”.  
7. **XAI es aproximada.** SHAP explica el modelo entrenado, no causalidad económica; los waterfalls ilustran casos, no promedios poblacionales.  
8. **Reproducibilidad de modelos grandes.** Los `.joblib` de Random Forest son pesados y están fuera de git; la reproducción exige reentrenar o disponer de los artefactos locales.

Estas limitaciones no invalidan los resultados: **acotan** la interpretación y refuerzan el carácter científico del TFG.

---

## 8. Cómo usar este documento en la memoria

Sugerencia de mapeo a capítulos:

| Sección memoria | Usar de aquí |
|---|---|
| Introducción / objetivos | §1 tesis + §2 hilo |
| Metodología | §4 decisiones + §6 desbalance |
| Resultados Fase 1 | §5.1–5.2 + filas F1 de §3 |
| Resultados Fase 2 | §5.3 + ablación de §2/§3 |
| Discusión | §2 síntesis + §7 limitaciones |
| Conclusiones | §1 + 5 números de §5.4 |
| Defensa (slides) | §5.4 + tabla §3 (5–6 filas) |

---

## 9. Referencias internas de artefactos

| Contenido | Ruta |
|---|---|
| EDA / volúmenes | `reports/memoria/eda/` |
| Informe y comparación Fase 1 | `reports/fase1/` |
| Figuras Fase 1 | `reports/figures/fase1/` |
| Informe y comparación Fase 2 | `reports/fase2/` |
| Ablación, errores, waterfalls | `reports/fase2/cierre/` · `reports/figures/fase2/cierre/` |
| Notebooks | `notebooks/ingenieria_datos/01_eda.ipynb` · `notebooks/modelado/02_resultados_fase2.ipynb` |

*Cifras de los informes de Fase 1 (ago. 2026) y Fase 2.*
