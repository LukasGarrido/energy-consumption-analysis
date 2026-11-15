"""
app/estilos.py
Estilos CSS globales, componentes HTML reutilizables y helpers visuales
para la aplicación Streamlit del estudio de demanda PJM.

Compatibles con modo claro y oscuro. Sin emojis.
"""

import streamlit as st


def aplicar_estilos_globales() -> None:
    """
    Inyecta CSS global que mejora la tipografía, las tarjetas métricas,
    la barra lateral, los contenedores y la coherencia visual general.
    Compatible con modo claro y modo oscuro de Streamlit.
    """
    st.markdown(_CSS_GLOBAL, unsafe_allow_html=True)


def renderizar_hero_banner(titulo_modulo: str) -> None:
    """
    Muestra un encabezado de módulo con un subtítulo institucional y el
    nombre del módulo actual, dentro de un contenedor visualmente diferenciado.

    Parámetros
    ----------
    titulo_modulo : str
        Nombre del módulo que se muestra como título principal.
    """
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-tag">Estudio de Demanda Electrica — PJM Interconnection</div>
            <div class="hero-title">{titulo_modulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_metrica(etiqueta: str, valor: str, descripcion: str = "") -> str:
    """
    Genera el HTML de una tarjeta métrica individual con etiqueta, valor
    destacado y una descripción breve opcional.

    Parámetros
    ----------
    etiqueta : str
        Texto corto encima del valor (por ejemplo 'Regiones').
    valor : str
        Valor principal (por ejemplo '12' o '15,499 MW').
    descripcion : str
        Texto explicativo corto debajo del valor (opcional).

    Retorna
    -------
    str
        Fragmento HTML listo para inyectar con ``unsafe_allow_html=True``.
    """
    desc_html = (
        f'<div class="kpi-desc">{descripcion}</div>' if descripcion else ""
    )
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{etiqueta}</div>
        <div class="kpi-value">{valor}</div>
        {desc_html}
    </div>
    """


def renderizar_fila_metricas(tarjetas: list[str]) -> None:
    """
    Renderiza una fila horizontal de tarjetas métricas HTML.

    Parámetros
    ----------
    tarjetas : list[str]
        Lista de fragmentos HTML generados por ``tarjeta_metrica()``.
    """
    interior = "".join(tarjetas)
    st.markdown(
        f'<div class="kpi-row">{interior}</div>',
        unsafe_allow_html=True,
    )


def renderizar_seccion(titulo: str, descripcion: str = "") -> None:
    """
    Muestra un encabezado de sección con una línea divisoria sutil y una
    descripción opcional que orienta al usuario sobre qué buscar en el
    gráfico que sigue.

    Parámetros
    ----------
    titulo : str
        Nombre de la sección.
    descripcion : str
        Frase orientadora (opcional).
    """
    desc_html = (
        f'<p class="section-desc">{descripcion}</p>' if descripcion else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <h3 class="section-title">{titulo}</h3>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_nota_filtro(texto: str = "Este grafico usa datos agregados y no responde al filtro de fecha.") -> None:
    """
    Muestra una nota discreta bajo un gráfico indicando que no responde
    a cierto filtro.

    Parámetros
    ----------
    texto : str
        Texto de la nota.
    """
    st.markdown(
        f'<div class="filter-note">{texto}</div>',
        unsafe_allow_html=True,
    )


def renderizar_interpretacion(texto: str) -> None:
    """
    Muestra una frase breve de interpretación bajo un gráfico, con un
    estilo diferenciado del caption estándar.

    Parámetros
    ----------
    texto : str
        Frase interpretativa.
    """
    st.markdown(
        f'<div class="chart-interpretation">{texto}</div>',
        unsafe_allow_html=True,
    )


# CSS global inyectado una sola vez al inicio de la app
_CSS_GLOBAL = """
<style>
/* Ocultar elementos predeterminados de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Tipografía general */
h1, h2, h3 {
    letter-spacing: -0.02em;
}

/* Barra lateral: navegación limpia */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.15);
}
section[data-testid="stSidebar"] .stRadio > label {
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    opacity: 0.65;
}
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    margin-bottom: 2px;
    transition: background 0.15s ease;
    font-weight: 500;
    text-transform: none;
    letter-spacing: normal;
    opacity: 1;
}
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background: rgba(128,128,128,0.1);
}

/* Hero banner del módulo */
.hero-banner {
    padding: 1rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(128,128,128,0.2);
    background: linear-gradient(135deg, rgba(0,114,178,0.06), rgba(128,128,128,0.03));
}
.hero-tag {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    opacity: 0.55;
    margin-bottom: 0.25rem;
}
.hero-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.3;
}

/* Tarjetas KPI personalizadas */
.kpi-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 1rem 0 1.25rem 0;
}
.kpi-card {
    flex: 1 1 140px;
    min-width: 130px;
    padding: 1rem 1.1rem;
    border-radius: 10px;
    border: 1px solid rgba(128,128,128,0.2);
    background: rgba(128,128,128,0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.55;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.kpi-desc {
    font-size: 0.73rem;
    opacity: 0.6;
    margin-top: 0.3rem;
    line-height: 1.3;
}

/* Encabezados de sección */
.section-header {
    margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(0,114,178,0.25);
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 0 0 0.2rem 0;
}
.section-desc {
    font-size: 0.82rem;
    opacity: 0.6;
    margin: 0;
    line-height: 1.4;
}

/* Nota de filtro (bajo gráficos que no responden a fecha) */
.filter-note {
    font-size: 0.72rem;
    font-style: italic;
    opacity: 0.45;
    margin-top: 0.25rem;
    padding: 0.3rem 0.6rem;
    border-left: 3px solid rgba(128,128,128,0.25);
}

/* Interpretación de gráfico */
.chart-interpretation {
    font-size: 0.82rem;
    opacity: 0.7;
    margin: 0.4rem 0 0.25rem 0;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    background: rgba(0,114,178,0.04);
    border-left: 3px solid rgba(0,114,178,0.35);
    line-height: 1.45;
}

/* Panel de filtros (expander) */
div[data-testid="stExpander"] {
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 8px;
    margin-bottom: 1rem;
}
div[data-testid="stExpander"] summary {
    font-weight: 600;
    font-size: 0.85rem;
}

/* Métricas nativas de Streamlit (st.metric) */
div[data-testid="stMetric"] {
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid rgba(128,128,128,0.2);
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

/* Botones */
div.stButton > button {
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s ease;
}

/* Separadores */
hr {
    margin: 1.5rem 0;
    border-color: rgba(128,128,128,0.15);
}

/* DataFrames */
div[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}
</style>
"""
