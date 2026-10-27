# Documentación del modelo

Este documento describe los tres componentes analíticos del proyecto y cómo se evalúan.

| Parte | Tema | Pregunta | Notebook | Estado |
|---|---|---|---|---|
| A | Pronóstico de referencia a 24 horas | P4 y base de P3 | 04 | Hecho; ampliación por hacer |
| B | Agrupamiento de perfiles diarios | P1 y P2 | 05 | Por hacer |
| C | Detección de días atípicos | P3 | 06 | Por hacer |

---

# Parte A. Pronóstico de referencia

> Las cifras de esta parte corresponden a la versión actual, con las variables de calendario calculadas desde `Datetime` tal como viene. Si se adopta el día operativo (`Datetime` − 1 h), hay que repetir el notebook 04 y actualizar estos valores.

## 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Región | `PJME` (zona este de PJM) |
| Periodo | 2002-01-01 01:00 → 2018-08-03 00:00 |
| Filas | 145,392 (serie horaria regular, sin vacíos) |
| Variable objetivo | Consumo horario en MW |
| Archivo de entrada | `data/processed/consumo_horario.parquet`, filtrado por `region == 'PJME'` |

Se eligió `PJME` por ser la región con el historial más largo (16 años completos) y la de mayor tamaño.

## 2. Preparación de los datos

**Calidad.** Los datos provienen de la limpieza (`02_limpieza.ipynb`): en `PJME` se unificaron 4 duplicados y se agregaron e interpolaron 30 horas (17 de primavera, 12 de otoño y 1 de otra causa). No se aplicó ningún tratamiento adicional.

**Variables creadas.**

| Variable | Tipo | Descripción |
|---|---|---|
| `hora` | Calendario | Hora del día (0 a 23) |
| `dia_semana` | Calendario | 0 = lunes, 6 = domingo |
| `mes` | Calendario | 1 a 12 |
| `es_fin_de_semana` | Calendario | Sábado o domingo |
| `es_festivo` | Calendario | Festivo federal de EE. UU. |
| `MW_lag_24`, `MW_lag_48`, `MW_lag_168` | Historia | Consumo de hace 1 día, 2 días y 1 semana |
| `MW_media_24h`, `MW_media_168h` | Historia | Promedio de las 24 y 168 horas previas, desplazado 24 horas |

**Variables excluidas:**

- `anio`: los árboles de decisión no extrapolan a años que no vieron en el entrenamiento.
- `MW_rel`: usa el promedio de toda la región, incluido el futuro.
- `estacion`: es texto y `mes` ya contiene esa información.

Las primeras 191 filas (24 + 168 − 1) se descartan porque no tienen historia suficiente para calcular los rezagos y las medias móviles.

## 3. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Horizonte | 24 horas: para predecir la hora *t* solo se usa información hasta *t − 24* |
| Entrenamiento | 2002-01-01 → 2016-12-31 (131,495 filas; 131,304 tras descartar las sin historia) |
| Prueba | 2017-01-01 → 2018-08-03 (13,897 filas, unos 19 meses) |
| División | Cronológica, nunca al azar |
| Modelos base | Consumo de hace 24 horas y de hace 168 horas |
| Semilla | 42 |

**Control de fuga de datos.** Todos los rezagos son de 24 horas o más, y las medias móviles se desplazan 24 horas. `agregar_rezagos` lanza un error si algún rezago es menor que el horizonte. Los rezagos se calcularon antes de dividir, de modo que las primeras horas de la prueba usan el final del entrenamiento, información que existiría en la práctica.

**Ampliación prevista (por hacer).** La partición única (2017-01-01) se amplía a una validación en ventana móvil por años, con al menos 3 pliegues. El modelo debe superar al base en todos los pliegues. Se añade el MASE (error escalado por el pronóstico ingenuo), que debe ser menor que 1. Los residuos fuera de muestra de todo el historial alimentan la Parte C.

## 4. Algoritmos

| Modelo | Motivo de elección | Parámetros |
|---|---|---|
| Base 24 h | Referencia mínima: "mañana será como hoy" a la misma hora | N/A |
| Base 168 h | Referencia semanal: "será como la semana pasada" | N/A |
| XGBoost | Funciona bien con datos tabulares, captura relaciones no lineales entre variables y entrena rápido | 500 árboles, tasa de aprendizaje 0.05, profundidad 6, `subsample` 0.8, `colsample_bytree` 0.8, `random_state` 42 |

Se descartaron Prophet y los modelos ARIMA: con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.

## 5. Métricas y resultados

Métricas definidas en `06_plan_proyecto.md`: MAE y RMSE (en MW) y MAPE (en %), evaluadas sobre los 13,897 registros de la prueba.

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) |
|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 |
| **XGBoost** | **1,862.27** | **2,513.11** | **5.89** |

**Mejora de XGBoost**

