# Diccionario de datos — EPA (INE)

Generado automáticamente a partir del diseño de registro oficial del INE (`diseno_registro_2021_en_adelante.xlsx`, bloque metodológico **2021 en adelante**).

- **Población cubierta:** personas de 16 y más años (`NIVEL = 1`), que es la población de análisis del TFG.
- **Fuente de verdad:** el Excel oficial del INE. Si el INE actualiza el diseño de registro, regenera este documento con `python -m src.data_engineering.diccionario_datos`.
- **Última generación:** 2026-07-20
- **Total de variables documentadas:** 91

## Índice de secciones

- [Datos de control](#datos-de-control)
- [Datos demográficos](#datos-demograficos)
- [Formación y nivel de estudios](#formacion-y-nivel-de-estudios)
- [Trabajó en la semana de referencia](#trabajo-en-la-semana-de-referencia)
- [Datos del empleo principal](#datos-del-empleo-principal)
- [Segundo empleo](#segundo-empleo)
- [Deseo de trabajar mas horas](#deseo-de-trabajar-mas-horas)
- [Búsqueda de empleo](#busqueda-de-empleo)
- [Experiencia profesional](#experiencia-profesional)
- [Inscripción en la oficina de empleo pública](#inscripcion-en-la-oficina-de-empleo-publica)
- [Situaciones diversas](#situaciones-diversas)
- [Días de ausencia](#dias-de-ausencia)
- [Si trabajó el año pasado](#si-trabajo-el-ano-pasado)
- [Variables derivadas](#variables-derivadas)

## Datos de control

### `CICLO`

Período de referencia Todas las personas / viviendas Valores: 194 (T1-2021), 195 (T2-2021) ... 203 (T2-2023)

| Campo | Valor |
| --- | --- |
| Posición | 1 |
| Longitud | 3 |
| Tipo | A |
| Nº de códigos | 120 |

| Código | Significado |
| --- | --- |
| 194 | 2021T1 |
| 195 | 2021T2 |
| 196 | 2021T3 |
| 197 | 2021T4 |
| 198 | 2022T1 |
| 199 | 2022T2 |
| 200 | 2022T3 |
| 201 | 2022T4 |
| 202 | 2023T1 |
| 203 | 2023T2 |
| 204 | 2023T3 |
| 205 | 2023T4 |
| 206 | 2024T1 |
| 207 | 2024T2 |
| 208 | 2024T3 |
| 209 | 2024T4 |
| 210 | 2025T1 |
| 211 | 2025T2 |
| 212 | 2025T3 |
| 213 | 2025T4 |
| 214 | 2026T1 |
| 215 | 2026T2 |
| 216 | 2026T3 |
| 217 | 2026T4 |
| 218 | 2027T1 |
| 219 | 2027T2 |
| 220 | 2027T3 |
| 221 | 2027T4 |
| 222 | 2028T1 |
| 223 | 2028T2 |
| 224 | 2028T3 |
| 225 | 2028T4 |
| 226 | 2029T1 |
| 227 | 2029T2 |
| 228 | 2029T3 |
| 229 | 2029T4 |
| 230 | 2030T1 |
| 231 | 2030T2 |
| 232 | 2030T3 |
| 233 | 2030T4 |
| 234 | 2031T1 |
| 235 | 2031T2 |
| 236 | 2031T3 |
| 237 | 2031T4 |
| 238 | 2032T1 |
| 239 | 2032T2 |
| 240 | 2032T3 |
| 241 | 2032T4 |
| 242 | 2033T1 |
| 243 | 2033T2 |
| 244 | 2033T3 |
| 245 | 2033T4 |
| 246 | 2034T1 |
| 247 | 2034T2 |
| 248 | 2034T3 |
| 249 | 2034T4 |
| 250 | 2035T1 |
| 251 | 2035T2 |
| 252 | 2035T3 |
| 253 | 2035T4 |
| 254 | 2036T1 |
| 255 | 2036T2 |
| 256 | 2036T3 |
| 257 | 2036T4 |
| 258 | 2037T1 |
| 259 | 2037T2 |
| 260 | 2037T3 |
| 261 | 2037T4 |
| 262 | 2038T1 |
| 263 | 2038T2 |
| 264 | 2038T3 |
| 265 | 2038T4 |
| 266 | 2039T1 |
| 267 | 2039T2 |
| 268 | 2039T3 |
| 269 | 2039T4 |
| 270 | 2040T1 |
| 271 | 2040T2 |
| 272 | 2040T3 |
| 273 | 2040T4 |
| 274 | 2041T1 |
| 275 | 2041T2 |
| 276 | 2041T3 |
| 277 | 2041T4 |
| 278 | 2042T1 |
| 279 | 2042T2 |
| 280 | 2042T3 |
| 281 | 2042T4 |
| 282 | 2043T1 |
| 283 | 2043T2 |
| 284 | 2043T3 |
| 285 | 2043T4 |
| 286 | 2044T1 |
| 287 | 2044T2 |
| 288 | 2044T3 |
| 289 | 2044T4 |
| 290 | 2045T1 |
| 291 | 2045T2 |
| 292 | 2045T3 |
| 293 | 2045T4 |
| 294 | 2046T1 |
| 295 | 2046T2 |
| 296 | 2046T3 |
| 297 | 2046T4 |
| 298 | 2047T1 |
| 299 | 2047T2 |
| 300 | 2047T3 |
| 301 | 2047T4 |
| 302 | 2048T1 |
| 303 | 2048T2 |
| 304 | 2048T3 |
| 305 | 2048T4 |
| 306 | 2049T1 |
| 307 | 2049T2 |
| 308 | 2049T3 |
| 309 | 2049T4 |
| 310 | 2050T1 |
| 311 | 2050T2 |
| 312 | 2050T3 |
| 313 | 2050T4 |

### `CCAA`

Comunidad autónoma Todas las personas / viviendas

| Campo | Valor |
| --- | --- |
| Posición | 4 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 19 |

| Código | Significado |
| --- | --- |
| 01 | Andalucía |
| 02 | Aragón |
| 03 | Asturias, Principado de |
| 04 | Balears, Illes |
| 05 | Canarias |
| 06 | Cantabria |
| 07 | Castilla y León |
| 08 | Castilla-La Mancha |
| 09 | Cataluña |
| 10 | Comunitat Valenciana |
| 11 | Extremadura |
| 12 | Galicia |
| 13 | Madrid, Comunidad de |
| 14 | Murcia, Región de |
| 15 | Navarra, Comunidad Foral de |
| 16 | País Vasco |
| 17 | Rioja, La |
| 51 | Ceuta |
| 52 | Melilla |

### `PROV`

Provincia donde se ubica la vivienda Todas las personas / viviendas

| Campo | Valor |
| --- | --- |
| Posición | 6 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 52 |

| Código | Significado |
| --- | --- |
| 01 | Araba/Álava |
| 02 | Albacete |
| 03 | Alicante/Alacant |
| 04 | Almería |
| 05 | Ávila |
| 06 | Badajoz |
| 07 | Balears, Illes |
| 08 | Barcelona |
| 09 | Burgos |
| 10 | Cáceres |
| 11 | Cádiz |
| 12 | Castellón /Castelló |
| 13 | Ciudad Real |
| 14 | Córdoba |
| 15 | Coruña, A |
| 16 | Cuenca |
| 17 | Girona |
| 18 | Granada |
| 19 | Guadalajara |
| 20 | Gipuzkoa |
| 21 | Huelva |
| 22 | Huesca |
| 23 | Jaén |
| 24 | León |
| 25 | Lleida |
| 26 | Rioja, La |
| 27 | Lugo |
| 28 | Madrid |
| 29 | Málaga |
| 30 | Murcia |
| 31 | Navarra |
| 32 | Ourense |
| 33 | Asturias |
| 34 | Palencia |
| 35 | Palmas, Las |
| 36 | Pontevedra |
| 37 | Salamanca |
| 38 | Santa Cruz de Tenerife |
| 39 | Cantabria |
| 40 | Segovia |
| 41 | Sevilla |
| 42 | Soria |
| 43 | Tarragona |
| 44 | Teruel |
| 45 | Toledo |
| 46 | Valencia/València |
| 47 | Valladolid |
| 48 | Bizkaia |
| 49 | Zamora |
| 50 | Zaragoza |
| 51 | Ceuta |
| 52 | Melilla |

### `NVIVI`

Número de orden del hogar

| Campo | Valor |
| --- | --- |
| Posición | 8 |
| Longitud | 5 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `NIVEL`

Variable que indica el nivel del registro en el fichero Tipo de registro: Persona de 16 y más años Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 13 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Persona de 16 o más años |
| 2 | Menor de 16 años |

### `NPERS`

Número de orden de la persona en el hogar Todas las personas 01-19

| Campo | Valor |
| --- | --- |
| Posición | 14 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

## Datos demográficos

### `EDAD1`

Edad, grupos quinquenales de años cumplidos Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 16 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 14 |

| Código | Significado |
| --- | --- |
| 00 | 0 a 4 años |
| 05 | 5 a 9 años |
| 10 | 10 a 15 años |
| 16 | 16 a 19 años |
| 20 | 20 a 24 años |
| 25 | 25 a 29 años |
| 30 | 30 a 34 años |
| 35 | 35 a 39 años |
| 40 | 40 a 44 años |
| 45 | 45 a 49 años |
| 50 | 50 a 54 años |
| 55 | 55 a 59 años |
| 60 | 60 a 64 años |
| 65 | 65 o más años |

### `RELPP1`

Relación con la persona de referencia Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 18 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 9 |

| Código | Significado |
| --- | --- |
| 1 | Persona de referencia (p.r.) |
| 2 | Cónyuge o pareja de la p.r. |
| 3 | Hijo/a, hijastro/a (de la p.r o pareja del mismo) |
| 4 | Yerno , nuera de la p.r. o de su pareja (o pareja del hijo/a, hijastro/a) |
| 5 | Nieto/a, nieto/a de la p.r. o de su pareja (incluye nietastros/as e ambos) |
| 6 | Padre, madre, suegro/a de la p.r o pareja de los mismos (padrastro, madrastra) |
| 7 | Otro pariente de la p.r (o pareja del mismo) |
| 8 | Persona del servicio doméstico |
| 9 | Sin parentesco con la p.r. |

### `SEXO1`

Sexo Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 19 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Hombre |
| 6 | Mujer |

### `NCONY`

Número de orden del cónyuge o pareja en el hogar Todas las personas (sólo se pregunta a aquellas personas de 16 y más años) 01-19 00 No tiene o no reside en la vivienda

| Campo | Valor |
| --- | --- |
| Posición | 20 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 00 | No tiene o no reside en la vivienda |

### `NPADRE`

Número de orden del padre en el hogar Todas las personas 01-19 00 No tiene o no reside en la vivienda

| Campo | Valor |
| --- | --- |
| Posición | 22 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 00 | No tiene o no reside en la vivienda |

### `NMADRE`

Número de orden de la madre en el hogar Todas las personas 01-19 00 No tiene o no reside en la vivienda

| Campo | Valor |
| --- | --- |
| Posición | 24 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 00 | No tiene o no reside en la vivienda |

### `RELLMILI`

Relleno antigua variable MILI

| Campo | Valor |
| --- | --- |
| Posición | 26 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `ECIV1`

Estado civil legal Todas las personas (sólo se pregunta a aquellas personas de 16 o más años)

| Campo | Valor |
| --- | --- |
| Posición | 27 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 4 |

| Código | Significado |
| --- | --- |
| 1 | Soltero |
| 2 | Casado |
| 3 | Viudo |
| 4 | Separado o divorciado |

### `PRONA1`

Si es en España, indicar provincia Personas nacidas en España

| Campo | Valor |
| --- | --- |
| Posición | 28 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 52 |

| Código | Significado |
| --- | --- |
| 01 | Araba/Álava |
| 02 | Albacete |
| 03 | Alicante/Alacant |
| 04 | Almería |
| 05 | Ávila |
| 06 | Badajoz |
| 07 | Balears, Illes |
| 08 | Barcelona |
| 09 | Burgos |
| 10 | Cáceres |
| 11 | Cádiz |
| 12 | Castellón /Castelló |
| 13 | Ciudad Real |
| 14 | Córdoba |
| 15 | Coruña, A |
| 16 | Cuenca |
| 17 | Girona |
| 18 | Granada |
| 19 | Guadalajara |
| 20 | Gipuzkoa |
| 21 | Huelva |
| 22 | Huesca |
| 23 | Jaén |
| 24 | León |
| 25 | Lleida |
| 26 | Rioja, La |
| 27 | Lugo |
| 28 | Madrid |
| 29 | Málaga |
| 30 | Murcia |
| 31 | Navarra |
| 32 | Ourense |
| 33 | Asturias |
| 34 | Palencia |
| 35 | Palmas, Las |
| 36 | Pontevedra |
| 37 | Salamanca |
| 38 | Santa Cruz de Tenerife |
| 39 | Cantabria |
| 40 | Segovia |
| 41 | Sevilla |
| 42 | Soria |
| 43 | Tarragona |
| 44 | Teruel |
| 45 | Toledo |
| 46 | Valencia/València |
| 47 | Valladolid |
| 48 | Bizkaia |
| 49 | Zamora |
| 50 | Zaragoza |
| 51 | Ceuta |
| 52 | Melilla |

### `REGNA1`

Región del país extranjero de nacimiento Personas nacidas en el extranjero

| Campo | Valor |
| --- | --- |
| Posición | 30 |
| Longitud | 3 |
| Tipo | A |
| Nº de códigos | 12 |

| Código | Significado |
| --- | --- |
| 115 | UE- 15 |
| 125 | UE- 25 (no UE-15) |
| 128 | UE- 28 (no UE-27) |
| 100 | Resto de Europa |
| 200 | África |
| 300 | América del Norte |
| 310 | Centroamérica y Caribe |
| 350 | Sudamérica |
| 400 | Asia Oriental (Lejano Oriente) |
| 410 | Asia Occidental (Oriente Próximo) |
| 420 | Asia del Sur y Sudoeste |
| 500 | Oceanía |

### `NAC1`

Nacionalidad Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 33 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Española |
| 2 | Española y doble nacionalidad |
| 3 | Extranjera |

### `EXREGNA1`

Región del país de la nacionalidad extranjera Todas las personas con nacionalidad extranjera o doble nacionalidad

| Campo | Valor |
| --- | --- |
| Posición | 34 |
| Longitud | 3 |
| Tipo | A |
| Nº de códigos | 13 |

| Código | Significado |
| --- | --- |
| 115 | UE- 15 |
| 125 | UE- 25 (no UE-15) |
| 128 | UE- 28 (no UE-27) |
| 100 | Resto de Europa |
| 200 | África |
| 300 | América del Norte |
| 310 | Centroamérica y Caribe |
| 350 | Sudamérica |
| 400 | Asia Oriental (Lejano Oriente) |
| 410 | Asia Occidental (Oriente Próximo) |
| 420 | Asia del Sur y Sudoeste |
| 500 | Oceanía |
| 999 | Apátridas |

### `ANORE1`

Años de residencia en España Extranjeros o nacidos en España que han residido fuera del país por un período superior o igual a 1 año (0-99) 0 para menos de un año en España

| Campo | Valor |
| --- | --- |
| Posición | 37 |
| Longitud | 2 |
| Tipo | N |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 00 | Menos de un año en España |

## Formación y nivel de estudios

### `NFORMA`

Nivel de estudios 2 * Todas las personas de 16 y más años CNED 2014 (01-81) CNED 2000 (11-80)

| Campo | Valor |
| --- | --- |
| Posición | 39 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| AN | Analfabetos (código 01 en CNED-2014), (código 80 en CNED-2000) |
| P1 | Educación primaria incompleta (código 02 en CNED-2014), (código 11 en CNED-2000) |
| P2 | Educación primaria (código 10 en CNED-2014), (código 12 en CNED 2000) |
| S1 | Primera etapa de educación secundaria (códigos 21-24 en CNED-2014), (códigos 21-23, 31, 36* en CNED-2000) |
| SG | Segunda etapa de educación secundaria. Orientación general (código 32 en CNED-2014), (código 32 en CNED-2000) |
| SP | Segunda etapa de educación secundaria. Orientación profesional (incluye educación postsecundaria no superior) (códigos 33-35, 38**, 41 en CNED-2014), (códigos 33, 34, 41 en CNED-2000) |
| SU | Educación superior (códigos 51, 52, 61-63, 71-75, 81 en CNED-2014), (códigos 50-56, 59, 61 en CNED-2000) |

### `RELLB1`

Relleno en apartado de formación

| Campo | Valor |
| --- | --- |
| Posición | 41 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `EDADEST`

Edad en la que alcanzó el máximo nivel de estudios Todas las personas de 16 y más años no analfabetas (7-110) 0 - No sabe fecha en la que alcanzó el máximo nivel de estudios

| Campo | Valor |
| --- | --- |
| Posición | 43 |
| Longitud | 3 |
| Tipo | N |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 00 | No sabe la fecha en la que alcanzó el máximo nivel de estudios |

### `CURSR`

Ha cursado estudios reglados (enseñanza regular) durante las cuatro últimas semanas Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 46 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 2 | Estudiante en vacaciones |
| 3 | No |

### `NCURSR`

Nivel de los estudios reglados que cursa 2 * Todas las personas de 16 y más años que han cursado estudios reglados durante las 4 últimas semanas CNED 2014 (11-81) CNED 2000 (11-61)

| Campo | Valor |
| --- | --- |
| Posición | 47 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 5 |

| Código | Significado |
| --- | --- |
| PR | Educación primaria (códigos 11-13 en CNED-2014), (códigos 11-13 en CNED-2000) |
| S1 | Primera etapa de educación secundaria (códigos 21-23 en CNED-2014), (códigos 22, 23, 36** en CNED-2000) |
| SG | Segunda etapa de educación secundaria. Orientación general (códigos 31, 32 en CNED-2014), (código 32 en CNED-2000) |
| SP | Segunda etapa de educación secundaria. Orientación profesional (incluye educación postsecundaria no superior (códigos 33-35*, 36-37, 38***, 41 en CNED-2014), (códigos 33, 34 en CNED-2000) |
| SU | Educación superior (códigos 51, 52, 61-63, 71-75, 81 en CNED-2014), (códigos 50-52, 54-56, 59, 61 en CNED-2000) |

### `CURSNR`

Ha realizado algún curso de formación no reglada, durante las cuatro últimas semanas Todas las personas de 16 y más años CNED 2014 (91-94) CNED 2000 (21-93)

| Campo | Valor |
| --- | --- |
| Posición | 49 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 2 | Estudiante en vacaciones |
| 3 | No |

### `OBJFORM`

Objetivo de la formación no reglada Todas las personas

| Campo | Valor |
| --- | --- |
| Posición | 50 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Proporcionar formación relacionada con la ocupación actual |
| 2 | Proporcionar formación relacionada con un posible empleo futuro |
| 3 | Proporcionar formación no relacionada con el trabajo (interés personal u otros motivos) |

### `RELLB2`

Relleno en apartado de formación

| Campo | Valor |
| --- | --- |
| Posición | 51 |
| Longitud | 6 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

## Trabajó en la semana de referencia

### `TRAREM`

Si ha realizado un trabajo remunerado durante la semana pasada Todas las personas de 16 a 89 años

| Campo | Valor |
| --- | --- |
| Posición | 57 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `AYUDFA`

Ayuda familiar. Realización de trabajo no remunerado empresa familiar Todas las personas que no trabajaron en la semana de referencia a cambio de remuneración

| Campo | Valor |
| --- | --- |
| Posición | 58 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `AUSENT`

A pesar de no haber trabajado ¿tenía un empleo o negocio? Todas las personas que no trabajaron en la semana de referencia a cambio de remuneración

| Campo | Valor |
| --- | --- |
| Posición | 59 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `RZNOTB`

Razones por las que no trabajó, teniendo empleo Todas las personas que no trabajaron la semana de referencia, ni ayudan en el negocio familiar, y tenían empleo

| Campo | Valor |
| --- | --- |
| Posición | 60 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 16 |

| Código | Significado |
| --- | --- |
| 01 | Vacaciones o dias de permiso |
| 02 | Permiso por nacimiento de un hijo |
| 03 | Excedencia por nacimiento de un hijo |
| 04 | Enfermedad, accidente o incapacidad temporal del encuestado |
| 05 | Jornada de verano, horario variable, flexible o similar |
| 06 | Actividades de representación sindical |
| 07 | Nuevo empleo en el que aún no había empezado a trabajar |
| 08 | Fijo discontinuo o trabajador estacional en la época de menor actividad |
| 09 | Mal tiempo |
| 10 | Paro parcial por razones técnicas o económicas |
| 11 | Se encuentra en expediente de regulación de empleo |
| 12 | Huelga o conflicto laboral |
| 13 | Haber recibido enseñanza o formación relacionada con el trabajo |
| 14 | Razones personales o responsabilidades familiares |
| 15 | Otras razones |
| 00 | No sabe |

### `VINCUL`

Vinculación con el empleo de personas con empleo ausentes en la semana de referencia Personas que tenían un empleo del cual estaban ausentes la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 62 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Vacaciones o día de permiso;  Permiso por nacimiento de un hijo;  Enfermedad, accidente o incapacidad temporal del encuestado; Jornada de verano, horario variable, flexible o similar; Haber recibido enseñanza o formación relacionada con el trabajo |
| 02 | Excedencia por cuidado de hijos con vinculación fuerte con el empleo. |
| 04 | Fijo discontinuo o trabajador estacional en la época de menor actividad, que realiza regularmente alguna tarea relacionada con el empleo estacional |
| 05 | Actividades de representación sindical; Mal tiempo; Expediente de regulación de empleo; Paro parcial por razones técnicas; Encontrarse en expediente de regulación de empleo; Huelga o conflicto laboral; Razones personales o responsabilidades familiares, Otras razones; No sabe. En todos los casos, siempre que mantengan un vínculo fuerte con el empleo. |
| 07 | Excedencia por cuidado de hijos, con vinculación débil con el empleo |
| 08 | Fijo discontinuo o trabajador estacional en la época de menor actividad, que ya no realiza regularmente ninguna tarea relacionada con el empleo estacional |
| 09 | Actividades de representación sindical; Mal tiempo; Expediente de regulación de empleo; Paro parcial por razones técnicas; Encontrarse en expediente de regulación de empleo; Huelga o conflicto laboral; Razones personales o responsabilidades familiares, Otras razones; No sabe. En todos los casos, siempre que su vinculación con el empleo sea débil. |
| 11 | Nuevo empleo en el que aún no había empezado a trabajar |

### `NUEVEM`

Ha encontrado empleo Personas de 16 a 74 años sin empleo y que no han buscado uno en las cuatro últimas semanas

| Campo | Valor |
| --- | --- |
| Posición | 64 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Sí, se incorporará en un plazo inferior o igual a  tres meses |
| 2 | Sí, se incorporará en un plazo superior a tres meses |
| 3 | No |

## Datos del empleo principal

### `OCUP1`

Ocupación principal Todas las personas que trabajaron o tenían empleo la semana de referencia Categorías generadas a partir de T1-2011 con códigos según CNO 2011

| Campo | Valor |
| --- | --- |
| Posición | 65 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Ocupaciones militares (códigos CNO-2011). Fuerzas armadas (códigos CNO-1994) |
| 1 | Directores y gerentes (códigos CNO-2011). Dirección de las empresas y de las  Administraciones Públicas (códigos CNO-1994) |
| 2 | Técnicos y Profesionales científicos e intelectuales (códigos CNO-2011) |
| 3 | Técnicos y Profesionales de apoyo (códigos CNO-2011) |
| 4 | Empleados contables, administrativos y otros empleados de oficina (códigos CNO-2011). Empleados de tipo administrativo (códigos CNO-1994) |
| 5 | Trabajadores de servicios de restauración, personales, protección y vendedores de comercio (códigos CNO-2011) |
| 6 | Trabajadores cualificados en el sector agrícola, ganadero, forestal y pesquero (códigos CNO-2011).Trabajadores cualificados en la agricultura y en la pesca (códigos CNO-1994) |
| 7 | Artesanos y trabajadores cualificados de las industrias manufactureras y la construcción (excepto operadores de instalaciones y maquinaria (códigos CNO-2011). Artesanos y trabajadores cualificados de las industrias manufactureras, la construcción, y la minería, excepto operadores de instalaciones y maquinaria (códigos CNO-1994) |
| 8 | Operadores de instalaciones y maquinaria, y montadores (códigos CNO-2011) |
| 9 | Ocupaciones elementales (códigos CNO-2011). Trabajadores no cualificados (códigos CNO-1994) |

### `ACT1`

Actividad principal 1 Todas las personas que trabajaron o tenían empleo la semana de referencia Categorías generadas a partir de T1-2008 con Códigos según CNAE 2009. Hasta T4-2007 se obtuvieron con la clasificación de actividades CNAE-93 rev-1. (véase Anexo códigos CNAE 2009 y 1993 para más información sobre la correspondencia entre ambas clasificaciones)

| Campo | Valor |
| --- | --- |
| Posición | 66 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Agricultura, ganadería, silvicultura y pesca (códigos CNAE-09: 01, 02 y 03), (códigos CNAE-93: 01, 02 y 05) |
| 1 | Industria de la alimentación, textil, cuero, madera y papel (códigos CNAE-09: del 10 al 18), (códigos CNAE-93 del 15 al 22) |
| 2 | Industrias extractivas, refino de petróleo, industria química, farmaceutica, industria del caucho y materias plásticas, suministro energía eléctrica, gas, vapor y aire acondicionado, suministro de agua, gestión de residuos. Metalurgia (códigos CNAE-09: del 05 al 09, del 19 al 25, 35 y del 36 al 39), (códigos CNAE-93: del 10 al 14, del 23 al 28, 40 y 41) |
| 3 | Construcción de maquinaria, equipo eléctrico y material de transporte. Instalación y reparación industrial  (códigos CNAE-09 del 26 al 33), (códigos CNAE-93 del 29 al 37) |
| 4 | Construcción (códigos CNAE-09: del 41 al 43), (código CNAE-93: 45) |
| 5 | Comercio al por mayor y al por menor y sus instalaciones y reparaciones. Reparación de automóviles, hostelería (códigos CNAE-09: del 45 al 47, 55 y 56), (códigos CNAE-93: 50, 51, 52 y 55) |
| 6 | Transporte y almacenamiento. Información y comunicaciones (códigos CNAE-09 del 49 al 53 y del 58 al 63), (códigos CNAE-93 del 60 al 64) |
| 7 | Intermediación financiera, seguros, actividades inmobiliarias, servicios profesionales, científicos, administrativos y otros (códigos CNAE-09: del 64 al 66, 68, del 69 al 75 y del 77 al 82), (códigos CNAE-93 del 65 al 67 y del 70 al 74) |
| 8 | Administración Pública, educación y actividades sanitarias (códigos CNAE-09: 84, 85 y del 86 al 88), (códigos CNAE-93: 75, 80 y 85) |
| 9 | Otros servicios (códigos CNAE-09: del 90 al 93, del 94 al 96, 97y  99), (códigos CNAE-93: del 90 al 93, 95 y 99) |

### `SITU`

¿Cuál es su situación profesional (actividad principal)? Todas las personas que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 67 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| 01 | Empresario con asalariados |
| 03 | Trabajador independiente o empresario sin asalariados |
| 05 | Miembro de una cooperativa |
| 06 | Ayuda en la empresa o negocio familiar |
| 07 | Asalariado sector público |
| 08 | Asalariado sector privado |
| 09 | Otra situación |

### `SP`

Tipo de administración en la que trabaja Todos los asalariados del sector público

| Campo | Valor |
| --- | --- |
| Posición | 69 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| 1 | Administración central |
| 2 | Administración de la Seguridad Social |
| 3 | Administración de Comunidad Autónoma |
| 4 | Administración local |
| 5 | Empresas públicas e Instituciones financieras públicas |
| 6 | Otro tipo |
| 0 | No sabe |

### `DUCON1`

Tiene contrato indefinido o temporal Todos los asalariados

| Campo | Valor |
| --- | --- |
| Posición | 70 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Indefinido |
| 6 | Temporal |

### `DUCON2`

Relación laboral de carácter permanente o discontinuo Asalariados con contrato o relación laboral indefinidos

| Campo | Valor |
| --- | --- |
| Posición | 71 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Permanente |
| 6 | Discontinuo |

### `DUCON3`

Tipo de contrato o relación laboral de carácter temporal Asalariados con contrato temporal

| Campo | Valor |
| --- | --- |
| Posición | 72 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 01 | Eventual por circunstancias de la producción |
| 02 | De formación o aprendizaje |
| 03 | Estacional o de temporada |
| 04 | Cubre un período de prueba |
| 05 | Cubre la ausencia total o parcial de otro trabajador |
| 06 | Para obra o servicio determinado |
| 07 | Verbal no incluido en las opciones anteriores |
| 08 | Otro tipo |
| 09 | De prácticas (becarios, períodos de prácticas, asistentes de investigación, etc.) |
| 00 | No sabe |

### `TCONTM`

Duración en meses del contrato o relación laboral temporal (si ha trabajado un mes o más) Asalariados con contrato temporal cuya duración mínima de contrato es un mes Valores: 00-96

| Campo | Valor |
| --- | --- |
| Posición | 74 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 96 | 96 meses o más |
| 00 | Desconoce la respuesta pero es al menos un mes |

### `TCONTD`

Duración en días del contrato o relación laboral temporal (si ha trabajado menos de un mes) Asalariados con contrato temporal cuya duración máxima de contrato es menos de un mes Valores: 00-30; 99

| Campo | Valor |
| --- | --- |
| Posición | 76 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 99 | No sabe |
| 00 | Desconoce la respuesta pero es menos de un mes |

### `DREN`

Tiempo en meses desde la renovación del contrato Asalariados Valores: 0-720

| Campo | Valor |
| --- | --- |
| Posición | 78 |
| Longitud | 3 |
| Tipo | N |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `DCOM`

Tiempo en meses en la empresa Ocupados Valores: 0-720

| Campo | Valor |
| --- | --- |
| Posición | 81 |
| Longitud | 3 |
| Tipo | N |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `PROEST`

Provincia donde está ubicado Todas las personas que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 84 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 52 |

| Código | Significado |
| --- | --- |
| 01 | Araba/Álava |
| 02 | Albacete |
| 03 | Alicante/Alacant |
| 04 | Almería |
| 05 | Ávila |
| 06 | Badajoz |
| 07 | Balears, Illes |
| 08 | Barcelona |
| 09 | Burgos |
| 10 | Cáceres |
| 11 | Cádiz |
| 12 | Castellón /Castelló |
| 13 | Ciudad Real |
| 14 | Córdoba |
| 15 | Coruña, A |
| 16 | Cuenca |
| 17 | Girona |
| 18 | Granada |
| 19 | Guadalajara |
| 20 | Gipuzkoa |
| 21 | Huelva |
| 22 | Huesca |
| 23 | Jaén |
| 24 | León |
| 25 | Lleida |
| 26 | Rioja, La |
| 27 | Lugo |
| 28 | Madrid |
| 29 | Málaga |
| 30 | Murcia |
| 31 | Navarra |
| 32 | Ourense |
| 33 | Asturias |
| 34 | Palencia |
| 35 | Palmas, Las |
| 36 | Pontevedra |
| 37 | Salamanca |
| 38 | Santa Cruz de Tenerife |
| 39 | Cantabria |
| 40 | Segovia |
| 41 | Sevilla |
| 42 | Soria |
| 43 | Tarragona |
| 44 | Teruel |
| 45 | Toledo |
| 46 | Valencia/València |
| 47 | Valladolid |
| 48 | Bizkaia |
| 49 | Zamora |
| 50 | Zaragoza |
| 51 | Ceuta |
| 52 | Melilla |

### `REGEST`

Región o País donde está ubicado Todas las personas que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 86 |
| Longitud | 3 |
| Tipo | A |
| Nº de códigos | 16 |

| Código | Significado |
| --- | --- |
| 115 | UE- 15 (Excepto Francia y Portugal) |
| 125 | UE- 25 (no UE-15) |
| 128 | UE- 28 (no UE-27) |
| 100 | Resto de Europa (Excepto Andorra) |
| 200 | África (Excepto Marruecos) |
| 300 | América del Norte |
| 310 | Centroamérica y Caribe |
| 350 | Sudamérica |
| 400 | Asia Oriental (Lejano Oriente) |
| 410 | Asia Occidental (Oriente Próximo) |
| 420 | Asia del Sur y Sudoeste |
| 500 | Oceanía |
| 600 | Portugal |
| 610 | Francia |
| 620 | Andorra |
| 630 | Marruecos |

### `PARCO1`

Tipo de jornada, completa o parcial Todas las personas que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 89 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Completa |
| 6 | Parcial |

### `PARCO2`

Motivo de tener jornada parcial Ocupados a tiempo parcial

| Campo | Valor |
| --- | --- |
| Posición | 90 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Seguir cursos de enseñanza o formación |
| 02 | Enfermedad o incapacidad propia |
| 03 | Responsabilidades de cuidado de hijos u otros familiares |
| 04 | Otras razones familiares o personales |
| 05 | No haber podido encontrar un trabajo de jornada completa |
| 06 | No querer un trabajo de jornada completa |
| 07 | Otras razones |
| 00 | Desconoce el motivo |

### `HORASP`

Horas pactadas en contrato o acuerdo de trabajo (hhmm) Todos los asalariados Valores: hhmm 01:00-98:00 Horario conocido; valores válidos hh:mm 99:99 No sabe (incluye "No tiene horas pactadas por contratro")

| Campo | Valor |
| --- | --- |
| Posición | 92 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 9999 | No sabe (incluye "No tiene horas pactadas por contrato") |

### `HORASH`

Número de horas semanales que dedica a este trabajo habitualmente (hhmm) Todas las personas que trabajaron o tenían empleo la semana de referencia Valores: hhmm 01:00-98:00 Horario conocido; valores válidos hh:mm 99:00 Las horas varían de una semana a otra / no puede dar una estimación 99:99 No sabe horas:minutos

| Campo | Valor |
| --- | --- |
| Posición | 96 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 9999 | No sabe horas:minutos |
| 9900 | Las horas varían de una semana a otra/no puede dar una estimación |

### `HORASE`

Número de horas efectivas que dedicó a este trab. la semana pasada (hhmm) Todas las personas que trabajaron o tenían empleo la semana de referencia Valores: hhmm 00:00-98:00 Horario conocido; valores válidos hh:mm 99:99 No sabe horas:minutos 98:59 Mas de 98:00 horas en la semana de referencia (código específico pandemia COVID19) Las horas de aquellos que estuvieron recibiendo formación relacionada con el empleo fuera del establecimiento en la semana de referencia se consideran horas efectivas trabajadas

| Campo | Valor |
| --- | --- |
| Posición | 100 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 9999 | No sabe horas:minutos |
| 9859 | Más de 98:00 horas en la semana de referencia (código específico pandemia COVID19) |
| 0000 | No trabajó durante la semana de referencia |

### `EXTRA`

Realizó horas extraordinarias en la semana de referencia Asalariados

| Campo | Valor |
| --- | --- |
| Posición | 104 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `EXTPAG`

Número de horas extraordinarias pagadas realizadas en la semana de referencia (hhmm) Asalariados (y asimilados) que han realizado horas extra Valores: hhmm 00:00-98:00 00= No hizo horas extra pagadas durante la semana de referencia 9999 99= No puede precisar / no sabe

| Campo | Valor |
| --- | --- |
| Posición | 105 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 9999 | No puede precisar /No sabe |
| 0000 | No hizo horas extra durante la semana de referencia |

### `EXTNPG`

Número de horas extraordinarias NO pagadas realizadas en la semana de referencia (hhmm) Asalariados (y asimilados) que han realizado horas extra Valores: hhmm 00:00-98:00 00= No hizo horas extra pagadas durante la semana de referencia 9999 99= No puede precisar / no sabe

| Campo | Valor |
| --- | --- |
| Posición | 109 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 9999 | No puede precisar /No sabe |
| 0000 | No hizo horas extra durante la semana de referencia |

### `RELLB3`

Relleno apartado caracteristicas empleo

| Campo | Valor |
| --- | --- |
| Posición | 113 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

## Segundo empleo

### `TRAPLU`

Si tiene otro u otros empleos Todas las personas de 16 y más años que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 115 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `OCUPLU1`

¿Cuál es la ocupación u oficio en el segundo empleo? Todas las personas de 16 y más años que trabajaron o tenían segundo empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 116 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Ocupaciones militares (códigos CNO-2011). Fuerzas armadas (códigos CNO-1994) |
| 1 | Directores y gerentes (códigos CNO-2011). Dirección de las empresas y de las  Administraciones Públicas (códigos CNO-1994) |
| 2 | Técnicos y Profesionales científicos e intelectuales (códigos CNO-2011) |
| 3 | Técnicos y Profesionales de apoyo (códigos CNO-2011) |
| 4 | Empleados contables, administrativos y otros empleados de oficina (códigos CNO-2011). Empleados de tipo administrativo (códigos CNO-1994) |
| 5 | Trabajadores de servicios de restauración, personales, protección y vendedores de comercio (códigos CNO-2011) |
| 6 | Trabajadores cualificados en el sector agrícola, ganadero, forestal y pesquero (códigos CNO-2011).Trabajadores cualificados en la agricultura y en la pesca (códigos CNO-1994) |
| 7 | Artesanos y trabajadores cualificados de las industrias manufactureras y la construcción (excepto operadores de instalaciones y maquinaria (códigos CNO-2011). Artesanos y trabajadores cualificados de las industrias manufactureras, la construcción, y la minería, excepto operadores de instalaciones y maquinaria (códigos CNO-1994) |
| 8 | Operadores de instalaciones y maquinaria, y montadores (códigos CNO-2011) |
| 9 | Ocupaciones elementales (códigos CNO-2011). Trabajadores no cualificados (códigos CNO-1994) |

### `ACTPLU1`

Actividad del establecimiento donde tiene el segundo empleo 1 Todas las personas de 16 y más años que tenían segundo empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 117 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Agricultura, ganadería, silvicultura y pesca (códigos CNAE-09: 01, 02 y 03), (códigos CNAE-93: 01, 02 y 05) |
| 1 | Industria de la alimentación, textil, cuero, madera y papel (códigos CNAE-09: del 10 al 18), (códigos CNAE-93 del 15 al 22) |
| 2 | Industrias extractivas, refino de petróleo, industria química, farmaceutica, industria del caucho y materias plásticas, suministro energía eléctrica, gas, vapor y aire acondicionado, suministro de agua, gestión de residuos. Metalurgia (códigos CNAE-09: del 05 al 09, del 19 al 25, 35 y del 36 al 39), (códigos CNAE-93: del 10 al 14, del 23 al 28, 40 y 41) |
| 3 | Construcción de maquinaria, equipo eléctrico y material de transporte. Instalación y reparación industrial  (códigos CNAE-09 del 26 al 33), (códigos CNAE-93 del 29 al 37) |
| 4 | Construcción (códigos CNAE-09: del 41 al 43), (código CNAE-93: 45) |
| 5 | Comercio al por mayor y al por menor y sus instalaciones y reparaciones. Reparación de automóviles, hostelería (códigos CNAE-09: del 45 al 47, 55 y 56), (códigos CNAE-93: 50, 51, 52 y 55) |
| 6 | Transporte y almacenamiento. Información y comunicaciones (códigos CNAE-09 del 49 al 53 y del 58 al 63), (códigos CNAE-93 del 60 al 64) |
| 7 | Intermediación financiera, seguros, actividades inmobiliarias, servicios profesionales, científicos, administrativos y otros (códigos CNAE-09: del 64 al 66, 68, del 69 al 75 y del 77 al 82), (códigos CNAE-93 del 65 al 67 y del 70 al 74) |
| 8 | Administración Pública, educación y actividades sanitarias (códigos CNAE-09: 84, 85 y del 86 al 88), (códigos CNAE-93: 75, 80 y 85) |
| 9 | Otros servicios (códigos CNAE-09: del 90 al 93, del 94 al 96, 97y  99), (códigos CNAE-93: del 90 al 93, 95 y 99) |

### `SITPLU`

Situación profesional en el segundo empleo Todas las personas de 16 y más años que tenían segundo empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 118 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| 01 | Empresario con asalariados |
| 03 | Trabajador independiente o empresario sin asalariados |
| 05 | Miembro de una cooperativa |
| 06 | Ayuda en la empresa o negocio familiar |
| 07 | Asalariado sector público |
| 08 | Asalariado sector privado |
| 09 | Otra situación |

### `HOREPLU`

Nº de horas efectivas trabaj. la semana pasada en el segundo empleo (hhmm) Todas las personas de 16 y más años que tenían segundo empleo la semana de referencia Valores: hhmm '00:00-98:00 Horario conocido; valores válidos hh:mm 99:99 No sabe horas:minutos

| Campo | Valor |
| --- | --- |
| Posición | 120 |
| Longitud | 4 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 9999 | No sabe horas:minutos |
| 9859 | Más de 98:00 horas en la semana de referencia (código específico pandemia COVID19) |
| 0000 | No trabajó durante la semana de referencia |

## Deseo de trabajar mas horas

### `MASHOR`

Si desearía trabajar más o menos horas Todas las personas de 16 y más años que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 124 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 2 | No, desearía trabajar menos horas con reducción proporcional de salario |
| 3 | No |

### `DISMAS`

Estaría disponible para trabajar más horas antes de 15 días desde la semana de referencia Todas las personas de 16 y más años que trabajaron o tenían empleo la semana de referencia y desean trabajar más horas

| Campo | Valor |
| --- | --- |
| Posición | 125 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `RZNDISH`

Razones por las que no podría trabajar más horas Personas de 16 y más años que trabajaron o tenían empleo la semana de referencia, que desean trabajar más horas pero no están disponibles para hacerlo antes de 15 días

| Campo | Valor |
| --- | --- |
| Posición | 126 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 5 |

| Código | Significado |
| --- | --- |
| 01 | Tener que completar estudios o formación |
| 02 | Responsabilidades de cuidado de hijos u otros familiares |
| 03 | Enfermedad o incapacidad propia |
| 04 | Otras razones |
| 05 | Por no poder dejar su empleo actual debido al periodo de preaviso |

### `HORDES`

Número de horas que desearía trabajar habitualmente Todas las personas de 16 y más años que trabajaron o tenían empleo la semana de referencia y desean trabajar más o menos horas Valores: hh hh=01-98 De 1 a 98 horas hh=99 No puede precisar / no sabe

| Campo | Valor |
| --- | --- |
| Posición | 128 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 99 | No puede precisar /no sabe |

### `BUSOTR`

Busca otro empleo o está haciendo gestiones para establecerse por su cuenta Todas las personas de 16 y más años que trabajaron o tenían empleo la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 130 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

## Búsqueda de empleo

### `BUSCA`

Ha buscado empleo en las últimas cuatro semanas Personas de 16 a 74 años sin empleo que no han trabajado en la semana de referencia

| Campo | Valor |
| --- | --- |
| Posición | 131 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `DESEA`

Desearía tener un empleo Personas de 16 a 74 años sin empleo que no han trabajado en la semana de referencia, no han encontrado empleo y no han buscado empleo en las últimas 4 semanas

| Campo | Valor |
| --- | --- |
| Posición | 132 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `FOBACT`

Búsqueda de empleo activa. Métodos activos de encontrar empleo

| Campo | Valor |
| --- | --- |
| Posición | 133 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Métodos activos de búsqueda de empleo |
| 6 | Métodos no activos de búsqueda de empleo |

### `NBUSCA`

Razones por las que no busca empleo Personas sin empleo que no buscan empleo (ni han encontrado uno al que aún no se han incorporado) ni desean tener uno

| Campo | Valor |
| --- | --- |
| Posición | 134 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 9 |

| Código | Significado |
| --- | --- |
| 01 | No hay empleo adecuado disponible |
| 02 | Está afectado por una regulación de empleo |
| 03 | Por enfermedad o incapacidad propia |
| 04 | Responsabilidades de cuidado de hijos u otros familiares |
| 05 | Tiene otras responsabilidades familiares o personales |
| 06 | Está cursando estudios o recibiendo formación |
| 07 | Está jubilado |
| 08 | Otras razones |
| 00 | No sabe |

### `RZULT`

Razón principal por la que dejó el último empleo Personas de 16 a 89 años que no tienen empleo ni trabajaron la semana de referencia, pero trabajaron antes y que dejaron su empleo hace 8 años o menos

| Campo | Valor |
| --- | --- |
| Posición | 136 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 01 | Despido o supresión del puesto (incluye regulación de empleo) |
| 02 | Fin del contrato (incluye los fijos-discontinuos y los trabajos estacionales) s |
| 03 | Enfermedad o incapacidad propia |
| 04 | Realizar estudios o recibir formación |
| 05 | Responsabilidades de cuidado de hijos u otros familiares |
| 06 | Otras razones familiares o personales |
| 07 | Jubilación anticipada |
| 08 | Jubilación normal |
| 09 | Otras razones (incluye el cese en una actividad propia y por voluntad propia) |
| 00 | No sabe |

### `ITBU`

Tiempo que lleva buscando empleo / estuvo buscando empleo Personas que buscan empleo o que han encontrado un empleo al que se van a incorporar

| Campo | Valor |
| --- | --- |
| Posición | 138 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Menos de 1 mes |
| 02 | De 1 a < 3 meses |
| 03 | De 3 a < 6 meses |
| 04 | De  6 meses a < 1 año |
| 05 | De 1 año a < 1 año y medio |
| 06 | De 1 año y medio a < 2 años |
| 07 | De 2 a < 4 años |
| 08 | 4 años o más |

### `DISP`

Disponible para trabajar en un plazo de 15 días Todas las personas de 16 a 74 años sin empleo que lo buscan o no lo buscan pero lo han encontrado (incluye quienes han empezado a trabajar con posterioridad a la semana de referencia y antes de la entrevista)

| Campo | Valor |
| --- | --- |
| Posición | 140 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `RZNDIS`

Razones para no poder empezar a trabajar en un plazo de 15 días Todas las personas de 16 a 74 años sin empleo que lo buscan o que no lo buscan pero lo han encontrado y que no estarían disponibles para incorporarse en dicho plazo

| Campo | Valor |
| --- | --- |
| Posición | 141 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 4 |

| Código | Significado |
| --- | --- |
| 1 | Tener que completar estudios o formación |
| 2 | Responsabilidades de cuidado de hijos u otros familiares |
| 3 | Por enfermedad o incapacidad propia |
| 4 | Por otras razones |

## Experiencia profesional

### `EMPANT`

Si ha realizado antes algún trabajo Todas las personas de 16 a 89 años que no trabajaron la semana de referencia y no tienen empleo

| Campo | Valor |
| --- | --- |
| Posición | 142 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |

### `DTANT`

Número de meses transcurridos desde que dejó su último empleo No ocupados de 16 a 89 años que trabajaron antes Valores: 0-924

| Campo | Valor |
| --- | --- |
| Posición | 143 |
| Longitud | 3 |
| Tipo | N |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `OCUPA`

Ocupación u oficio que desempeñaba en su último empleo, si hace menos de un año que lo dejó (*) Personas de 16 a 89 años que no tienen empleo ni trabajaron la semana de referencia, pero trabajaron antes y que dejaron su empleo hace 1 año o menos Si dejaron su empleo hace más de un año es una variable anual

| Campo | Valor |
| --- | --- |
| Posición | 146 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Ocupaciones militares (códigos CNO-2011). Fuerzas armadas (códigos CNO-1994) |
| 1 | Directores y gerentes (códigos CNO-2011). Dirección de las empresas y de las  Administraciones Públicas (códigos CNO-1994) |
| 2 | Técnicos y Profesionales científicos e intelectuales (códigos CNO-2011) |
| 3 | Técnicos y Profesionales de apoyo (códigos CNO-2011) |
| 4 | Empleados contables, administrativos y otros empleados de oficina (códigos CNO-2011). Empleados de tipo administrativo (códigos CNO-1994) |
| 5 | Trabajadores de servicios de restauración, personales, protección y vendedores de comercio (códigos CNO-2011) |
| 6 | Trabajadores cualificados en el sector agrícola, ganadero, forestal y pesquero (códigos CNO-2011).Trabajadores cualificados en la agricultura y en la pesca (códigos CNO-1994) |
| 7 | Artesanos y trabajadores cualificados de las industrias manufactureras y la construcción (excepto operadores de instalaciones y maquinaria (códigos CNO-2011). Artesanos y trabajadores cualificados de las industrias manufactureras, la construcción, y la minería, excepto operadores de instalaciones y maquinaria (códigos CNO-1994) |
| 8 | Operadores de instalaciones y maquinaria, y montadores (códigos CNO-2011) |
| 9 | Ocupaciones elementales (códigos CNO-2011). Trabajadores no cualificados (códigos CNO-1994) |

### `ACTA`

Actividad del establecimiento donde trabajaba, si hace menos de un año que lo dejó (1, *) Personas de 16 a 89 años que no tienen empleo ni trabajaron la semana de referencia, pero trabajaron antes y que dejaron su empleo hace 1 año o menos Si dejaron su empleo hace más de un año es una variable anual

| Campo | Valor |
| --- | --- |
| Posición | 147 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 10 |

| Código | Significado |
| --- | --- |
| 0 | Agricultura, ganadería, silvicultura y pesca (códigos CNAE-09: 01, 02 y 03), (códigos CNAE-93: 01, 02 y 05) |
| 1 | Industria de la alimentación, textil, cuero, madera y papel (códigos CNAE-09: del 10 al 18), (códigos CNAE-93 del 15 al 22) |
| 2 | Industrias extractivas, refino de petróleo, industria química, farmaceutica, industria del caucho y materias plásticas, suministro energía eléctrica, gas, vapor y aire acondicionado, suministro de agua, gestión de residuos. Metalurgia (códigos CNAE-09: del 05 al 09, del 19 al 25, 35 y del 36 al 39), (códigos CNAE-93: del 10 al 14, del 23 al 28, 40 y 41) |
| 3 | Construcción de maquinaria, equipo eléctrico y material de transporte. Instalación y reparación industrial  (códigos CNAE-09 del 26 al 33), (códigos CNAE-93 del 29 al 37) |
| 4 | Construcción (códigos CNAE-09: del 41 al 43), (código CNAE-93: 45) |
| 5 | Comercio al por mayor y al por menor y sus instalaciones y reparaciones. Reparación de automóviles, hostelería (códigos CNAE-09: del 45 al 47, 55 y 56), (códigos CNAE-93: 50, 51, 52 y 55) |
| 6 | Transporte y almacenamiento. Información y comunicaciones (códigos CNAE-09 del 49 al 53 y del 58 al 63), (códigos CNAE-93 del 60 al 64) |
| 7 | Intermediación financiera, seguros, actividades inmobiliarias, servicios profesionales, científicos, administrativos y otros (códigos CNAE-09: del 64 al 66, 68, del 69 al 75 y del 77 al 82), (códigos CNAE-93 del 65 al 67 y del 70 al 74) |
| 8 | Administración Pública, educación y actividades sanitarias (códigos CNAE-09: 84, 85 y del 86 al 88), (códigos CNAE-93: 75, 80 y 85) |
| 9 | Otros servicios (códigos CNAE-09: del 90 al 93, del 94 al 96, 97y  99), (códigos CNAE-93: del 90 al 93, 95 y 99) |

### `SITUA`

Situación profesional que tenía en su anterior trabajo, si hace menos de un año que lo dejó (*) Personas de 16 a 89 años que no tienen empleo ni trabajaron la semana de referencia, pero trabajaron antes y que dejaron su empleo hace 1 año o menos Si dejaron su empleo hace más de un año es una variable anual

| Campo | Valor |
| --- | --- |
| Posición | 148 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| 01 | Empresario con asalariados |
| 03 | Trabajador independiente o empresario sin asalariados |
| 05 | Miembro de una cooperativa |
| 06 | Ayuda en la empresa o negocio familiar |
| 07 | Asalariado sector público |
| 08 | Asalariado sector privado |
| 09 | Otra situación |

## Inscripción en la oficina de empleo pública

### `OFEMP`

Situación el domingo pasado, en relación con las of. Empleo de la admon. Todas las personas de 16 a 74 años

| Campo | Valor |
| --- | --- |
| Posición | 150 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 4 |

| Código | Significado |
| --- | --- |
| 1 | Estaba inscrito como demandante y recibía algún tipo de prestación |
| 2 | Estaba inscrito como demandante sin recibir subsidio o prestación por desempleo |
| 3 | No estaba inscrito como demandante |
| 4 | No contesta / No sabe |

## Situaciones diversas

### `SIDI1`

Situación inactividad autopercibida en la que estaba la semana pasada Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 151 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Estudiante (aunque esté de vacaciones) |
| 02 | Percibía una pensión de jubilación o unos ingresos de prejubilación |
| 03 | Dedicado a las labores del hogar |
| 04 | Incapacitado permanente |
| 05 | Percibiendo una pensión distinta a la de jubilación (o prejubilación) |
| 06 | Realizando sin remuneración trabajos sociales, actividades benéficas… |
| 07 | Otras situaciones |
| 00 | No sabe / No refiere estado de inactividad |

### `SIDI2`

Situación inactividad autopercibida en la que estaba la semana pasada Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 153 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Estudiante (aunque esté de vacaciones) |
| 02 | Percibía una pensión de jubilación o unos ingresos de prejubilación |
| 03 | Dedicado a las labores del hogar |
| 04 | Incapacitado permanente |
| 05 | Percibiendo una pensión distinta a la de jubilación (o prejubilación) |
| 06 | Realizando sin remuneración trabajos sociales, actividades benéficas… |
| 07 | Otras situaciones |
| 00 | No sabe / No refiere estado de inactividad |

### `SIDI3`

Situación inactividad autopercibida en la que estaba la semana pasada Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 155 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 8 |

| Código | Significado |
| --- | --- |
| 01 | Estudiante (aunque esté de vacaciones) |
| 02 | Percibía una pensión de jubilación o unos ingresos de prejubilación |
| 03 | Dedicado a las labores del hogar |
| 04 | Incapacitado permanente |
| 05 | Percibiendo una pensión distinta a la de jubilación (o prejubilación) |
| 06 | Realizando sin remuneración trabajos sociales, actividades benéficas… |
| 07 | Otras situaciones |
| 00 | No sabe / No refiere estado de inactividad |

### `SIDAC1`

Situación de actividad autopercibida en la que estaba la semana pasada Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 157 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Trabajando |
| 2 | Buscando empleo |

### `SIDAC2`

Situación de actividad autopercibida en la que estaba la semana pasada Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 158 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 2 |

| Código | Significado |
| --- | --- |
| 1 | Trabajando |
| 2 | Buscando empleo |

## Días de ausencia

### `DAUSVAC`

Dias de ausencia por vacaciones, días festivos, horario flexible o similar Todas las personas de 16 y más años con empleo que informan de ausencia por vacaciones, días festivos, horario flexible o similar 0,5; 1,0; 1,5; 2,0; … 6,5; 7,0 Valores válidos enteros /medios días 9,9 No sabe días de ausencia

| Campo | Valor |
| --- | --- |
| Posición | 159 |
| Longitud | 2 |
| Tipo | N |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 99 | No sabe días de ausencia |

### `DAUSENF`

Días de ausencia por enfermedad Todas las personas de 16 y más años con empleo que informan de ausencia por enfermedad 0,5; 1,0; 1,5; 2,0; … 6,5; 7,0 Valores válidos enteros /medios días 9,9 No sabe días de ausencia

| Campo | Valor |
| --- | --- |
| Posición | 161 |
| Longitud | 2 |
| Tipo | N |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 99 | No sabe días de ausencia |

### `DAUSOTR`

Días de ausencia por otras razones Todas las personas de 16 y más años con empleo que informan de ausencia por otras razones distintas de vacaciones, festivos, horario flexible o similar o enfermedad 0,5; 1,0; 1,5; 2,0; … 6,5; 7,0 Valores válidos enteros /medios días 9,9 No sabe días de ausencia

| Campo | Valor |
| --- | --- |
| Posición | 163 |
| Longitud | 2 |
| Tipo | N |
| Nº de códigos | 1 |

| Código | Significado |
| --- | --- |
| 99 | No sabe días de ausencia |

## Si trabajó el año pasado

### `TRAANT`

Si trabajó en algún momento el año pasado Todas las personas de 16 y más años, sólo en el primer trimestre

| Campo | Valor |
| --- | --- |
| Posición | 165 |
| Longitud | 1 |
| Tipo | A |
| Nº de códigos | 3 |

| Código | Significado |
| --- | --- |
| 1 | Sí |
| 6 | No |
| 0 | No sabe |

## Variables derivadas

### `AOI`

Clasificación de los entrevistados por relación con la actividad económica según criterios OIT Todas las personas de 16 y más años

| Campo | Valor |
| --- | --- |
| Posición | 166 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | 7 |

| Código | Significado |
| --- | --- |
| 03 | Ocupados subempleados por insuficiencia de horas |
| 04 | Resto de ocupados |
| 05 | Parados que buscan primer empleo |
| 06 | Parados que han trabajado antes |
| 07 | Inactivos 1 (desanimados) |
| 08 | Inactivos 2 (junto con los desanimados forman los activos potenciales) |
| 09 | Inactivos 3 (resto de inactivos) |

### `RELLB4`

Relleno variables derivadas

| Campo | Valor |
| --- | --- |
| Posición | 168 |
| Longitud | 2 |
| Tipo | A |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._

### `FACTOREL`

Factor de elevación Todos los registros Valores: XXXXX.XX Para reproducir los datos publicados en INEbase (presentados en miles de personas) hay que dividir por mil

| Campo | Valor |
| --- | --- |
| Posición | 170 |
| Longitud | 7 |
| Tipo | N |
| Nº de códigos | — |

_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._
