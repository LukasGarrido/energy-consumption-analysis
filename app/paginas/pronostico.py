"""
app/paginas/pronostico.py
Página 'Pronóstico': métricas de validación por pliegue, error desglosado
por hora, mes y tipo de dia, y comparación real vs. pronóstico.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app import filtros
from app.graficos import mostrar_grafico


# Número máximo de días a mostrar en el gráfico hora a hora para mantener
# la legibilidad cuando el rango de fechas es muy largo
_MAX_DIAS_DETALLE = 28


def mostrar(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """
    Renderiza la página de Pronóstico (modelo XGBoost de PJME).

    Incluye:
    - Tabla de métricas por pliegue de validación.
    - Barras del MAE por pliegue y modelo.
    - Selector MAE / MAPE para las barras de error por hora, mes y tipo.
    - Gráfico hora a hora de real vs. pronóstico en el periodo filtrado.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
    regiones : list[str]
    fecha_inicio : pd.Timestamp
    fecha_fin : pd.Timestamp
    estaciones : list[str]
    """
    st.header("Pronóstico de referencia (PJME — XGBoost)")

    met = tablas["pronostico_metricas"].copy()

    _tabla_metricas(met)
    st.divider()
    _barras_mae_pliegue(met)
    st.divider()
    _error_desglosado(tablas, fecha_inicio, fecha_fin, estaciones)
    st.divider()
    _real_vs_pronostico(tablas, fecha_inicio, fecha_fin, estaciones)


# ---------------------------------------------------------------------------
# Subgráficos
# ---------------------------------------------------------------------------

def _tabla_metricas(met: pd.DataFrame) -> None:
    """Tabla de MAE, RMSE, MAPE y MASE por pliegue y modelo."""
    st.subheader("Métricas por pliegue de validación")

    if filtros.verificar_vacio(met):
        return

    columnas = [
        c for c in [
            "pliegue", "modelo", "inicio_prueba", "fin_prueba",
            "MAE", "RMSE", "MAPE_pct", "MASE", "mejora_MAE_pct",
        ]
        if c in met.columns
    ]
    st.dataframe(met[columnas].sort_values(["pliegue", "modelo"]), hide_index=True)


def _barras_mae_pliegue(met: pd.DataFrame) -> None:
    """Barras del MAE por pliegue, agrupadas por modelo."""
    st.subheader("MAE por pliegue y modelo")

    if filtros.verificar_vacio(met):
        return

    fig = px.bar(
        met,
        x="pliegue",
        y="MAE",
        color="modelo",
        barmode="group",
        title="MAE por pliegue de validación",
        labels={"pliegue": "Pliegue", "MAE": "MAE (MW)", "modelo": "Modelo"},
    )
    mostrar_grafico(fig)
    st.caption(
        "Un MAE de XGBoost consistentemente menor que el modelo base "
        "confirma la utilidad del modelo para detectar lo normal y acotar los residuos."
    )
    st.caption("Este gráfico no responde al filtro de fecha.")


def _error_desglosado(
    tablas: dict[str, pd.DataFrame],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """Barras del error medio (MAE o MAPE) por hora, mes y tipo de dia."""
    st.subheader("Error por hora, mes y tipo de dia")

    metrica_sel = st.radio(
        "Métrica de error",
        options=["MAE", "MAPE_pct"],
        format_func=lambda m: "MAE (MW)" if m == "MAE" else "MAPE (%)",
        horizontal=True,
        key="metrica_error",
    )
    col_error = "error_abs" if metrica_sel == "MAE" else "error_pct"
    etiqueta = "MAE (MW)" if metrica_sel == "MAE" else "MAPE (%)"

    ph = filtros.por_fecha(
        tablas["pronostico_horario"].copy(), "fecha", fecha_inicio, fecha_fin
    )
    ph = filtros.por_estacion(ph, estaciones)

    if filtros.verificar_vacio(ph):
        return

    # Por hora
    st.markdown("**Por hora del dia**")
    err_hora = ph.groupby("hora")[col_error].mean().reset_index()
    if not filtros.verificar_vacio(err_hora):
        fig_h = px.bar(
            err_hora,
            x="hora",
            y=col_error,
            title=f"{etiqueta} medio por hora del dia",
            labels={"hora": "Hora de inicio (0–23)", col_error: etiqueta},
        )
        mostrar_grafico(fig_h)
        st.caption(
            "Las horas con mayor error suelen coincidir con transiciones de consumo "
            "(mañana y tarde), donde la variabilidad es mayor."
        )

    # Por mes
    st.markdown("**Por mes**")
    err_mes = ph.groupby("mes")[col_error].mean().reset_index()
    if not filtros.verificar_vacio(err_mes):
        fig_m = px.bar(
            err_mes,
            x="mes",
            y=col_error,
            title=f"{etiqueta} medio por mes",
            labels={"mes": "Mes (1–12)", col_error: etiqueta},
        )
        mostrar_grafico(fig_m)
        st.caption(
            "Los meses de verano e invierno suelen tener mayor error "
            "por la alta variabilidad de la temperatura."
        )

    # Por tipo de dia
    st.markdown("**Por tipo de dia**")
    ph_ng = ph.dropna(subset=["nombre_grupo"])
    err_tipo = ph_ng.groupby("nombre_grupo")[col_error].mean().reset_index()
    if not filtros.verificar_vacio(err_tipo):
        fig_t = px.bar(
            err_tipo,
            x="nombre_grupo",
            y=col_error,
            title=f"{etiqueta} medio por tipo de dia",
            labels={"nombre_grupo": "Tipo de dia", col_error: etiqueta},
        )
        mostrar_grafico(fig_t)
        st.caption(
            "Un error mayor en dias de verano o invierno indica que esos perfiles "
            "son más difíciles de pronosticar con variables de calendario."
        )


def _real_vs_pronostico(
    tablas: dict[str, pd.DataFrame],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """Gráfico hora a hora de consumo real vs. pronosticado en el periodo elegido."""
    st.subheader("Real vs. pronóstico en periodo seleccionado")

    ph = filtros.por_fecha(
        tablas["pronostico_horario"].copy(), "fecha", fecha_inicio, fecha_fin
    )
    ph = filtros.por_estacion(ph, estaciones)

    if filtros.verificar_vacio(ph):
        return

    # Limitar a las primeras N semanas si el rango es muy largo
    if ph["Datetime"].nunique() > 24 * _MAX_DIAS_DETALLE:
        fecha_tope = ph["Datetime"].min() + pd.Timedelta(days=_MAX_DIAS_DETALLE)
        ph = ph[ph["Datetime"] <= fecha_tope].copy()
        st.caption(
            f"Mostrando solo los primeros {_MAX_DIAS_DETALLE} dias del periodo "
            "para mantener la legibilidad."
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ph["Datetime"],
            y=ph["real"],
            mode="lines",
            name="Real (MW)",
            line=dict(color="#0072B2", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ph["Datetime"],
            y=ph["prediccion"],
            mode="lines",
            name="Pronóstico (MW)",
            line=dict(color="#E69F00", width=1.5, dash="dash"),
        )
    )
    fig.update_layout(
        title="Real vs. pronóstico hora a hora — PJME",
        xaxis_title="Fecha y hora",
        yaxis_title="Consumo (MW)",
        hovermode="x unified",
    )
    mostrar_grafico(fig)
    st.caption(
        "El pronóstico captura el ritmo diario, pero los picos extremos suelen quedar "
        "subestimados o sobreestimados: esos son los dias de mayor interés para el análisis."
    )
