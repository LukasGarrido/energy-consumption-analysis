"""
app/paginas/anomalias.py
Página 'Anomalias': línea de tiempo de residuos con episodios sombreados,
ranking de dias atípicos, tabla de episodios históricos y caso hora a hora.

Solo hay datos de PJME; si esa región no está seleccionada se muestra un aviso.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import filtros
from app.graficos import mostrar_grafico
from app.config import UMBRAL_Z_DEFECTO


def mostrar(
    tablas: dict[str, pd.DataFrame],
    regiones: list[str],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
) -> None:
    """
    Renderiza la página de Anomalias.

    Incluye:
    - Deslizador de umbral que recalcula ``es_atipico`` en la vista.
    - Línea de tiempo de ``residuo_pct`` con atípicos resaltados.
    - Lista de los 20 dias con mayor |z_mod|.
    - Tabla de episodios históricos documentados.
    - Selector de dia atípico para ver real vs. pronóstico hora a hora.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
    regiones : list[str]
    fecha_inicio : pd.Timestamp
    fecha_fin : pd.Timestamp
    estaciones : list[str]
    """
    st.header("Anomalias y dias atipicos")

    if "PJME" not in regiones:
        st.info(
            "La detección de anomalías solo está disponible para la región **PJME**. "
            "Selecciona PJME en el filtro de región para ver esta página."
        )
        return

    umbral = st.slider(
        "Umbral del z modificado para marcar dias atipicos",
        min_value=1.0,
        max_value=6.0,
        value=UMBRAL_Z_DEFECTO,
        step=0.1,
        key="umbral_z",
    )

    ad = _preparar_anomalias(tablas, fecha_inicio, fecha_fin, estaciones, umbral)

    if filtros.verificar_vacio(ad):
        return

    _linea_de_tiempo(ad, tablas)
    st.divider()
    _ranking_atipicos(ad)
    st.divider()
    _tabla_episodios(tablas)
    st.divider()
    _caso_hora_a_hora(ad, tablas)


# Helpers internos
def _preparar_anomalias(
    tablas: dict[str, pd.DataFrame],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
    umbral: float,
) -> pd.DataFrame:
    """
    Filtra ``anomalias_dias`` para PJME y recalcula ``es_atipico`` con el
    umbral del deslizador. Añade la columna ``color_punto`` para el gráfico.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
    fecha_inicio : pd.Timestamp
    fecha_fin : pd.Timestamp
    estaciones : list[str]
    umbral : float
        Valor del deslizador de la interfaz.

    Retorna
    -------
    pd.DataFrame
    """
    ad = tablas["anomalias_dias"].copy()
    ad = ad[ad["region"] == "PJME"].copy()
    ad = filtros.por_fecha(ad, "fecha", fecha_inicio, fecha_fin)
    ad = filtros.por_estacion(ad, estaciones)

    # Recalcular es_atipico en la vista (no se escribe en disco)
    ad["es_atipico"] = ad["z_mod"].abs() > umbral

    ad["color_punto"] = ad.apply(
        lambda r: (
            "#E69F00" if r["es_atipico"] and r.get("direccion", "") == "alta"
            else "#009E73" if r["es_atipico"] and r.get("direccion", "") == "baja"
            else "#CCCCCC"
        ),
        axis=1,
    )
    return ad


def _linea_de_tiempo(
    ad: pd.DataFrame,
    tablas: dict[str, pd.DataFrame],
) -> None:
    """Línea de tiempo del residuo diario con atípicos resaltados y episodios sombreados."""
    st.subheader("Residuo diario de PJME (%)")

    ep = tablas["anomalias_episodios"]
    ep = ep[ep["region"] == "PJME"].copy()

    fig = go.Figure()

    # Sombreado de episodios históricos
    for _, row in ep.iterrows():
        if pd.notna(row.get("inicio")) and pd.notna(row.get("fin")):
            fig.add_vrect(
                x0=row["inicio"],
                x1=row["fin"],
                fillcolor="rgba(100,100,200,0.12)",
                line_width=0,
                annotation_text=str(row["episodio"])[:30],
                annotation_position="top left",
                annotation=dict(font_size=9),
            )

    # Serie de residuos
    fig.add_trace(
        go.Scatter(
            x=ad["fecha"],
            y=ad["residuo_pct"],
            mode="lines",
            name="Residuo (%)",
            line=dict(color="#AAAAAA", width=1),
        )
    )

    # Puntos atípicos
    at = ad[ad["es_atipico"]]
    if not at.empty:
        fig.add_trace(
            go.Scatter(
                x=at["fecha"],
                y=at["residuo_pct"],
                mode="markers",
                name="Atipico",
                marker=dict(
                    color=at["color_punto"].tolist(),
                    size=8,
                    line=dict(color="black", width=0.5),
                ),
                customdata=at[["nombre_grupo", "z_mod"]].values,
                hovertemplate=(
                    "Fecha: %{x|%Y-%m-%d}<br>"
                    "Residuo: %{y:.1f}%<br>"
                    "Tipo: %{customdata[0]}<br>"
                    "z_mod: %{customdata[1]:.2f}<extra></extra>"
                ),
            )
        )

    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(
        title="Residuo diario del pronóstico — PJME (naranja: alto, verde: bajo)",
        xaxis_title="Fecha",
        yaxis_title="Residuo (%)",
        hovermode="x unified",
    )
    mostrar_grafico(fig)
    st.caption(
        "Las regiones sombreadas corresponden a episodios históricos documentados. "
        "Un residuo positivo indica que el consumo real superó al pronosticado."
    )


def _ranking_atipicos(ad: pd.DataFrame) -> None:
    """Tabla con los 20 dias con mayor valor absoluto de z_mod."""
    st.subheader("Dias atipicos con mayor z modificado")

    at = ad[ad["es_atipico"]].sort_values("z_mod", key=abs, ascending=False).head(20)

    if at.empty:
        st.info("No hay dias atipicos con el umbral actual.")
        return

    columnas = [
        c for c in ["fecha", "residuo_pct", "z_mod", "direccion", "nombre_grupo"]
        if c in at.columns
    ]
    st.dataframe(at[columnas], hide_index=True)


def _tabla_episodios(tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla de episodios históricos documentados con estado, fuente y verificación."""
    st.subheader("Episodios históricos documentados")

    ep = tablas["anomalias_episodios"]
    ep = ep[ep["region"] == "PJME"].copy()

    if ep.empty:
        st.info("Sin episodios registrados.")
        return

    columnas = [
        c for c in [
            "episodio", "inicio", "fin", "tipo", "direccion_esperada",
            "estado", "fuente", "verificado", "coincide_direccion",
        ]
        if c in ep.columns
    ]
    st.dataframe(ep[columnas], hide_index=True)


