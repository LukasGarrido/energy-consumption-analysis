"""
app/paginas/anomalias.py
Página 'Anomalias': línea de tiempo de residuos con episodios sombreados,
ranking de dias atípicos, tabla de episodios históricos y caso hora a hora.

Solo hay datos de PJME; si esa región no está seleccionada se muestra un aviso.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import filtros
from app.graficos import mostrar_grafico
from app.config import UMBRAL_Z_DEFECTO
from app.estilos import renderizar_hero_banner


# Color de los dias atípicos según el signo del residuo (Okabe-Ito)
_COLORES_DIRECCION: dict[str, str] = {"alta": "#E69F00", "baja": "#009E73"}

# Fracción del eje de fechas que debe separar dos números de episodio de una fila
_SEPARACION_ETIQUETAS = 0.045

# Cuadro emergente de la línea de tiempo
_DATOS_EMERGENTE: list[str] = ["nombre_grupo", "z_mod"]
_PLANTILLA_EMERGENTE = (
    "Fecha: %{x|%Y-%m-%d}<br>"
    "Residuo: %{y:.1f}%<br>"
    "Tipo: %{customdata[0]}<br>"
    "z_mod: %{customdata[1]:.2f}<extra></extra>"
)


def mostrar(tablas: dict[str, pd.DataFrame]) -> None:
    """
    Renderiza el módulo del estudio de Anomalias.
    """
    renderizar_hero_banner("Deteccion de Anomalias y Dias Atipicos")

    regiones, fecha_inicio, fecha_fin, estaciones = filtros.selector_filtros_modulo(
        tablas, "anomalias", con_fechas=True
    )

    if "PJME" not in regiones:
        st.info(
            "La detección de anomalías solo está disponible para la región **PJME**. "
            "Selecciona PJME en el selector de regiones para ver este módulo."
        )
        return

    st.session_state.setdefault("umbral_z", UMBRAL_Z_DEFECTO)
    umbral = st.slider(
        "Umbral del z modificado para marcar dias atipicos",
        min_value=1.0,
        max_value=6.0,
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
def _formato_fechas(*columnas: str) -> dict:
    """Configuración de ``st.dataframe`` para mostrar fechas sin la hora."""
    return {c: st.column_config.DateColumn(format="YYYY-MM-DD") for c in columnas}


def _preparar_anomalias(
    tablas: dict[str, pd.DataFrame],
    fecha_inicio: pd.Timestamp,
    fecha_fin: pd.Timestamp,
    estaciones: list[str],
    umbral: float,
) -> pd.DataFrame:
    """
    Filtra ``anomalias_dias`` para PJME y recalcula ``es_atipico`` y
    ``direccion`` (signo de ``z_mod``) con el umbral del deslizador.

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

    # Recalcular es_atipico y direccion en la vista (no se escribe en disco):
    # con un umbral distinto del exportado cambian los dias marcados.
    ad["es_atipico"] = ad["z_mod"].abs() > umbral
    ad["direccion"] = np.select(
        [ad["es_atipico"] & (ad["z_mod"] > 0), ad["es_atipico"] & (ad["z_mod"] < 0)],
        ["alta", "baja"],
        default="",
    )
    return ad


