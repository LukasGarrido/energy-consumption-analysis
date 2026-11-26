"""
app/paginas/resumen.py
Módulo 'Resumen': tarjetas de indicadores clave y tendencia anual por región.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from app.config import COLORES_REGION, UMBRAL_Z_DEFECTO
from app import filtros
from app.graficos import mostrar_grafico
from app.estilos import renderizar_hero_banner


def mostrar(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Renderiza el módulo del estudio de Resumen.
    """
    renderizar_hero_banner("Resumen Ejecutivo y KPIs")

    regiones, fecha_inicio, fecha_fin, estaciones = filtros.selector_filtros_modulo(
        tablas, "resumen", con_fechas=True
    )

    # Datos filtrados para las tarjetas
    hd = filtros.por_region(tablas["hechos_diario"], regiones)
    hd = filtros.por_fecha(hd, "fecha", fecha_inicio, fecha_fin)
    hd = filtros.por_estacion(hd, estaciones)

    metricas_xgb = tablas["pronostico_metricas"]
    metricas_xgb = metricas_xgb[metricas_xgb["modelo"] == "XGBoost"]

    n_tipos = tablas["dim_tipo_dia"]["grupo"].nunique()
    # Solo hay pronóstico de PJME: sin esa región no se muestran sus métricas
    hay_pjme = "PJME" in regiones
    mae_medio = metricas_xgb["MAE"].mean() if hay_pjme else float("nan")
    mase_medio = metricas_xgb["MASE"].mean() if hay_pjme else float("nan")

    col_mw = "MW_medio" if "MW_medio" in hd.columns else ("MW_medio_dia" if "MW_medio_dia" in hd.columns else None)
    consumo_str = (
        f"{hd[col_mw].mean():,.0f}" if (not hd.empty and col_mw is not None) else "—"
    )
    mae_str = f"{mae_medio:,.0f}" if pd.notna(mae_medio) else "—"
    mase_str = f"{mase_medio:.3f}" if pd.notna(mase_medio) else "—"

    # Dos filas de tres: en una sola fila los valores se cortan
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col1.metric("Regiones", len(regiones))
    col2.metric("Dias filtrados", f"{hd['fecha'].nunique():,}")
    col3.metric("Consumo medio (MW)", consumo_str)
    col4.metric("Tipos de dia", n_tipos)
    ayuda = "Media de XGBoost en los pliegues de validación, solo para PJME."
    col5.metric("MAE PJME (MW)", mae_str, help=ayuda)
    col6.metric("MASE PJME", mase_str, help=ayuda)

    # Aviso de dias atípicos de PJME
    if "PJME" in regiones:
        ad = tablas["anomalias_dias"]
        ad = ad[ad["region"] == "PJME"].copy()
        ad = filtros.por_fecha(ad, "fecha", fecha_inicio, fecha_fin)
        ad = filtros.por_estacion(ad, estaciones)
        n_atipicos = int((ad["z_mod"].abs() > UMBRAL_Z_DEFECTO).sum())
        st.info(
            f"PJME: **{n_atipicos}** dias atipicos en el periodo y las estaciones elegidas "
            f"(|z_mod| > {UMBRAL_Z_DEFECTO})."
        )

    st.divider()

    # Tendencia anual (solo años completos)
    st.subheader("Tendencia anual del consumo medio")

    if "completo" not in tablas["tendencia_anual"].columns:
        st.error(
            "`tendencia_anual.csv` no tiene la columna `completo`. "
            "Ejecuta `python src/export.py` para actualizar las tablas."
        )
        return

    tend = filtros.por_region(tablas["tendencia_anual"], regiones)
    tend = tend[tend["completo"] == "Sí"].copy()

    if filtros.verificar_vacio(tend):
        return

    fig = px.line(
        tend,
        x="anio",
        y="MW_medio",
        color="region",
        color_discrete_map=COLORES_REGION,
        markers=True,
        title="Consumo anual medio por región (solo años completos)",
        labels={
            "anio": "Año",
            "MW_medio": "Consumo medio (MW)",
            "region": "Región",
        },
    )
    # Un punto cada vez: las regiones cubren años distintos y un cuadro unificado
    # mezclaría valores de otros años
    fig.update_layout(hovermode="closest")
    mostrar_grafico(fig)
    st.caption(
        "Observar si la tendencia es estable, creciente o decreciente. "
        "Solo se incluyen años con datos completos para evitar sesgos de borde."
    )
    st.caption("Este gráfico no responde a los filtros de estación ni de fecha.")
