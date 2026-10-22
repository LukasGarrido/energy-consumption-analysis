# Documentación del modelo

> Este documento se completa a medida que avanza el proyecto. Los campos marcados como `[por definir]` se llenan al terminar el EDA (Análisis exploratorio) y al elegir los modelos.

---

## 1. Datos de entrada

| Elemento            | Detalle                                                                   |
| ------------------- | ------------------------------------------------------------------------- |
| Regiones utilizadas | `PJME` (zona este de PJM)                                                 |
| Periodo             | 2002-01-01 01:00 → 2018-08-03 00:00                                       |
| Variable objetivo   | Consumo horario en MW                                                     |
| Archivo de entrada  | `data/processed/consumo_horario.parquet`, filtrado por `region == 'PJME'` |
Se eligió `PJME` por ser la región con el historial más largo (16 años completos) y la de mayor tamaño.

---

## 2. Preparación de los datos

### 2.1 Tratamiento de calidad

**Calidad.** Los datos provienen de la limpieza (`02_limpieza.ipynb`): en `PJME` se unificaron 4 duplicados y se agregaron e interpolaron 30 horas (17 de primavera, 12 de otoño y 1 de otra causa). No se aplicó ningún tratamiento adicional.

### 2.2 Variables creadas

|Variable|Tipo|Descripción|
|---|---|---|
|`hora`|Calendario|Hora del día (0 a 23)|
|`dia_semana`|Calendario|0 = lunes, 6 = domingo|
|`mes`|Calendario|1 a 12|
|`es_fin_de_semana`|Calendario|Sábado o domingo|
|`es_festivo`|Calendario|Festivo federal de EE. UU.|
|`MW_lag_24`, `MW_lag_48`, `MW_lag_168`|Historia|Consumo de hace 1 día, 2 días y 1 semana|
|`MW_media_24h`, `MW_media_168h`|Historia|Promedio de las 24 y 168 horas previas, desplazado 24 horas

---

## 3. Diseño del experimento

### 3.1 División de los datos

Por tratarse de una serie de tiempo, la división respeta el orden cronológico: no se mezclan fechas entre entrenamiento y prueba.

|Conjunto|Periodo|
|---|---|
|Entrenamiento|`[por definir]`|
|Validación (si aplica)|`[por definir]`|
|Prueba|`[por definir]`|

---

## 4. Algoritmos

|Modelo|Motivo de elección|Parámetros|
|---|---|---|
|Base 24 h|Referencia mínima: "mañana será como hoy" a la misma hora|N/A|
|Base 168 h|Referencia semanal: "será como la semana pasada"|N/A|
|XGBoost|Funciona bien con datos tabulares, captura relaciones no lineales entre variables y entrena rápido|500 árboles, tasa de aprendizaje 0.05, profundidad 6, `subsample` 0.8, `colsample_bytree` 0.8, `random_state` 42|

Se descartaron Prophet y los modelos ARIMA: con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el alcance del proyecto se centró en comparar contra un modelo base.

---

## 5. Métricas y resultados

Métricas definidas en `06_plan_proyecto.md`: MAE y RMSE (en MW) y MAPE (en %), evaluadas sobre los 13,897 registros de la prueba.

|Modelo|MAE (MW)|RMSE (MW)|MAPE (%)|
|---|---|---|---|
|Base 24 h|2,300.08|3,134.18|7.32|
|Base 168 h|3,511.18|4,793.98|10.99|
|**XGBoost**|**1,862.27**|**2,513.11**|**5.89**|

**Mejora de XGBoost:**

|Frente a|MAE|RMSE|MAPE|
|---|---|---|---|
|Base 24 h|−19.0 %|−19.8 %|−19.5 %|
|Base 168 h|−47.0 %|−47.6 %|−46.4 %|

El MAE de XGBoost equivale a cerca del 6 % del consumo medio de `PJME` (≈ 31 500 MW en el periodo 2013-06 a 2018-08).

**Error por tipo de día (MAE en MW)**

|Tipo de día|Horas|Base 24 h|XGBoost|Mejora|
|---|---|---|---|---|
|Laborable|9,577|2,177.8|1,842.8|15.4 %|
|Fin de semana|3,912|2,556.7|1,909.0|25.3 %|
|Festivo|408|2,708.8|1,872.4|30.9 %|

**Error por hora del día.** Lecturas aproximadas de la gráfica:

- El error de XGBoost es menor de madrugada y por la mañana (≈ 1,500–1,700 MW entre las 0 y las 10 h) y mayor por la tarde-noche (hasta ≈ 2,340 MW hacia las 18 h).
- El modelo base tiene un máximo marcado hacia las 8 h (≈ 2,830 MW): al usar el día anterior, falla en la transición entre laborables y fines de semana. XGBoost casi lo elimina (≈ 1,680 MW).
- Por la tarde ambos modelos mantienen errores altos.

**Error por mes.** Lecturas aproximadas de la gráfica:

- XGBoost tiene el mayor error en junio (≈ 2,430 MW), julio (≈ 2,380), enero (≈ 2,150) y agosto (≈ 2,120).
- El menor error está en noviembre (≈ 1,120), abril (≈ 1,170) y octubre (≈ 1,250).
- En diciembre la ventaja sobre el modelo base casi desaparece (≈ 1,860 frente a ≈ 1,900 MW).
- Enero a agosto aparecen dos veces en la prueba (2017 y 2018) y septiembre a diciembre una sola, así que las comparaciones entre meses no tienen el mismo respaldo

**Los 10 días con mayor error**

|Fecha|MAE XGBoost|MAE Base 24 h|
|---|---|---|
|2017-05-20|7,776.6|11,804.0|
|2018-06-03|6,614.6|7,221.8|
|2018-07-07|6,328.3|10,218.8|
|2017-07-29|5,498.8|6,634.8|
|2018-01-11|5,171.9|3,488.7|
|2017-03-15|5,127.2|3,518.2|
|2017-01-11|4,921.9|6,336.6|
|2018-01-05|4,889.6|3,132.8|
|2017-09-28|4,853.6|5,367.5|
|2017-12-31|4,814.5|1,748.6|

Ninguno es festivo. En 4 de los 10 días (2018-01-11, 2017-03-15, 2018-01-05 y 2017-12-31) el modelo base **supera** a XGBoost. Son fechas de invierno, época de olas de frío (hipótesis, sin verificar con datos de temperatura).

**Importancia de las variables**

|Variable|Importancia|
|---|---|
|`MW_lag_24`|0.711|
|`MW_lag_168`|0.091|
|`es_fin_de_semana`|0.081|
|`dia_semana`|0.039|
|`hora`|0.020|
|`es_festivo`|0.019|
|`MW_lag_48`|0.012|
|`mes`|0.011|
|`MW_media_24h`|0.009|
|`MW_media_168h`|0.007|

### Interpretación

XGBoost reduce el error cerca de un 19 % respecto al modelo base de 24 horas y casi un 47 % respecto al semanal. La mejora es moderada: el 71 % de la importancia recae en el consumo del día anterior a la misma hora, por lo que el modelo es esencialmente "ayer" con correcciones por tipo de día. Esas correcciones explican dónde gana más: en la transición matutina entre laborables y fines de semana y en los festivos, donde la referencia del día anterior es peor.

Donde menos mejora es en los episodios de clima extremo. Las variables disponibles (calendario e historial) no contienen información sobre la temperatura, que es el principal determinante de la demanda, y los errores más altos se concentran en la tarde-noche, en los meses de verano y en las olas de frío.

Un MAPE de 5.89 % para un pronóstico con 24 horas de antelación es un resultado razonable y no hay señales de fuga de datos: un error cercano a cero habría sido sospechoso.

---

## 6. Limitaciones

- **Sin temperatura.** Es el principal determinante de la demanda y el dataset no la incluye. Los picos extremos son los más difíciles de pronosticar.
- **Los árboles no extrapolan.** Un modelo de árboles no predice valores fuera del rango que vio en el entrenamiento, lo que podría explicar los errores en olas de frío intensas (hipótesis).
- **Una sola partición temporal.** Los resultados dependen del periodo de prueba (2017-01 a 2018-08).
- **Una sola región.** El modelo se entrenó con `PJME`; para otras regiones hay que repetir el proceso.
- **Festivos federales.** No se incluyen los festivos de cada estado.
- **Hiperparámetros por defecto.** XGBoost no se ajustó con búsqueda de parámetros.
- **Convención horaria.** `Datetime` marca el final de la hora. Para la fila de las 00:00, el día de la semana, el fin de semana y el festivo quedan desplazados un día (1 de cada 24 horas)

---

## 7. Reproducibilidad

El código está en `notebooks/04_modelado.ipynb`, `src/modeling.py` y `src/features.py`. Los parámetros del experimento están en `src/config.py` (`HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `SEMILLA`). Los pasos para ejecutarlo están en la guía de usuario.