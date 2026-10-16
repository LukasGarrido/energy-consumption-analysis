"""
/src/modeling.py: preparación de datos, modelos de pronóstico y métricas.

Flujo de uso (pronóstico a HORIZONTE_HORAS horas):

    features.agregar_variables_temporales -> features.agregar_rezagos
    -> features.agregar_medias_moviles -> dividir_train_test
    -> construir_X_y -> entrenar_xgboost -> predecir -> comparar_modelos
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from src.config import FECHA_CORTE, SEMILLA

# Variables de calendario: se conocen de antemano, así que no hay fuga de datos.
# No se incluyen `anio` (los árboles no extrapolan a años no vistos) ni `MW_rel`
# (usa el promedio de toda la región, incluido el futuro).
VARIABLES_CALENDARIO = ["hora", "dia_semana", "mes", "es_fin_de_semana", "es_festivo"]
PREFIJOS_HISTORIA = ("MW_lag_", "MW_media_")


def seleccionar_variables(df: pd.DataFrame) -> list[str]:
    """Devuelve las variables permitidas para modelar: calendario + rezagos y medias móviles."""
    faltan = [c for c in VARIABLES_CALENDARIO if c not in df.columns]
    if faltan:
        raise KeyError(f"Faltan variables {faltan}: ejecuta agregar_variables_temporales.")

    historia = [c for c in df.columns if c.startswith(PREFIJOS_HISTORIA)]
    return VARIABLES_CALENDARIO + historia


def dividir_train_test(df: pd.DataFrame, fecha_corte: str = FECHA_CORTE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide por fecha (nunca al azar): antes del corte entrena, desde el corte prueba."""
    corte = pd.Timestamp(fecha_corte)
    train = df[df["Datetime"] < corte]
    test = df[df["Datetime"] >= corte]

    if train.empty or test.empty:
        raise ValueError(f"La fecha de corte {fecha_corte} deja un conjunto vacío.")

    print(
        f"Entrenamiento: {len(train):,} filas ({train['Datetime'].min():%Y-%m-%d} → {train['Datetime'].max():%Y-%m-%d})\n"
        f"Prueba:        {len(test):,} filas ({test['Datetime'].min():%Y-%m-%d} → {test['Datetime'].max():%Y-%m-%d})"
    )
    return train, test


def construir_X_y(
    df: pd.DataFrame, variables: list[str] | None = None, objetivo: str = "MW"
) -> tuple[pd.DataFrame, pd.Series]:
    """Separa las variables (X) del objetivo (y), descartando filas con vacíos.

    Los rezagos dejan vacías las primeras filas de cada región. El índice original
    se conserva para poder recuperar la fecha de cada predicción.
    """
    variables = variables or seleccionar_variables(df)
    datos = df.dropna(subset=variables + [objetivo])

    print(f"Filas descartadas por vacíos en las variables: {len(df) - len(datos):,}")
    return datos[variables], datos[objetivo]


def pronostico_base(df: pd.DataFrame, rezago: int = 24) -> pd.Series:
    """Modelo base: predice el consumo de hace `rezago` horas (24 = ayer a la misma hora).

    Usa la columna MW_lag_<rezago>, que debe haberse creado antes con agregar_rezagos.
    """
    columna = f"MW_lag_{rezago}"
    if columna not in df.columns:
        raise KeyError(f"Falta {columna}: ejecuta agregar_rezagos con ese rezago.")
    return df[columna].rename(f"base_{rezago}h")


def entrenar_xgboost(X_train: pd.DataFrame, y_train: pd.Series, **parametros) -> XGBRegressor:
    """Entrena un XGBRegressor. Los `parametros` sobrescriben los valores por defecto."""
    por_defecto = dict(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=SEMILLA,
        n_jobs=-1,
    )
    modelo = XGBRegressor(**{**por_defecto, **parametros})
    modelo.fit(X_train, y_train)
    return modelo


def predecir(modelo, X: pd.DataFrame) -> pd.Series:
    """Devuelve las predicciones como Series con el mismo índice que X."""
    return pd.Series(modelo.predict(X), index=X.index, name="prediccion")


def calcular_metricas(real: pd.Series, predicho: pd.Series) -> pd.Series:
    """Calcula MAE y RMSE (en MW) y MAPE (en %) sobre las filas con ambos valores."""
    real, predicho = real.align(predicho, join="inner")
    validos = real.notna() & predicho.notna()
    real, predicho = real[validos], predicho[validos]

    error = predicho - real
    return pd.Series({
        "MAE": error.abs().mean(),
        "RMSE": np.sqrt((error ** 2).mean()),
        "MAPE_%": (error.abs() / real).mean() * 100,
    })


def comparar_modelos(real: pd.Series, predicciones: dict[str, pd.Series]) -> pd.DataFrame:
    """Tabla de métricas por modelo, calculadas sobre las mismas filas para que sean comparables."""
    tabla = pd.DataFrame(predicciones).dropna()
    real = real.reindex(tabla.index)
    return pd.DataFrame({nombre: calcular_metricas(real, tabla[nombre]) for nombre in tabla}).T


def importancia_variables(modelo, variables: list[str]) -> pd.DataFrame:
    """Importancia de cada variable según el modelo, de mayor a menor."""
    importancia = pd.Series(modelo.feature_importances_, index=variables, name="importancia")
    return importancia.sort_values(ascending=False).to_frame()
