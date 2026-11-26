"""
app/filtros.py
Helpers de filtrado y validación de DataFrames según los controles
de la barra lateral (región, estación y rango de fechas).
"""

import pandas as pd
import streamlit as st

from app.config import ESTACIONES


def por_region(df: pd.DataFrame, regiones: list[str]) -> pd.DataFrame:
    """
    Filtra ``df`` por las regiones seleccionadas si la columna ``region``
    existe. Si la lista está vacía no queda ninguna fila.

    Parámetros
    ----------
    df : pd.DataFrame
    regiones : list[str]
        Lista de nombres de región seleccionados en la barra lateral.

    Retorna
    -------
    pd.DataFrame
    """
    if "region" in df.columns:
        return df[df["region"].isin(regiones)].copy()
    return df


def por_estacion(df: pd.DataFrame, estaciones: list[str]) -> pd.DataFrame:
    """
    Filtra ``df`` por estaciones si la columna ``estacion`` existe. Si la
    lista está vacía no queda ninguna fila.

    Parámetros
    ----------
    df : pd.DataFrame
    estaciones : list[str]
        Lista de estaciones seleccionadas en la barra lateral.

    Retorna
    -------
    pd.DataFrame
    """
    if "estacion" in df.columns:
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


# Regiones sin cobertura hasta 2018-08-03 (series históricas cerradas)
_REGIONES_HISTORICAS: tuple[str, ...] = ("NI", "PJM_Load")
# Inicio del periodo común de las 10 regiones vigentes
_INICIO_PERIODO_COMUN = pd.Timestamp("2013-06-01").date()


# Claves de widgets cuyo valor debe sobrevivir al cambiar de página
_PREFIJOS_PERSISTENTES: tuple[str, ...] = ("regiones_", "estaciones_", "fecha_rango_")
_CLAVES_PERSISTENTES: tuple[str, ...] = (
    "heatmap_region", "cal_region", "modo_periodo", "umbral_z",
    "fecha_atipica_sel", "metrica_error",
)


def conservar_estado_widgets() -> None:
    """
    Evita que Streamlit borre el valor de los filtros de las páginas que no se
    están mostrando.

    Streamlit elimina de ``st.session_state`` la clave de un widget que no se
    renderiza en una ejecución. Reasignarla la convierte en un valor propio de
    la sesión. Debe llamarse en cada ejecución, antes de crear los widgets.
    """
    for clave in list(st.session_state.keys()):
        if clave in _CLAVES_PERSISTENTES or str(clave).startswith(_PREFIJOS_PERSISTENTES):
            st.session_state[clave] = st.session_state[clave]


def descartar_si_no_es_opcion(clave: str, opciones: list) -> None:
    """
    Borra ``st.session_state[clave]`` si su valor ya no está entre las opciones
    del widget (por ejemplo, tras quitar una región), para que vuelva al
    valor por defecto.

    Parámetros
    ----------
    clave : str
        Clave del widget de selección única.
    opciones : list
        Opciones que se ofrecerán en esta ejecución.
    """
    if clave in st.session_state and st.session_state[clave] not in opciones:
        del st.session_state[clave]


def _fijar(clave: str, valor) -> None:
    """Callback auxiliar: escribe ``valor`` en ``st.session_state[clave]``."""
    st.session_state[clave] = valor


def _chips_resumen(
    regiones: list[str],
    total_regiones: int,
    estaciones: list[str] | None,
    f_inicio: pd.Timestamp | None,
    f_fin: pd.Timestamp | None,
) -> str:
    """
    Construye el HTML de los chips que resumen los filtros activos.

    Parámetros
    ----------
    regiones : list[str]
        Regiones seleccionadas.
    total_regiones : int
        Número total de regiones disponibles.
    estaciones : list[str] | None
        Estaciones seleccionadas (``None`` si el módulo no filtra por estación).
    f_inicio, f_fin : pd.Timestamp | None
        Rango de fechas (``None`` si el módulo no filtra por fecha).

    Retorna
    -------
    str
        Fragmento HTML con los chips.
    """
    chips = [f"{len(regiones)} de {total_regiones} regiones"]
    if estaciones is not None:
        chips.append(
            "Todas las estaciones"
            if len(estaciones) == len(ESTACIONES)
            else ", ".join(estaciones) or "Sin estaciones"
        )
    if f_inicio is not None and f_fin is not None:
        chips.append(f"{f_inicio:%d %b %Y} → {f_fin:%d %b %Y}")
    return "".join(f'<span class="filter-chip">{c}</span>' for c in chips)