| Frente a | MAE | RMSE | MAPE |
|---|---|---|---|
| Base 24 h | −19.0 % | −19.8 % | −19.5 % |
| Base 168 h | −47.0 % | −47.6 % | −46.4 % |

El MAE de XGBoost equivale a cerca del 6 % del consumo medio de `PJME` (≈ 31 500 MW en el periodo 2013-06 a 2018-08).

**Error por tipo de día (MAE en MW)**

| Tipo de día | Horas | Base 24 h | XGBoost | Mejora |
|---|---|---|---|---|
| Laborable | 9,577 | 2,177.8 | 1,842.8 | 15.4 % |
| Fin de semana | 3,912 | 2,556.7 | 1,909.0 | 25.3 % |
| Festivo | 408 | 2,708.8 | 1,872.4 | 30.9 % |

**Error por hora del día.** Lecturas aproximadas de la gráfica:

- El error de XGBoost es menor de madrugada y por la mañana (≈ 1,500–1,700 MW entre las 0 y las 10 h) y mayor por la tarde-noche (hasta ≈ 2,340 MW hacia las 18 h).
- El modelo base tiene un máximo marcado hacia las 8 h (≈ 2,830 MW): al usar el día anterior, falla en la transición entre laborables y fines de semana. XGBoost casi lo elimina (≈ 1,680 MW).
- Por la tarde ambos modelos mantienen errores altos.

**Error por mes.** Lecturas aproximadas de la gráfica:

- XGBoost tiene el mayor error en junio (≈ 2,430 MW), julio (≈ 2,380), enero (≈ 2,150) y agosto (≈ 2,120).
- El menor error está en noviembre (≈ 1,120), abril (≈ 1,170) y octubre (≈ 1,250).
- En diciembre la ventaja sobre el modelo base casi desaparece (≈ 1,860 frente a ≈ 1,900 MW).
- Enero a agosto aparecen dos veces en la prueba (2017 y 2018) y septiembre a diciembre una sola, así que las comparaciones entre meses no tienen el mismo respaldo.

**Los 10 días con mayor error**

| Fecha | MAE XGBoost | MAE Base 24 h |
|---|---|---|
| 2017-05-20 | 7,776.6 | 11,804.0 |
| 2018-06-03 | 6,614.6 | 7,221.8 |
| 2018-07-07 | 6,328.3 | 10,218.8 |
| 2017-07-29 | 5,498.8 | 6,634.8 |
| 2018-01-11 | 5,171.9 | 3,488.7 |
| 2017-03-15 | 5,127.2 | 3,518.2 |
| 2017-01-11 | 4,921.9 | 6,336.6 |
| 2018-01-05 | 4,889.6 | 3,132.8 |
| 2017-09-28 | 4,853.6 | 5,367.5 |
| 2017-12-31 | 4,814.5 | 1,748.6 |

Ninguno es festivo. En 4 de los 10 días (2018-01-11, 2017-03-15, 2018-01-05 y 2017-12-31) el modelo base **supera** a XGBoost. Son fechas de invierno, época de olas de frío (hipótesis, sin verificar con datos de temperatura). El día de mayor error (2017-05-20, un sábado) tiene un MAE cercano al 25 % del consumo medio y se revisará para descartar un error de datos.

**Importancia de las variables**

| Variable | Importancia |
|---|---|
| `MW_lag_24` | 0.711 |
| `MW_lag_168` | 0.091 |
| `es_fin_de_semana` | 0.081 |
| `dia_semana` | 0.039 |
| `hora` | 0.020 |
| `es_festivo` | 0.019 |
| `MW_lag_48` | 0.012 |
| `mes` | 0.011 |
| `MW_media_24h` | 0.009 |
| `MW_media_168h` | 0.007 |

### Interpretación

XGBoost reduce el error cerca de un 19 % respecto al modelo base de 24 horas y casi un 47 % respecto al semanal. La mejora es moderada: el 71 % de la importancia recae en el consumo del día anterior a la misma hora, por lo que el modelo es esencialmente "ayer" con correcciones por tipo de día. Esas correcciones explican dónde gana más: en la transición matutina entre laborables y fines de semana y en los festivos, donde la referencia del día anterior es peor.

Donde menos mejora es en los episodios de clima extremo. Las variables disponibles (calendario e historial) no contienen información sobre la temperatura, que es el principal determinante de la demanda, y los errores más altos se concentran en la tarde-noche, en los meses de verano y en las olas de frío.

Un MAPE de 5.89 % para un pronóstico con 24 horas de antelación es un resultado razonable y no hay señales de fuga de datos: un error cercano a cero habría sido sospechoso.

## 6. Limitaciones

