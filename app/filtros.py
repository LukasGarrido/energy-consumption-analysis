"""
app/filtros.py
Helpers de filtrado y validación de DataFrames según los controles
de la barra lateral (región, estación y rango de fechas).
"""

import pandas as pd
import streamlit as st

from app.config import ESTACIONES


def por_region(df: pd.DataFrame, regiones: list[str]) -> pd.DataFrame:
    """
    Filtra ``df`` por las regiones seleccionadas si la columna ``region``
    existe. Si la lista está vacía devuelve el DataFrame sin cambios.

    Parámetros
    ----------
    df : pd.DataFrame
    regiones : list[str]
        Lista de nombres de región seleccionados en la barra lateral.

    Retorna
    -------
    pd.DataFrame
    """
    if "region" in df.columns and regiones:
        return df[df["region"].isin(regiones)].copy()
    return df


def por_estacion(df: pd.DataFrame, estaciones: list[str]) -> pd.DataFrame:
    """
    Filtra ``df`` por estaciones si la columna ``estacion`` existe.

    Parámetros
    ----------
    df : pd.DataFrame
    estaciones : list[str]
        Lista de estaciones seleccionadas en la barra lateral.

    Retorna
    -------
    pd.DataFrame
    """
    if "estacion" in df.columns and estaciones:
        return df[df["estacion"].isin(estaciones)].copy()
    return df


def por_fecha(
    df: pd.DataFrame,
    col_fecha: str,
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
) -> pd.DataFrame:
    """
    Filtra ``df`` por rango de fechas usando la columna indicada.

    Parámetros
    ----------
    df : pd.DataFrame
    col_fecha : str
        Nombre de la columna de fecha sobre la que aplicar el rango.
    fecha_inicio : pd.Timestamp
        Límite inferior del rango (inclusive).
    fecha_fin : pd.Timestamp
        Límite superior del rango (inclusive).

    Retorna
    -------
    pd.DataFrame
    """
    if col_fecha in df.columns:
        return df[
            (df[col_fecha] >= fecha_inicio) & (df[col_fecha] <= fecha_fin)
        ].copy()
    return df


def verificar_vacio(df: pd.DataFrame) -> bool:
    """
    Si el DataFrame está vacío, muestra ``st.info("Sin datos con estos
    filtros.")`` y devuelve ``True``.

    El llamador debe cortar su propia ejecución si esta función retorna
    ``True`` (patrón guard-clause).

    Parámetros
    ----------
    df : pd.DataFrame

    Retorna
    -------
    bool
        ``True`` si el DataFrame está vacío, ``False`` en caso contrario.
    """
    if df.empty:
        st.info("Sin datos con estos filtros.")
        return True
    return False


def selector_filtros_modulo(
    tablas: dict[str, pd.DataFrame],
    key_sufijo: str,
    con_fechas: bool = True,
) -> tuple[list[str], pd.Timestamp, pd.Timestamp, list[str]]:
    """
    Renderiza un panel de filtros integrado en el módulo actual para el estudio,
    permitiendo filtrar datos de forma local y limpia sin sobrecargar el menú lateral.
    """
    todas_las_regiones = sorted(tablas["dim_region"]["region"].unique().tolist())
    hd_fechas = tablas["hechos_diario"]["fecha"].dropna()
    fecha_global_min = hd_fechas.min().date()
    fecha_global_max = hd_fechas.max().date()
    fecha_global_max_ts = pd.Timestamp(fecha_global_max)

    k_regiones = f"regiones_{key_sufijo}"
    k_estaciones = f"estaciones_{key_sufijo}"
    k_fechas = f"fecha_rango_{key_sufijo}"

    if k_regiones not in st.session_state:
        st.session_state[k_regiones] = todas_las_regiones
    if k_estaciones not in st.session_state:
        st.session_state[k_estaciones] = ESTACIONES
    if k_fechas not in st.session_state:
        st.session_state[k_fechas] = (fecha_global_min, fecha_global_max)

    with st.expander("Filtros y parametros del modulo", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            regiones_sel = st.multiselect(
                "Regiones",
                options=todas_las_regiones,
                key=k_regiones,
            )
        with col2:
            estaciones_sel = st.multiselect(
                "Estaciones",
                options=ESTACIONES,
                key=k_estaciones,
            )
        with col3:
            if con_fechas:
                fecha_rango = st.date_input(
                    "Rango de fechas",
                    min_value=fecha_global_min,
                    max_value=fecha_global_max,
                    key=k_fechas,
                )
            else:
                fecha_rango = (fecha_global_min, fecha_global_max)

    if con_fechas:
        if isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 2:
            f_inicio, f_fin = pd.Timestamp(fecha_rango[0]), pd.Timestamp(fecha_rango[1])
        elif isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 1:
            f_inicio, f_fin = pd.Timestamp(fecha_rango[0]), fecha_global_max_ts
        else:
            f_inicio, f_fin = pd.Timestamp(fecha_rango), fecha_global_max_ts
    else:
        f_inicio, f_fin = pd.Timestamp(fecha_global_min), fecha_global_max_ts

    return regiones_sel, f_inicio, f_fin, estaciones_sel
