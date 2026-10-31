# Documentación del modelo

Este documento describe los tres componentes analíticos del proyecto y cómo se evalúan.

| Parte | Tema | Pregunta | Notebook | Estado |
|---|---|---|---|---|
| A | Pronóstico de referencia a 24 horas | P4 y base de P3 | 04 | Hecho, con ventana móvil y MASE |
| B | Agrupamiento de perfiles diarios | P1 y P2 | 05 | Implementado, resultados por documentar |
| C | Detección de días atípicos | P3 | 06 | Implementado, resultados por documentar |

---

# Parte A. Pronóstico de referencia

> Las cifras de la sección 5 se calcularon con las variables de calendario desde `Datetime` tal como viene (hora de fin). El notebook 04 ya usa el día operativo (`Datetime − 1 h`): sustituir estas cifras por las salidas nuevas. Mientras tanto, se marcan como **por recalcular**.

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
| `fecha` | Calendario | Día operativo (`Datetime − 1 h`), no entra al modelo, sirve para agrupar por día |
| `hora` | Calendario | Hora del día (0 a 23) |
| `dia_semana` | Calendario | 0 = lunes, 6 = domingo |
| `mes` | Calendario | 1 a 12 |
| `es_fin_de_semana` | Calendario | Sábado o domingo |
| `es_festivo` | Calendario | Festivo federal de EE. UU. |
| `MW_lag_24`, `MW_lag_48`, `MW_lag_168` | Historia | Consumo de hace 1 día, 2 días y 1 semana |
| `MW_media_24h`, `MW_media_168h` | Historia | Promedio de las 24 y 168 horas previas, desplazado 24 horas |

Todas las variables de calendario se calculan con el día operativo: `hora` va de 0 (00:00–01:00) a 23 (23:00–24:00).

**Variables excluidas:**

- `anio`: los árboles de decisión no extrapolan a años que no vieron en el entrenamiento.
- `MW_rel`: usa el promedio de toda la región, incluido el futuro.
- `estacion`: es texto y `mes` ya contiene esa información.

Las primeras 191 filas (24 + 168 − 1) se descartan porque no tienen historia suficiente para calcular los rezagos y las medias móviles.

## 3. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Horizonte | 24 horas: para predecir la hora *t* solo se usa información hasta *t − 24* |
| Entrenamiento | 2002-01-01 → 2016-12-31 (131,495 filas, 131,304 tras descartar las sin historia), por recalcular |
| Prueba | 2017-01-01 → 2018-08-03 (13,897 filas, unos 19 meses), por recalcular |
| División | Cronológica, nunca al azar |
| Modelos base | Consumo de hace 24 horas y de hace 168 horas |
| Validación | Ventana móvil con entrenamiento creciente: 6 pliegues de 12 meses (mínimo 3) |
| Métrica de escala | MASE con la escala del pronóstico ingenuo estacional de 24 h |
| Semilla | 42 |

**Control de fuga de datos.** Todos los rezagos son de 24 horas o más, y las medias móviles se desplazan 24 horas. `agregar_rezagos` lanza un error si algún rezago es menor que el horizonte. Los rezagos se calcularon antes de dividir, de modo que las primeras horas de la prueba usan el final del entrenamiento, información que existiría en la práctica.

Con la hora de fin, la prueba de la partición única empieza en `2017-01-01 00:00`, que es la hora 23 del 2016-12-31. Ese primer día queda incompleto y se excluye del análisis por día.

**Validación en ventana móvil (implementada).** Los pliegues son bloques consecutivos de 12 meses que terminan el 2018-08-03: en cada uno se entrena con todo lo anterior y se prueba en el bloque. Los bloques no se solapan, así que cada hora se predice una sola vez fuera de muestra. Con 6 pliegues, los residuos cubren **2012-08 → 2018-08**, que incluye el huracán Sandy, el vórtice polar de 2014 y el frío de 2015. Criterio: XGBoost supera al base en todos los pliegues y su MASE es menor que 1. Los residuos (`real − predicción`) se guardan en `data/processed/residuos_PJME.parquet` y alimentan la Parte C.

## 4. Algoritmos

| Modelo | Motivo de elección | Parámetros |
|---|---|---|
| Base 24 h | Referencia mínima: "mañana será como hoy" a la misma hora | N/A |
| Base 168 h | Referencia semanal: "será como la semana pasada" | N/A |
| XGBoost | Funciona bien con datos tabulares, captura relaciones no lineales entre variables y entrena rápido | 500 árboles, tasa de aprendizaje 0.05, profundidad 6, `subsample` 0.8, `colsample_bytree` 0.8, `random_state` 42 |

Se descartaron Prophet y los modelos ARIMA: con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.

## 5. Métricas y resultados

Métricas definidas en `06_plan_proyecto.md`: MAE y RMSE (en MW), MAPE (en %) y MASE, evaluadas sobre los 13,897 registros de la prueba (partición única). **Cifras por recalcular con el día operativo.**

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) |
|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 |
| **XGBoost** | **1,862.27** | **2,513.11** | **5.89** |

