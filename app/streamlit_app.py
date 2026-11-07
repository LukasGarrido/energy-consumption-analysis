"""
app/streamlit_app.py
Punto de entrada del panel interactivo PJM.

Este archivo contiene únicamente la configuración de la página, la barra
lateral con filtros y el despacho a la página elegida. Toda la lógica
de visualización vive en ``app/paginas/`` y los módulos auxiliares.

Para ejecutar la app:
    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path para imports del paquete 'app' y 'src'
_RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(_RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_PROYECTO))

import pandas as pd
import streamlit as st

from app.config import ESTACIONES, PAGINAS, resolver_directorio_powerbi
from app.data_loader import cargar_datos
from app.paginas import anomalias, patrones, pronostico, regiones, resumen, tipos_de_dia


def _normalizar_rango_fecha(
    valor,
    fecha_global_max: pd.Timestamp,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Convierte el valor devuelto por ``st.date_input`` en un par de
    ``pd.Timestamp`` (inicio, fin), cualquiera que sea su forma
    (tupla de dos fechas, tupla de una o fecha única).

    Parámetros
    ----------
    valor
        Resultado de ``st.date_input``.
    fecha_global_max : pd.Timestamp
        Fecha máxima del historial, usada como fin cuando solo hay una fecha.

    Retorna
    -------
    tuple[pd.Timestamp, pd.Timestamp]
    """
    if isinstance(valor, (list, tuple)) and len(valor) == 2:
        return pd.Timestamp(valor[0]), pd.Timestamp(valor[1])
    if isinstance(valor, (list, tuple)) and len(valor) == 1:
        return pd.Timestamp(valor[0]), fecha_global_max
    return pd.Timestamp(valor), fecha_global_max


def _restablecer_filtros(
    todas_las_regiones: list[str],
    fecha_min,
    fecha_max,
) -> None:
    """
    Callback del botón 'Restablecer filtros': restaura todos los valores
    del ``st.session_state`` a sus valores por defecto.

    Parámetros
    ----------
    todas_las_regiones : list[str]
    fecha_min : date
    fecha_max : date
    """
    st.session_state["regiones_sel"] = todas_las_regiones
    st.session_state["fecha_rango"] = (fecha_min, fecha_max)
    st.session_state["estaciones_sel"] = ESTACIONES


def main() -> None:
    """
    Punto de entrada principal de la aplicación.

    Configura la página, carga los datos con caché, construye la barra
    lateral con filtros y despacha la página elegida.
    """
    st.set_page_config(
        page_title="Panel PJM — Demanda eléctrica",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Demanda eléctrica PJM — Panel de caracterización")
    st.markdown(
        "Panel interactivo basado en las tablas exportadas por el notebook "
        "**07_exportacion.ipynb**. Solo visualiza resultados ya calculados; "
        "no entrena ni recalcula modelos."
    )

    # Carga con caché
    tablas = cargar_datos()

    # Valores por defecto derivados de los datos
    todas_las_regiones: list[str] = sorted(
        tablas["dim_region"]["region"].unique().tolist()
    )
    hd_fechas = tablas["hechos_diario"]["fecha"].dropna()
    fecha_global_min = hd_fechas.min().date()
    fecha_global_max = hd_fechas.max().date()
    fecha_global_max_ts = pd.Timestamp(fecha_global_max)

    # Inicializar session_state con valores por defecto (solo la primera vez)
    if "regiones_sel" not in st.session_state:
        st.session_state["regiones_sel"] = todas_las_regiones
    if "fecha_rango" not in st.session_state:
        st.session_state["fecha_rango"] = (fecha_global_min, fecha_global_max)
    if "estaciones_sel" not in st.session_state:
        st.session_state["estaciones_sel"] = ESTACIONES

    # Barra lateral
    with st.sidebar:
        st.header("Navegación y filtros")

        pagina = st.radio(
            "Página",
            options=PAGINAS,
            key="pagina_sel",
        )

        st.divider()

        regiones_sel: list[str] = st.multiselect(
            "Región",
            options=todas_las_regiones,
            default=st.session_state["regiones_sel"],
            key="regiones_sel",
        )

        fecha_rango = st.date_input(
            "Rango de fechas",
            value=st.session_state["fecha_rango"],
            min_value=fecha_global_min,
            max_value=fecha_global_max,
            key="fecha_rango",
        )

        estaciones_sel: list[str] = st.multiselect(
            "Estación",
            options=ESTACIONES,
            default=st.session_state["estaciones_sel"],
            key="estaciones_sel",
        )

        st.button(
            "Restablecer filtros",
            on_click=_restablecer_filtros,
            args=(todas_las_regiones, fecha_global_min, fecha_global_max),
            use_container_width=True,
        )

        st.divider()
        st.caption(f"Datos: {resolver_directorio_powerbi()}")

    # Validación mínima antes de despachar
    if not regiones_sel:
        st.warning("Selecciona al menos una región en la barra lateral.")
        return
    if not estaciones_sel:
        st.warning("Selecciona al menos una estación en la barra lateral.")
        return

    fecha_inicio, fecha_fin = _normalizar_rango_fecha(fecha_rango, fecha_global_max_ts)

    # Despacho de páginas
    if pagina == "Resumen":
        resumen.mostrar(tablas, regiones_sel, fecha_inicio, fecha_fin, estaciones_sel)

    elif pagina == "Patrones":
        patrones.mostrar(tablas, regiones_sel, estaciones_sel)

    elif pagina == "Tipos de dia":
        tipos_de_dia.mostrar(tablas, regiones_sel, fecha_inicio, fecha_fin, estaciones_sel)

    elif pagina == "Regiones":
        regiones.mostrar(tablas, regiones_sel, estaciones_sel)

    elif pagina == "Anomalias":
        anomalias.mostrar(tablas, regiones_sel, fecha_inicio, fecha_fin, estaciones_sel)

    elif pagina == "Pronóstico":
        pronostico.mostrar(tablas, regiones_sel, fecha_inicio, fecha_fin, estaciones_sel)


if __name__ == "__main__":
    main()
