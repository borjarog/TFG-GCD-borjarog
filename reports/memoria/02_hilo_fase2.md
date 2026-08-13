# Fase 2 — Hilo científico, métricas, diseño y limitaciones

**TFG:** Machine Learning explicable para analizar el estado laboral y la calidad del empleo en España  
**Fase 2:** subempleo por insuficiencia de horas (ocupados, AOI=03)  
**Evaluación:** split temporal — train ≤ 2024T4 · test ≥ 2025T1  

Documento paralelo a `01_hilo_cientifico.md`, centrado solo en **Fase 2**. Listo para el capítulo de resultados/discusión de calidad del empleo.

Complementa: `reports/fase2/informe_final.txt`, `reports/fase2/cierre/`, `notebooks/modelado/02_resultados_fase2.ipynb`.

---

## 1. Tesis de la Fase 2 (una frase)

> Entre los **ocupados**, el **subempleo** (definición oficial AOI=03) **no se explica bien solo con demografía**; las variables del **puesto** (horas, jornada, ocupación, contrato, antigüedad…) aportan el salto predictivo principal (+0,32 PR-AUC en ablación) y permiten una lectura explicable del riesgo.

Puente con Fase 1: allí la demografía bastaba para **participación** y fallaba para el **paro**; aquí se demuestra que, para **calidad del empleo**, hace falta mirar **cómo se trabaja**.

---

## 2. Hilo narrativo de la Fase 2

### 2.1. Planteamiento

- **Universo:** solo ocupados (~1,08 M filas en el dataset de modelado; test temporal ~244 k).  
- **Target:** `TARGET_SUBEMPLEO = 1` si **AOI=03** (ocupados subempleados por insuficiencia de horas, OIT/INE).  
- **Tasa global:** ≈ **7,59 %** (clase rara → PR-AUC y umbral F1, no accuracy).  
- **Predictoras (~28):** demografía + laborales.  
- **Exclusiones anti-leakage:** MASHOR, DISMAS, RZNDISH, HORDES, BUSOTR (fuente/síntoma casi directo de AOI=03). Las **horas habituales/efectivas** sí entran como factores de riesgo, no como etiqueta.

### 2.2. Modelado

Comparación LogReg / Random Forest / LightGBM, búsqueda por **PR-AUC**, `class_weight=balanced`, umbral F1 calibrado en train.

| Resultado | Valor |
|---|---|
| Ganador | **LightGBM** |
| PR-AUC test | **0,479** |
| ROC-AUC test | **0,896** |
| Umbral F1 (train) | **0,825** |
| F1 test @ umbral | **0,516** |
| Accuracy @ umbral | **0,93** |

**Mensaje:** el modelo **ordena muy bien** el riesgo (ROC ~0,90) y, con umbral alto, prioriza **no etiquetar a la ligera** (precision del subempleo sube respecto a 0,5).

### 2.3. Ablación (prueba estrella)

Misma familia (LightGBM), mismo split, dos sets de features:

| Modelo | # vars | PR-AUC | ROC-AUC | F1 @ umbral óptimo |
|---|---:|---:|---:|---:|
| Baseline prevalencia | 0 | 0,069 | 0,500 | 0 |
| Solo demografía | 14 | 0,163 | 0,714 | 0,235 |
| Completo (+ laborales) | 28 | **0,479** | **0,896** | **0,516** |
| **Salto** demografía → completo | | **+0,316** | +0,182 | +0,281 |

**Mensaje para el tribunal:** Fase 2 no es un “retoque” de Fase 1. Sin laborales, el PR-AUC se queda en el mismo orden de magnitud que el techo débil de Fase 1-B; con laborales, **casi se triplica**.

### 2.4. Explicabilidad

- **Global:** SHAP beeswarm + barras → dominan **horas**, **tipo de jornada**, antigüedad, ocupación, sector.  
- **Local (waterfalls):**  
  - **TP:** parcial + pocas horas + poca antigüedad + ocupación elemental → P≈0,97.  
  - **TN:** completa + muchas horas + profesional + mucha antigüedad + público → P≈0,003.  
  - **FN:** parcial + pocas horas, pero antigüedad alta y sector público tiran hacia abajo → P≈0,825 (justo en el umbral).

**Mensaje:** el modelo rediscubre el mecanismo OIT (insuficiencia de horas / parcialidad), no un artefacto opaco.

### 2.5. Errores estructurados (lectura de calidad del empleo)

| Corte | Hallazgo |
|---|---|
| **Jornada parcial** | Real ~33 % vs predicho ~58 % → **sobrepredice** el proxy parcialidad |
| **Jornada completa** | Real ~2,8 % vs predicho ~0,6 % → casi no se atreve |
| **Ocupaciones elementales / servicios** | Sobrepredicción donde el subempleo ya es alto |
| **Industria / construcción / oficios cualificados** | Infraestimación (subempleo menos “prototípico”) |
| **CCAA** | Ranking razonable (Extremadura arriba; Cataluña/Aragón bien calibradas); sesgo a predecir de más en varias CCAA |