**MASE (partición única)**

| Modelo | MASE |
|---|---|
| Base 24 h | `[completar]` |
| Base 168 h | `[completar]` |
| XGBoost | `[completar]` |

El MASE se calcula con la escala del pronóstico ingenuo de 24 h incluso para el modelo base de 168 h. Menor que 1 significa que el modelo se equivoca menos que ese pronóstico ingenuo.

**Mejora de XGBoost**

| Frente a | MAE | RMSE | MAPE |
|---|---|---|---|
| Base 24 h | −19.0 % | −19.8 % | −19.5 % |
| Base 168 h | −47.0 % | −47.6 % | −46.4 % |

El MAE de XGBoost equivale a cerca del 6 % del consumo medio de `PJME` (≈ 31 500 MW en el periodo 2013-06 a 2018-08).

**Validación en ventana móvil (6 pliegues de 12 meses)**

| Pliegue | Prueba | MAE XGBoost (MW) | MAE base (MW) | Mejora (%) | MASE XGBoost |
|---|---|---|---|---|---|
| 1 a 6 | `[completar]` | `[completar]` | `[completar]` | `[completar]` | `[completar]` |

¿XGBoost supera al base en todos los pliegues? `[completar]`

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

Las horas de esta lectura estaban en hora de fin y deben desplazarse 1 h al recalcular con el día operativo.

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
- **Pliegues de 12 meses.** La ventana móvil reduce la dependencia de un solo periodo, pero cada pliegue es un año concreto con su clima, y los primeros entrenan con menos historia que los últimos.
- **Una sola región.** El modelo y los residuos son de `PJME`, para otras regiones hay que repetir el proceso, y entrenar un modelo por región y pliegue es lento.
- **Festivos federales.** No se incluyen los festivos de cada estado.
- **Hiperparámetros por defecto.** XGBoost no se ajustó con búsqueda de parámetros.
- **Convención horaria.** `Datetime` marca el final de la hora. Se resolvió con el día operativo (decisión D1), las cifras de esta parte deben recalcularse con él.

## 7. Reproducibilidad

