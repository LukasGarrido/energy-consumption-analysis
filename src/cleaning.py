"""
/src/cleaning.py: Este archivo se encarga de la limpieza de los datos.

Cada función recibe el DataFrame de UNA región (columnas Datetime y MW) y
devuelve uno nuevo, sin modificar el original. Orden de uso:

    unificar_duplicados -> marcar_valores_sospechosos -> reindexar_calendario_horario
    -> recortar_extremos_vacios -> interpolar_huecos -> validar_limpieza

limpiar_region encadena esos pasos para una región, y run_cleaning lo aplica
a las 12 regiones y guarda los resultados en data/processed/.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DIR, PROCESSED_DIR
from src.data_loader import load_regions_dict


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

    Los atípicos aislados (por ejemplo DOM 1,253 MW o PJMW 487 MW) NO se tocan:
    detectarlos exige comparar contra el patrón esperado (decisión D2, por hacer).
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


def recortar_extremos_vacios(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina las filas vacías del inicio y del final de la serie.

    Los vacíos de los extremos no se pueden interpolar (falta un dato válido
    a un lado), así que se recortan. Debe ejecutarse después de reindexar.
    """
    validos = df["MW"].notna()
    if not validos.any():
        raise ValueError("La región no tiene ningún valor válido.")

    primero = validos.idxmax()
    ultimo = validos[::-1].idxmax()
    n_recortadas = len(df) - (ultimo - primero + 1)

    print(f"Filas recortadas en los extremos: {n_recortadas}")
    return df.loc[primero:ultimo].reset_index(drop=True)


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


def limpiar_region(df: pd.DataFrame, limite_horas: int = 2) -> pd.DataFrame:
    """Aplica todos los pasos de limpieza a UNA región y la valida.

    Lanza un error si la región no supera validar_limpieza.
    """
    df = unificar_duplicados(df)
    df = marcar_valores_sospechosos(df)
    df = reindexar_calendario_horario(df)
    df = recortar_extremos_vacios(df)
    df = interpolar_huecos(df, limite_horas=limite_horas)
    return validar_limpieza(df)


def run_cleaning(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Limpia las 12 regiones y guarda un parquet por región y uno conjunto.

    Salidas en processed_dir: {REGION}.parquet y consumo_horario.parquet
    (formato largo: Datetime, MW, region). Lanza un error si alguna región
    no supera la validación.
    """
    regiones = load_regions_dict(raw_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    limpias = []
    for nombre, df in regiones.items():
        print(f"\n--- {nombre} ---")
        limpia = limpiar_region(df)
        limpia["region"] = nombre
        limpia.to_parquet(processed_dir / f"{nombre}.parquet", index=False)
        limpias.append(limpia)

    todo = pd.concat(limpias, ignore_index=True)
    todo.to_parquet(processed_dir / "consumo_horario.parquet", index=False)
    print(f"\nTotal: {len(todo):,} filas en {len(limpias)} regiones.")
    return todo