"""
/src/cleaning.py: Este archivo se encarga de la limpieza de los datos.
"""

from pathlib import Path
import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR

COMBINED_FILE = "pjm_hourly_est.csv" #archivo con todas las regiones, se omite

#Si una misma hora aparece varias veces, deja una sola fila con el promedio de sus valores.
def unificar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

#Reemplaza por vacío los valores que se consideran errores. La fila se queda, pero sin dato.
def marcar_valores_sospechosos(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

#Construye el calendario completo, una fila por hora entre la 
# primera y la última fecha de la región, y lo compara con lo que existe. 
# Las horas que no estaban aparecen como filas nuevas con MW vacío.
def reindexar_calendario_horario(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

#Estima cada vacío a partir de las horas vecinas. 
# En el ejemplo, entre 105 (02:00) y 110 (05:00) hay dos horas vacías,
#y se reparten en línea recta: 106.7 y 108.3.
def interpolar_huecos(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

#Comprueba que la región quedó como debe y avisa si no. Revisa:
def validar_limpieza(df: pd.DataFrame) -> pd.DataFrame:
    return pass 

#Ejecuta todos los pasos anteriores en orden.
def run_cleaning(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR) -> None:
    pass 

