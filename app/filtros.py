"""
app/filtros.py
Helpers de filtrado y validación de DataFrames según los controles
de la barra lateral (región, estación y rango de fechas).
"""

import pandas as pd
import streamlit as st


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
