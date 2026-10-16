"""
/src/config.py: Este archivo solo define rutas, para escribirlas una vez y reutilizarlas.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] #ubicación del propio archivo, es decir energy-consumption-analysis/src/config.py.
RAW_DIR = ROOT / "data" / "raw" #ubicación de los datos sin procesar
PROCESSED_DIR = ROOT / "data" / "processed" #ubicación de los datos procesados  

HORIZONTE_HORAS = 24            # se pronostica con 24 horas de antelación
REZAGOS_HORAS = [24, 48, 168]   # consumo de hace 1 día, 2 días y 1 semana
VENTANAS_HORAS = [24, 168]      # ventanas de las medias móviles (1 día y 1 semana)
FECHA_CORTE = "2017-01-01"      # antes: entrenamiento · desde esta fecha: prueba
SEMILLA = 42                    # para que los resultados sean reproducibles