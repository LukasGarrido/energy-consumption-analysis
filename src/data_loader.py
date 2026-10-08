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


#Funcion que carga un archivo individual y lo deja listo para usar
def load_region(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = ["Datetime", "MW"]
    df["Datetime"] = pd.to_datetime(df["Datetime"]) #convierte el texto de fecha en un tipo fecha real, necesario para extraer hora, mes, etc.
    return df.sort_values("Datetime").reset_index(drop=True) #ordena cronológicamente

