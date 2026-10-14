"""
/src/features.py: variables derivadas de la fecha y normalización por región.

Cada función recibe el DataFrame en formato largo (Datetime, MW, region) y
devuelve uno nuevo, sin modificar el original.
"""

import holidays
import pandas as pd

# Estaciones meteorológicas del hemisferio norte, por meses completos
ESTACIONES = {
    12: "Invierno", 1: "Invierno", 2: "Invierno",
    3: "Primavera", 4: "Primavera", 5: "Primavera",
    6: "Verano", 7: "Verano", 8: "Verano",
    9: "Otoño", 10: "Otoño", 11: "Otoño",
}


def agregar_variables_temporales(df: pd.DataFrame, col_fecha: str = "Datetime") -> pd.DataFrame:
    """Agrega variables calculadas a partir de la fecha.

    Columnas nuevas: anio, mes, hora, dia_semana (0 = lunes), es_fin_de_semana,
    estacion y es_festivo (festivos federales de EE. UU.).
    """
    df = df.copy()
    fecha = df[col_fecha]

    df["anio"] = fecha.dt.year
    df["mes"] = fecha.dt.month
    df["hora"] = fecha.dt.hour
    df["dia_semana"] = fecha.dt.dayofweek
    df["es_fin_de_semana"] = df["dia_semana"] >= 5
    df["estacion"] = df["mes"].map(ESTACIONES)

    feriados = holidays.country_holidays(
        "US", years=range(int(fecha.dt.year.min()), int(fecha.dt.year.max()) + 1)
    )
    df["es_festivo"] = fecha.dt.normalize().isin(pd.to_datetime(list(feriados.keys())))
    return df


def normalizar_por_region(df: pd.DataFrame, columna: str = "MW") -> pd.DataFrame:
    """Agrega MW_rel: el consumo dividido entre el promedio de su región.

    Permite comparar la forma del consumo entre regiones de distinto tamaño
    (1.2 significa 20 % por encima del promedio de esa región).
    """
    df = df.copy()
    df["MW_rel"] = df[columna] / df.groupby("region")[columna].transform("mean")
    return df
