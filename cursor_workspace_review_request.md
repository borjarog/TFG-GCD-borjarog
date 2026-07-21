# Workspace review request
_Exported on 7/20/2026 at 23:02:10 GMT+2 from Cursor (3.11.13)_

---

**User**

Puedes ver mi workspace?

---

**Cursor**

Sí, puedo ver tu workspace. Voy a echar un vistazo rápido a la estructura para confirmarlo.

Sí, tengo acceso completo a tu workspace **TFG-GCD-borjarog**. Es un Trabajo de Fin de Grado sobre datos de la EPA (Encuesta de Población Activa), con esta estructura general:

- **`data/raw/`**: microdatos EPA en formato `.csv`/`.tab`, `.sas`, `.R` y ficheros de metadatos (`md_EPA_*.txt`), organizados por trimestre (2021T1 a 2026T1).
- **`src/data_engineering/`**: módulos de ingeniería de datos (`ingestion.py`, `validation.py`, `features.py`, `diccionarios.py`, `pipeline.py`, `config.py`).
- **`src/modeling/`**: módulos de modelado (`models.py`, `model_fase1_baseline.py`, `visualization.py`).
- **`notebooks/ingenieria_datos/`**: `01_eda.ipynb`, `02_preprocesamiento.ipynb`.
- **`notebooks/modelado/`**: notebooks de fases de modelado (macro, micro, ocupados vs. parados).
- Archivos raíz: `run_data_pipeline.py`, `requirements.txt`, `README.md`, `contexto.md`, `pipeline_run.log`, además de `scripts/` con utilidades para auditar/explorar los Excel.

¿Quieres que explore algo en concreto (por ejemplo, el pipeline de datos, algún notebook o el estado de los modelos)?

---

**User**

el pipeline de datos está hecho?

---

**Cursor**

Sí, el pipeline de ingeniería de datos **está funcionalmente completo** — el código cubre todo el flujo (ingesta → validación → feature engineering) y ya tiene una ejecución exitosa registrada en `pipeline_run.log`. Pero hay matices importantes:

## ✅ Lo que está hecho

- **`ingestion.py`**: descarga/parsea los ZIP del INE o usa los `.csv`/`.tab` locales, y consolida por bloque metodológico (2005-2020 vs 2021+) en parquet.
- **`validation.py`**: sanity checks de estructura, población, sexo, estado de actividad y nulos.
- **`features.py`**: filtra población 16+, construye variables derivadas (`TRAMO_EDAD`, `NIVEL_EDUC`, `CARGA_FAMILIAR`, `VULNERABILIDAD_JOVEN`, etc.) y genera los dos targets:
  - **Fase 1** (`TARGET_MACRO`: Ocupado/Parado/Inactivo)
  - **Fase 2** (`TARGET_SUBEMPLEO`, solo ocupados)
- **`pipeline.py`** orquesta todo, con opción `--skip-ingestion`.
- El log de la última ejecución (13/07/2026) confirma éxito: **2.627.372 registros** (2021–2026T1) → **Fase 1: 2.627.372×17** y **Fase 2: 1.079.939×20**, con una tasa de subempleo detectada del 8,38%.

## ⚠️ Pendientes / cosas a revisar

1. **Los artefactos no están en este workspace.** Las carpetas `data/processed/interim/` y `data/processed/modeling/` existen pero están vacías aquí (están en `.gitignore`, y esa ejecución se hizo en otro equipo — el log muestra rutas de `C:\Users\Borja\Desktop\...`). Si quieres seguir en este equipo, tendrías que volver a ejecutar `python run_data_pipeline.py` (los `.xlsx` de metadatos y los `.csv/.tab` crudos sí están disponibles en este workspace).
2. **Aviso de población no cuadra**: el sanity check reporta ~478.891 personas/trimestre en vez de los ~40-48M esperados. Parece un problema con la columna del factor de elevación (`FACTOR_ELEVACION`/`FACTOREL`) que aún no se ha depurado.
3. **Aviso "proporción inusual de ocupados"**: probablemente un falso positivo — en `validation.py` (línea ~123) se comparan códigos AOI sin padding (`"1"`,`"2"`...) contra los códigos reales que vienen con cero delante (`"03"`,`"04"`...), por lo que la suma nunca coincide. No afecta a `features.py` (que sí usa `normalizar_codigo` correctamente), pero merece un pequeño arreglo en la función de sanity check.
4. **2026T2, T3, T4** no están disponibles todavía (404 desde el INE) — normal, aún no se han publicado.
5. Según el checklist de `docs/ingenieria_datos.md`, falta marcar como completado el punto de "Notebook 02 documentado con decisiones de limpieza".