- **Sin temperatura.** Es el principal determinante de la demanda y el dataset no la incluye. Los picos extremos son los más difíciles de pronosticar.
- **Los árboles no extrapolan.** Un modelo de árboles no predice valores fuera del rango que vio en el entrenamiento, lo que podría explicar los errores en olas de frío intensas (hipótesis).
- **Una sola partición temporal.** Los resultados dependen del periodo de prueba (2017-01 a 2018-08); se corregirá con la ventana móvil.
- **Una sola región.** El modelo se entrenó con `PJME`; para otras regiones hay que repetir el proceso. Los residuos fuera de muestra exigen entrenar un modelo por región y pliegue, por lo que se empieza con `PJME`.
- **Festivos federales.** No se incluyen los festivos de cada estado.
- **Hiperparámetros por defecto.** XGBoost no se ajustó con búsqueda de parámetros.
- **Convención horaria.** `Datetime` marca el final de la hora. Para la fila de las 00:00, el día de la semana, el fin de semana y el festivo quedan desplazados un día (1 de cada 24 horas).

## 7. Reproducibilidad

El código está en `notebooks/04_modelado.ipynb`, `src/modeling.py` y `src/features.py`. Los parámetros del experimento están en `src/config.py` (`HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `SEMILLA`). Los pasos para ejecutarlo están en la [guía de usuario](09_guia_usuario.md).

---

# Parte B. Agrupamiento de perfiles diarios (por hacer)

> No confundir con la variable `tipo_dia` de los notebooks 03 y 04 (laborable, fin de semana, festivo), que se define por el calendario. Aquí el tipo de día lo descubre el agrupamiento a partir de la forma de la curva.

## 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Unidad de análisis | Un día de una región (unos 45,000 perfiles) |
| Perfil | 24 valores, uno por hora, del día operativo |
| Normalización | Cada valor se divide entre el promedio de su día, para capturar la forma y no el tamaño |
| Magnitud | El consumo medio diario se analiza aparte |
| Días incluidos | Solo días completos (24 horas) |

## 2. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Algoritmos | K-medias y agrupamiento jerárquico (criterio de Ward) |
| Rango de k | 2 a 10 |
| Selección de k | Mayor silueta media |
| Calidad de la estructura | Razonable si la silueta es ≥ 0.50; débil entre 0.26 y 0.50, y se reporta como tal |
| Tamaño mínimo | Ningún grupo con menos del 5 % de los días |
| Estabilidad | Se repite con distintas semillas y debe mantenerse la solución |
| Interpretación | Cada grupo se describe con su curva media, su banda de dispersión (percentiles 10 a 90), su frecuencia y su relación con el calendario (día de la semana, mes y festivo) |

## 3. Resultados

| Concepto | Valor |
|---|---|
| Algoritmo elegido | `[completar]` |
| k elegido | `[completar]` |
| Silueta media | `[completar]` |
| Descripción de cada grupo | `[completar]` |
| Mezcla de tipos de día por región | `[completar]` |

## 4. Limitaciones

- K-medias asume grupos compactos con distancia euclidiana, y los perfiles diarios forman en parte un continuo: la estructura puede resultar débil.
- Al normalizar por el promedio del día se pierde la información de magnitud.
- La definición del día depende de la convención horaria adoptada.

## 5. Reproducibilidad

El código estará en `notebooks/05_agrupamiento.ipynb` y `src/profiles.py` (por crear). Los parámetros (`K_RANGO`, `TAMANO_MIN_GRUPO`, `SEMILLA`) estarán en `src/config.py`.

---

# Parte C. Detección de días atípicos (por hacer)

## 1. Definición

Un día es atípico si su demanda se aleja de lo esperable. Lo esperable lo da el modelo de pronóstico de la Parte A, evaluado fuera de muestra en todo el historial mediante la ventana móvil.

## 2. Diseño

| Elemento | Decisión |
|---|---|
| Residuo | Diferencia entre la demanda observada y la pronosticada |
| Residuo diario | Error absoluto medio de las 24 horas del día |
| Umbral | z modificado del residuo diario > 3.5, con z = 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana |
| Validación | Contraste con episodios externos (olas de calor o frío, huracanes). Los datos no traen etiquetas de anomalías |
| Complemento | Distancia de cada día al centro de su grupo (Parte B) |

## 3. Resultados

| Concepto | Valor |
|---|---|
| Número de días atípicos | `[completar]` |
| Episodios recuperados | `[completar]` |
| Días atípicos compartidos entre regiones | `[completar]` |

## 4. Limitaciones

- Sin temperatura, las anomalías solo pueden interpretarse por coincidencia con eventos.
- Un residuo grande también puede deberse a un error de los datos; por eso se revisan las horas vecinas antes de concluir.
- No hay verdad de referencia con la que medir la detección.

## 5. Reproducibilidad

El código estará en `notebooks/06_anomalias.ipynb` y `src/anomalies.py` (por crear). El umbral (`UMBRAL_Z_MODIFICADO`) estará en `src/config.py`.