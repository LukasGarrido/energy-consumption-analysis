"""
app/config.py
Constantes globales, paleta de colores y resolución de rutas de datos.

Todas las demás partes de la app importan desde aquí; los valores
se definen una sola vez para garantizar consistencia visual y de rutas.
"""

from pathlib import Path

# Paleta Okabe-Ito (máximo 8 colores, apta para daltonismo)
# Referencia: Okabe & Ito (2002) "Color Universal Design"
OKABE_ITO: list[str] = [
    "#E69F00",  # naranja
    "#56B4E9",  # azul cielo
    "#009E73",  # verde esmeralda
    "#F0E442",  # amarillo
    "#0072B2",  # azul oscuro
    "#D55E00",  # rojo ladrillo
    "#CC79A7",  # rosa-morado
    "#000000",  # negro
]

# Color fijo por región (hasta 12 regiones del dataset PJM)
COLORES_REGION: dict[str, str] = {
    "AEP":      "#0072B2",
    "COMED":    "#E69F00",
    "DAYTON":   "#009E73",
    "DEOK":     "#D55E00",
    "DOM":      "#CC79A7",
    "DUQ":      "#56B4E9",
    "EKPC":     "#F0E442",
    "FE":       "#000000",
    "NI":       "#8B4513",
    "PJME":     "#6A0DAD",
    "PJMW":     "#2E8B57",
    "PJM_Load": "#A52A2A",
}

# Tablas que el notebook 07 debe haber exportado
TABLAS_REQUERIDAS: list[str] = [
    "dim_region",
    "dim_fecha",
    "dim_estacion",
    "dim_tipo_dia",
    "hechos_diario",
    "patron_hora_dia",
    "patron_tipo_calendario",
    "tendencia_anual",
    "estacionalidad_mensual",
    "indicadores_region",
    "curvas_tipo_dia",
    "mezcla_region_tipo",
    "silueta_k",
    "pronostico_horario",
    "pronostico_metricas",
    "anomalias_dias",
    "anomalias_episodios",
]

# Umbral por defecto del z modificado (Iglewicz y Hoaglin, 1993)
UMBRAL_Z_DEFECTO: float = 3.5

# Nombre de las cuatro estaciones en el orden del año
ESTACIONES: list[str] = ["Invierno", "Primavera", "Verano", "Otoño"]

# Páginas disponibles en la barra de navegación
PAGINAS: list[str] = [
    "Resumen",
    "Patrones",
    "Tipos de dia",
    "Regiones",
    "Anomalias",
    "Pronóstico",
]


# Resolución de la ruta a los CSV de Power BI
def resolver_directorio_powerbi() -> Path:
    """
    Devuelve la ruta absoluta a data/processed/powerbi/.

    Intenta importar ``src.config.PROCESSED_DIR``; si el import falla
    (entorno sin el paquete src en el PYTHONPATH), construye la ruta
    relativa a la ubicación de este archivo.

    Retorna
    -------
    Path
        Directorio que contiene los CSV exportados por el notebook 07.
    """
    try:
        from src.config import PROCESSED_DIR  # type: ignore
        return PROCESSED_DIR / "powerbi"
    except Exception:
        # app/ está un nivel por debajo de la raíz del proyecto
        return Path(__file__).resolve().parents[1] / "data" / "processed" / "powerbi"