¿Quieres que revise/arregle el bug del sanity check en `validation.py`, o que vuelva a ejecutar el pipeline aquí para regenerar los parquet?

---

**User**

quiero que el pipeline de datos se haga de cero, me fío más de ti, que arregles la estructura del proyecto de cero borrando lo innecesario, haciendola más clara y sencilla pero lógica y con estructura de proyecto de ciencia de datos, una vez arregles la estructura quiero que empecemos generando un file nuevo que sirva de diccionario de datos, pero más claro y sencilla que contenga todas las variables y los posibles valores su significado y así luego hagamos el procesado y tratamiento bien

---

**Cursor**

**Decisiones para la reestructuración del proyecto**

> **¿Qué alcance debe tener la reestructuración del proyecto?**
> - Solo la parte de datos: data/, src/data_engineering/, notebooks/ingenieria_datos/, scripts/ y configs de raíz. src/modeling/ y notebooks/modelado/ se dejan intactos por ahora (Recomendado)
> - Todo el proyecto, incluyendo también reorganizar (sin reescribir lógica) src/modeling/ y notebooks/modelado/ ✔

> **Hay dos notebooks con contenido real ya hecho: 01_eda.ipynb (214KB) y 03_modelo_b_ocupados_vs_parados.ipynb (159KB), que quedarán desactualizados al rehacer el pipeline desde cero. ¿Qué hacemos con ellos?**
> - Moverlos a una carpeta notebooks/_archive/ como referencia histórica y empezar limpio (Recomendado)
> - Dejarlos donde están, aunque queden desactualizados
> - Eliminarlos y empezar totalmente de cero ✔

> **En data/raw/ hay carpetas SAS/, R/, SPSS/, STATA/ (~100 ficheros de sintaxis para otros programas estadísticos) que el pipeline no usa (solo usa los .csv/.tab + el Excel de diseño), y también el Excel de diseño 2005-2020 sin datos crudos de esa época. ¿Los elimino como parte de la limpieza?**
> - Sí, eliminar las carpetas SAS/R/SPSS/STATA y el diseño 2005-2020 (Recomendado, no se usan) ✔
> - No, mantenerlos por si acaso

> **¿Qué formato quieres para el nuevo diccionario de datos (todas las variables, códigos y significados)?**
> - Un script que lo genera automáticamente desde el Excel oficial del INE, produciendo un Markdown legible por variable (Recomendado: reproducible y siempre sincronizado con la fuente) ✔
> - Un CSV/JSON plano (variable, código, significado) pensado para que el código lo lea directamente
> - Ambos: un CSV/JSON como fuente de datos y un Markdown legible generado a partir de él
> - Un Markdown escrito/curado a mano por ti ahora mismo, sin script

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Ahora elimino la carpeta `scripts/` completa y los notebooks acordados.

Ahora añado los `.gitkeep` a las carpetas de notebooks que quedan vacías.

Ahora elimino el pipeline viejo y los archivos obsoletos de raíz/docs.

Ahora simplifico `config.py` y actualizo el `__init__.py` (que referenciaba el `pipeline.py` ya eliminado).

Ahora construyo el nuevo módulo del diccionario de datos. Primero reviso las hojas del Excel oficial del INE para asegurarme de capturar bien la posición/longitud y todas las tablas de códigos.

