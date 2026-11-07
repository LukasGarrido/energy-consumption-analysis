"""
app/data_loader.py
Carga y caché de todas las tablas CSV exportadas por el notebook 07.

La función principal usa ``st.cache_data`` para leer los archivos una
sola vez por sesión y aplicar las conversiones de tipo necesarias.
"""

import pandas as pd
import streamlit as st

from app.config import TABLAS_REQUERIDAS, resolver_directorio_powerbi


@st.cache_data(show_spinner="Cargando tablas de datos…")
def cargar_datos() -> dict[str, pd.DataFrame]:
    """
    Lee todos los CSV de la carpeta ``powerbi/`` y los devuelve en un
    diccionario cuyas claves son los nombres de tabla (sin extensión .csv).

    Si faltan archivos, muestra un aviso con la lista de CSV faltantes,
    indica que hay que ejecutar el notebook 07 y detiene la aplicación
    con ``st.stop()``.

    Retorna
    -------
    dict[str, pd.DataFrame]
        Diccionario con todas las tablas listas para consumir.
    """
    directorio = resolver_directorio_powerbi()

    # Comprobar que todos los archivos existen antes de leer ninguno
    faltantes = [
        nombre
        for nombre in TABLAS_REQUERIDAS
        if not (directorio / f"{nombre}.csv").exists()
    ]
    if faltantes:
        st.error(
            "Faltan los siguientes archivos CSV en la carpeta de datos:\n\n"
            + "\n".join(f"- `{nombre}.csv`" for nombre in faltantes)
            + "\n\nEjecuta el notebook **07_exportacion.ipynb** para generarlos."
        )
        st.stop()

    tablas: dict[str, pd.DataFrame] = {}
    for nombre in TABLAS_REQUERIDAS:
        tablas[nombre] = pd.read_csv(
            directorio / f"{nombre}.csv",
            encoding="utf-8-sig",
        )

    _convertir_fechas(tablas)
    _convertir_grupos(tablas)
    _convertir_numericos(tablas)
    _unir_estacion_anomalias(tablas)

    return tablas


# ---------------------------------------------------------------------------
# Conversiones internas
# ---------------------------------------------------------------------------

def _convertir_fechas(tablas: dict[str, pd.DataFrame]) -> None:
    """Convierte columnas de fecha a ``datetime64`` en las tablas indicadas."""
    mapa: dict[str, list[str]] = {
        "dim_fecha":           ["fecha"],
        "hechos_diario":       ["fecha"],
        "pronostico_horario":  ["Datetime", "fecha"],
        "pronostico_metricas": ["inicio_prueba", "fin_prueba"],
        "anomalias_dias":      ["fecha"],
        "anomalias_episodios": ["inicio", "fin"],
    }
    for nombre, columnas in mapa.items():
        df = tablas[nombre]
        for col in columnas:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")


def _convertir_grupos(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Convierte la columna ``grupo`` a entero nullable (``Int64``) en las
    tablas que pueden tenerla vacía.
    """
    tablas_con_grupo = [
        "hechos_diario",
        "pronostico_horario",
        "anomalias_dias",
        "curvas_tipo_dia",
        "mezcla_region_tipo",
        "dim_tipo_dia",
    ]
    for nombre in tablas_con_grupo:
        df = tablas[nombre]
        if "grupo" in df.columns:
            df["grupo"] = pd.to_numeric(df["grupo"], errors="coerce").astype("Int64")


def _convertir_numericos(tablas: dict[str, pd.DataFrame]) -> None:
    """Convierte a numérico las columnas que llegan como texto en cada tabla."""
    mapa: dict[str, list[str]] = {
        "pronostico_metricas":    ["MAE", "RMSE", "MAPE_pct", "MASE", "mejora_MAE_pct"],
        "pronostico_horario":     ["real", "prediccion", "residuo", "error_abs", "error_pct", "hora", "mes"],
        "anomalias_dias":         ["residuo_pct", "z_mod"],
        "silueta_k":              ["silueta", "k"],
        "dim_tipo_dia":           ["n_dias", "pct_dias", "hora_pico", "amplitud", "pct_fin_de_semana"],
        "mezcla_region_tipo":     ["pct_dias_total", "pct_dias_comun"],
        "indicadores_region":     ["razon_inv_ver_comun", "amplitud_diaria_comun",
                                   "razon_inv_ver", "amplitud_diaria"],
        "curvas_tipo_dia":        ["hora", "media", "inferior", "superior"],
        "patron_hora_dia":        ["hora", "MW_medio", "MW_rel_medio"],
        "patron_tipo_calendario": ["hora", "MW_rel_medio"],
        "tendencia_anual":        ["anio", "MW_medio"],
        "estacionalidad_mensual": ["mes", "MW_rel_medio"],
        "hechos_diario":          ["MW_medio"],
    }
    for nombre, columnas in mapa.items():
        df = tablas[nombre]
        for col in columnas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")


def _unir_estacion_anomalias(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Añade la columna ``estacion`` a ``anomalias_dias`` uniéndola desde
    ``dim_fecha``, si aún no está presente.
    """
    df_ad = tablas["anomalias_dias"]
    if "estacion" not in df_ad.columns:
        df_f = tablas["dim_fecha"][["fecha", "estacion"]].drop_duplicates()
        tablas["anomalias_dias"] = df_ad.merge(df_f, on="fecha", how="left")
