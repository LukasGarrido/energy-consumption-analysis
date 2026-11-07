"""
app/graficos.py
Helpers de colores, compatibilidad de API de Streamlit y utilidades
visuales compartidas por todas las páginas.
"""

import inspect

import plotly.graph_objects as go
import streamlit as st

from app.config import COLORES_REGION, OKABE_ITO


# Compatibilidad de API de st.plotly_chart entre versiones de Streamlit
def _tiene_param_width() -> bool:
    """
    Detecta si la versión instalada de Streamlit acepta el parámetro
    ``width`` en ``st.plotly_chart``.

    En versiones recientes se usa ``use_container_width=True``; en algunas
    anteriores existía ``width="stretch"``.

    Retorna
    -------
    bool
    """
    sig = inspect.signature(st.plotly_chart)
    return "width" in sig.parameters


def mostrar_grafico(fig: go.Figure) -> None:
    """
    Muestra un gráfico Plotly ocupando el ancho del contenedor,
    compatible con distintas versiones de Streamlit.

    Parámetros
    ----------
    fig : go.Figure
        Figura de Plotly lista para renderizar.
    """
    if _tiene_param_width():
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)


# Utilidades de color
def color_region(region: str) -> str:
    """
    Devuelve el color hexadecimal asignado a una región PJM.
    Si la región no está en el mapa, devuelve gris (#888888).

    Parámetros
    ----------
    region : str

    Retorna
    -------
    str
    """
    return COLORES_REGION.get(region, "#888888")


def color_grupo(grupo_id: int) -> str:
    """
    Devuelve el color Okabe-Ito correspondiente al identificador de grupo.
    Los grupos se numeran desde 1; el índice en la paleta es ``(grupo - 1) % 8``.

    Parámetros
    ----------
    grupo_id : int
        Identificador numérico del grupo (empieza en 1).

    Retorna
    -------
    str
    """
    idx = (int(grupo_id) - 1) % len(OKABE_ITO)
    return OKABE_ITO[idx]


def hex_a_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """
    Convierte un color hexadecimal (#RRGGBB) a una cadena rgba() compatible
    con Plotly.

    Parámetros
    ----------
    hex_color : str
        Color en formato hexadecimal, por ejemplo '#E69F00'.
    alpha : float
        Canal alfa entre 0.0 y 1.0.

    Retorna
    -------
    str
        Cadena en formato 'rgba(r,g,b,alpha)'.
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def mapa_colores_grupos(
    df_fuente,
    col_grupo: str = "grupo",
    col_nombre: str = "nombre_grupo",
) -> dict[str, str]:
    """
    Construye un diccionario ``{nombre_grupo: color_hex}`` a partir de un
    DataFrame que contiene las columnas de grupo y nombre de grupo.

    Los colores provienen de la paleta Okabe-Ito, indexada por el id de grupo,
    para mantener consistencia entre páginas.

    Parámetros
    ----------
    df_fuente : pd.DataFrame
    col_grupo : str
        Columna con el identificador numérico del grupo.
    col_nombre : str
        Columna con el nombre legible del grupo.

    Retorna
    -------
    dict[str, str]
    """
    pares = (
        df_fuente[[col_grupo, col_nombre]]
        .dropna()
        .drop_duplicates()
        .sort_values(col_grupo)
    )
    return {
        str(row[col_nombre]): color_grupo(int(row[col_grupo]))
        for _, row in pares.iterrows()
    }