def _numerar_episodios(tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Episodios de PJME ordenados por fecha de inicio, con su número ``n``, que
    identifica cada episodio en el gráfico y en la tabla.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]

    Retorna
    -------
    pd.DataFrame
    """
    ep = tablas["anomalias_episodios"]
    if "region" in ep.columns:
        ep = ep[ep["region"] == "PJME"]
    ep = ep.sort_values("inicio").reset_index(drop=True)
    ep.insert(0, "n", range(1, len(ep) + 1))
    return ep


def _niveles_etiquetas(inicios: pd.Series, separacion: pd.Timedelta) -> list[int]:
    """
    Asigna a cada etiqueta, en orden de fecha, la fila más baja en la que no
    se solapa con la anterior de esa misma fila.

    Parámetros
    ----------
    inicios : pd.Series
        Fechas de las etiquetas, en orden creciente.
    separacion : pd.Timedelta
        Distancia mínima entre dos etiquetas de la misma fila.

    Retorna
    -------
    list[int]
        Fila (0 es la inferior) de cada etiqueta.
    """
    ultimo_por_nivel: list[pd.Timestamp] = []
    niveles: list[int] = []
    for inicio in inicios:
        nivel = next(
            (i for i, previo in enumerate(ultimo_por_nivel) if inicio - previo >= separacion),
            len(ultimo_por_nivel),
        )
        if nivel == len(ultimo_por_nivel):
            ultimo_por_nivel.append(inicio)
        else:
            ultimo_por_nivel[nivel] = inicio
        niveles.append(nivel)
    return niveles


def _linea_de_tiempo(
    ad: pd.DataFrame,
    tablas: dict[str, pd.DataFrame],
) -> None:
    """Línea de tiempo del residuo diario con atípicos resaltados y episodios sombreados."""
    st.subheader("Residuo diario de PJME (%)")

    # Solo los episodios que caen en el periodo mostrado: los anteriores
    # estirarían el eje de fechas fuera de los datos.
    ep = _numerar_episodios(tablas)
    primero, ultimo = ad["fecha"].min(), ad["fecha"].max()
    ep = ep[(ep["fin"] >= primero) & (ep["inicio"] <= ultimo)]

    fig = go.Figure()

    # Sombreado de episodios históricos, identificados por su número
    niveles = _niveles_etiquetas(ep["inicio"], (ultimo - primero) * _SEPARACION_ETIQUETAS)
    for (_, row), nivel in zip(ep.iterrows(), niveles):
        x0 = max(row["inicio"], primero)
        fig.add_vrect(
            x0=x0,
            x1=min(row["fin"], ultimo),
            fillcolor="rgba(100,100,200,0.12)",
            line_width=0,
        )
        fig.add_annotation(
            x=x0,
            y=1,
            yref="y domain",
            yanchor="bottom",
            yshift=nivel * 14,
            text=str(row["n"]),
            hovertext=str(row["episodio"]),
            showarrow=False,
            font=dict(size=11),
        )

    # Serie de residuos
    fig.add_trace(
        go.Scatter(
            x=ad["fecha"],
            y=ad["residuo_pct"],
            mode="lines",
            name="Residuo (%)",
            line=dict(color="#AAAAAA", width=1),
            customdata=ad[_DATOS_EMERGENTE].values,
            # Mismo cuadro que los marcadores: la línea pasa por sus puntos
            hovertemplate=_PLANTILLA_EMERGENTE,
        )
    )

    # Puntos atípicos: una traza por dirección para que la leyenda explique el color
    for direccion, color in _COLORES_DIRECCION.items():
        at = ad[ad["direccion"] == direccion]
        if at.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=at["fecha"],
                y=at["residuo_pct"],
                mode="markers",
                name=f"Atipico {direccion}",
                marker=dict(
                    color=color,
                    size=8,
                    line=dict(color="black", width=0.5),
                ),
                customdata=at[_DATOS_EMERGENTE].values,
                hovertemplate=_PLANTILLA_EMERGENTE,
            )
        )

    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(
        title="Residuo diario del pronóstico — PJME",
        xaxis_title="Fecha",
        yaxis_title="Residuo (%)",
        # Un punto cada vez: un cuadro unificado mostraría atípicos de otras fechas
        hovermode="closest",
        # Espacio sobre el área de dibujo para las filas de números
        margin=dict(t=60 + 14 * (max(niveles, default=0) + 1)),
    )
    mostrar_grafico(fig)
    st.caption(
        "Las franjas sombreadas son los episodios históricos documentados del periodo "
        "mostrado; su número remite a la tabla de episodios. "
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
    st.dataframe(at[columnas], hide_index=True, column_config=_formato_fechas("fecha"))


def _tabla_episodios(tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla de episodios históricos documentados con estado, fuente y verificación."""
    st.subheader("Episodios históricos documentados")

    ep = _numerar_episodios(tablas)

    if ep.empty:
        st.info("Sin episodios registrados.")
        return

    columnas = [
        c for c in [
            "n", "episodio", "inicio", "fin", "tipo", "direccion_esperada",
            "estado", "fuente", "verificado", "coincide_direccion",
        ]
        if c in ep.columns
    ]
    st.dataframe(ep[columnas], hide_index=True, column_config=_formato_fechas("inicio", "fin"))


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
    filtros.descartar_si_no_es_opcion("fecha_atipica_sel", fechas_atipicas)
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
    if "region" in ph.columns:
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
