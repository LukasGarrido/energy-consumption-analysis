"""
app/streamlit_app.py
Punto de entrada del panel interactivo PJM.

Este archivo contiene únicamente la configuración de la página, la barra
lateral de navegación y el despacho a la página elegida. Toda la lógica
de filtros y visualización vive en ``app/paginas/`` y los módulos auxiliares.

Para ejecutar la app:
    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path para imports del paquete 'app' y 'src'
_RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(_RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_PROYECTO))

import streamlit as st

from app.config import PAGINAS, resolver_directorio_panel
from app.data_loader import cargar_datos
from app.filtros import conservar_estado_widgets
from app.estilos import aplicar_estilos_globales, renderizar_hero_banner
from app.paginas import anomalias, patrones, pronostico, regiones, resumen, tipos_de_dia


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

    # Conservar los filtros de las páginas que no se muestran
    conservar_estado_widgets()

    # Aplicar estilos globales y limpieza
    aplicar_estilos_globales()

    # Carga con caché
    tablas = cargar_datos()

    # Barra lateral de navegación (solo navegación y metadatos)
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div>'
            '<div class="sidebar-name">Panel de demanda</div>'
            '<div class="sidebar-sub">12 regiones · 1998–2018</div></div></div>',
            unsafe_allow_html=True,
        )
        pagina = st.radio(
            "Seleccionar modulo",
            options=PAGINAS,
            key="pagina_sel",
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("Estudio de Demanda PJM")
        st.caption(f"Datos: {resolver_directorio_panel()}")

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
