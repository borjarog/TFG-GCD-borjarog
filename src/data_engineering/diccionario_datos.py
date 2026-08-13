"""Diccionario de variables EPA a partir del Excel de diseño de registro del INE."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd  # type: ignore

from .config import DISENO_REGISTRO_EPA, RUTA_DICCIONARIO_DATOS

HOJA_DISENO = 0  # hoja "Diseño": población de 16 y más años (NIVEL=1)


@dataclass
class VariableEPA:
    nombre: str
    seccion: str
    descripcion: str
    posicion: int | None
    longitud: int | None
    tipo: str | None
    tabla_codigos: str | None
    codigos: dict[str, str] = field(default_factory=dict)


def _limpiar_texto(valor) -> str:
    """Colapsa los saltos de línea/espacios del Excel en un texto legible."""
    if pd.isna(valor):
        return ""
    texto = str(valor).replace("\r", "\n")
    texto = re.sub(r"\s*\n\s*", " ", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.strip(" .…")


def _buscar_columna(df: pd.DataFrame, incluye: str, excluye: str | None = None) -> str:
    for col in df.columns:
        texto = str(col).strip().lower()
        if incluye in texto and (excluye is None or excluye not in texto):
            return col
    raise KeyError(
        f"No se encontró ninguna columna que contenga '{incluye}' en {list(df.columns)}"
    )


def _parsear_tablas_codigos(xlsx: pd.ExcelFile) -> dict[str, dict[str, str]]:
    """Parsea las hojas Tablas1..5 -> {nombre_tabla: {codigo: descripcion}}."""
    tablas: dict[str, dict[str, str]] = {}

    for sheet in xlsx.sheet_names:
        if not sheet.startswith("Tablas"):
            continue

        df = pd.read_excel(xlsx, sheet_name=sheet, header=None)
        tabla_actual: str | None = None
        leyendo = False

        for _, row in df.iterrows():
            c0 = row.iloc[0] if pd.notna(row.iloc[0]) else None
            c1 = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None
            c2 = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else None

            if c0 and c2 and isinstance(c2, str) and "Variables" not in c2:
                tabla_actual = str(c0).strip()
                tablas.setdefault(tabla_actual, {})
                leyendo = False
                continue

            if isinstance(c0, str) and c0.strip() == "Código":
                leyendo = True
                continue

            if (
                leyendo
                and tabla_actual
                and c0 is not None
                and str(c0).strip() not in ("", "nan")
            ):
                codigo = str(c0).strip()
                if codigo.lower() == "código":
                    continue
                descripcion = (
                    str(c1).strip()
                    if c1 is not None and str(c1).strip() not in ("", "nan")
                    else codigo
                )
                tablas[tabla_actual][codigo] = descripcion

    return tablas


def _construir_variables(xlsx: pd.ExcelFile) -> list[VariableEPA]:
    df = pd.read_excel(xlsx, sheet_name=HOJA_DISENO, header=1)

    col_var = _buscar_columna(df, "variable", excluye="diccionario")
    col_tabla = _buscar_columna(df, "diccionario de la variable")
    col_longitud = _buscar_columna(df, "longitud")
    col_tipo = _buscar_columna(df, "tipo")
    col_posicion = _buscar_columna(df, "posici")
    col_descripcion = _buscar_columna(df, "descripci")
    col_seccion = df.columns[-1]  # última columna: etiqueta temática del bloque

    df[col_seccion] = df[col_seccion].ffill()
    tablas_codigos = _parsear_tablas_codigos(xlsx)

    variables: list[VariableEPA] = []
    for _, row in df.iterrows():
        nombre = row[col_var]
        # Las filas sin posición/longitud son notas al pie o separadores del Excel
        # (p.ej. "*** TOTAL ***" o comentarios metodológicos), no variables reales.
        if pd.isna(nombre) or pd.isna(row[col_posicion]) or pd.isna(row[col_longitud]):
            continue
        nombre = str(nombre).strip()
        if nombre.lower() == "variable" or not re.match(
            r"^[A-Za-z][A-Za-z0-9_]*$", nombre
        ):
            continue

        tabla = row[col_tabla]
        tabla = str(tabla).strip() if pd.notna(tabla) else None

        variables.append(
            VariableEPA(
                nombre=nombre,
                seccion=str(row[col_seccion]).strip()
                if pd.notna(row[col_seccion])
                else "Otros",
                descripcion=_limpiar_texto(row[col_descripcion]),
                posicion=int(row[col_posicion])
                if pd.notna(row[col_posicion])
                else None,
                longitud=int(row[col_longitud])
                if pd.notna(row[col_longitud])
                else None,
                tipo=str(row[col_tipo]).strip() if pd.notna(row[col_tipo]) else None,
                tabla_codigos=tabla,
                codigos=dict(tablas_codigos.get(tabla, {})) if tabla else {},
            )
        )

    return variables


def cargar_diccionario_variables(ruta: str | None = None) -> list[VariableEPA]:
    """Carga y estructura el diseño de registro oficial en memoria (para uso futuro en el pipeline)."""
    xlsx = pd.ExcelFile(ruta or DISENO_REGISTRO_EPA)
    return _construir_variables(xlsx)


def obtener_codigos(
    variable: str, variables: list[VariableEPA] | None = None
) -> dict[str, str]:
    """Devuelve {codigo: significado} de una variable concreta."""
    variables = variables or cargar_diccionario_variables()
    for var in variables:
        if var.nombre == variable:
            return var.codigos
    raise KeyError(f"Variable '{variable}' no encontrada en el diseño de registro")


def normalizar_codigo(valor) -> str | None:
    """Normaliza un código para comparar de forma tolerante ('1' == '01')."""
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto.lower() in ("", "nan", "none"):
        return None
    return texto.lstrip("0") or "0" if texto.isdigit() else texto


def codigo_en(serie: pd.Series, codigos: set[str]) -> pd.Series:
    """True si el valor de la serie coincide con alguno de los códigos (tolera '1' vs '01')."""
    normalizados = {normalizar_codigo(c) for c in codigos}
    return serie.map(normalizar_codigo).isin(normalizados)


def mapear_variable(
    serie: pd.Series,
    variable: str,
    variables: list[VariableEPA] | None = None,
    default: str | None = "Desconocido",
) -> pd.Series:
    """Traduce una columna de códigos EPA a las etiquetas oficiales del diccionario."""
    codigos = obtener_codigos(variable, variables)
    codigos_normalizados = {
        normalizar_codigo(c): etiqueta for c, etiqueta in codigos.items()
    }

    def _lookup(valor):
        codigo = normalizar_codigo(valor)
        if codigo is None:
            return pd.NA
        return codigos_normalizados.get(codigo, default)

    return serie.map(_lookup)


def colspecs_ancho_fijo(
    variables: list[VariableEPA] | None = None,
) -> tuple[list[tuple[int, int]], list[str]]:
    """Construye (colspecs, nombres) para `pandas.read_fwf` a partir de posición/longitud.

    Se usa como fallback en la ingesta cuando el INE entrega un fichero de ancho fijo
    en vez de un CSV/TAB ya delimitado.
    """
    variables = variables or cargar_diccionario_variables()
    variables_ordenadas = sorted(variables, key=lambda v: v.posicion or 0)

    colspecs = [
        (v.posicion - 1, v.posicion - 1 + v.longitud) for v in variables_ordenadas
    ]
    nombres = [v.nombre for v in variables_ordenadas]
    return colspecs, nombres


def _tabla_markdown(cabeceras: list[str], filas: list[list[str]]) -> str:
    lineas = [
        "| " + " | ".join(cabeceras) + " |",
        "| " + " | ".join(["---"] * len(cabeceras)) + " |",
    ]
    for fila in filas:
        lineas.append("| " + " | ".join(fila) + " |")
    return "\n".join(lineas)


def generar_markdown(variables: list[VariableEPA]) -> str:
    partes = [
        "# Diccionario de datos — EPA (INE)",
        "",
        "Generado automáticamente a partir del diseño de registro oficial del INE "
        f"(`{DISENO_REGISTRO_EPA.name}`, bloque metodológico **2021 en adelante**).",
        "",
        "- **Población cubierta:** personas de 16 y más años (`NIVEL = 1`), que es la población de análisis del TFG.",
        "- **Fuente de verdad:** el Excel oficial del INE. Si el INE actualiza el diseño de registro, "
        "regenera este documento con `python -m src.data_engineering.diccionario_datos`.",
        f"- **Última generación:** {date.today().isoformat()}",
        f"- **Total de variables documentadas:** {len(variables)}",
        "",
        "## Índice de secciones",
        "",
    ]

    secciones: dict[str, list[VariableEPA]] = {}
    for var in variables:
        secciones.setdefault(var.seccion, []).append(var)

    def _slug(texto: str) -> str:
        texto = texto.lower()
        for origen, destino in (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ñ", "n"),
        ):
            texto = texto.replace(origen, destino)
        return re.sub(r"[^a-z0-9\-]", "", texto.replace(" ", "-"))

    for seccion in secciones:
        partes.append(f"- [{seccion}](#{_slug(seccion)})")
    partes.append("")

    for seccion, vars_seccion in secciones.items():
        partes.append(f"## {seccion}")
        partes.append("")
        for var in vars_seccion:
            partes.append(f"### `{var.nombre}`")
            partes.append("")
            if var.descripcion:
                partes.append(var.descripcion)
                partes.append("")

            info_filas = []
            if var.posicion is not None:
                info_filas.append(["Posición", str(var.posicion)])
            if var.longitud is not None:
                info_filas.append(["Longitud", str(var.longitud)])
            if var.tipo:
                info_filas.append(["Tipo", var.tipo])
            info_filas.append(
                ["Nº de códigos", str(len(var.codigos)) if var.codigos else "—"]
            )
            partes.append(_tabla_markdown(["Campo", "Valor"], info_filas))
            partes.append("")

            if var.codigos:
                filas_codigos = [
                    [codigo, significado] for codigo, significado in var.codigos.items()
                ]
                partes.append(_tabla_markdown(["Código", "Significado"], filas_codigos))
            else:
                partes.append(
                    "_Variable numérica o de texto libre: no tiene un diccionario de códigos asociado._"
                )
            partes.append("")

    return "\n".join(partes)


def generar_diccionario_datos(ruta_salida=None) -> Path:
    """Genera el Markdown del diccionario de datos completo y lo guarda a disco."""
    ruta_salida = Path(ruta_salida) if ruta_salida else RUTA_DICCIONARIO_DATOS
    variables = cargar_diccionario_variables()
    markdown = generar_markdown(variables)

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(markdown, encoding="utf-8")

    print(f"Diccionario de datos generado: {ruta_salida} ({len(variables)} variables)")
    return ruta_salida


if __name__ == "__main__":
    generar_diccionario_datos()
