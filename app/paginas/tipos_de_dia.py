"""
app/paginas/tipos_de_dia.py
Página 'Tipos de dia': curvas medias con bandas de confianza, calendario
visual de tipos, barras de frecuencia y curva de silueta.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app import filtros
from app.graficos import color_grupo, hex_a_rgba, mapa_colores_grupos, mostrar_grafico


def mostrar(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """
    Renderiza la página de Tipos de dia.

    Incluye cuatro visualizaciones:
    - Curvas medias con banda inferior-superior por tipo de dia.
    - Calendario de color (año × día del año, color por tipo).
    - Barras del porcentaje de dias por tipo.
    - Curva de silueta frente a k con umbrales de referencia.
    - Tabla resumen de ``dim_tipo_dia``.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
    regiones : list[str]
    fecha_inicio : pd.Timestamp
    fecha_fin : pd.Timestamp
    estaciones : list[str]
    """
    st.header("Tipos de dia")

    _curvas_medias(tablas)
    st.divider()
    _calendario_de_color(tablas, regiones, fecha_inicio, fecha_fin, estaciones)
    st.divider()
    _barras_frecuencia(tablas)
    st.divider()
    _curva_silueta(tablas)
    st.divider()
    _tabla_resumen(tablas)


# Subgráficos
def _curvas_medias(tablas: dict[str, pd.DataFrame]) -> None:
    """Curvas medias de consumo relativo con banda inter-percentil."""
    st.subheader("Curvas medias de consumo relativo por tipo de dia")

    ctd = tablas["curvas_tipo_dia"].copy()

    if filtros.verificar_vacio(ctd):
        return

    grupos = sorted(ctd["grupo"].dropna().unique().tolist())
    fig = go.Figure()

    for g in grupos:
        nombre = ctd[ctd["grupo"] == g]["nombre_grupo"].iloc[0]
        sub = ctd[ctd["grupo"] == g].sort_values("hora")
        color = color_grupo(g)

        # Banda de confianza (toself rellena el área entre superior e inferior)
        fig.add_trace(
            go.Scatter(
                x=list(sub["hora"]) + list(sub["hora"])[::-1],
                y=list(sub["superior"]) + list(sub["inferior"])[::-1],
                fill="toself",
                fillcolor=hex_a_rgba(color, 0.15),
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                name=nombre,
                hoverinfo="skip",
            )
        )
        # Curva de la media
        fig.add_trace(
            go.Scatter(
                x=sub["hora"],
                y=sub["media"],
                mode="lines",
                name=nombre,
                line=dict(color=color, width=2),
            )
        )

    fig.update_layout(
        title=f"Curvas medias por tipo de dia ({len(grupos)} grupos)",
        xaxis_title="Hora de inicio (0–23)",
        yaxis_title="Consumo relativo",
        hovermode="x unified",
    )
    mostrar_grafico(fig)
    st.caption(
        "La banda muestra el intervalo entre los percentiles 10 y 90. "
        "Un tipo de dia con banda estrecha tiene un perfil muy regular."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _calendario_de_color(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """Dispersión año × día-del-año coloreada por tipo de dia."""
    st.subheader("Calendario de tipos de dia")

    if not regiones:
        st.info("Sin datos con estos filtros.")
        return

    region_sel = st.selectbox(
        "Región para el calendario",
        options=sorted(regiones),
        key="cal_region",
    )

    hd = tablas["hechos_diario"].copy()
    hd = hd[hd["region"] == region_sel].copy()
    hd = filtros.por_fecha(hd, "fecha", fecha_inicio, fecha_fin)
    hd = filtros.por_estacion(hd, estaciones)
    hd = hd.dropna(subset=["grupo"])

    if filtros.verificar_vacio(hd):
        return

    hd["anio"] = hd["fecha"].dt.year
    hd["dia_del_anio"] = hd["fecha"].dt.dayofyear

    mapa_colores = mapa_colores_grupos(hd)

    fig = px.scatter(
        hd,
        x="dia_del_anio",
        y="anio",
        color="nombre_grupo",
        color_discrete_map=mapa_colores,
        custom_data=["fecha", "nombre_grupo"],
        title=f"Distribución de tipos de dia — {region_sel}",
        labels={
            "dia_del_anio": "Día del año",
            "anio": "Año",
            "nombre_grupo": "Tipo de dia",
        },
    )
    fig.update_traces(
        marker=dict(size=4, symbol="square"),
        hovertemplate=(
            "Fecha: %{customdata[0]|%Y-%m-%d}<br>"
            "Tipo: %{customdata[1]}<extra></extra>"
        ),
    )
    fig.update_layout(hovermode="closest")
    mostrar_grafico(fig)
    st.caption(
        "Cada punto es un dia. El color indica el tipo de dia según el agrupamiento. "
        "Se pueden apreciar la estacionalidad anual y cambios históricos de régimen."
    )


def _barras_frecuencia(tablas: dict[str, pd.DataFrame]) -> None:
    """Barras del porcentaje global de dias por tipo."""
    st.subheader("Frecuencia de cada tipo de dia")

    dtd = tablas["dim_tipo_dia"].copy()
    dtd = dtd.dropna(subset=["grupo"]).sort_values("grupo")

    if filtros.verificar_vacio(dtd):
        return

    mapa_colores = mapa_colores_grupos(dtd)

    fig = px.bar(
        dtd,
        x="nombre_grupo",
        y="pct_dias",
        color="nombre_grupo",
        color_discrete_map=mapa_colores,
        title="Porcentaje de dias por tipo",
        labels={
            "nombre_grupo": "Tipo de dia",
            "pct_dias": "Porcentaje de dias (%)",
        },
    )
    fig.update_layout(showlegend=False)
    mostrar_grafico(fig)
    st.caption(
        "Un tipo con un porcentaje muy bajo podría no ser representativo "
        "o indicar condiciones climáticas excepcionales."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _curva_silueta(tablas: dict[str, pd.DataFrame]) -> None:
    """Línea del coeficiente de silueta frente a k con umbrales de referencia."""
    st.subheader("Calidad del agrupamiento: coeficiente de silueta")

    sk = tablas["silueta_k"].copy()

    if filtros.verificar_vacio(sk):
        return

    fig = px.line(
        sk,
        x="k",
        y="silueta",
        color="metodo",
        markers=True,
        title="Coeficiente de silueta por número de grupos (k)",
        labels={
            "k": "Número de grupos (k)",
            "silueta": "Coeficiente de silueta",
            "metodo": "Método",
        },
    )
    fig.add_hline(
        y=0.51,
        line_dash="dash",
        line_color="green",
        annotation_text="Estructura razonable (0.51)",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=0.26,
        line_dash="dash",
        line_color="orange",
        annotation_text="Estructura débil (0.26)",
        annotation_position="bottom right",
    )
    mostrar_grafico(fig)
    st.caption(
        "Un coeficiente superior a 0.51 indica separación razonable entre grupos; "
        "entre 0.26 y 0.51 la estructura es débil pero interpretable."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _tabla_resumen(tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla con las métricas descriptivas de cada tipo de dia."""
    st.subheader("Resumen de tipos de dia")

    dtd = tablas["dim_tipo_dia"].copy()

    if filtros.verificar_vacio(dtd):
        return

    columnas = [
        c for c in [
            "grupo", "nombre_grupo", "n_dias", "pct_dias",
            "hora_pico", "amplitud", "pct_fin_de_semana", "estacion_dominante",
        ]
        if c in dtd.columns
    ]
    st.dataframe(dtd[columnas].sort_values("grupo"), hide_index=True)
