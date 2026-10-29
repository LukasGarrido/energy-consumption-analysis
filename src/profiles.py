"""
/src/profiles.py: perfiles diarios normalizados, elección de k, agrupamiento y descripción de grupos.

Flujo de uso (sobre el formato largo con features.agregar_variables_temporales aplicado):

    construir_perfiles -> elegir_k -> recomendar_k -> agrupar
    -> describir_grupos / curvas_grupo / mezcla_por_region -> tabla_dias

Un "tipo de día" es un grupo de días con la misma FORMA de curva horaria: cada día
se divide entre su promedio, así que se compara la forma y no el nivel.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestCentroid

from src.config import (
    HORAS_POR_DIA, K_MAX, K_MIN, MUESTRA_AGRUPAMIENTO, SEMILLA,
    SILUETA_DEBIL, SILUETA_RAZONABLE, TAMANO_MIN_GRUPO,
)

METODOS = ("kmeans", "ward")


def construir_perfiles(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Convierte la serie horaria en un perfil de 24 valores por día y región.

    Requiere las columnas region, fecha (día operativo), hora y MW. Solo conserva
    los días con las 24 horas (se descartan los extremos incompletos de cada serie).

    Devuelve:
      - perfiles: índice (region, fecha), columnas 0..23; cada fila dividida
        entre el promedio de su día (1.1 = 10 % sobre el promedio del día).
      - nivel: promedio del día en MW, para recuperar la magnitud.
    """
    faltan = {"region", "fecha", "hora", "MW"} - set(df.columns)
    if faltan:
        raise KeyError(f"Faltan columnas {sorted(faltan)}: aplica agregar_variables_temporales.")

    ancho = df.pivot_table(index=["region", "fecha"], columns="hora", values="MW", aggfunc="mean")
    ancho = ancho.reindex(columns=range(HORAS_POR_DIA))
    n_total = len(ancho)
    ancho = ancho.dropna()
    print(f"Días descartados por tener menos de {HORAS_POR_DIA} horas: {n_total - len(ancho):,}")

    nivel = ancho.mean(axis=1).rename("MW_medio_dia")
    perfiles = ancho.div(nivel, axis=0)
    perfiles.columns.name = "hora"
    print(f"Perfiles: {len(perfiles):,} días en {perfiles.index.get_level_values('region').nunique()} regiones")
    return perfiles, nivel


def _ordenar_por_tamano(etiquetas: np.ndarray) -> np.ndarray:
    """Renumera los grupos de 1 a k, del más grande al más pequeño (numeración estable)."""
    orden = pd.Series(etiquetas).value_counts().index
    mapa = {viejo: nuevo for nuevo, viejo in enumerate(orden, start=1)}
    return np.array([mapa[e] for e in etiquetas])


def _ajustar(X: np.ndarray, k: int, metodo: str, max_ward: int) -> np.ndarray:
    """Agrupa X en k grupos. Ward ajusta sobre una muestra si hay demasiados días."""
    if metodo == "kmeans":
        return KMeans(n_clusters=k, n_init=10, random_state=SEMILLA).fit_predict(X)
    if metodo == "ward":
        if len(X) <= max_ward:
            return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)
        idx = np.random.default_rng(SEMILLA).choice(len(X), max_ward, replace=False)
        etiquetas_muestra = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X[idx])
        # El resto de días se asigna al centroide más cercano
        return NearestCentroid().fit(X[idx], etiquetas_muestra).predict(X)
    raise ValueError(f"Método desconocido: {metodo}. Usa uno de {METODOS}.")


def elegir_k(
    perfiles: pd.DataFrame,
    k_min: int = K_MIN,
    k_max: int = K_MAX,
    metodos: tuple[str, ...] = METODOS,
    muestra: int = MUESTRA_AGRUPAMIENTO,
) -> pd.DataFrame:
    """Compara métodos y valores de k con la silueta media.

    Trabaja sobre una muestra aleatoria (reproducible) de hasta `muestra` días,
    porque la silueta y Ward escalan de forma cuadrática. Devuelve una fila por
    (método, k): silueta, tamaño del grupo más pequeño (fracción) y si cumple
    el tamaño mínimo.
    """
    X = perfiles.to_numpy()
    if len(X) > muestra:
        X = X[np.random.default_rng(SEMILLA).choice(len(X), muestra, replace=False)]

    filas = []
    for metodo in metodos:
        for k in range(k_min, k_max + 1):
            etiquetas = _ajustar(X, k, metodo, max_ward=len(X))
            fracciones = pd.Series(etiquetas).value_counts(normalize=True)
            filas.append({
                "metodo": metodo,
                "k": k,
                "silueta": silhouette_score(X, etiquetas),
                "min_tamano": fracciones.min(),
                "cumple_tamano": fracciones.min() >= TAMANO_MIN_GRUPO,
            })
    return pd.DataFrame(filas)