def _caso_hora_a_hora(
    ad: pd.DataFrame,
    tablas: dict[str, pd.DataFrame],
) -> None:
    """Selector de dia atípico y gráfico hora a hora en ventana de ±3 dias."""
    st.subheader("Caso hora a hora: real vs. pronostico")

    at = ad[ad["es_atipico"]]

    if at.empty:
        st.info("No hay dias atipicos para analizar hora a hora.")
        return

    fechas_atipicas = sorted(at["fecha"].dt.date.unique().tolist())
    fecha_sel = st.selectbox(
        "Elegir un dia atipico",
        options=fechas_atipicas,
        format_func=str,
        key="fecha_atipica_sel",
    )

    if fecha_sel is None:
        return

    fecha_ts = pd.Timestamp(fecha_sel)
    ph = tablas["pronostico_horario"].copy()
    ph = ph[ph["region"] == "PJME"].copy()
    ph = ph[
        (ph["fecha"] >= fecha_ts - pd.Timedelta(days=3))
        & (ph["fecha"] <= fecha_ts + pd.Timedelta(days=3))
    ].copy()

    if filtros.verificar_vacio(ph):
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ph["Datetime"],
            y=ph["real"],
            mode="lines",
            name="Real (MW)",
            line=dict(color="#0072B2", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ph["Datetime"],
            y=ph["prediccion"],
            mode="lines",
            name="Pronóstico (MW)",
            line=dict(color="#E69F00", width=2, dash="dash"),
        )
    )
    fig.add_vrect(
        x0=fecha_ts,
        x1=fecha_ts + pd.Timedelta(days=1),
        fillcolor="rgba(213,94,0,0.15)",
        line_width=0,
        annotation_text="Dia atipico",
        annotation_position="top left",
    )
    fig.update_layout(
        title=f"Real vs. pronóstico — ventana ±3 dias alrededor de {fecha_sel}",
        xaxis_title="Fecha y hora",
        yaxis_title="Consumo (MW)",
        hovermode="x unified",
    )
    mostrar_grafico(fig)
    st.caption(
        "La diferencia entre la línea azul (real) y la naranja discontinua (pronóstico) "
        "muestra en qué horas fue mayor el desvío."
    )