def selector_filtros_modulo(
    tablas: dict[str, pd.DataFrame],
    key_sufijo: str,
    con_fechas: bool = True,
    con_estaciones: bool = True,
) -> tuple[list[str], pd.Timestamp, pd.Timestamp, list[str]]:
    """
    Renderiza el panel de filtros del módulo actual: regiones y estaciones
    como botones seleccionables (*pills*), atajos de selección, atajos de
    rango de fechas y un resumen de los filtros activos.

    Parámetros
    ----------
    tablas : dict[str, pd.DataFrame]
        Tablas cargadas (se usan ``dim_region`` y ``hechos_diario``).
    key_sufijo : str
        Sufijo para que cada módulo conserve sus propios filtros.
    con_fechas : bool
        Si es ``False`` se oculta el selector de fechas y se usa todo el rango.
    con_estaciones : bool
        Si es ``False`` se oculta el selector de estaciones y se devuelven todas.

    Retorna
    -------
    tuple[list[str], pd.Timestamp, pd.Timestamp, list[str]]
        Regiones, fecha de inicio, fecha de fin y estaciones.
    """
    todas = sorted(tablas["dim_region"]["region"].unique().tolist())
    vigentes = [r for r in todas if r not in _REGIONES_HISTORICAS]
    hd_fechas = tablas["hechos_diario"]["fecha"].dropna()
    f_min = hd_fechas.min().date()
    f_max = hd_fechas.max().date()
    inicio_comun = max(_INICIO_PERIODO_COMUN, f_min)

    k_reg = f"regiones_{key_sufijo}"
    k_est = f"estaciones_{key_sufijo}"
    k_fec = f"fecha_rango_{key_sufijo}"

    if k_reg not in st.session_state:
        st.session_state[k_reg] = todas
    if k_est not in st.session_state:
        st.session_state[k_est] = list(ESTACIONES)
    if k_fec not in st.session_state:
        st.session_state[k_fec] = (f_min, f_max)

    with st.container(border=True, key=f"panel_filtros_{key_sufijo}"):
        st.markdown(
            '<div class="filter-title">Filtros</div>', unsafe_allow_html=True
        )

        # Regiones
        st.markdown('<div class="filter-label">Regiones</div>', unsafe_allow_html=True)
        # Los atajos ocupan su propia fila: junto al título se cortaban
        c_a, c_b, c_c = st.columns(3)
        c_a.button("Todas", key=f"b_todas_{key_sufijo}", on_click=_fijar,
                   args=(k_reg, todas), width="stretch")
        c_b.button("Vigentes", key=f"b_vig_{key_sufijo}", on_click=_fijar,
                   args=(k_reg, vigentes), width="stretch",
                   help="Las 10 regiones con datos hasta 2018-08-03")
        c_c.button("Ninguna", key=f"b_nin_{key_sufijo}", on_click=_fijar,
                   args=(k_reg, []), width="stretch")
        regiones_sel = st.pills(
            "Regiones", options=todas, selection_mode="multi",
            key=k_reg, label_visibility="collapsed",
        ) or []

        # Estaciones
        if con_estaciones:
            st.markdown('<div class="filter-label">Estaciones</div>', unsafe_allow_html=True)
            estaciones_sel = st.pills(
                "Estaciones", options=ESTACIONES, selection_mode="multi",
                key=k_est, label_visibility="collapsed",
            ) or []
        else:
            estaciones_sel = list(ESTACIONES)

        # Fechas
        if con_fechas:
            with st.container():
                st.markdown('<div class="filter-label">Periodo</div>', unsafe_allow_html=True)
                p1, p2, p3, p4 = st.columns(4)
                p1.button("Todo", key=f"f_todo_{key_sufijo}", on_click=_fijar,
                          args=(k_fec, (f_min, f_max)), width="stretch")
                p2.button("Común", key=f"f_com_{key_sufijo}", on_click=_fijar,
                          args=(k_fec, (inicio_comun, f_max)), width="stretch",
                          help="Periodo común de las 10 regiones vigentes (desde 2013-06-01)")
                p3.button("2 años", key=f"f_2a_{key_sufijo}", on_click=_fijar,
                          args=(k_fec, (max(f_min, (pd.Timestamp(f_max) - pd.DateOffset(years=2)).date()), f_max)),
                          width="stretch", help="Últimos 2 años del historial")
                p4.button("1 año", key=f"f_1a_{key_sufijo}", on_click=_fijar,
                          args=(k_fec, (max(f_min, (pd.Timestamp(f_max) - pd.DateOffset(years=1)).date()), f_max)),
                          width="stretch", help="Último año del historial")
                fecha_rango = st.date_input(
                    "Rango de fechas", min_value=f_min, max_value=f_max,
                    key=k_fec, label_visibility="collapsed",
                )
        else:
            fecha_rango = (f_min, f_max)

        if not regiones_sel:
            st.caption("Sin regiones seleccionadas: elige al menos una para ver resultados.")

    if con_fechas:
        if isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 2:
            f_inicio, f_fin = pd.Timestamp(fecha_rango[0]), pd.Timestamp(fecha_rango[1])
        elif isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 1:
            f_inicio, f_fin = pd.Timestamp(fecha_rango[0]), pd.Timestamp(f_max)
        else:
            f_inicio, f_fin = pd.Timestamp(fecha_rango), pd.Timestamp(f_max)
    else:
        f_inicio, f_fin = pd.Timestamp(f_min), pd.Timestamp(f_max)

    st.markdown(
        '<div class="filter-chips">'
        + _chips_resumen(
            regiones_sel, len(todas), estaciones_sel if con_estaciones else None,
            f_inicio if con_fechas else None, f_fin if con_fechas else None,
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    return list(regiones_sel), f_inicio, f_fin, list(estaciones_sel)