def clasificar_silueta(silueta: float) -> str:
    """Interpreta la silueta media con los umbrales del proyecto (Kaufman y Rousseeuw)."""
    if silueta >= SILUETA_RAZONABLE:
        return "estructura razonable"
    if silueta >= SILUETA_DEBIL:
        return "estructura débil"
    return "sin estructura sustancial"


def recomendar_k(tabla: pd.DataFrame) -> pd.Series:
    """Elige la combinación (método, k) de mayor silueta entre las que cumplen el tamaño mínimo.

    Lanza un error si ninguna cumple el criterio "grupos con al menos el 5 % de los días".
    """
    validas = tabla[tabla["cumple_tamano"]]
    if validas.empty:
        raise ValueError("Ningún k cumple el tamaño mínimo de grupo: revisa el rango de k.")
    mejor = validas.loc[validas["silueta"].idxmax()].copy()
    mejor["interpretacion"] = clasificar_silueta(mejor["silueta"])
    return mejor


def agrupar(perfiles: pd.DataFrame, k: int, metodo: str = "kmeans") -> pd.Series:
    """Asigna cada día a un grupo (1 = el más frecuente). Usa todos los días."""
    etiquetas = _ajustar(perfiles.to_numpy(), k, metodo, max_ward=MUESTRA_AGRUPAMIENTO)
    return pd.Series(_ordenar_por_tamano(etiquetas), index=perfiles.index, name="grupo")


def calendario_dias(df: pd.DataFrame) -> pd.DataFrame:
    """Variables de calendario de cada día (region, fecha), tomadas del formato largo."""
    columnas = ["dia_semana", "es_fin_de_semana", "es_festivo", "estacion", "mes"]
    return df.drop_duplicates(["region", "fecha"]).set_index(["region", "fecha"])[columnas]


def describir_grupos(
    perfiles: pd.DataFrame, etiquetas: pd.Series, calendario: pd.DataFrame
) -> pd.DataFrame:
    """Resume cada grupo: tamaño, forma de la curva y composición del calendario.

    Columnas: n_dias, pct_dias, hora_pico, hora_minimo, amplitud (máximo menos mínimo,
    en fracción del promedio del día), pct_fin_de_semana, pct_festivo,
    estacion_dominante, pct_estacion_dominante y cumple_tamano.
    """
    cal = calendario.reindex(perfiles.index)
    curva = perfiles.groupby(etiquetas).mean()
    n = etiquetas.value_counts().sort_index()

    resumen = pd.DataFrame({
        "n_dias": n,
        "pct_dias": n / n.sum() * 100,
        "hora_pico": curva.idxmax(axis=1),
        "hora_minimo": curva.idxmin(axis=1),
        "amplitud": curva.max(axis=1) - curva.min(axis=1),
        "pct_fin_de_semana": cal["es_fin_de_semana"].astype(float).groupby(etiquetas).mean() * 100,
        "pct_festivo": cal["es_festivo"].astype(float).groupby(etiquetas).mean() * 100,
        "estacion_dominante": cal["estacion"].groupby(etiquetas).agg(lambda s: s.mode().iloc[0]),
    })
    resumen["pct_estacion_dominante"] = [
        (cal.loc[etiquetas == g, "estacion"] == resumen.loc[g, "estacion_dominante"]).mean() * 100
        for g in resumen.index
    ]
    resumen["cumple_tamano"] = resumen["pct_dias"] >= TAMANO_MIN_GRUPO * 100
    return resumen


def curvas_grupo(
    perfiles: pd.DataFrame, etiquetas: pd.Series, banda: tuple[float, float] = (0.10, 0.90)
) -> pd.DataFrame:
    """Curva media y banda de dispersión por grupo y hora, en formato largo (para graficar).

    Columnas: grupo, hora, media, inferior, superior.
    """
    g = perfiles.groupby(etiquetas)
    tabla = pd.concat(
        {
            "media": g.mean().stack(),
            "inferior": g.quantile(banda[0]).stack(),
            "superior": g.quantile(banda[1]).stack(),
        },
        axis=1,
    )
    return tabla.reset_index()


def mezcla_por_region(etiquetas: pd.Series) -> pd.DataFrame:
    """Matriz región por tipo de día: porcentaje de días de cada grupo en cada región."""
    region = pd.Series(etiquetas.index.get_level_values("region"), index=etiquetas.index, name="region")
    return pd.crosstab(region, etiquetas, normalize="index") * 100


def tabla_dias(perfiles: pd.DataFrame, etiquetas: pd.Series, nivel: pd.Series) -> pd.DataFrame:
    """Una fila por día y región con su grupo y su nivel en MW (para el calendario del panel)."""
    return pd.concat([etiquetas, nivel], axis=1).reset_index()