**Mensaje:** el modelo identifica el **canal correcto** y **exagera** al convertirlo en etiqueta dura; eso es discutible y valioso, no un fracaso ocultable.

---

## 3. Afirmación ↔ evidencia (Fase 2)

| Afirmación | Evidencia | Artefacto |
|---|---|---|
| El target es la definición oficial, no una construcción ad hoc | AOI=03 (OIT/INE) | `features.py` · informe Fase 2 |
| No hay fuga por variables de definición del target | Excluidos MASHOR, DISMAS, HORDES, BUSOTR | docstring `fase2.py` |
| LightGBM es el mejor ranking | PR-AUC 0,479 > RF 0,468 > LogReg 0,422 | `comparacion_modelos.json` |
| El umbral 0,5 no es el operativo | F1 0,42 @0,5 vs **0,52** @0,825 | matrices @0,5 y @óptimo |
| La demografía sola no basta | Ablación PR-AUC 0,163 | `ablacion_demografia_vs_laboral.png` |
| Las laborales aportan el salto | +0,316 PR-AUC | `cierre/resumen_cierre.md` |
| Horas y jornada impulsan la predicción | SHAP global + waterfall TP | `figures/fase2/` · `cierre/shap_waterfall_*` |
| Hay sesgo hacia jornada parcial | 33 % real vs 58 % predicho | `errores_por_jornada.csv` |
| El riesgo se concentra en ocupaciones elementales/servicios | Tasas reales y predichas más altas | `errores_por_ocupacion.*` |
| El puente con Fase 1 es coherente | Demografía floja en F1-B y en ablación F2 | `01_hilo_cientifico.md` §2 |

---

## 4. Decisiones de diseño (solo Fase 2)

| Decisión | Por qué | Alternativa descartada |
|---|---|---|
| Solo **ocupados** | El subempleo AOI=03 se define sobre ocupados | Incluir parados/inactivos (target sin sentido) |
| Target **AOI=03** | Definición oficial comparable | Regla casera MASHOR+DISMAS (fuga / menos defendible) |
| Incluir **horas** como predictores | Son factores de riesgo laborales, no la etiqueta AOI | Excluirlas todas (perder el mecanismo) o meter MASHOR (leakage) |
| Excluir **REGION_TRABAJO** | ~99 % nulo; basta provincia de trabajo | Forzarla con imputación absurda |
| Misma lógica **PR-AUC + pesos + umbral F1** que Fase 1 | Homogeneidad metodológica ante clase rara | Accuracy / SMOTE |
| **Ablación** demografía vs completo | Demostrar valor añadido de Fase 2 frente a Fase 1 | Solo reportar el modelo full |
| **Errores por jornada/sector/ocupación/CCAA** | Pasar de métrica global a lectura de calidad del empleo | Solo matriz de confusión |
| **Waterfalls** TP / TN / FN | XAI individual para defensa | Solo beeswarm global |
| No reentrenar RF “una noche más” por décimas | LightGBM ya gana; coste/beneficio pobre | Grid search masivo |

---

## 5. Tabla maestra Fase 2

### 5.1. Comparación de candidatos (test, @0,50 salvo umbral)

| Modelo | PR-AUC | ROC-AUC | F1 @0,50 | Umbral F1 | F1 @umbral |
|---|---:|---:|---:|---:|---:|
| Baseline prevalencia | 0,069 | 0,500 | 0,000 | — | — |
| Regresión logística | 0,422 | 0,868 | 0,420 | — | — |
| Random Forest | 0,468 | 0,892 | 0,425 | — | — |
| **LightGBM completo** | **0,479** | **0,896** | 0,422 | **0,825** | **0,516** |
| LightGBM solo demografía | 0,163 | 0,714 | 0,214 | 0,625 | 0,235 |

### 5.2. Informe operativo @ umbral 0,825 (ganador)

| Clase | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| No subempleo | 0,97 | 0,95 | 0,96 | 227.097 |
| Subempleo | 0,47 | 0,57 | **0,52** | 16.821 |
| Accuracy | | | **0,93** | 243.918 |

### 5.3. Jornada (test, umbral del modelo completo)

| Jornada | n | % subempleo real | % predicho | Accuracy del corte |
|---|---:|---:|---:|---:|
| Parcial | 32.746 | 33,3 | 58,1 | 64,1 |
| Completa | 211.172 | 2,8 | 0,6 | 97,1 |

### 5.4. Números de diapositiva (Fase 2)

