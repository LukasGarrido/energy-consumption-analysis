"""
/src/cleaning.py: Este archivo se encarga de la limpieza de los datos.

Cada función recibe el DataFrame de UNA región (columnas Datetime y MW) y
devuelve uno nuevo, sin modificar el original. Orden de uso:

    unificar_duplicados -> marcar_valores_sospechosos -> reindexar_calendario_horario
    -> interpolar_huecos -> validar_limpieza
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR
from src.data_loader import load_regions_dict, load_all_regions


def unificar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Si una misma hora aparece varias veces, deja una sola fila con el promedio de sus valores."""
    n_filas_originales = len(df)
    df = df.groupby("Datetime", as_index=False)["MW"].mean()
    print(f"Filas eliminadas por duplicados: {n_filas_originales - len(df)}")
    return df


def marcar_valores_sospechosos(df: pd.DataFrame) -> pd.DataFrame:
    """Reemplaza por vacío (NaN) los valores que se consideran errores.

    La fila se queda, pero sin dato. Por ahora se consideran errores los
    valores menores o iguales a 0 y los infinitos.
    """
    df = df.copy()
    vacios_antes = df["MW"].isna().sum()

    sospechoso = (df["MW"] <= 0) | np.isinf(df["MW"])
    df.loc[sospechoso, "MW"] = np.nan

    print(f"Valores sospechosos marcados como vacío: {df['MW'].isna().sum() - vacios_antes}")
    return df


def reindexar_calendario_horario(df: pd.DataFrame) -> pd.DataFrame:
    """Construye el calendario completo (una fila por hora entre la primera y la última fecha).

    Las horas que no estaban aparecen como filas nuevas con MW vacío.
    Requiere fechas sin repetir: ejecutar antes unificar_duplicados.
    """
    if df["Datetime"].duplicated().any():
        raise ValueError("Hay fechas repetidas: ejecuta unificar_duplicados antes de reindexar.")

    n_filas_originales = len(df)
    calendario = pd.date_range(
        start=df["Datetime"].min(),
        end=df["Datetime"].max(),
        freq="h",
        name="Datetime",
    )

    df = df.set_index("Datetime").reindex(calendario).reset_index()

    print(f"Horas agregadas al calendario: {len(df) - n_filas_originales}")
    return df


def interpolar_huecos(df: pd.DataFrame, limite_horas: int = 2) -> pd.DataFrame:
    """Estima cada vacío a partir de las horas vecinas (interpolación lineal).

    Solo rellena los huecos de hasta `limite_horas` horas seguidas que tengan
    un valor válido a cada lado. Los huecos más largos y los de los extremos
    de la serie se dejan vacíos.
    """
    df = df.copy()
    serie = df["MW"]
    es_nan = serie.isna()

    # Largo de la racha de vacíos a la que pertenece cada fila
    grupo = (es_nan != es_nan.shift()).cumsum()
    largo_racha = es_nan.groupby(grupo).transform("sum")

    estimada = serie.interpolate(method="linear", limit_area="inside")
    rellenar = es_nan & (largo_racha <= limite_horas)
    df["MW"] = serie.where(~rellenar, estimada)

    n_rellenados = int((rellenar & estimada.notna()).sum())
    print(f"Huecos interpolados: {n_rellenados} | Vacíos que quedan: {int(df['MW'].isna().sum())}")
    return df


def validar_limpieza(df: pd.DataFrame) -> pd.DataFrame:
    """Comprueba que la región quedó como debe y lanza un error si no.

    Revisa: fechas sin repetir, orden cronológico, una hora exacta entre filas
    consecutivas, sin vacíos y sin valores menores o iguales a 0.
    """
    problemas = []

    if df["Datetime"].duplicated().any():
        problemas.append("hay fechas repetidas")
    if not df["Datetime"].is_monotonic_increasing:
        problemas.append("las fechas no están en orden cronológico")

    saltos = df["Datetime"].diff().dropna()
    n_saltos = int((saltos != pd.Timedelta(hours=1)).sum())
    if n_saltos > 0:
        problemas.append(f"{n_saltos} saltos distintos de 1 hora")

    n_vacios = int(df["MW"].isna().sum())
    if n_vacios > 0:
        problemas.append(f"{n_vacios} valores vacíos")

    n_no_positivos = int((df["MW"] <= 0).sum())
    if n_no_positivos > 0:
        problemas.append(f"{n_no_positivos} valores menores o iguales a 0")

    if problemas:
        raise ValueError("Limpieza incompleta: " + "; ".join(problemas))

    print(f"Validación correcta: {len(df)} filas, una por hora, sin vacíos.")
    return df


def run_cleaning(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR) -> None:
    """Ejecuta todos los pasos anteriores en orden (pendiente)."""
    pass