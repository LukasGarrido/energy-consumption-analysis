"""
/src/modeling.py: preparación de datos, modelos de pronóstico y métricas.

Flujo de uso (pronóstico a HORIZONTE_HORAS horas, UNA región a la vez):

    features.agregar_variables_temporales -> features.agregar_rezagos
    -> features.agregar_medias_moviles -> dividir_train_test
    -> construir_X_y -> entrenar_xgboost -> predecir -> comparar_modelos

Validación en ventana móvil: validar_ventana_movil repite el entrenamiento y la
prueba en varios pliegues cronológicos y devuelve métricas y residuos fuera de muestra.
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from src.config import FECHA_CORTE, MESES_PLIEGUE, N_PLIEGUES, SEMILLA

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


def escala_ingenua(real_train: pd.Series, estacionalidad: int = 24) -> float:
    """Error absoluto medio del pronóstico ingenuo estacional dentro del entrenamiento.

    Es el denominador del MASE (Hyndman y Koehler). `real_train` debe ser la serie
    de UNA región, en orden cronológico y sin huecos.
    """
    escala = real_train.diff(estacionalidad).abs().mean()
    if not np.isfinite(escala) or escala == 0:
        raise ValueError("No se puede calcular la escala ingenua del entrenamiento.")
    return float(escala)


def calcular_metricas(
    real: pd.Series,
    predicho: pd.Series,
    real_train: pd.Series | None = None,
    estacionalidad: int = 24,
) -> pd.Series:
    """Calcula MAE y RMSE (en MW), MAPE (en %) y, si se da `real_train`, MASE.

    MASE < 1 significa que el modelo se equivoca menos que el pronóstico ingenuo
    estacional (ayer a la misma hora, si estacionalidad = 24) medido en el entrenamiento.
    """
    real, predicho = real.align(predicho, join="inner")
    validos = real.notna() & predicho.notna()
    real, predicho = real[validos], predicho[validos]

    error = predicho - real
    mae = error.abs().mean()
    metricas = {
        "MAE": mae,
        "RMSE": np.sqrt((error ** 2).mean()),
        "MAPE_%": (error.abs() / real).mean() * 100,
    }
    if real_train is not None:
        metricas["MASE"] = mae / escala_ingenua(real_train, estacionalidad)
    return pd.Series(metricas)


def comparar_modelos(
    real: pd.Series,
    predicciones: dict[str, pd.Series],
    real_train: pd.Series | None = None,
) -> pd.DataFrame:
    """Tabla de métricas por modelo, calculadas sobre las mismas filas para que sean comparables."""
    tabla = pd.DataFrame(predicciones).dropna()
    real = real.reindex(tabla.index)
    return pd.DataFrame(
        {nombre: calcular_metricas(real, tabla[nombre], real_train) for nombre in tabla}
    ).T


def validar_ventana_movil(
    df: pd.DataFrame,
    n_pliegues: int = N_PLIEGUES,
    meses_prueba: int = MESES_PLIEGUE,
    rezago_base: int = 24,
    **parametros,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validación en ventana móvil (origen móvil con entrenamiento creciente).

    Los pliegues son bloques consecutivos de `meses_prueba` meses que terminan en
    la última fecha del DataFrame. En cada pliegue se entrena con todo lo anterior
    al bloque y se prueba en el bloque, así que los bloques no se solapan y cada
    hora se predice una sola vez, siempre fuera de muestra.

    `df` debe ser de UNA región, con variables de calendario, rezagos y medias móviles.

    Devuelve:
      - metricas: una fila por pliegue y modelo (XGBoost y base), con MAE, RMSE,
        MAPE_% y MASE, más la mejora del MAE frente al base.
      - residuos: Datetime, real, prediccion, residuo (real - prediccion), pliegue.
        Un residuo positivo indica demanda por encima de lo esperable.
    """
    if "region" in df.columns and df["region"].nunique() > 1:
        raise ValueError("Pasa los datos de una sola región.")

    df = df.sort_values("Datetime")
    variables = seleccionar_variables(df)
    fin = df["Datetime"].max() + pd.Timedelta(hours=1)

    filas, residuos = [], []
    for i in range(n_pliegues):
        inicio_test = fin - pd.DateOffset(months=meses_prueba * (n_pliegues - i))
        fin_test = fin - pd.DateOffset(months=meses_prueba * (n_pliegues - i - 1))

        train = df[df["Datetime"] < inicio_test]
        test = df[(df["Datetime"] >= inicio_test) & (df["Datetime"] < fin_test)]
        if train.empty or test.empty:
            raise ValueError(f"El pliegue {i + 1} deja un conjunto vacío: reduce n_pliegues o meses_prueba.")

        X_train, y_train = construir_X_y(train, variables)
        X_test, y_test = construir_X_y(test, variables)

        modelo = entrenar_xgboost(X_train, y_train, **parametros)
        prediccion = predecir(modelo, X_test)
        base = pronostico_base(test, rezago_base).reindex(X_test.index)

        for nombre, pred in {"XGBoost": prediccion, "Base": base}.items():
            m = calcular_metricas(y_test, pred, train["MW"])
            m["pliegue"] = i + 1
            m["modelo"] = nombre
            m["inicio_prueba"] = inicio_test.normalize()
            m["fin_prueba"] = fin_test.normalize()
            filas.append(m)

        residuos.append(pd.DataFrame({
            "Datetime": df.loc[X_test.index, "Datetime"],
            "real": y_test,
            "prediccion": prediccion,
            "residuo": y_test - prediccion,
            "pliegue": i + 1,
        }))

    metricas = pd.DataFrame(filas).set_index(["pliegue", "modelo"])

    # Mejora del MAE de XGBoost frente al base, por pliegue
    mae = metricas["MAE"].unstack("modelo")
    metricas["mejora_MAE_%"] = np.nan
    for p in mae.index:
        metricas.loc[(p, "XGBoost"), "mejora_MAE_%"] = (mae.loc[p, "XGBoost"] / mae.loc[p, "Base"] - 1) * 100

    supera = (mae["XGBoost"] < mae["Base"]).all()
    print(f"El modelo supera al base en todos los pliegues: {supera}")

    return metricas, pd.concat(residuos).sort_values("Datetime")


def importancia_variables(modelo, variables: list[str]) -> pd.DataFrame:
    """Importancia de cada variable según el modelo, de mayor a menor."""
    importancia = pd.Series(modelo.feature_importances_, index=variables, name="importancia")
    return importancia.sort_values(ascending=False).to_frame()