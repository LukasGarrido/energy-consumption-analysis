"""
/src/anomalies.py: residuo diario, z modificado y contraste con episodios conocidos.

Flujo de uso (residuos fuera de muestra de modeling.validar_ventana_movil):

    residuo_diario -> detectar_atipicos -> listar_atipicos -> contrastar_episodios

Convención: residuo = real - predicción. Positivo = demanda por encima de lo esperable.
"""

import pandas as pd

from src.config import (
    DESFASE_FIN_DE_HORA, HORAS_POR_DIA, TOLERANCIA_EPISODIO_DIAS, UMBRAL_Z_MODIFICADO,
)

CONSTANTE_Z = 0.6745  # Iglewicz y Hoaglin: z modificado = 0.6745 (x - mediana) / MAD

# Episodios de referencia, con la dirección esperada del residuo, la fuente de las
# fechas y si están verificadas. Verificado significa que la fuente confirma el
# episodio en esas fechas: en varios solo menciona el día del pico (2006, 2011,
# 2013, 7 de enero de 2014 y 2015) y el intervalo que lo rodea es criterio del
# proyecto; en Sandy la fuente cubre el 29 y el 30. Los no verificados no deben
# citarse en el informe.
EPISODIOS_CONOCIDOS = pd.DataFrame(
    [
        ("Ola de calor de agosto de 2006 (récord de PJM el 2 de agosto)", "2006-08-01", "2006-08-03", "calor extremo", "alta",
         "https://prnewswire.com/news-releases/pjm-and-members-set-new-record-for-peak-power-use-126010833.html", True),
        ("Ola de calor de julio de 2011", "2011-07-20", "2011-07-22", "calor extremo", "alta",
         "https://prnewswire.com/news-releases/pjm-and-members-set-new-record-for-peak-power-use-126010833.html", True),
        ("Huracán Sandy", "2012-10-29", "2012-10-31", "evento climático", "baja",
         "https://www.eia.gov/todayinEnergy/detail.php?id=8750", True),
        ("Ola de calor de julio de 2013 (pico de PJM el 18 de julio)", "2013-07-15", "2013-07-19", "calor extremo", "alta",
         "https://prnewswire.com/news-releases/pjm-meets-high-electricity-demand-during-unusual-heat-wave-223504311.html", True),
        ("Calor de septiembre de 2013", "2013-09-10", "2013-09-12", "calor extremo", "alta",
         "https://prnewswire.com/news-releases/pjm-sets-record-sept-peak-power-use-weather-and-local-grid-conditions-require-load-reductions-223345231.html", True),
        ("Vórtice polar de enero de 2014 (récord invernal del 7)", "2014-01-06", "2014-01-08", "frío extremo", "alta",
         "https://www.eia.gov/todayinEnergy/detail.php?id=14671", True),
        ("Vórtice polar de fines de enero de 2014", "2014-01-24", "2014-01-30", "frío extremo", "alta",
         "https://www.witf.org/2018/01/05/heating_bills_spike_like_its_the_polar_vortex_of_january_2014/", True),
        ("Ola de frío de febrero de 2015 (récord invernal del 20)", "2015-02-14", "2015-02-21", "frío extremo", "alta",
         "https://insidelines.pjm.com/?p=89180", True),
        ("Tormenta Jonas", "2016-01-22", "2016-01-24", "evento climático", "por verificar",
         "https://www.noaa.gov/media-release/january-2016-blizzard-ranked-category-4-on-northeast-snowfall-scale", True),
        ("Ola de frío de enero de 2018", "2018-01-01", "2018-01-07", "frío extremo", "alta",
         "https://pjm.com/-/media/library/reports-notices/weather-related/20180226-january-2018-cold-weather-event-report.ashx", True),
    ],
    columns=["episodio", "inicio", "fin", "tipo", "direccion_esperada", "fuente", "verificado"],
).assign(inicio=lambda d: pd.to_datetime(d["inicio"]), fin=lambda d: pd.to_datetime(d["fin"]))