Ahora añado la ruta `RUTA_DICCIONARIO_DATOS` al `config.py`.

Ahora ejecuto el script para generar el diccionario y verifico que todo funciona.

Funcionó. Voy a revisar el resultado generado para comprobar que está limpio y bien formateado.

Ahora regenero el documento y verifico que el recuento de variables es correcto y que `FACTOREL` aparece bien documentada.

Anclas correctas ahora. Reviso rápidamente algunas variables sin diccionario de códigos y una tabla larga para confirmar que todo se ve limpio, y compruebo si quedan lints en el módulo.

No hay errores de lint y el documento se ve consistente. Ahora actualizo el `README.md` y el `.gitignore`.

Ahora reescribo el `README.md` para reflejar la nueva estructura.

Veo que han quedado artefactos generados por el pipeline viejo (parquets) y cachés de Python obsoletas. Los limpio para que la reestructuración quede completa y coherente.

Este archivo no referencia nada eliminado, no requiere cambios. Ejecuto una última verificación de que todo el módulo funciona correctamente tras la limpieza final.

Todos los pasos del plan están completos. Resumen de lo hecho:

**Limpieza realizada:**
- Eliminadas las carpetas `data/raw/SAS/`, `R/`, `SPSS/`, `STATA/` (sintaxis de otros programas, sin uso) y `data/meta/diseno_registro_2005_2020.xlsx`
- Eliminada la carpeta `scripts/` completa
- Eliminados los 5 notebooks acordados (con `.gitkeep` en su lugar)
- Eliminado el pipeline viejo completo (`ingestion.py`, `validation.py`, `features.py`, `pipeline.py`, `diccionarios.py`, `run_data_pipeline.py`), el log obsoleto y la documentación desactualizada
- Eliminados también los parquets generados por el pipeline viejo que habían aparecido en `data/processed/` (sincronizados por OneDrive desde otra ejecución) y las cachés de Python obsoletas

**Estructura nueva:**
- `src/data_engineering/` ahora solo contiene `config.py` (simplificado) y el nuevo `diccionario_datos.py`
- `README.md` y `.gitignore` actualizados

**Diccionario de datos nuevo:**
- `src/data_engineering/diccionario_datos.py`: parsea el Excel oficial del INE (hoja de diseño + hojas `Tablas1-5`), filtra automáticamente las filas basura (notas al pie, separadores), y genera un Markdown organizado por **secciones temáticas** (usando la columna de agrupación del propio Excel del INE), con posición/longitud/tipo y tabla código→significado para cada variable
- `docs/diccionario_datos.md`: **91 variables** documentadas, regenerable en cualquier momento con `python -m src.data_engineering.diccionario_datos`

Un hallazgo útil para la siguiente fase: la variable `FACTOREL` (factor de elevación) indica en su descripción oficial que hay que **dividir entre 1000** para reproducir las cifras de INEbase (no entre 100, como asumía el código antiguo) — esto explica el aviso de "población no cuadra" que vimos en la ejecución anterior.

¿Seguimos ahora con la reconstrucción del pipeline (ingesta → validación → feature engineering) apoyándonos en este diccionario?

---

**User**

sí

---

**Cursor**

**Decisiones para reconstruir el pipeline de datos**

> **Para la nueva ingesta (ingestion.py), ¿mantenemos la descarga automática desde el INE para trimestres futuros que aún no estén en data/raw/CSV/?**
> - Sí, mantener el fallback de descarga automática (útil cuando el INE publique 2026T2 en adelante) (Recomendado) ✔
> - No, simplificar a solo lectura de los archivos ya descargados en data/raw/CSV/

> **Para el target de Fase 2 (subempleo), el diccionario revela que el propio INE ya clasifica esto directamente en AOI=03 ('Ocupados subempleados por insuficiencia de horas'), la misma definición OIT. ¿Cuál usamos?**
> - Usar directamente AOI=03 como target (definición oficial del INE, más simple y fiable) (Recomendado) ✔
> - Mantener el cálculo manual anterior (MASHOR=1 y DISMAS=1)
> - Calcular ambas versiones y comparar si coinciden, documentando cualquier diferencia

