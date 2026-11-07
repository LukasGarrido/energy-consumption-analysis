"""
app/paginas/regiones.py
Página 'Regiones': comparativa entre regiones mediante barras apiladas al
100 % y dispersión de indicadores estructurales.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.config import COLORES_REGION
from app import filtros
from app.graficos import color_grupo, mostrar_grafico


def mostrar(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    estaciones: list[str],
) -> None:
    """
    Renderiza la página de comparativa entre regiones.

    Incluye:
    - Interruptor entre historial completo y periodo comun.
    - Barras apiladas al 100 % ordenadas por el peso del grupo 1.
    - Dispersión de razón invierno/verano frente a amplitud diaria.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
    regiones : list[str]
    estaciones : list[str]
        Parámetro recibido por simetría con las demás páginas;
        ninguna tabla de esta página filtra por estación porque los
        indicadores son promedios del periodo completo o comun.
    """
    st.header("Comparativa entre regiones")

    modo = st.radio(
        "Periodo de referencia",
        options=["Historial completo", "Periodo comun"],
        horizontal=True,
        key="modo_periodo",
    )
    col_pct = "pct_dias_total" if modo == "Historial completo" else "pct_dias_comun"

    _barras_apiladas(tablas, regiones, col_pct, modo)
    st.divider()
    _dispersion_indicadores(tablas, regiones)


# ---------------------------------------------------------------------------
# Subgráficos
# ---------------------------------------------------------------------------

def _barras_apiladas(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    col_pct: str,
    modo: str,
) -> None:
    """Barras apiladas al 100 % de la mezcla de tipos de dia por región."""
    st.subheader("Mezcla de tipos de dia por región")

    mrt = filtros.por_region(tablas["mezcla_region_tipo"], regiones)

    if filtros.verificar_vacio(mrt):
        return

    # Ordenar regiones de mayor a menor peso del grupo 1
    orden_regiones: list[str] = (
        mrt[mrt["grupo"] == 1]
        .sort_values(col_pct, ascending=False)["region"]
        .tolist()
    )
    # Incluir regiones sin grupo 1
    for r in mrt["region"].unique():
        if r not in orden_regiones:
            orden_regiones.append(r)

    grupos = sorted(mrt["grupo"].dropna().unique().tolist())

    fig = go.Figure()
    for g in grupos:
        sub = mrt[mrt["grupo"] == g].set_index("region")
        nombre = sub["nombre_grupo"].iloc[0] if not sub.empty else f"G{g}"
        valores = [
            float(sub.loc[r, col_pct]) if r in sub.index else 0.0
            for r in orden_regiones
        ]
        fig.add_trace(
            go.Bar(
                x=orden_regiones,
                y=valores,
                name=nombre,
                marker_color=color_grupo(g),
            )
        )

    fig.update_layout(
        barmode="stack",
        title=f"Mezcla de tipos de dia al 100 % — {modo}",
        xaxis_title="Región",
        yaxis_title="Porcentaje de dias (%)",
        legend_title="Tipo de dia",
        hovermode="x unified",
    )
    mostrar_grafico(fig)
    st.caption(
        "Las regiones están ordenadas de mayor a menor predominio del tipo G1. "
        "Diferencias grandes entre regiones revelan distintos perfiles estructurales de demanda."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _dispersion_indicadores(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
) -> None:
    """Dispersión de razón invierno/verano frente a amplitud diaria media."""
    st.subheader("Indicadores por región: razón invierno/verano vs. amplitud diaria")

    ind = filtros.por_region(tablas["indicadores_region"], regiones)

    if filtros.verificar_vacio(ind):
        return

    fig = px.scatter(
        ind,
        x="razon_inv_ver_comun",
        y="amplitud_diaria_comun",
        text="region",
        color="region",
        color_discrete_map=COLORES_REGION,
        title="Razón invierno/verano vs. amplitud diaria media (periodo comun)",
        labels={
            "razon_inv_ver_comun": "Razón consumo invierno / verano",
            "amplitud_diaria_comun": "Amplitud diaria relativa media",
            "region": "Región",
        },
    )
    fig.update_traces(textposition="top center", marker=dict(size=10))
    fig.update_layout(showlegend=False)
    mostrar_grafico(fig)
    st.caption(
        "Regiones con razón > 1 tienen mayor consumo en invierno (calefacción eléctrica); "
        "con razón < 1, mayor consumo en verano (refrigeración). "
        "Una amplitud alta indica perfiles diarios más pronunciados."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")