def residuo_diario(residuos: pd.DataFrame, region: str | None = None) -> pd.DataFrame:
    """Agrega los residuos horarios por día operativo.

    `residuos` viene de validar_ventana_movil (Datetime, real, prediccion, residuo).
    Solo se conservan los días con las 24 horas. El residuo en % se mide sobre
    la predicción (lo esperable), así se puede comparar entre regiones.

    Columnas: fecha, horas, residuo_medio_MW, residuo_pct, residuo_hora_max_MW
    (mayor desviación horaria en valor absoluto), real_medio_MW, prediccion_media_MW
    y region (si se indica).
    """
    r = residuos.copy()
    r["fecha"] = (r["Datetime"] - DESFASE_FIN_DE_HORA).dt.normalize()
    r["residuo_abs"] = r["residuo"].abs()

    dia = r.groupby("fecha").agg(
        horas=("residuo", "size"),
        residuo_medio_MW=("residuo", "mean"),
        residuo_hora_max_MW=("residuo_abs", "max"),
        real_medio_MW=("real", "mean"),
        prediccion_media_MW=("prediccion", "mean"),
    )
    n_total = len(dia)
    dia = dia[dia["horas"] == HORAS_POR_DIA].copy()
    print(f"Días descartados por tener menos de {HORAS_POR_DIA} horas: {n_total - len(dia)}")

    dia["residuo_pct"] = dia["residuo_medio_MW"] / dia["prediccion_media_MW"] * 100
    dia = dia.reset_index()
    if region is not None:
        dia.insert(0, "region", region)
    return dia


def z_modificado(serie: pd.Series) -> pd.Series:
    """z modificado: 0.6745 * (x - mediana) / MAD. Robusto a los propios atípicos."""
    mediana = serie.median()
    mad = (serie - mediana).abs().median()
    if mad == 0:
        raise ValueError("La MAD es 0: el z modificado no está definido para esta serie.")
    return CONSTANTE_Z * (serie - mediana) / mad


def detectar_atipicos(
    diario: pd.DataFrame, columna: str = "residuo_pct", umbral: float = UMBRAL_Z_MODIFICADO
) -> pd.DataFrame:
    """Agrega z_mod, es_atipico y direccion ('alta' o 'baja') a la tabla diaria.

    El z modificado se calcula por región si existe la columna region.
    Un día es atípico si |z_mod| > umbral.
    """
    d = diario.copy()
    if "region" in d.columns:
        d["z_mod"] = d.groupby("region")[columna].transform(z_modificado)
    else:
        d["z_mod"] = z_modificado(d[columna])

    d["es_atipico"] = d["z_mod"].abs() > umbral
    d["direccion"] = pd.Series(pd.NA, index=d.index, dtype="object")
    d.loc[d["es_atipico"] & (d["z_mod"] > 0), "direccion"] = "alta"
    d.loc[d["es_atipico"] & (d["z_mod"] < 0), "direccion"] = "baja"

    n = int(d["es_atipico"].sum())
    print(f"Días atípicos: {n} de {len(d)} ({n / len(d) * 100:.1f} %)")
    return d


def listar_atipicos(diario_marcado: pd.DataFrame) -> pd.DataFrame:
    """Solo los días atípicos, de mayor a menor magnitud (|z_mod|)."""
    atipicos = diario_marcado[diario_marcado["es_atipico"]].copy()
    atipicos["magnitud"] = atipicos["z_mod"].abs()
    return atipicos.sort_values("magnitud", ascending=False).drop(columns="magnitud").reset_index(drop=True)


def contrastar_episodios(
    atipicos: pd.DataFrame,
    episodios: pd.DataFrame = EPISODIOS_CONOCIDOS,
    tolerancia_dias: int = TOLERANCIA_EPISODIO_DIAS,
    fecha_min: pd.Timestamp | None = None,
    fecha_max: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Para cada episodio, indica si algún día atípico cae dentro de su intervalo (± tolerancia).

    Si se dan fecha_min y fecha_max (el rango cubierto por los residuos), los
    episodios fuera de ese rango se marcan como 'fuera de rango' en lugar de
    'sin coincidencia', para no confundir "no detectado" con "no evaluado".
    """
    margen = pd.Timedelta(days=tolerancia_dias)
    filas = []
    for _, ep in episodios.iterrows():
        if fecha_min is not None and fecha_max is not None and (
            ep["fin"] < fecha_min or ep["inicio"] > fecha_max
        ):
            filas.append({**ep, "estado": "fuera de rango", "n_dias_atipicos": 0,
                          "max_abs_z": float("nan"), "fechas": ""})
            continue

        dentro = atipicos[(atipicos["fecha"] >= ep["inicio"] - margen) & (atipicos["fecha"] <= ep["fin"] + margen)]
        filas.append({
            **ep,
            "estado": "coincide" if len(dentro) else "sin coincidencia",
            "n_dias_atipicos": len(dentro),
            "max_abs_z": dentro["z_mod"].abs().max() if len(dentro) else float("nan"),
            "fechas": ", ".join(dentro["fecha"].dt.strftime("%Y-%m-%d")),
        })
    return pd.DataFrame(filas)