1. Tasa de subempleo ≈ **7,6 %**.  
2. LightGBM: PR-AUC **0,48** · ROC **0,90**.  
3. Ablación: **0,16 → 0,48** (+0,32).  
4. Umbral **0,825** → F1 **0,52**.  
5. Parcial: real **33 %** / predicho **58 %** (sesgo del proxy).

---

## 6. Variables (qué entra y qué no)

### Entran (modelo completo, 28)

**Demográficas / hogar / tiempo:** ANIO_REF, TRIMESTRE_REF, CCAA, PROV, SEXO, TRAMO_EDAD, NIVEL_EDUC, ESTADO_CIVIL, NACIONALIDAD, ROL_HOGAR, ESTUDIANDO_AHORA, TAM_HOGAR, CARGA_FAMILIAR, VULNERABILIDAD_JOVEN  

**Laborales:** TIPO_CONTRATO, TIPO_JORNADA, SITUACION_PROF, SECTOR_ACTIVIDAD, SEGUNDO_EMPLEO, HORAS_HABITUALES, HORAS_EFECTIVAS, ANTIGUEDAD_MESES, OCUPACION, TIPO_ADMINISTRACION, CONTRATO_PERMANENTE_DISCONTINUO, TIPO_CONTRATO_TEMPORAL, PROVINCIA_TRABAJO, HIZO_HORAS_EXTRA  

### Ablación “solo demografía” (14)

Las demográficas/hogar/tiempo de arriba (sin bloque laboral).

### No entran (anti-leakage / calidad)

MASHOR, DISMAS, RZNDISH, HORDES, BUSOTR, REGION_TRABAJO (~99 % nulo), nombres redundantes CCAA_NOMBRE / PROV_NOMBRE.

---

## 7. Desbalance en Fase 2 (párrafo listo)

Con ~7,6 % de positivos, un clasificador trivial “todo no-subempleo” alcanza ~92 % de accuracy y F1 de subempleo nulo. Por eso la Fase 2 no optimiza accuracy: se elige el modelo por **PR-AUC**, se entrenan estimadores con **`class_weight=balanced`** y se traduce la probabilidad a etiqueta con un **umbral F1 calibrado en train (0,825)**. No se usa SMOTE: a escala EPA, con decenas de categóricas, el oversampling sintético es poco defendible y no sustituye la falta de señal demográfica que ya mide la ablación.

---

## 8. Limitaciones específicas de Fase 2

1. **Clase rara y umbral alto.** El F1 0,52 @0,825 implica recall ~57 %: se deja fuera casi la mitad de los subempleos reales a cambio de menos falsas alarmas. Otra política (más recall) es legítima.  
2. **Sobrepredicción en jornada parcial.** El mejor proxy del target se convierte en sesgo operativo; hay que narrarlo, no ocultarlo.  
3. **Infraestimación en perfiles no prototípicos** (industria, construcción, oficios cualificados).  
4. **Horas como predictores.** Son centrales en la definición conceptual del subempleo; se usan sin las variables de “deseo de trabajar más” que definirían AOI=03. La frontera anti-leakage debe explicarse en la memoria.  
5. **Ablación con un solo algoritmo (LightGBM).** Suficiente para demostrar el salto; no es un diseño factorial completo de todos los modelos × todos los subsets.  
6. **SHAP explica el modelo, no la causalidad.** Los waterfalls son casos ilustrativos.  
7. **EPA muestral.** Las tasas por CCAA/ocupación en errores son del test temporal del modelo, no un mapa oficial de subempleo INE sustituible.  
8. **Modelo completo congelado (julio) + cierre (agosto).** La ablación y los errores se evalúan sobre el LightGBM guardado; las cifras de comparación de candidatos siguen siendo las del entrenamiento original de Fase 2.

---

## 9. Cómo pegarlo en la memoria

| Sección | Usar |
|---|---|
| Intro / puente tras Fase 1 | §1 + primera frase de §2.3 |
| Metodología Fase 2 | §4 + §6 + §6 variables |
| Resultados | §5 tablas + §2.3 ablación |
| XAI | §2.4 + waterfalls |
| Discusión calidad del empleo | §2.5 errores |
| Limitaciones | §8 |
| Defensa (1–2 slides F2) | §5.4 |

---

## 10. Artefactos Fase 2

| Contenido | Ruta |
|---|---|
| Informe + JSON comparación | `reports/fase2/` |
| Figuras globales (PR, matrices, SHAP) | `reports/figures/fase2/` |
| Ablación, errores, waterfalls | `reports/figures/fase2/cierre/` · `reports/fase2/cierre/` |
| Notebook | `notebooks/modelado/02_resultados_fase2.ipynb` |
| Entrada cierre | `run_fase2_cierre.py` |
| Hilo global TFG | `reports/memoria/01_hilo_cientifico.md` |

*Notas de Fase 2 para la memoria.*
