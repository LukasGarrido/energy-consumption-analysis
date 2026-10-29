"""
/src/features.py: variables derivadas de la fecha y normalización por región.

Cada función recibe el DataFrame en formato largo (Datetime, MW, region) y
devuelve uno nuevo, sin modificar el original.
"""

import holidays
import pandas as pd

from src.config import DESFASE_FIN_DE_HORA, HORIZONTE_HORAS, REZAGOS_HORAS, VENTANAS_HORAS


# Estaciones meteorológicas del hemisferio norte, por meses completos
ESTACIONES = {
    12: "Invierno", 1: "Invierno", 2: "Invierno",
    3: "Primavera", 4: "Primavera", 5: "Primavera",
    6: "Verano", 7: "Verano", 8: "Verano",
    9: "Otoño", 10: "Otoño", 11: "Otoño",
}


def agregar_variables_temporales(df: pd.DataFrame, col_fecha: str = "Datetime") -> pd.DataFrame:
    """Agrega variables de calendario según el día operativo.

    En el dataset, Datetime marca el final de la hora (00:00 es la hora 23 del
    día anterior). Las variables se calculan desde Datetime - 1 h, de modo que
    cada día operativo tenga sus 24 horas (0 a 23).

    Columnas nuevas: fecha (día operativo), anio, mes, hora (0 = 00:00-01:00),
    dia_semana (0 = lunes), es_fin_de_semana, estacion y es_festivo
    (festivos federales de EE. UU.).
    """
    df = df.copy()
    inicio_hora = df[col_fecha] - DESFASE_FIN_DE_HORA

    df["fecha"] = inicio_hora.dt.normalize()
    df["anio"] = inicio_hora.dt.year
    df["mes"] = inicio_hora.dt.month
    df["hora"] = inicio_hora.dt.hour
    df["dia_semana"] = inicio_hora.dt.dayofweek
    df["es_fin_de_semana"] = df["dia_semana"] >= 5
    df["estacion"] = df["mes"].map(ESTACIONES)

    feriados = holidays.country_holidays(
        "US", years=range(int(df["anio"].min()), int(df["anio"].max()) + 1)
    )
    df["es_festivo"] = df["fecha"].isin(pd.to_datetime(list(feriados.keys())))
    return df


def normalizar_por_region(df: pd.DataFrame, columna: str = "MW") -> pd.DataFrame:
    """Agrega MW_rel: el consumo dividido entre el promedio de su región.

    Permite comparar la forma del consumo entre regiones de distinto tamaño
    (1.2 significa 20 % por encima del promedio de esa región).
    """
    df = df.copy()
    df["MW_rel"] = df[columna] / df.groupby("region")[columna].transform("mean")
    return df


def agregar_rezagos(
    df: pd.DataFrame,
    rezagos: list[int] = REZAGOS_HORAS,
    horizonte: int = HORIZONTE_HORAS,
    columna: str = "MW",
) -> pd.DataFrame:
    """Agrega el consumo de hace k horas (MW_lag_k), calculado por región.

    Supone una serie horaria regular y sin huecos (lo garantiza la limpieza).
    Lanza un error si algún rezago es menor que el horizonte: usaría información
    que no se tendría al pronosticar (fuga de datos).
    """
    if min(rezagos) < horizonte:
        raise ValueError(
            f"Hay rezagos menores que el horizonte ({horizonte} h): usarían "
            "información que no se tendría al momento de pronosticar."
        )

    df = df.sort_values(["region", "Datetime"]).reset_index(drop=True)
    grupo = df.groupby("region")[columna]
    for k in rezagos:
        df[f"{columna}_lag_{k}"] = grupo.shift(k)
    return df


def agregar_medias_moviles(
    df: pd.DataFrame,
    ventanas: list[int] = VENTANAS_HORAS,
    horizonte: int = HORIZONTE_HORAS,
    columna: str = "MW",
) -> pd.DataFrame:
    """Agrega el consumo medio de las `w` horas previas (MW_media_{w}h), por región.

    La ventana se desplaza `horizonte` horas: para la hora t usa solo datos hasta
    t - horizonte, es decir, información disponible al pronosticar.
    """
    df = df.sort_values(["region", "Datetime"]).reset_index(drop=True)
    grupo = df.groupby("region")[columna]
    for w in ventanas:
        df[f"{columna}_media_{w}h"] = grupo.transform(
            lambda s: s.shift(horizonte).rolling(w).mean()
        )
    return df