> **¿Qué conjunto de variables predictoras quieres para los datasets de Fase 1 y Fase 2?**
> - Mantener el mismo conjunto que antes: sexo, tramo edad, nivel educativo, estado civil, nacionalidad, rol en el hogar, si estudia, tamaño hogar, CCAA/provincia, y las derivadas CARGA_FAMILIAR/VULNERABILIDAD_JOVEN (compatible con el script de modelado existente) (Recomendado)
> - Quiero que propongas un conjunto revisado/ampliado ahora que tenemos el diccionario completo de las 91 variables ✔

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Ahora añado las nuevas utilidades al módulo del diccionario de datos.

Ahora reintroduzco `INTERIM_EPA` y `URL_TEMPLATE` en `config.py`.

Ahora construyo `validation.py` con los sanity checks corregidos.

Ahora construyo `features.py` con el fix de `TAM_HOGAR`, las variables demográficas, y los targets de Fase 1 y Fase 2.

Confirmado. Ahora escribo `features.py`.

Ahora creo `pipeline.py` y `run_data_pipeline.py`.

Actualizo `__init__.py` de `data_engineering` para exponer el pipeline de nuevo, y reviso lints antes de ejecutar.

Ahora ejecuto el pipeline completo de punta a punta para verificar que todo funciona.

Completó con éxito. Reviso la salida completa.

Detecté que la corrección del factor de elevación quedó invertida: la población salió en 47.889 (miles) en vez de ~47,9 millones. Reviso la descripción oficial de `FACTOREL` de nuevo para corregirlo bien.

Verifico rápidamente la calidad de los datasets generados y la compatibilidad con el script de modelado existente.

Compatibilidad confirmada (el único fallo es que `lightgbm` no está instalado en el entorno, algo preexistente y ajeno al pipeline). Marco la verificación como completada.

Bien, no quedaron restos de descargas fallidas. Actualizo el `README.md` para reflejar que el pipeline ya está reconstruido y funcionando.

Todos los pasos del plan están completos. Resumen de lo implementado:

**Módulos nuevos/reconstruidos:**
- [`diccionario_datos.py`](src/data_engineering/diccionario_datos.py): añadidas las utilidades `normalizar_codigo`, `codigo_en`, `mapear_variable` y `colspecs_ancho_fijo`, reutilizadas por el resto del pipeline
- [`ingestion.py`](src/data_engineering/ingestion.py): lee los 21 trimestres locales y mantiene el fallback de descarga del INE
- [`validation.py`](src/data_engineering/validation.py): sanity checks con etiquetas del diccionario y bugs corregidos
- [`features.py`](src/data_engineering/features.py): feature engineering con `TAM_HOGAR` corregido y nuevo target de subempleo
- [`pipeline.py`](src/data_engineering/pipeline.py) y `run_data_pipeline.py`: orquestador recreado

**Bugs corregidos y verificados con datos reales:**
- **Población:** el sanity check anterior calculaba mal el factor de elevación. Al implementarlo por primera vez también dividí por 1000 de más (dio 47.889 en vez de personas); revisé de nuevo la descripción oficial de `FACTOREL` ("dividir por mil" es para pasar a *miles* de personas de INEbase, no para llegar a personas) y until corregí: ahora da **47.889.137 personas**, dentro del rango esperado.
- **AOI:** ya no hay falso aviso de "proporción inusual de ocupados" (era por comparar códigos sin ceros a la izquierda).
- **TAM_HOGAR:** antes usaba `NPERS` (número de orden de la persona, no el tamaño del hogar) directamente — bug real. Ahora se calcula contando personas por hogar; la media pasó a ser 2,49 (antes cualquier valor sin sentido).
- **Subempleo (Fase 2):** ahora usa directamente `AOI = 03` (definición oficial OIT del propio INE) en vez de reconstruirlo con `MASHOR`+`DISMAS`. Tasa resultante: **7,59%** (antes 8,38%).