El código está en `notebooks/04_modelado.ipynb`, `src/modeling.py` y `src/features.py`. Los parámetros del experimento están en `src/config.py` (`HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `N_PLIEGUES`, `MESES_PLIEGUE`, `SEMILLA`). Salidas: `residuos_PJME.parquet` y `metricas_ventana_movil_PJME.parquet` en `data/processed/`. Los pasos para ejecutarlo están en la [guía de usuario](09_guia_usuario.md).

---

# Parte B. Agrupamiento de perfiles diarios

> No confundir con la variable `tipo_dia` de los notebooks 03 y 04 (laborable, fin de semana, festivo), que se define por el calendario. Aquí el tipo de día lo descubre el agrupamiento a partir de la forma de la curva.

## 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Unidad de análisis | Un día de una región (unos 45,000 perfiles) |
| Perfil | 24 valores, uno por hora, del día operativo (`Datetime − 1 h`) |
| Normalización | Cada valor se divide entre el promedio de su día, para capturar la forma y no el tamaño |
| Magnitud | El consumo medio diario (`MW_medio_dia`) se guarda aparte |
| Días incluidos | Solo días completos (24 horas) |
| Alcance | Las 12 regiones juntas, de modo que los tipos de día son los mismos y se puede construir la matriz región por tipo de día |

## 2. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Algoritmos | K-medias y agrupamiento jerárquico (criterio de Ward) |
| Rango de k | 2 a 10 (`K_MIN`, `K_MAX`) |
| Muestra | La silueta y Ward se calculan sobre una muestra reproducible de 10,000 días (`MUESTRA_AGRUPAMIENTO`), porque escalan de forma cuadrática. Ward asigna el resto de los días al centro más cercano, k-medias usa todos |
| Selección de k | Mayor silueta media entre las combinaciones en que ningún grupo baja del 5 % de los días |
| Calidad de la estructura | Kaufman y Rousseeuw: 0.71 o más, fuerte, 0.51 a 0.70, razonable, 0.26 a 0.50, débil, 0.25 o menos, sin estructura sustancial. Se reporta tal como sale |
| Estabilidad | Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado). La repetición con distintas semillas queda por hacer |
| Alineación horaria | Parámetro `ALINEAR_HORA_CENTRAL`: la curva de `COMED` (y quizá `NI`) llega una hora más tarde, con `True` se les resta 1 h antes de calcular el día operativo. El notebook mide el desfase de cada región para decidir (decisión D7) |
| Interpretación | Curva media de cada grupo con banda de percentiles 10 a 90, frecuencia y composición por día de la semana, mes, estación y festivo |
| Días que no encajan | Distancia de cada día al centro de su grupo (`distancia_centroide`), insumo del notebook 06 |

## 3. Resultados

| Concepto | Valor |
|---|---|
| Algoritmo elegido | `[completar]` |
| k elegido | `[completar]` |
| Silueta media (muestra) y su interpretación | `[completar]` |
| Concordancia entre k-medias y Ward (Rand ajustado) | `[completar]` |
| Descripción de cada grupo (nombre, curva, hora pico, calendario) | `[completar]` |
| Mezcla de tipos de día por región (historial completo y periodo común) | `[completar]` |
| Alineación de `COMED` y `NI` | `[completar]` |

**Salidas** (`data/processed/`): `tipos_de_dia.parquet`, `tipos_de_dia_curvas.parquet`, `tipos_de_dia_resumen.parquet`, `tipos_de_dia_mezcla_region.parquet` y `tipos_de_dia_silueta_k.parquet`.

## 4. Limitaciones

- K-medias asume grupos compactos con distancia euclidiana, y los perfiles diarios forman en parte un continuo: la estructura puede resultar débil. Con frecuencia k = 2 gana en silueta, si ocurre, se justifica la elección de un k mayor por interpretabilidad.
- Al normalizar por el promedio del día se pierde la información de magnitud.
- Las regiones cubren periodos distintos, y eso afecta a su mezcla de tipos de día, por eso se compara también en el periodo común.
- Si `COMED` y `NI` no se alinean a hora central, su curva puede separarse por la hora y no por la forma.
- La silueta y Ward se calculan sobre una muestra de días.

## 5. Reproducibilidad

El código está en `notebooks/05_agrupamiento.ipynb` y `src/profiles.py`. Los parámetros (`K_MIN`, `K_MAX`, `TAMANO_MIN_GRUPO`, `SILUETA_RAZONABLE`, `SILUETA_DEBIL`, `MUESTRA_AGRUPAMIENTO`, `SEMILLA`) están en `src/config.py`.

---

# Parte C. Detección de días atípicos

## 1. Definición

Un día es atípico si su demanda se aleja de lo esperable. Lo esperable lo da el modelo de pronóstico de la Parte A, evaluado fuera de muestra con la ventana móvil (2012-08 → 2018-08).

## 2. Diseño

| Elemento | Decisión |
|---|---|
| Residuo | `real − predicción`: positivo es demanda por encima de lo esperable (dirección `alta`), negativo, por debajo (`baja`) |
| Residuo diario | Residuo medio de las 24 horas, con signo, en % de la predicción media del día (`residuo_pct`), solo días completos |
| Regla | z modificado del residuo diario > 3.5 en valor absoluto, con z = 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana (Iglewicz y Hoaglin, 1993) |
| Comprobaciones | Sensibilidad al umbral (3, 3.5, 4 y 5), concentración de atípicos por estación y pliegue, y tasa en festivos. Opción `Z_POR_ESTACION` |
| Validación | Contraste con episodios externos (olas de calor o frío, huracán Sandy), cada uno con su fuente y marca de verificación. Los episodios fuera del rango de los residuos se marcan como no evaluados. Los datos no traen etiquetas de anomalías |
| Dirección esperada | Frío o calor extremo: residuos positivos, huracán Sandy: negativos |
| Complemento | Relación con la distancia de cada día al centro de su grupo (Parte B) |

## 3. Resultados

| Concepto | Valor |
|---|---|
| Número de días atípicos (altos y bajos) | `[completar]` |
| Sensibilidad al umbral | `[completar]` |
| Episodios recuperados y dirección coincidente | `[completar]` |
| Atípicos sin episodio conocido | `[completar]` |
| Relación con la forma del día | `[completar]` |

**Salidas** (`data/processed/`): `anomalias_PJME_diario.parquet`, `anomalias_PJME_lista.parquet` y `anomalias_PJME_episodios.parquet`.

## 4. Limitaciones

- Sin temperatura, las anomalías solo pueden interpretarse por coincidencia con eventos. Un día extremo por clima puede no salir atípico si los rezagos y medias móviles del modelo ya lo incorporaban.
- Lo atípico depende del modelo: otro pronóstico daría otros residuos y otra lista.
- Un residuo grande también puede deberse a un error de los datos, por eso se revisan las horas vecinas antes de concluir.
- Solo hay residuos de `PJME`, y cubren los últimos seis años, los episodios anteriores (2006, 2011) quedan fuera de rango.
- El umbral de 3.5 se calibró para datos normales, los residuos no lo son, por eso se muestra la sensibilidad.
- Los días de cambio de horario tienen una hora estimada o promediada en la limpieza.
- No hay verdad de referencia con la que medir la detección.

## 5. Reproducibilidad

El código está en `notebooks/06_anomalias.ipynb` y `src/anomalies.py`. Los parámetros (`UMBRAL_Z_MODIFICADO`, `TOLERANCIA_EPISODIO_DIAS`) están en `src/config.py`. La tabla de episodios, con sus fuentes, está en el notebook 06.