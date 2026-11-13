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
from app.estilos import aplicar_estilos_globales, renderizar_hero_banner
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
    Punto de entrada principal de la aplicación del estudio.

    Configura la página, carga los datos con caché, muestra el menú de
    navegación lateral y despacha el módulo seleccionado.
    """
    st.set_page_config(
        page_title="Panel PJM — Demanda eléctrica",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Aplicar estilos globales y limpieza
    aplicar_estilos_globales()

    # Carga con caché
    tablas = cargar_datos()

    # Barra lateral de navegación (solo navegación y metadatos)
    with st.sidebar:
        st.markdown("### Modulos de Estudio")
        pagina = st.radio(
            "Seleccionar modulo",
            options=PAGINAS,
            key="pagina_sel",
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("Estudio de Demanda PJM")
        st.caption(f"Datos: {resolver_directorio_powerbi()}")

    # Despacho de módulos del estudio
    if pagina == "Resumen":
        resumen.mostrar(tablas)

    elif pagina == "Patrones":
        patrones.mostrar(tablas)

    elif pagina == "Tipos de dia":
        tipos_de_dia.mostrar(tablas)

    elif pagina == "Regiones":
        regiones.mostrar(tablas)

    elif pagina == "Anomalias":
        anomalias.mostrar(tablas)

    elif pagina == "Pronóstico":
        pronostico.mostrar(tablas)


if __name__ == "__main__":
    main()