**Resultado final:**
- `dataset_fase1_macro.parquet`: 2.246.970 filas × 17 columnas (Ocupado 48,1% / Inactivo 45,5% / Parado 6,4%)
- `dataset_fase2_micro.parquet`: 1.079.939 filas × 24 columnas
- Compatibilidad verificada con [`model_fase1_baseline.py`](src/modeling/model_fase1_baseline.py) (todas las columnas que espera están presentes; el único fallo al ejecutarlo es que `lightgbm` no está instalado en el entorno, algo previo y ajeno a este trabajo)

También actualicé el `README.md` para reflejar el pipeline ya construido.

¿Quieres que instale `lightgbm` (y demás dependencias de modelado que falten) para poder probar el script de modelado de extremo a extremo, o prefieres seguir con los notebooks de EDA/preprocesamiento ahora que el pipeline está cerrado?

---

**User**

pero el modelado lo hacemos de nuevas no?

---

**Cursor**

Sí, exacto — el modelado también lo reconstruiremos de cero cuando le toque. Ahora mismo `src/modeling/` está en un estado muy preliminar:

- [`models.py`](src/modeling/models.py) y [`visualization.py`](src/modeling/visualization.py): solo funciones vacías (`pass`), sin implementar.
- [`model_fase1_baseline.py`](src/modeling/model_fase1_baseline.py): es una prueba rápida y antigua (un baseline jerárquico con LightGBM), no el modelado final. Lo dejé tal cual únicamente para comprobar que los nombres de columnas del nuevo `dataset_fase1_macro.parquet` seguían siendo compatibles — no lo he tocado ni mejorado.

Es decir, el modelado real (Fase 1 multiclase con el desbalance de clases, y Fase 2 con interpretabilidad SHAP, según `contexto.md`) todavía está por construir desde cero, igual que hicimos con el pipeline de datos.

**Siguiente fase del TFG**

> **Ahora que el pipeline de datos está cerrado, ¿por dónde seguimos?**
> - Primero los notebooks de EDA/preprocesamiento (para explorar bien los datasets nuevos antes de modelar) (Recomendado)
> - Directamente con el modelado de cero (Fase 1 y Fase 2)
>
> Answer: Pero has descartado muchísimas variables en los parquet, no?

No, no se han perdido — siguen todas ahí. Te explico exactamente qué pasó:

**El parquet intermedio (`data/processed/interim/epa_2021_en_adelante.parquet`) tiene las 97 columnas originales intactas**, incluidas las 91 variables del diccionario. Ese archivo no se ha tocado ni recortado.

**Lo que sí recorté deliberadamente son los datasets *finales* de modelado** (`dataset_fase1_macro.parquet` con 17 columnas, `dataset_fase2_micro.parquet` con 24), porque:

1. **Variables técnicas/estructurales que no aportan como predictor**: `CICLO` (id de la oleada), `NVIVI`/`NPERS`/`NCONY`/`NPADRE`/`NMADRE` (identificadores para enlazar personas del mismo hogar — ya los usé para calcular `TAM_HOGAR`, pero no como predictor directo), las variables `RELLB1/RELLB2/RELLB3/RELLMILI` (el propio diccionario las marca como "Relleno", campos heredados sin datos reales), `FACTOREL` (peso muestral, no predictor).
2. **Fase 1 — exclusión por fuga de información**: descarté a propósito *todas* las variables condicionadas al empleo (`OCUP1`, `ACT1`, `SITU`, `DUCON1`, horas trabajadas, `BUSCA`, `MASHOR`...) porque solo existen si la persona ya tiene o busca empleo — usarlas sería casi "regalarle" el target al modelo.
3. **Fase 2 — exclusión por fuga de información**: descarté `MASHOR`, `DISMAS`, `RZNDISH`, `HORDES`, `BUSOTR` porque son la fuente directa de la clasificación `AOI=03` que ahora es el target.

