"""
/src/cleaning.py: Este archivo se encarga de la limpieza de los datos.
"""

from pathlib import Path
import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR

COMBINED_FILE = "pjm_hourly_est.csv" #archivo con todas las regiones, se omite

def unificar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

def marcar_valores_sospechosos(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

def reindexar_calendario_horario(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

def interpolar_huecos(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

def validar_limpieza(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

def run_cleaning(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR) -> None:
    pass 

