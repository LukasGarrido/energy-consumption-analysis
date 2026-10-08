"""
/src/config.py: Este archivo solo define rutas, para escribirlas una vez y reutilizarlas.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent[1] #ubicación del propio archivo, es decir energy-consumption-analysis/src/config.py.
RAW_DIR = ROOT / "data" / "raw" #ubicación de los datos sin procesar
PROCESSED_DIR = ROOT / "data" / "processed" #ubicación de los datos procesados  