Pero hay un grupo de variables que **no descarté por fuga, simplemente no las incluí en esta primera propuesta** y podrían aportar valor real, por ejemplo:
- `OCUP1` (ocupación/profesión, CNO) — para Fase 2, distinto de `ACT1` (sector de actividad) que sí incluí
- `SIDI1/SIDI2/SIDI3`, `SIDAC1/SIDAC2` (situación de actividad/inactividad autopercibida) — cualitativamente interesantes
- `EDADEST`, `NCURSR`, `CURSNR`, `OBJFORM` (detalle de formación)
- `OCUPLU1`, `ACTPLU1`, `SITPLU`, `HOREPLU` (detalle del segundo empleo, más allá de si lo tiene)
- `PRONA1`/`REGNA1`/`EXREGNA1`/`ANORE1` (detalle de provincia/región de nacimiento y años de residencia) — estas usan una hoja auxiliar del Excel (`AuxTabla3`) con formato irregular que mi script del diccionario no parsea automáticamente

**Alcance de variables en los datasets de modelado**

> **¿Quieres que amplíe el conjunto de predictores en los datasets de modelado con alguno de estos grupos, o dejamos el conjunto actual (más reducido y ya validado) y ampliamos más adelante si el EDA lo pide?**
> - Mantener el conjunto actual (17/24 columnas): es manejable y ya evita fugas de información (Recomendado para empezar)
> - Ampliarlo ya con las variables adicionales que propones (ocupación, situación autopercibida, formación, segundo empleo...)
> - Quiero revisar variable por variable qué se incluye antes de decidir
>
> Answer: Quiero que se usen muchas variables en el modelado porque si no quedará muy pobre no? Hay muchas variables en el dataset. Entiendo que muchas servirán, no?

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Ahora amplío `COLUMNAS_NECESARIAS`.

Ahora la Fase 2: mapeo de las 7 variables nuevas y ampliación de `COLUMNAS_FASE2`.

Ahora regenero los datasets con `--skip-ingestion`.

El pipeline corrió con éxito. Ahora verifico shapes, nulos y compatibilidad de los nuevos datasets.

He completado las 5 tareas del plan de ampliación de variables. Resumen de lo hecho:

**1. `COLUMNAS_NECESARIAS`** — añadidas las 22 columnas fuente nuevas (`PRONA1`, `REGNA1`, `EXREGNA1`, `ANORE1`, `EDADEST`, `CURSNR`, `NCURSR`, `NCONY`, `NPADRE`, `NMADRE`, `OCUP1`, `SP`, `DUCON2`, `DUCON3`, `PROEST`, `REGEST`, `HORASE`, `EXTRA`).

**2. `crear_features_demograficas`** — añadidas las 7 variables mapeadas directamente del diccionario más las 2 derivadas: `TIENE_CONYUGE_HOGAR` (`NCONY != "00"`) y `VIVE_CON_PADRES` (`NPADRE != "00"` o `NMADRE != "00"`).

**3. `COLUMNAS_FASE1`** — pasó de 17 a 26 columnas.

**4. `COLUMNAS_FASE2`** — pasó de 24 a 32 columnas (el plan hablaba de 31 porque agrupaba `PROVINCIA_TRABAJO`/`REGION_TRABAJO` en un solo punto, pero son 2 variables separadas; funcionalmente están las 8 variables descritas en la sección 2 del plan).

**5. Regeneración y verificación:**
- `dataset_fase1_macro.parquet`: **2,246,970 filas × 26 columnas**
- `dataset_fase2_micro.parquet`: **1,079,939 filas × 32 columnas**, tasa de subempleo 7.59% (81,958 personas), sin cambios respecto a antes (como se esperaba, al no tocar el target)

