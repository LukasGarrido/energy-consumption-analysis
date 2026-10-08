"""
/src/data_loader.py: Carga los datos, detecta regiones y construye un dataframe unificado.
"""


from pathlib import Path
import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR

COMBINED_FILE = "pjm_hourly_est.csv"  # archivo con todas las regiones, se omite

#Esta función es la que detecta archivos nuevos automáticamente
def list_region_files(raw_dir: Path = RAW_DIR) -> dict[str, Path]:
    """
    Busca todos los archivos CSV en RAW_DIR, ignorando el archivo combinado.
    Devuelve un diccionario: { 'region_name': Path_to_file }
    """
    files = {}

    for path in sorted(raw_dir.glob("*.csv")):
        if path.name.lower() == COMBINED_FILE:
            continue
        region = path.stem.replace("_hourly", "")
        files[region] = path
    return files

