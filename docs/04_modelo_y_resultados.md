<div align="center">

# Modelo y resultados

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [Resumen](#resumen)
- [Hallazgos del análisis descriptivo](#hallazgos-del-análisis-descriptivo)
- [Parte A. Pronóstico de referencia](#parte-a-pronóstico-de-referencia)
- [Parte B. Agrupamiento de perfiles diarios](#parte-b-agrupamiento-de-perfiles-diarios)
- [Parte C. Detección de días atípicos](#parte-c-detección-de-días-atípicos)
- [Exportación para el panel](#exportación-para-el-panel)
- [Glosario](#glosario)

---

## Resumen

Este documento describe los componentes analíticos del proyecto, cómo se evalúan y los resultados obtenidos. Las cifras salen de la ejecución de los notebooks con el día operativo (decisión D1). Las horas son horas de inicio (0 = 00:00–01:00). Los objetivos y su estado están en [01_proyecto.md](01_proyecto.md) y las decisiones en [05_decisiones.md](05_decisiones.md).

| Componente | Tema | Pregunta | Dónde se ejecuta | Estado |
|---|---|---|---|---|
| Descriptivo | Patrones por hora, día y estación, tendencia, comparación y picos | P1 y P2 | `01_datos` y `02_patrones` | Hecho |
| A | Pronóstico de referencia a 24 horas | P4 y base de P3 | `03_pronostico_anomalias` | Hecho: supera al base en los 6 pliegues, MASE de 0.72 a 0.87 |
| B | Agrupamiento de perfiles diarios | P1 y P2 | `02_patrones` | Hecho: k = 2 (estacionales), silueta 0.413 (débil). se reporta k = 2 (D26) |
| C | Detección de días atípicos | P3 | `03_pronostico_anomalias` | Hecho: 22 días atípicos, 5 episodios coinciden |
| Exportación | Modelo en estrella para el panel | P1 a P4 | `src/export.py` y `app/streamlit_app.py` | Hecho: 17 tablas con claves validadas y panel en Streamlit de seis páginas |

---

## Hallazgos del análisis descriptivo

- **Periodo:** no existe un periodo común a las 12 regiones, 10 comparten 2013-06-01 → 2018-08-03 (días operativos hasta el 2018-08-02).
- **Ciclo diario:** mínimo entre las 3 y las 4 h, subida desde las 5–6 h y máximo entre las 17 y las 19 h (18 h en 7 de 10 regiones, `DUQ` y `PJME` a las 17 h, `EKPC` a las 19 h).
- **Forma por estación:** en verano hay una sola curva con máximo por la tarde (hasta 1.2–1.4 del promedio) y en invierno hay dos picos, uno hacia las 7 h y otro hacia las 18–19 h.
- **Calendario:** el fin de semana consume entre un 3.9 % (`EKPC`) y un 13.9 % (`DAYTON`) menos que un laborable (≈ −9 % en promedio). Un festivo consume cerca de un 5 % menos (de −0.7 % en `DOM` a −8.8 % en `DAYTON`; `EKPC` es la excepción con +1.7 %).
- **Estacionalidad:** dos máximos anuales (verano e invierno) con valles en abril y octubre. `EKPC` (1.20) y `PJMW` (1.12) son invernales, `COMED` (0.93), `DUQ` (0.92), `DEOK` y `PJME` (0.95), veraniegas.
- **Tendencia:** estabilidad o ligera baja (`PJME` −9 % entre 2007 y 2017, de 33,612 a 30,653 MW; `AEP` −13 %; `DUQ` −10 %). `DOM` sube cerca de un 6 % desde 2006.
- **Picos:** `PJME` alcanzó 62,009 MW el 2006-08-02. `DOM`, `EKPC` y `PJMW` tienen su récord el 2015-02-20 a las 7 h. Ambas fechas coinciden con episodios documentados por PJM: el récord de demanda de verano y el de invierno. El máximo de `AEP` es 25,164 MW (2007-08-08): el valor crudo mayor (2008-10-20) se descartó como atípico aislado (D2).
- **Correlaciones:** de 0.56 a 0.96. Los pares más parecidos son `AEP`–`PJMW` y `DAYTON`–`FE` (0.96), y la región más distinta es `EKPC`.
- **Hora de `COMED` y `NI`:** su curva diaria llega una hora más tarde que la del resto (error de 0.014 con +1 h frente a 0.024 sin desplazar). Es lo esperable si las series están en hora del este y esas zonas son de hora central. Se conserva la hora de la fuente (ver D7).
- **`NI` y `COMED`:** cociente de niveles 1.00 y empalme el 2011-01-01, compatibles con una misma zona; se mantienen como series separadas (D3).

---

## Parte A. Pronóstico de referencia

> Todas las cifras de esta parte salen de la ejecución de `03_pronostico_anomalias.ipynb` con el día operativo (`Datetime − 1 h`, decisión D1). Las horas son horas de inicio (0 = 00:00–01:00).

### 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Región | `PJME` (zona este de PJM) |
| Periodo | 2002-01-01 01:00 → 2018-08-03 00:00 |
| Filas | 145,392 (serie horaria regular, sin vacíos) |
| Variable objetivo | Consumo horario en MW |
| Archivo de entrada | `data/processed/consumo_horario.parquet`, filtrado por `region == 'PJME'` |

Se eligió `PJME` por ser la región con el historial más largo (16 años completos) y la de mayor tamaño.

### 2. Preparación de los datos

**Calidad.** Los datos provienen de la limpieza (`01_datos.ipynb`): en `PJME` se unificaron 4 duplicados y se agregaron e interpolaron 30 horas (17 de primavera, 12 de otoño y 1 de otra causa, el 2010-12-10 00:00, que también falta en otras 6 regiones). No se aplicó ningún tratamiento adicional.

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

### 3. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Horizonte | 24 horas: para predecir la hora *t* solo se usa información hasta *t − 24* |
| Entrenamiento | 2002-01-01 → 2016-12-31 (131,495 filas, 131,304 tras descartar las 191 sin historia) |
| Prueba | 2017-01-01 → 2018-08-03 (13,897 filas, unos 19 meses) |
| División | Cronológica, nunca al azar |
| Modelos base | Consumo de hace 24 horas y de hace 168 horas |
| Validación | Ventana móvil con entrenamiento creciente: 6 pliegues de 12 meses (mínimo 3) |
| Métrica de escala | MASE con la escala del pronóstico ingenuo estacional de 24 h |
| Semilla | 42 |

**Control de fuga de datos.** Todos los rezagos son de 24 horas o más, y las medias móviles se desplazan 24 horas. `agregar_rezagos` lanza un error si algún rezago es menor que el horizonte. Los rezagos se calcularon antes de dividir, de modo que las primeras horas de la prueba usan el final del entrenamiento, información que existiría en la práctica.

Con la hora de fin, la prueba de la partición única empieza en `2017-01-01 00:00`, que es la hora 23 del 2016-12-31. Ese primer día queda incompleto y se excluye del análisis por día.

**Validación en ventana móvil.** Los pliegues son bloques consecutivos de 12 meses que terminan el 2018-08-03: en cada uno se entrena con todo lo anterior y se prueba en el bloque. Los bloques no se solapan, así que cada hora se predice una sola vez fuera de muestra (52,584 horas). Con 6 pliegues, los residuos cubren **2012-08-03 → 2018-08-03**, que incluye el huracán Sandy, el vórtice polar de 2014 y el frío de 2015. Criterio: XGBoost supera al base en todos los pliegues y su MASE es menor que 1. Los residuos (`real − predicción`) se guardan en `data/processed/residuos_PJME.parquet` y alimentan la Parte C.

### 4. Algoritmos

| Modelo | Motivo de elección | Parámetros |
|---|---|---|
| Base 24 h | Referencia mínima: "mañana será como hoy" a la misma hora | N/A |
| Base 168 h | Referencia semanal: "será como la semana pasada" | N/A |
| XGBoost | Funciona bien con datos tabulares, captura relaciones no lineales entre variables y entrena rápido | 500 árboles, tasa de aprendizaje 0.05, profundidad 6, `subsample` 0.8, `colsample_bytree` 0.8, `random_state` 42 |

Se descartaron Prophet y los modelos ARIMA: con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.

### 5. Métricas y resultados

Métricas: MAE y RMSE (en MW), MAPE (en %) y MASE, evaluadas sobre los 13,897 registros de la prueba (partición única).

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) | MASE |
|---|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 | 1.06 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 | 1.63 |
| **XGBoost** | **1,861.58** | **2,512.52** | **5.89** | **0.86** |

El MASE se calcula con la escala del pronóstico ingenuo de 24 h incluso para el modelo base de 168 h. Menor que 1 significa que el modelo se equivoca menos que ese pronóstico ingenuo: XGBoost lo cumple (0.86) y el modelo base de 24 h queda ligeramente por encima (1.06).

**Mejora de XGBoost**

| Frente a | MAE | RMSE | MAPE |
|---|---|---|---|
| Base 24 h | −19.1 % | −19.8 % | −19.5 % |
| Base 168 h | −47.0 % | −47.6 % | −46.4 % |

El MAE de XGBoost equivale a cerca del 6 % del consumo medio de `PJME` (≈ 31,500 MW en el periodo 2013-06 a 2018-08).

**Validación en ventana móvil (6 pliegues de 12 meses)**

| Pliegue | Prueba | MAE XGBoost (MW) | MAE base (MW) | Mejora (%) | MASE XGBoost |
|---|---|---|---|---|---|
| 1 | 2012-08-03 → 2013-08-03 | 1,551 | 2,049 | 24.3 | 0.72 |
| 2 | 2013-08-03 → 2014-08-03 | 1,723 | 2,402 | 28.3 | 0.80 |
| 3 | 2014-08-03 → 2015-08-03 | 1,688 | 2,252 | 25.0 | 0.78 |
| 4 | 2015-08-03 → 2016-08-03 | 1,581 | 2,013 | 21.5 | 0.73 |
| 5 | 2016-08-03 → 2017-08-03 | 1,727 | 2,174 | 20.5 | 0.80 |
| 6 | 2017-08-03 → 2018-08-03 | 1,884 | 2,307 | 18.3 | 0.87 |

**¿XGBoost supera al base en todos los pliegues?** Sí. Su MAE es menor en los 6 pliegues y su MASE es menor que 1 en todos (0.72 a 0.87), así que se cumple el criterio de cierre. La mejora es estable pero decreciente: el pliegue 6 es el de mayor error y menor mejora, coherente con el resultado de la partición única.

**Error por tipo de día (MAE en MW, partición única)**

| Tipo de día | Horas | Base 24 h | XGBoost | Mejora |
|---|---|---|---|---|
| Laborable | 9,576 | 2,179.0 | 1,842.0 | 15.5 % |
| Fin de semana | 3,913 | 2,554.5 | 1,906.9 | 25.4 % |
| Festivo | 408 | 2,701.2 | 1,886.9 | 30.1 % |

**Error por hora del día.**

- El error de XGBoost es menor de madrugada (≈ 1,500 MW) y mayor por la tarde (≈ 2,350 MW a las 17 h).
- El modelo base falla mucho en las horas de subida de la mañana (5 a 9 h, hasta ≈ 2,830 MW), porque al usar el día anterior no capta la transición entre laborables y fines de semana. XGBoost reduce ese error cerca de un 40 %.
- Por la tarde ambos modelos mantienen errores altos.

**Error por mes.**

- XGBoost tiene el mayor error en junio y julio (≈ 2,400 MW), meses de verano.
- El menor error está en octubre, noviembre y abril (≈ 1,150 a 1,250 MW), los meses templados.
- Enero a agosto aparecen dos veces en la prueba (2017 y 2018) y septiembre a diciembre una sola, así que las comparaciones entre meses no tienen el mismo respaldo.

**Los 10 días con mayor error**

| Fecha | MAE XGBoost | MAE Base 24 h |
|---|---|---|
| 2017-05-20 | 8,097.7 | 12,062.3 |
| 2018-06-03 | 6,665.2 | 7,405.4 |
| 2018-07-07 | 6,161.3 | 10,061.4 |
| 2017-07-29 | 5,671.2 | 6,826.7 |
| 2017-03-15 | 5,143.6 | 3,515.7 |
| 2017-09-28 | 5,032.7 | 5,605.8 |
| 2017-12-31 | 5,000.1 | 1,858.7 |
| 2018-05-29 | 4,949.0 | 7,582.1 |
| 2017-07-25 | 4,938.2 | 4,091.5 |
| 2018-01-05 | 4,924.1 | 3,033.6 |

Ninguno es festivo. En 4 de los 10 días (2017-03-15, 2017-07-25, 2017-12-31 y 2018-01-05) el modelo base **supera** a XGBoost, lo que sugiere que ante cambios bruscos de condiciones el modelo puede amplificar el patrón del día anterior (hipótesis, sin verificar con datos de temperatura). El día de mayor error (2017-05-20, un sábado) tiene un MAE cercano al 26 % del consumo medio. También es un día atípico en la Parte C (residuo de −23.6 %): la demanda cayó a ≈ 27,000 MW tras un viernes de ≈ 47,000 MW, un patrón que apunta a un cambio brusco de temperatura, aunque sin datos de clima es una hipótesis.

**Importancia de las variables**

| Variable | Importancia |
|---|---|
| `MW_lag_24` | 0.713 |
| `MW_lag_168` | 0.095 |
| `es_fin_de_semana` | 0.077 |
| `dia_semana` | 0.040 |
| `es_festivo` | 0.019 |
| `hora` | 0.018 |
| `MW_lag_48` | 0.012 |
| `mes` | 0.011 |
| `MW_media_24h` | 0.009 |
| `MW_media_168h` | 0.006 |

#### Interpretación

XGBoost reduce el error cerca de un 19 % respecto al modelo base de 24 horas y casi un 47 % respecto al semanal, y la mejora se mantiene en los 6 pliegues (entre un 18 % y un 28 %). La mejora es moderada: el 71 % de la importancia recae en el consumo del día anterior a la misma hora, por lo que el modelo es esencialmente "ayer" con correcciones por tipo de día. Esas correcciones explican dónde gana más: en la transición matutina entre laborables y fines de semana y en los festivos, donde la referencia del día anterior es peor.

Donde menos mejora es en los episodios de clima extremo. Las variables disponibles (calendario e historial) no contienen información sobre la temperatura, que es el principal determinante de la demanda, y los errores más altos se concentran en la tarde, en los meses de verano y en los cambios bruscos de condiciones.

Un MAPE de 5.89 % para un pronóstico con 24 horas de antelación es un resultado razonable y no hay señales de fuga de datos: un error cercano a cero habría sido sospechoso.

### 6. Limitaciones

- **Sin temperatura.** Es el principal determinante de la demanda y el dataset no la incluye. Los picos extremos son los más difíciles de pronosticar, y un residuo grande puede ser clima y no una anomalía de otro tipo.
- **Los árboles no extrapolan.** Un modelo de árboles no predice valores fuera del rango que vio en el entrenamiento, lo que podría explicar los errores en olas de frío intensas (hipótesis).
- **Pliegues de 12 meses.** La ventana móvil reduce la dependencia de un solo periodo, pero cada pliegue es un año concreto con su clima, y los primeros entrenan con menos historia que los últimos.
- **Una sola región.** El modelo y los residuos son de `PJME`, para otras regiones hay que repetir el proceso, y entrenar un modelo por región y pliegue es lento.
- **Festivos federales.** No se incluyen los festivos de cada estado.
- **Hiperparámetros por defecto.** XGBoost no se ajustó con búsqueda de parámetros.
- **Sesgo.** El modelo tiende a sobrepronosticar: la mediana del residuo diario es negativa (de −0.65 % a −1.74 % según el pliegue), coherente con la ligera baja de demanda de largo plazo.

### 7. Reproducibilidad

El código está en `notebooks/03_pronostico_anomalias.ipynb`, `src/modeling.py` y `src/features.py`. Los parámetros del experimento están en `src/config.py` (`HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `N_PLIEGUES`, `MESES_PLIEGUE`, `SEMILLA`). El notebook usa 6 pliegues, por encima del mínimo `N_PLIEGUES`. Salidas: `residuos_PJME.parquet` y `metricas_ventana_movil_PJME.parquet` en `data/processed/`. Los pasos para ejecutarlo están en la [guía de usuario](06_guia_usuario.md).

---

## Parte B. Agrupamiento de perfiles diarios

> No confundir con la variable `tipo_dia` de `02_patrones.ipynb` y `03_pronostico_anomalias.ipynb` (laborable, fin de semana, festivo), que se define por el calendario. Aquí el tipo de día lo descubre el agrupamiento a partir de la forma de la curva.

### 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Unidad de análisis | Un día de una región (45,428 perfiles de 12 regiones) |
| Perfil | 24 valores, uno por hora, del día operativo (`Datetime − 1 h`) |
| Normalización | Cada valor se divide entre el promedio de su día, para capturar la forma y no el tamaño |
| Magnitud | El consumo medio diario (`MW_medio_dia`) se guarda aparte |
| Días incluidos | Solo días completos (24 horas). Se descartó 1 día con menos de 24 horas |
| Alcance | Las 12 regiones juntas, de modo que los tipos de día son los mismos y se puede construir la matriz región por tipo de día (decisión D6) |

### 2. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Algoritmos | K-medias y agrupamiento jerárquico (criterio de Ward) |
| Rango de k | 2 a 10 (`K_MIN`, `K_MAX`) |
| Muestra | La silueta y Ward se calculan sobre una muestra reproducible de 10,000 días (`MUESTRA_AGRUPAMIENTO`), porque escalan de forma cuadrática. Ward asigna el resto de los días al centro más cercano, k-medias usa todos |
| Selección de k | Mayor silueta media entre las combinaciones en que ningún grupo baja del 5 % de los días |
| Calidad de la estructura | El proyecto usa 0.51 como umbral de estructura razonable (`SILUETA_RAZONABLE`) y 0.26 como límite de la estructura débil (`SILUETA_DEBIL`), siguiendo a Kaufman y Rousseeuw (D28). Por debajo de 0.26 no hay estructura sustancial. Se reporta tal como sale |
| Estabilidad | Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado) y repetición de k-medias con 20 semillas (`SEMILLAS_ESTABILIDAD`, D29) |
| Alineación horaria | Parámetro `ALINEAR_HORA_CENTRAL`: con `True` se resta 1 h a las regiones de `REGIONES_HORA_CENTRAL` antes de calcular el día operativo. `02_patrones.ipynb` mide el desfase de cada región y la decisión D7 es no alinear |
| Interpretación | Curva media de cada grupo con banda de percentiles 10 a 90, frecuencia y composición por día de la semana, mes, estación y festivo |
| Días que no encajan | Distancia de cada día al centro de su grupo (`distancia_centroide`), insumo de la detección de anomalías |

### 3. Resultados

| Concepto | Valor |
|---|---|
| Algoritmo elegido | K-medias |
| k elegido | 2 |
| Silueta media (muestra) y su interpretación | 0.413, estructura débil |
| Concordancia entre k-medias y Ward (Rand ajustado) | 0.95 (mediana 0.89 en 20 muestras) |
| Estabilidad entre 20 semillas (Rand ajustado) | 0.997 a 1.000 |
| Alineación de `COMED` y `NI` | No (`ALINEAR_HORA_CENTRAL = False`, D7). El diagnóstico detecta +1 h en ambas y 0 en el resto |

**Elección de k.** La mayor silueta con grupos de al menos el 5 % es k-medias con k = 2. Con k = 3 la silueta es 0.30 (débil) y con k ≥ 4 queda por debajo de 0.26 (sin estructura sustancial). Algún grupo baja del 5 % de los días desde k = 9 con k-medias y desde k = 8 con Ward.

**Por qué k = 2 (D26).** Un k mayor no separa el fin de semana. Sin relación con el calendario, cada grupo tendría 28.6 % de sábados y domingos:

| k | Silueta k-medias | % de fin de semana por grupo |
|---|---|---|
| 2 | 0.413 | 28.9 y 28.1 |
| 3 | 0.304 | 25.5, 29.6 y 32.9 |
| 4 | 0.242 | 30.2, 20.5, 32.6 y 32.0 |

Con k = 3 aparece un perfil de pico matinal (hacia las 8 h, 26.0 % de los días, sobre todo en invierno), a cambio de una silueta menor.

| k | Silueta k-medias | Silueta Ward | Grupo más pequeño k-medias (%) | Grupo más pequeño Ward (%) |
|---|---|---|---|---|
| 2 | 0.413 | 0.397 | 37.9 | 35.4 |
| 3 | 0.304 | 0.224 | 25.7 | 28.5 |
| 4 | 0.242 | 0.189 | 17.0 | 17.6 |
| 5 | 0.248 | 0.173 | 16.8 | 5.9 |
| 6 | 0.223 | 0.176 | 7.2 | 5.9 |
| 7 | 0.221 | 0.179 | 7.9 | 5.9 |
| 8 | 0.205 | 0.169 | 5.1 | 4.7 |
| 9 | 0.197 | 0.145 | 4.9 | 4.7 |
| 10 | 0.196 | 0.137 | 3.4 | 3.1 |

**Estabilidad entre semillas (D29).** Los grupos de k-medias no dependen de la inicialización: con 20 semillas, el índice de Rand ajustado frente a la asignación de referencia va de 0.997 a 1.000, cambia de grupo como máximo el 0.08 % de los días, el grupo 1 reúne entre 62.2 % y 62.3 % y la silueta va de 0.408 a 0.414. Ward, en cambio, depende de la muestra de días sobre la que se ajusta: con la semilla 42 el índice es 0.95, y al ajustar Ward sobre las muestras de 20 semillas va de 0.69 a 0.99 (mediana 0.89).

**Descripción de cada grupo.**

| Grupo | Nombre | Días | % de los días | Hora pico | Hora mínima | Amplitud | % fin de semana | % festivo | Estación dominante |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Temporada fría (oct–may) | 28,295 | 62.3 | 19 h | 3 h | 0.2 | 28.9 | 3.2 | Invierno (38.1 %) |
| 2 | Verano (jun–sep) | 17,133 | 37.7 | 17 h | 4 h | 0.4 | 28.1 | 2.8 | Verano (63.0 %) |

- **Grupo 1:** reúne los días de octubre a mayo, con una meseta de mañana (7 a 11 h), un pico nocturno a las 19–20 h, un mínimo a las 3 h y una amplitud de ≈ 0.2 del promedio del día.
- **Grupo 2:** reúne los días de junio a septiembre, con una sola curva de pico a las 16–17 h (≈ 1.19 del promedio), un mínimo a las 4 h y una amplitud de ≈ 0.4.
- **Son tipos estacionales, no de calendario.** El 28.9 % y el 28.1 % de los días son sábado o domingo, casi igual que el 28.6 % esperado si no hubiera relación, y los festivos no se concentran. No hay un tipo de día de fin de semana. Una hipótesis, sin verificar, es que el efecto de fin de semana es sobre todo de nivel (cerca de −9 % según `02_patrones.ipynb`) y desaparece al dividir cada perfil entre el promedio del día.
- Los nombres automáticos de `02_patrones.ipynb` («G1 · Invierno · mixto» y «G2 · Verano · mixto») se sustituyen por los nombres basados en el calendario, y `02_patrones.ipynb` ya guarda sus tablas con esos nombres. `src/export.py` exporta todas las tablas del panel con los nombres cortos «Temporada fría» y «Verano».

**Mezcla de tipos de día y estacionalidad por región.** «Común» es el periodo común de las 10 regiones vigentes (2013-06-01 → 2018-08-02).

| Región | % grupo 1, historial | % grupo 2, historial | % grupo 1, común | % grupo 2, común | Razón invierno/verano (común) | Amplitud diaria (común) |
|---|---|---|---|---|---|---|
| AEP | 67.8 | 32.2 | 64.0 | 36.0 | 1.059 | 0.302 |
| COMED | 60.4 | 39.6 | 59.3 | 40.7 | 0.928 | 0.340 |
| DAYTON | 65.1 | 34.9 | 61.8 | 38.2 | 1.008 | 0.342 |
| DEOK | 60.2 | 39.8 | 58.3 | 41.7 | 0.945 | 0.347 |
| DOM | 55.2 | 44.8 | 55.3 | 44.7 | 0.985 | 0.400 |
| DUQ | 65.4 | 34.6 | 63.3 | 36.7 | 0.917 | 0.327 |
| EKPC | 55.1 | 44.9 | 55.1 | 44.9 | 1.196 | 0.440 |
| FE | 69.4 | 30.6 | 69.1 | 30.9 | 0.996 | 0.306 |
| NI | 52.3 | 47.7 | n. a. | n. a. | n. a. | n. a. |
| PJME | 59.9 | 40.1 | 60.0 | 40.0 | 0.950 | 0.369 |
| PJMW | 67.3 | 32.7 | 64.4 | 35.6 | 1.119 | 0.322 |
| PJM_Load | 55.7 | 44.3 | n. a. | n. a. | n. a. | n. a. |

- En el periodo común, la proporción de días de verano va de ≈ 31 % (`FE`) a ≈ 45 % (`DOM` y `EKPC`).
- Sigue a la amplitud diaria de cada región (`EKPC` 0.44, `DOM` 0.40, `FE` 0.31) y no al sesgo invernal o veraniego: `EKPC` tiene sesgo invernal (1.20) y aun así es de las regiones con más días de forma veraniega.
- Al comparar el historial completo con el periodo común cambian las mezclas de `AEP`, `DAYTON` y `PJMW` (entre 3 y 4 puntos), por eso conviene reportar ambas.

**Días que no encajan en su grupo.** La distancia al centro tiene una mediana de ≈ 0.21 en ambos grupos (media 0.226 y 0.223). El día más lejano es el 2008-09-14 de `DAYTON` (1.54), y `EKPC` aparece 7 veces entre los 10 primeros. La distancia no es comparable entre regiones y conviene normalizarla antes de usarla como insumo de la detección de anomalías.

**Salidas** (`data/processed/`): `tipos_de_dia.parquet` (45,428 filas), `tipos_de_dia_curvas.parquet` (48 filas), `tipos_de_dia_resumen.parquet` (2 filas), `tipos_de_dia_mezcla_region.parquet` (24 filas) y `tipos_de_dia_silueta_k.parquet` (18 filas).

### 4. Limitaciones

- **Estructura débil.** La silueta de 0.413 indica que los perfiles diarios forman en parte un continuo, así que los tipos de día son una simplificación útil y no categorías naturalmente separadas.
- **k = 2 solo captura la estación.** No hay un tipo de día de fin de semana, y con k = 3 o k = 4 tampoco aparece (D26).
- K-medias asume grupos compactos con distancia euclidiana.
- Al normalizar por el promedio del día se pierde la información de magnitud.
- Las regiones cubren periodos distintos, y eso afecta a su mezcla de tipos de día, por eso se compara también en el periodo común.
- `COMED` y `NI` se analizan con la hora de la fuente, una hora más tarde que el resto. No hay una confirmación expresa de su zona horaria y alinearlas cambiaría de grupo el 1.33 % de los días y subiría el grupo 1 de 60.4 % a 67.1 % en `COMED` y de 52.3 % a 64.3 % en `NI` (silueta 0.420) (D7).
- El agrupamiento es conjunto para las 12 regiones, lo que permite compararlas pero puede esconder formas propias de una región.
- La silueta y Ward se calculan sobre una muestra de días (grupo más pequeño: 37.9 % en la muestra y 37.7 % con todos los días).
- Sin temperatura, los tipos de día se interpretan por el calendario y no por el clima.

### 5. Reproducibilidad

El código está en `notebooks/02_patrones.ipynb` y `src/profiles.py`. Los parámetros (`K_MIN`, `K_MAX`, `TAMANO_MIN_GRUPO`, `SILUETA_RAZONABLE`, `SILUETA_DEBIL`, `MUESTRA_AGRUPAMIENTO`, `SEMILLA`) están en `src/config.py`. `ALINEAR_HORA_CENTRAL` y `REGIONES_HORA_CENTRAL` deben tener el mismo valor en `02_patrones.ipynb` y en `src/export.py`.

---

## Parte C. Detección de días atípicos

### 1. Definición

Un día es atípico si su demanda se aleja de lo esperable. Lo esperable lo da el modelo de pronóstico de la Parte A, evaluado fuera de muestra con la ventana móvil (2012-08 → 2018-08).

### 2. Diseño

| Elemento | Decisión |
|---|---|
| Residuo | `real − predicción`: positivo es demanda por encima de lo esperable (dirección `alta`), negativo, por debajo (`baja`) |
| Residuo diario | Residuo medio de las 24 horas, con signo, en % de la predicción media del día (`residuo_pct`), solo días completos |
| Regla | z modificado del residuo diario > 3.5 en valor absoluto, con z = 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana (Iglewicz y Hoaglin, 1993) |
| Base del cálculo | Todos los días de la región (decisión D8). La opción `Z_POR_ESTACION` queda como alternativa |
| Comprobaciones | Sensibilidad al umbral (3, 3.5, 4 y 5), concentración de atípicos por estación y pliegue, y tasa en festivos |
| Validación | Contraste con episodios externos (olas de calor o frío, huracán Sandy), cada uno con su fuente y marca de verificación. Los episodios fuera del rango de los residuos se marcan como no evaluados. Los datos no traen etiquetas de anomalías |
| Dirección esperada | Frío o calor extremo: residuos positivos, huracán Sandy: negativos |
| Complemento | Relación con la distancia de cada día al centro de su grupo (Parte B) |

### 3. Resultados

| Concepto | Valor |
|---|---|
| Periodo cubierto por los residuos | 2012-08-03 → 2018-08-02 (6 pliegues de 12 meses) |
| Días evaluados | 2,191 (todos con 24 horas) |
| Residuo diario | Mediana −1.00 %, desviación estándar 5.54 %, rango de −27.91 % a +25.02 % |
| Número de días atípicos (altos y bajos) | 22 (1.0 % de los días): 15 altos y 7 bajos |
| Episodios recuperados y dirección coincidente | 5 de 8 evaluados (62 %), más 2 fuera de rango. La dirección coincide en 5 de 5 |
| Atípicos sin episodio conocido | 16 de 22 |
| Relación con la forma del día | Spearman entre \|z\| y la distancia al centro: 0.02. 8 de los 22 atípicos (36 %) tienen una forma lejana, frente a ≈ 5 % del resto |

**Sensibilidad al umbral.**

| Umbral | Días atípicos | % de los días |
|---|---|---|
| 3.0 | 52 | 2.37 |
| 3.5 | 22 | 1.00 |
| 4.0 | 9 | 0.41 |
| 5.0 | 2 | 0.09 |

El corte es frágil entre 3.5 y 4.0, donde la lista pasa de 22 a 9 días.

**Concentración por estación y pliegue.**

| Estación | Días | Atípicos | % |
|---|---|---|---|
| Invierno | 541 | 4 | 0.74 |
| Otoño | 546 | 5 | 0.92 |
| Primavera | 552 | 6 | 1.09 |
| Verano | 552 | 7 | 1.27 |

| Pliegue | Días | Atípicos | % |
|---|---|---|---|
| 1 | 365 | 3 | 0.82 |
| 2 | 365 | 7 | 1.92 |
| 3 | 365 | 2 | 0.55 |
| 4 | 366 | 3 | 0.82 |
| 5 | 365 | 5 | 1.37 |
| 6 | 365 | 2 | 0.55 |

El error del modelo no se reparte por igual: es más disperso en invierno y verano (MAD ≈ 3.8 %) que en otoño y primavera (≈ 2.5–2.7 %). Aun así, los atípicos no se concentran en ninguna estación (de 0.7 % a 1.3 %, con solo 4 a 7 días por estación), y el invierno, una de las estaciones más dispersas, es la que menos tiene. El pliegue 2 reúne 7 de los 22 atípicos, pero con tan pocos casos esa diferencia es difícil de interpretar. No hay evidencia de que la lista refleje sobre todo el error del modelo en una estación o pliegue concreto, así que se mantiene `Z_POR_ESTACION = False`. En festivos la tasa es 1.54 % (1 de 65 días) frente a 0.99 % en no festivos.

**Los 10 días de mayor magnitud.**

| Fecha | Dirección | Residuo (%) | z | Episodio |
|---|---|---|---|---|
| 2012-10-30 | Baja | −27.9 | −5.74 | Huracán Sandy |
| 2014-01-07 | Alta | +25.0 | 5.55 | Vórtice polar de enero de 2014 |
| 2015-02-15 | Alta | +21.7 | 4.85 | Ola de frío de febrero de 2015 |
| 2017-05-20 | Baja | −23.6 | −4.81 | Ninguno conocido |
| 2016-09-10 | Alta | +20.7 | 4.64 | Ninguno conocido |
| 2013-09-10 | Alta | +20.5 | 4.58 | Calor de septiembre de 2013 |
| 2013-11-24 | Alta | +20.0 | 4.48 | Ninguno conocido |
| 2018-06-03 | Baja | −20.5 | −4.16 | Ninguno conocido |
| 2018-05-29 | Alta | +18.0 | 4.04 | Ninguno conocido |
| 2014-03-13 | Alta | +17.5 | 3.94 | Ninguno conocido |

**Contraste con episodios externos.**

| Episodio | Fechas | Estado | Días atípicos | Máx. \|z\| | Dirección esperada / detectada | Verificado |
|---|---|---|---|---|---|---|
| Ola de calor de agosto de 2006 (récord de PJM) | 2006-08-01 → 08-03 | Fuera de rango | 0 | n. a. | Alta / n. a. | Sí |
| Ola de calor de julio de 2011 | 2011-07-20 → 07-22 | Fuera de rango | 0 | n. a. | Alta / n. a. | Sí |
| Huracán Sandy | 2012-10-29 → 10-31 | Coincide | 1 (2012-10-30) | 5.74 | Baja / Baja | Sí |
| Ola de calor de julio de 2013 (pico de PJM) | 2013-07-15 → 07-19 | Sin coincidencia | 0 | n. a. | Alta / n. a. | Sí |
| Calor de septiembre de 2013 | 2013-09-10 → 09-12 | Coincide | 2 (09-10 y 09-11) | 4.58 | Alta / Alta | Sí |
| Vórtice polar de enero de 2014 | 2014-01-06 → 01-08 | Coincide | 1 (2014-01-07) | 5.55 | Alta / Alta | Sí |
| Vórtice polar de fines de enero de 2014 | 2014-01-24 → 01-30 | Coincide | 1 (2014-01-28) | 3.57 | Alta / Alta | Sí |
| Ola de frío de febrero de 2015 | 2015-02-14 → 02-21 | Coincide | 1 (2015-02-15) | 4.85 | Alta / Alta | Sí |
| Tormenta Jonas | 2016-01-22 → 01-24 | Sin coincidencia | 0 | n. a. | Por verificar | Sí |
| Ola de frío de enero de 2018 | 2018-01-01 → 01-07 | Sin coincidencia | 0 | n. a. | Alta / n. a. | Sí |

#### Interpretación

- **El detector encuentra los eventos de mayor magnitud.** Sandy, el vórtice polar de enero de 2014 y la ola de frío de febrero de 2015 son los tres atípicos con mayor |z| entre los episodios, y en los 5 episodios detectados el signo coincide con el esperado: demanda por encima de lo esperable en frío y calor extremos y por debajo en Sandy.
- **Dónde falla.** No salen atípicos la ola de calor de julio de 2013, la ola de frío de enero de 2018 ni la tormenta Jonas. Una posible explicación, a confirmar, es que en episodios largos los rezagos y medias móviles del modelo ya incorporan el nivel alto de demanda y el residuo no se dispara.
- **Predominan los atípicos altos** (15 de 22). El modelo tiende además a sobrepronosticar, un sesgo coherente con la ligera baja de demanda de largo plazo de `02_patrones.ipynb`.
- **Los casos hora a hora apuntan al clima.** En Sandy la demanda real cayó a unos 15,000 MW frente a unos 30,000 esperados. El 2014-01-07 llegó a cerca de 50,000 MW con un pronóstico muy inferior. Sin temperatura en el dataset, esto es una hipótesis.
- **16 de los 22 atípicos no coinciden con ningún episodio de la tabla.** De los 15 que lista el notebook, 10 son altos y 5 bajos, y los 5 bajos caen entre mayo y julio (2017-05-20, 2018-06-03, 2014-07-04, 2013-07-25 y 2016-06-08), compatible con días templados con menos aire acondicionado (hipótesis). Varios se relacionan con el calendario (el 2014-07-04 es festivo, el 2016-07-05 y el 2018-05-29 son el día siguiente a un festivo, y 5 de los 15 caen en fin de semana), aunque la tasa en festivos (1.5 %) no difiere de la del resto (1.0 %). Sin temperatura no se puede confirmar la causa.
- **Forma frente a nivel.** La correlación de Spearman es 0.02, pero los días extremos en nivel tienden a serlo también en forma (36 % frente a ≈ 5 %; 102 de 2,169 días no atípicos), aunque no de manera lineal. Los otros 14 atípicos (64 %) tienen una forma normal para su tipo de día y se distinguen solo por tener más o menos demanda de la esperada. Por tipo de día, la tasa es 0.8 % en el grupo 1 (11 de 1,350 días) y 1.3 % en el grupo 2 (11 de 841).

#### Criterios de cierre

| Criterio | Estado |
|---|---|
| Lista contrastada con al menos un episodio externo, con fuente | Cumplido: 5 episodios con fuente y fechas verificadas coinciden con días atípicos y con la dirección esperada |
| Sensibilidad del umbral reportada | Cumplido |
| Revisión de concentración por estación y pliegue | Cumplido |

**Salidas** (`data/processed/`): `anomalias_PJME_diario.parquet` (2,191 filas), `anomalias_PJME_lista.parquet` (22 filas) y `anomalias_PJME_episodios.parquet` (10 filas).

### 4. Limitaciones

- Sin temperatura, las anomalías solo pueden interpretarse por coincidencia con eventos. Un día extremo por clima puede no salir atípico si los rezagos y medias móviles del modelo ya lo incorporaban.
- Lo atípico depende del modelo: otro pronóstico daría otros residuos y otra lista.
- Un residuo grande también puede deberse a un error de los datos, por eso se revisan las horas vecinas antes de concluir.
- Solo hay residuos de `PJME`, y cubren los últimos seis años, los episodios anteriores (2006 y 2011) quedan fuera de rango y no se evalúan.
- El umbral de 3.5 es el valor convencional para el z modificado y no garantiza una tasa de falsos positivos concreta. Los residuos no son normales, por eso se muestra la sensibilidad.
- Los primeros pliegues entrenan con menos historia. En la práctica el pliegue 2 concentra más atípicos (7 de 22) y el pliegue 1 solo 3.
- Los días de cambio de horario tienen una hora estimada o promediada en la limpieza, si resultan atípicos hay que descartar ese efecto.
- La tabla de episodios no es exhaustiva: que un atípico no coincida con un episodio no lo hace una falsa alarma. Solo recoge 10 eventos, y para la tormenta Jonas no hay dirección esperada.
- No hay verdad de referencia con la que medir la detección.

### 5. Reproducibilidad

El código está en `notebooks/03_pronostico_anomalias.ipynb` y `src/anomalies.py`. Los parámetros (`UMBRAL_Z_MODIFICADO`, `TOLERANCIA_EPISODIO_DIAS`) están en `src/config.py`. La tabla de episodios, con sus fuentes, es `EPISODIOS_CONOCIDOS` de `src/anomalies.py`.


---

## Exportación para el panel

`src/export.py` reúne los resultados de los notebooks 01 a 03 en un modelo en estrella que lee el panel de Streamlit, y el diccionario `diccionario_datos.csv` documenta 111 columnas. Al terminar, la exportación comprueba que cada valor de `region`, `fecha`, `estacion` y `grupo` de las tablas de hechos exista en su dimensión, y se detiene si no.

- **`pronostico_horario`:** `hora`, `mes` y `fecha` se calculan con el día operativo (D1), igual que en el notebook 03: la fila de las 00:00 es la hora 23 del día anterior.
- **`tendencia_anual`:** consumo medio por región y año, con la columna `completo` (`Sí` si el año tiene al menos 8,700 horas, D16). El panel solo dibuja los años completos.
- **`pronostico_metricas`:** `mejora_MAE_pct` es la reducción del MAE de XGBoost frente al base, positiva cuando XGBoost tiene menos error.
- **`mezcla_region_tipo`:** porcentaje de días de cada tipo por región en el historial completo (`pct_dias_total`) y en el periodo común de las 10 regiones vigentes (`pct_dias_comun`, vacío en `NI` y `PJM_Load`). Los valores coinciden con la tabla de mezcla de tipos de día de esta nota.
- **`indicadores_region`:** razón invierno/verano y amplitud diaria relativa (máximo menos mínimo entre el promedio del día, en días de 24 horas), para el historial completo y para el periodo común de las 10 regiones vigentes (columnas `_comun`). Los valores del periodo común coinciden con `02_patrones` (por ejemplo, PJME 0.950 y 0.369; DOM 0.985 y 0.400).

| Tabla | Filas | Tabla | Filas |
|---|---|---|---|
| `dim_region` | 12 | `indicadores_region` | 12 |
| `dim_fecha` | 7,429 | `curvas_tipo_dia` | 48 |
| `dim_estacion` | 4 | `mezcla_region_tipo` | 24 |
| `dim_tipo_dia` | 2 | `silueta_k` | 18 |
| `hechos_diario` | 45,428 | `pronostico_horario` | 52,584 |
| `patron_hora_dia` | 8,064 | `pronostico_metricas` | 12 |
| `patron_tipo_calendario` | 3,456 | `anomalias_dias` | 2,191 |
| `tendencia_anual` | 132 | `anomalias_episodios` | 10 |
| `estacionalidad_mensual` | 144 | | |

---

## Glosario

Los conceptos clave del proyecto, agrupados por tema. Cada entrada dice qué es y cómo se aplica aquí.

### Mapa: qué conceptos usa cada pregunta

| Pregunta | Conceptos principales |
|---|---|
| P1. Tipos de día | Perfil diario, normalización, k-medias, agrupamiento jerárquico, silueta, índice de Rand ajustado, distancia al centroide, mapa de calor de calendario |
| P2. Diferencias entre regiones | Normalización relativa, coeficiente de variación, correlación, mezcla de tipos de día, periodo común, desfase entre regiones |
| P3. Días atípicos | Residuo, validación en ventana móvil, z modificado, MAD, sensibilidad al umbral, validación sin etiquetas |
| P4. Error del pronóstico | Rezagos, fuga de datos, XGBoost, MAE, RMSE, MAPE, MASE, análisis por segmento |

### Datos y tiempo

- **Hora de fin de intervalo (*hour ending*).** Convención que etiqueta cada hora con el instante en que **termina**: la hora 1 va de 00:00 a 01:00 y la hora 24 es la última del día. PJM la usa en sus reportes. `Datetime` la sigue: todas las series empiezan a las 01:00 y terminan a las 00:00, en primavera falta la fila de las 03:00 (no la de las 02:00) y en otoño se repite la de las 02:00. Consecuencias: la fila de las 00:00 es la última hora del día anterior, y un «pico a las 19 h» en `Datetime` corresponde al intervalo 18:00–19:00. Si el calendario se calcula directamente desde `Datetime`, `dia_semana`, `es_fin_de_semana` y `es_festivo` quedan desplazados un día en esa fila (1 de cada 24 horas). Se corrige con el día operativo.
- **Día operativo.** Día definido según la convención de los datos y no según el calendario civil. Se resta una hora a `Datetime` antes de calcular la fecha: la fila de las 00:00 pasa a ser la hora 23 (23:00–24:00) del día anterior y `hora` va de 0 a 23. Decisión D1, aplicada en `src/features.py` (columna `fecha`). Es la base de los promedios diarios, de los perfiles del agrupamiento y de los residuos diarios.
- **Hora local y EPT.** EPT (*Eastern Prevailing Time*) es la hora civil del este de EE. UU., que cambia entre horario estándar y de verano. Un [documento de liquidaciones de PJM](https://www.pjm.com/-/media/markets-ops/settlements/msrs/desc/msrs-customer-report-documentation-hourly-load-data.ashx) publica la carga horaria como «EPT Hour Ending», con horas 1 a 24, e incluye `COMED` entre sus zonas. Con el desfase medido, indica que todas las series están en EPT, aunque el documento no lo dice zona por zona ni describe el conjunto de Kaggle.
- **Desfase entre regiones.** Diferencia de hora entre perfiles que deberían parecerse. `COMED` (y `NI`) aparece retrasada 1 hora (error de 0.014 con ese desplazamiento frente a 0.024 sin él), coherente con series en hora del este para zonas que operan en hora central. No se corrige en la limpieza. `ALINEAR_HORA_CENTRAL` permite restar 1 h a `COMED` y `NI` antes de comparar formas de día; el proyecto no lo aplica (D7).
- **Día completo.** Día con sus 24 horas. Con el día operativo, el primer registro de cada serie (01:00) y el último (00:00) cierran días completos. Aun así se exigen las 24 horas por día y región en los promedios diarios, los perfiles del agrupamiento y los residuos diarios. Los bordes de los pliegues de la ventana móvil pueden dejar días incompletos, que se descartan.
- **Error de medición frente a valor extremo real.** Un valor extremo puede ser un error del medidor o consumo real. El criterio es la **continuidad**: varias horas seguidas extremas sugieren un evento real, un valor aislado entre horas normales sugiere un error. Los picos altos forman una nube continua y se conservan. Aislados y sospechosos: el 0 de `FE` (su primer registro, se recorta), `DOM` (1,253 MW) y `PJMW` (487 MW), que se conservan hasta aplicar el z modificado (D2). El mínimo de `EKPC` (514 MW) es una racha de varias horas en la madrugada de un domingo: un valle real. `01_datos` los distingue con el cociente entre el valor y el promedio de sus horas vecinas.
- **Periodo común y regiones vigentes.** El periodo común es el intervalo en el que *todas* las regiones comparadas tienen datos: empieza en el inicio más tardío y termina en el final más temprano. Las regiones vigentes son las que llegan hasta el final del dataset. No existe periodo común a las 12 regiones: las 10 vigentes comparten 2013-06-01 → 2018-08-03 y las comparaciones entre regiones se hacen en ese intervalo.
- **Media móvil centrada y efecto de borde.** Explica por qué la línea gruesa de las gráficas de tendencia es más corta que la serie y por qué el tramo final de la tendencia STL de `PJME` no es fiable y no se interpreta.
- **Descomposición STL.** Separa tendencia, estacionalidad y resto. Se aplica con `period = 365` a la serie diaria de `PJME` (solo días completos) con `robust=True`, que reduce la influencia de los valores extremos. El periodo fijo de 365 días ignora los años bisiestos, por lo que el componente estacional es una aproximación.

### Agrupamiento de perfiles diarios (aprendizaje no supervisado)

- **Silueta.** Mide cuán bien separado está cada día de los demás grupos. Siguiendo a Kaufman y Rousseeuw, una silueta media de 0.71 a 1.00 indica estructura fuerte, de 0.51 a 0.70 razonable, de 0.26 a 0.50 débil (podría ser artificial) y de 0.25 o menos que no hay estructura sustancial. El código usa 0.51 y 0.26 (`SILUETA_RAZONABLE`, `SILUETA_DEBIL`, D28). Se calcula para cada *k* entre 2 y 10, con k-medias y con Ward, sobre una muestra reproducible de 10,000 días.
- **Elección del número de grupos (*k*).** Se prueba cada *k* de 2 a 10 con ambos métodos y se elige la mayor silueta entre las combinaciones en que ningún grupo tiene menos del 5 % de los días. Con frecuencia k = 2 gana en silueta; aquí se mantiene porque un k mayor no separa el fin de semana (D26).
- **Agrupamiento jerárquico y criterio de Ward.** Es costoso en memoria con decenas de miles de elementos, por eso se ajusta sobre una muestra de 10,000 días y el resto se asigna al centro más cercano.
- **Estabilidad del agrupamiento.** Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado, ARI). También se repite k-medias con 20 semillas, y el índice va de 0.997 a 1.000. La concordancia con Ward cambia más, porque depende de su muestra (D29).
- **Distancia al centroide.** Distancia de cada día al centro de su grupo. Mira la forma de la curva, mientras que el residuo del pronóstico mira el nivel: un día puede ser raro en una, en la otra o en ambas. La detección de anomalías mide su correlación.
- **Mapa de calor de calendario.** Las celdas son los días del año y el color indica el tipo de día: cada fila es un año y cada columna un día del año. Es una variante del esquema de van Wijk y van Selow (1999) y muestra cuándo ocurre cada forma de día.

### Detección de anomalías

- **Residuo diario.** Resumen de los 24 residuos horarios de un día en un solo número: el residuo medio, **con signo**, en porcentaje de la predicción media del día. El signo distingue los días `alta` (más demanda de la esperable) de los `baja`, y el porcentaje permite comparar épocas con niveles distintos. Solo se usan días completos.
- **z modificado.** `z = 0.6745 · (x − mediana) / MAD`, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana. Ejemplo ilustrativo con cifras inventadas: con una mediana de 0.1 % y un MAD de 1.0 punto porcentual, un residuo de +6 % da z ≈ 4.0, mayor que 3.5, y se marca como `alta`. El 3.5 se calibró para datos normales (Iglewicz y Hoaglin) y es una convención: un valor más bajo marca más días, con más falsos positivos, y uno más alto marca menos, con más falsos negativos.
- **Sensibilidad al umbral.** Repetir la detección con varios umbrales (3, 3.5, 4 y 5) para ver cuánto cambia el número de días marcados. Si cambia mucho entre 3.5 y 4, el corte es frágil y se reporta. También se compara la concentración de atípicos por estación y por pliegue, porque un error del modelo desigual produciría atípicos que reflejan al modelo y no al día.
- **Validación sin etiquetas.** Cada episodio de la tabla (huracán Sandy, vórtices polares de 2014, frío de 2015, olas de calor de 2013, entre otros) lleva su fuente y una marca de verificación. Se reporta cuántos se recuperan, si la dirección coincide con la esperada (frío y calor: `alta`, Sandy: `baja`) y cuántos atípicos no corresponden a ningún episodio. Los episodios fuera del rango de los residuos (2006 y 2011) se marcan como **fuera de rango**, distinto de **sin coincidencia**. La atribución a eventos sigue siendo una hipótesis sin datos de temperatura.

### Pronóstico (aprendizaje supervisado) y métricas

- **División cronológica entrenamiento/prueba.** Se entrena con 2002-01-01 → 2016-12-31 y se prueba con 2017-01-01 → 2018-08-03. Con la hora de fin, el primer día de la prueba empieza en su hora 23 y queda incompleto.
- **Validación en ventana móvil (*rolling-origin*).** Repite la evaluación con varias particiones cronológicas: el modelo se entrena con el pasado hasta un punto, se evalúa en el periodo siguiente y el corte avanza. Aquí son 6 bloques consecutivos de 12 meses que terminan el 2018-08-03, con entrenamiento creciente y sin solapamiento, de modo que cada hora se predice una sola vez fuera de muestra. Da una evaluación más estable que una sola partición (el modelo debe superar al base en todos los pliegues) y produce los residuos de 2012-08 → 2018-08 que alimentan las anomalías. Exige entrenar un modelo por pliegue (y por región), por eso se hace con `PJME`. Cada pliegue es un año concreto con su clima.
- **Fuga de datos.** Usar información que no se tendría al pronosticar. Se evita con rezagos de al menos 24 h y medias móviles desplazadas 24 h, y el código lanza un error si algún rezago es menor que el horizonte.
- **Extrapolación de los árboles.** Un modelo de árboles no predice fuera del rango que vio en el entrenamiento. Podría explicar por qué, ante cambios bruscos de condiciones, el modelo base supera a XGBoost en 4 de los 10 peores días (dos de invierno, uno de primavera y uno de verano). Es una hipótesis que no se verificó.
- **MASE (error absoluto medio escalado).** El MAE del modelo dividido entre el error del pronóstico ingenuo estacional medido sobre los datos de entrenamiento (Hyndman y Koehler, 2006). El denominador es el error absoluto medio de «ayer a la misma hora» en el entrenamiento (`escala_ingenua`, estacionalidad de 24 h), que no es lo mismo que dividir entre el MAE del base en la prueba (eso sería un error relativo). Menor que 1: el modelo supera al ingenuo, mayor que 1: lo empeora. No depende de la escala, así que sirve para comparar entre regiones.

### Herramientas y buenas prácticas

- **Notebooks de Jupyter.** Hay tres, en orden: `01_datos`, `02_patrones` y `03_pronostico_anomalias`. La exportación vive en `src/export.py`.
- **Módulo reutilizable y paquete editable.** `src/` contiene `config.py` (rutas y parámetros), `data_loader.py`, `cleaning.py`, `features.py`, `modeling.py`, `profiles.py`, `anomalies.py` y `export.py`. Con `pip install -e .` los notebooks lo encuentran y los cambios se reflejan sin reinstalar.
- **Modelo en estrella.** Forma de organizar tablas para un panel: **dimensiones** pequeñas, con una fila por valor de un filtro (región, fecha, estación, tipo de día), y **hechos** grandes, con una fila por observación. Cada hecho se relaciona con sus dimensiones por una clave, y un filtro sobre la dimensión actúa en todas las tablas relacionadas. La exportación genera 4 dimensiones y las tablas de hechos y resultados. Una clave sin su fila en la dimensión haría que esa fila desapareciera al filtrar. Las tablas ya agregadas no responden al filtro de fecha.
- **Streamlit.** Herramienta del panel interactivo, de seis páginas. Python genera los CSV (dimensiones, hechos, residuos, tipos de día y anomalías) y la app los lee y los dibuja con Plotly, sin recalcular nada. Se ejecuta en local o con Docker Compose y no requiere licencias.

### Siglas

| Sigla | Significado | Dónde aparece |
|---|---|---|
| PJM | Pennsylvania-New Jersey-Maryland Interconnection, operador de la red | Dataset |
| EPT | *Eastern Prevailing Time*, hora civil del este de EE. UU. | `02_datos.md`, desfase entre regiones |
| MW | Megavatio | Variable objetivo |
| MAE | Error absoluto medio | Pronóstico |
| RMSE | Raíz del error cuadrático medio | Pronóstico |
| MAPE | Error porcentual absoluto medio | Pronóstico |
| MASE | Error absoluto medio escalado | `03_pronostico_anomalias` |
| STL | Descomposición estacional y de tendencia con loess | `02_patrones` |
| MAD | Mediana de las desviaciones absolutas respecto de la mediana | z modificado |
| CV | Coeficiente de variación | Comparación de regiones |
| ARI | Índice de Rand ajustado | `02_patrones` |
| IQR | Rango intercuartílico | Calidad de los datos |
| OE, P, HU | Objetivo específico, pregunta de investigación, historia de usuario | `01_proyecto.md` |
| D1 a D44 | Decisiones de diseño del proyecto | `05_decisiones.md` |