Revisé los nulos de las columnas nuevas y todos son estructurales y esperados, no errores:
- `PROVINCIA_NACIMIENTO`/`REGION_NACIMIENTO_EXTRANJERO` (11.2%/88.8%): mutuamente excluyentes por diseño (nacido en España vs. extranjero).
- `NIVEL_ESTUDIOS_ACTUALES` (90.1%): solo aplica a quien estudia ahora.
- `ANOS_RESIDENCIA_ESPANA` (84.7%): solo aplica a extranjeros/retornados.
- `CONTRATO_PERMANENTE_DISCONTINUO`/`TIPO_CONTRATO_TEMPORAL` (31.7%/84.5%): mutuamente excluyentes (indefinido vs. temporal).
- `REGION_TRABAJO` (99.6%): la inmensa mayoría trabaja en España, así que `PROVINCIA_TRABAJO` cubre casi todo.

No se ha introducido ningún error de linter y el pipeline completo (`validación` + `feature engineering`) corrió sin fallos.

---

**User**

OK, AHORA DEBERÍAMOS VER EL MODELADO DE LA FASE 1, QUE NO SEA UN MODELADO POBRE

---

**Cursor**

**Decisiones para el modelado de Fase 1**

> **¿Qué arquitectura de modelo prefieres para Fase 1 (Ocupado/Parado/Inactivo)?**
> - Jerárquico en 2 etapas: Activo/Inactivo, luego Ocupado/Parado dentro de Activos (permite optimizar cada corte por separado, más interpretable) (Recomendado) ✔
> - Un único modelo multiclase con las 3 clases a la vez (más simple, una sola pipeline)
> - Implementar ambos y comparar métricas para justificar cuál es mejor en la memoria del TFG

> **¿Qué algoritmo(s) quieres usar como modelo principal?**
> - Solo LightGBM (rápido, soporta categóricas nativas, buen rendimiento tabular) (Recomendado)
> - Comparar varios: Regresión Logística (baseline simple) + Random Forest + LightGBM/XGBoost, y quedarnos con el mejor ✔

> **¿Qué nivel de ajuste de hiperparámetros quieres?**
> - Búsqueda aleatoria/Optuna con validación cruzada sobre los hiperparámetros clave (mejor rendimiento, más tiempo de cómputo) (Recomendado) ✔
> - Configuración manual razonable (class_weight balanced, n_estimators, max_depth) sin búsqueda automática, para iterar rápido

> **¿Cómo dividimos train/test?**
> - División temporal: entrenar con trimestres más antiguos, testear con los más recientes (evalúa capacidad de generalizar a futuro, más realista para EPA) (Recomendado) ✔
> - División aleatoria estratificada 80/20 (más simple, mezcla todos los trimestres)

> **¿Incluimos interpretabilidad (SHAP) ya en Fase 1, o la dejamos solo para Fase 2 como dice el contexto del TFG?**
> - Sí, incluir SHAP también en Fase 1 (consistencia y más contenido para la memoria) (Recomendado) ✔
> - No, dejar SHAP solo para Fase 2 como estaba planteado originalmente, y en Fase 1 usar solo feature importance nativa

Ahora reviso la config de data_engineering para reutilizar convenciones y luego construyo el módulo de modelado.

Ahora creo `config.py` para el módulo de modelado.

Ahora `interpretability.py` para los gráficos SHAP.

Bien, este archivo está completo. Ahora reviso lints de todos los archivos nuevos antes de ejecutar.

Ahora limpio los stubs antiguos y creo el entry point.

Ahora creo el entry point en la raíz, siguiendo la convención de `run_data_pipeline.py`.

Antes de lanzar el pipeline completo (que puede tardar bastante), hago una prueba rápida con una muestra pequeña para detectar errores cuanto antes.

Completó sin errores. Reviso el output completo para verificar que todo tiene sentido.

Perfecto, el smoke test terminó sin errores. Elimino el script temporal y lanzo el pipeline completo en segundo plano.

Mientras corre el pipeline completo en segundo plano, reviso el `.gitignore` para asegurarme de que los artefactos generados (`models/`, `reports/`) no se versionen.

