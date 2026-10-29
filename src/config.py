"""
/src/config.py: rutas y parámetros del proyecto, para definirlos una vez y reutilizarlos.
"""

from pathlib import Path

import pandas as pd

# Rutas
ROOT = Path(__file__).resolve().parents[1]  # energy-consumption-analysis/
RAW_DIR = ROOT / "data" / "raw"             # datos sin procesar
PROCESSED_DIR = ROOT / "data" / "processed" # datos procesados y tablas para el panel

# Convención horaria
DESFASE_FIN_DE_HORA = pd.Timedelta(hours=1)  # Datetime marca el final de la hora
HORAS_POR_DIA = 24                           # un día operativo completo tiene 24 horas

# Pronóstico
HORIZONTE_HORAS = 24            # se pronostica con 24 horas de antelación
REZAGOS_HORAS = [24, 48, 168]   # consumo de hace 1 día, 2 días y 1 semana
VENTANAS_HORAS = [24, 168]      # ventanas de las medias móviles (1 día y 1 semana)
FECHA_CORTE = "2017-01-01"      # antes: entrenamiento · desde esta fecha: prueba
N_PLIEGUES = 3                  # pliegues mínimos de la validación en ventana móvil

# Agrupamiento de perfiles diarios
K_MIN, K_MAX = 2, 10            # rango de k que se evalúa con la silueta
TAMANO_MIN_GRUPO = 0.05         # cada grupo debe tener al menos el 5 % de los días
SILUETA_RAZONABLE = 0.50        # >= 0.50: estructura razonable
SILUETA_DEBIL = 0.26            # entre 0.26 y 0.50: estructura débil

# Detección de anomalías 
UMBRAL_Z_MODIFICADO = 3.5       # z modificado (Iglewicz y Hoaglin) para marcar atípicos

# Reproducibilidad 
SEMILLA = 42                    # para que los resultados sean reproducibles