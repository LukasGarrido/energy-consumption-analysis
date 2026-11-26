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
from app.estilos import renderizar_hero_banner


def mostrar(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Renderiza el módulo del estudio de comparativa entre regiones.
    """
    renderizar_hero_banner("Comparativa Estructural entre Regiones")

    regiones, _, _, _ = filtros.selector_filtros_modulo(
        tablas, "regiones", con_fechas=False
    )

    modo = st.radio(
        "Periodo de referencia",
        options=["Historial completo", "Periodo comun"],
        horizontal=True,
        key="modo_periodo",
    )
    col_pct = "pct_dias_total" if modo == "Historial completo" else "pct_dias_comun"
    if col_pct not in tablas["mezcla_region_tipo"].columns:
        st.error(
            f"`mezcla_region_tipo.csv` no tiene la columna `{col_pct}`. "
            "Ejecuta `python src/export.py` para actualizar las tablas."
        )
        return

    _barras_apiladas(tablas, regiones, col_pct, modo)
    st.divider()
    _dispersion_indicadores(tablas, regiones)


# Subgráficos
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

    # Las regiones fuera del periodo común no tienen porcentaje en esa columna
    sin_datos = sorted(mrt.loc[mrt[col_pct].isna(), "region"].unique())
    if sin_datos:
        st.caption(
            f"Fuera del periodo común (no están entre las 10 regiones vigentes): "
            f"{', '.join(sin_datos)}."
        )
        mrt = mrt[mrt[col_pct].notna()]
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

    col_x = "razon_inv_ver_comun" if "razon_inv_ver_comun" in ind.columns and ind["razon_inv_ver_comun"].notna().any() else "razon_inv_ver"
    col_y = "amplitud_diaria_comun" if "amplitud_diaria_comun" in ind.columns and ind["amplitud_diaria_comun"].notna().any() else "amplitud_diaria"

    subtitulo_periodo = "periodo comun" if col_x == "razon_inv_ver_comun" else "historial completo"

    fig = px.scatter(
        ind,
        x=col_x,
        y=col_y,
        text="region",
        color="region",
        color_discrete_map=COLORES_REGION,
        title=f"Razón invierno/verano vs. amplitud diaria media ({subtitulo_periodo})",
        labels={
            col_x: "Razón consumo invierno / verano",
            col_y: "Amplitud diaria relativa media",
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
