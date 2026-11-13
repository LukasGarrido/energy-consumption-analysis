"""
app/estilos.py
Módulo de mejoras visuales y diseño adaptativo (compatible con modo claro y oscuro)
para la aplicación de Streamlit, libre de emojis y enfocado al estudio de demanda.
"""

import streamlit as str_lit


def aplicar_estilos_globales() -> None:
    """
    Inyecta estilos CSS ligeros y no intrusivos que respetan estrictamente
    el modo oscuro y claro de Streamlit, mejorando la tipografía, espaciado
    y apariencia de tarjetas y contenedores.
    """
    css = """
    <style>
    /* Ocultar elementos predeterminados */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Mejoras tipográficas generales */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* Contenedores y métricas estilizadas compatibles con dark/light mode */
    div[data-testid="stMetric"] {
        padding: 14px 18px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }

    /* Botones limpios y profesionales */
    div.stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Separadores sutiles */
    hr {
        margin: 1.5rem 0;
        border-color: rgba(128, 128, 128, 0.2);
    }
    </style>
    """
    str_lit.markdown(css, unsafe_allow_html=True)


def renderizar_hero_banner(titulo_modulo: str = "Panel de Control PJM") -> None:
    """
    Renderiza un encabezado de módulo limpio y profesional para el estudio de demanda.
    """
    str_lit.markdown(
        f"""
        <div style="padding: 0.85rem 1.25rem; border-radius: 8px; margin-bottom: 1.25rem; border: 1px solid rgba(128, 128, 128, 0.25); background: rgba(128, 128, 128, 0.03);">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; opacity: 0.7; margin-bottom: 0.1rem;">Estudio de Consumo y Demanda Electrica PJM</div>
            <div style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;">{titulo_modulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
