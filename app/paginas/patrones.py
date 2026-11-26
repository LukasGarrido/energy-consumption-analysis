"""
app/paginas/patrones.py
Página 'Patrones': mapa de calor hora x día, curvas por tipo de calendario
y estacionalidad mensual del consumo.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.config import COLORES_REGION
from app import filtros
from app.graficos import mostrar_grafico
from app.estilos import renderizar_hero_banner


# Orden canónico de días de la semana para el mapa de calor
_ORDEN_DIAS = [
    "Lunes", "Martes", "Miércoles", "Jueves",
    "Viernes", "Sábado", "Domingo",
]

# Orden canónico de meses para la estacionalidad
_ORDEN_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# Rango fijo de la escala de color del mapa de calor (igual para todas las regiones)
_HEATMAP_ZMIN = 0.75
_HEATMAP_ZMAX = 1.25


# Color y trazo de cada tipo de calendario (Okabe-Ito)
_ESTILO_CALENDARIO: dict[str, tuple[str, str]] = {
    "Laborable": ("#0072B2", "solid"),
    "Fin de semana": ("#E69F00", "dash"),
    "Festivo": ("#CC79A7", "dot"),
}

# Rejilla de paneles por región
_COLUMNAS_PANELES = 4
_ALTO_PANEL = 220
_ALTO_CABECERA = 140


def mostrar(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Renderiza el módulo del estudio de Patrones.
    """
    renderizar_hero_banner("Patrones de Consumo y Estacionalidad")

    regiones, _, _, estaciones = filtros.selector_filtros_modulo(
        tablas, "patrones", con_fechas=False
    )

    _mapa_de_calor(tablas, regiones, estaciones)
    st.divider()
    _curvas_tipo_calendario(tablas, regiones, estaciones)
    st.divider()
    _estacionalidad_mensual(tablas, regiones)


# Subgráficos
def _mapa_de_calor(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    estaciones: list[str],
) -> None:
    """Mapa de calor 7 × 24 de MW_rel_medio para una región elegida."""
    st.subheader("Mapa de calor: hora del dia x dia de la semana")

    if not regiones:
        st.info("Sin datos con estos filtros.")
        return

    filtros.descartar_si_no_es_opcion("heatmap_region", sorted(regiones))
    region_sel = st.selectbox(
        "Región para el mapa de calor",
        options=sorted(regiones),
        key="heatmap_region",
    )

    phd = tablas["patron_hora_dia"]
    phd = phd[phd["region"] == region_sel].copy()
    phd = filtros.por_estacion(phd, estaciones)

    if filtros.verificar_vacio(phd):
        return

    # Pivote: filas = dia_semana, columnas = hora
    phd_pivot = (
        phd.groupby(["nombre_dia", "hora"])["MW_rel_medio"]
        .mean()
        .reset_index()
        .pivot(index="nombre_dia", columns="hora", values="MW_rel_medio")
    )
    dias_presentes = [d for d in _ORDEN_DIAS if d in phd_pivot.index]
    phd_pivot = phd_pivot.reindex(dias_presentes)

    fig = go.Figure(
        go.Heatmap(
            z=phd_pivot.values,
            x=[str(h) for h in phd_pivot.columns],
            y=phd_pivot.index.tolist(),
            colorscale="Blues",
            zmin=_HEATMAP_ZMIN,
            zmax=_HEATMAP_ZMAX,
            colorbar=dict(title="MW relativo"),
        )
    )
    fig.update_layout(
        title=f"Consumo relativo por hora y día — {region_sel}",
        xaxis_title="Hora de inicio (0–23)",
        yaxis_title="Día de la semana",
    )
    mostrar_grafico(fig)
    st.caption(
        "Valores > 1 indican consumo superior al promedio de la región en todo su historial. "
        "La escala es fija e igual para todas las regiones, lo que permite comparar directamente."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _curvas_tipo_calendario(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    estaciones: list[str],
) -> None:
    """
    Un panel por región con el perfil diario de cada tipo de calendario
    (laborable, fin de semana, festivo), promediando las estaciones elegidas.
    """
    st.subheader("Perfil diario por tipo de calendario")

    ptc = filtros.por_region(tablas["patron_tipo_calendario"], regiones)
    ptc = filtros.por_estacion(ptc, estaciones)

    if filtros.verificar_vacio(ptc):
        return

    # Una sola curva por región y tipo: la tabla trae una fila por estación
    ptc = ptc.groupby(
        ["region", "tipo_calendario", "hora"], as_index=False
    )["MW_rel_medio"].mean()

    n_regiones = ptc["region"].nunique()
    columnas = min(_COLUMNAS_PANELES, n_regiones)
    n_filas = -(-n_regiones // columnas)

    fig = px.line(
        ptc,
        x="hora",
        y="MW_rel_medio",
        color="tipo_calendario",
        line_dash="tipo_calendario",
        facet_col="region",
        facet_col_wrap=columnas,
        category_orders={
            "region": sorted(ptc["region"].unique()),
            "tipo_calendario": list(_ESTILO_CALENDARIO),
        },
        color_discrete_map={t: c for t, (c, _) in _ESTILO_CALENDARIO.items()},
        line_dash_map={t: d for t, (_, d) in _ESTILO_CALENDARIO.items()},
        title="Consumo relativo medio por hora según tipo de calendario",
        labels={
            "hora": "Hora de inicio",
            "MW_rel_medio": "Consumo relativo",
            "region": "Región",
            "tipo_calendario": "Tipo",
        },
        height=_ALTO_CABECERA + _ALTO_PANEL * n_filas,
    )
    # El título de cada panel es solo el nombre de la región
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(hovermode="x unified")
    mostrar_grafico(fig)
    st.caption(
        "Cada panel es una región y todos comparten escala. Comparar la forma de la curva "
        "entre días laborables, fines de semana y festivos revela diferencias estructurales "
        "en el perfil de demanda. Las curvas son el promedio simple de las estaciones elegidas."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _estacionalidad_mensual(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
) -> None:
    """Líneas de consumo relativo medio por mes del año."""
    st.subheader("Estacionalidad mensual del consumo")

    em = filtros.por_region(tablas["estacionalidad_mensual"], regiones)

    if filtros.verificar_vacio(em):
        return

    em["nombre_mes"] = pd.Categorical(
        em["nombre_mes"], categories=_ORDEN_MESES, ordered=True
    )
    em = em.sort_values(["nombre_mes", "region"])

    fig = px.line(
        em,
        x="nombre_mes",
        y="MW_rel_medio",
        color="region",
        color_discrete_map=COLORES_REGION,
        markers=True,
        title="Consumo relativo medio por mes",
        labels={
            "nombre_mes": "Mes",
            "MW_rel_medio": "Consumo relativo",
            "region": "Región",
        },
    )
    fig.update_layout(hovermode="x unified")
    mostrar_grafico(fig)
    st.caption(
        "Un pico en julio-agosto señala demanda estival por refrigeración; "
        "uno en enero indica calefacción eléctrica dominante."
    )
    st.caption("Este gráfico no responde a los filtros de estación ni de fecha.")
