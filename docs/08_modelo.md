# Documentación del modelo

Este documento describe los tres componentes analíticos del proyecto y cómo se evalúan.

| Parte | Tema | Pregunta | Notebook | Estado |
|---|---|---|---|---|
| A | Pronóstico de referencia a 24 horas | P4 y base de P3 | 04 | Hecho: supera al base en los 6 pliegues, MASE de 0.72 a 0.87 |
| B | Agrupamiento de perfiles diarios | P1 y P2 | 05 | Hecho: k = 2 (estacionales), silueta 0.413 (débil). D7 y justificación de k pendientes |
| C | Detección de días atípicos | P3 | 06 | Hecho: 22 días atípicos, 5 episodios coinciden |

---

# Parte A. Pronóstico de referencia

> Todas las cifras de esta parte salen de la ejecución del notebook 04 con el día operativo (`Datetime − 1 h`, decisión D1). Las horas son horas de inicio (0 = 00:00–01:00).

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

**Calidad.** Los datos provienen de la limpieza (`02_limpieza.ipynb`): en `PJME` se unificaron 4 duplicados y se agregaron e interpolaron 30 horas (17 de primavera, 12 de otoño y 1 de otra causa, el 2010-12-10 00:00, que también falta en otras 6 regiones). No se aplicó ningún tratamiento adicional.

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

## 4. Algoritmos

| Modelo | Motivo de elección | Parámetros |
|---|---|---|
| Base 24 h | Referencia mínima: "mañana será como hoy" a la misma hora | N/A |
| Base 168 h | Referencia semanal: "será como la semana pasada" | N/A |
| XGBoost | Funciona bien con datos tabulares, captura relaciones no lineales entre variables y entrena rápido | 500 árboles, tasa de aprendizaje 0.05, profundidad 6, `subsample` 0.8, `colsample_bytree` 0.8, `random_state` 42 |

Se descartaron Prophet y los modelos ARIMA: con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.

## 5. Métricas y resultados

Métricas definidas en `06_plan_proyecto.md`: MAE y RMSE (en MW), MAPE (en %) y MASE, evaluadas sobre los 13,897 registros de la prueba (partición única).

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

### Interpretación

XGBoost reduce el error cerca de un 19 % respecto al modelo base de 24 horas y casi un 47 % respecto al semanal, y la mejora se mantiene en los 6 pliegues (entre un 18 % y un 28 %). La mejora es moderada: el 71 % de la importancia recae en el consumo del día anterior a la misma hora, por lo que el modelo es esencialmente "ayer" con correcciones por tipo de día. Esas correcciones explican dónde gana más: en la transición matutina entre laborables y fines de semana y en los festivos, donde la referencia del día anterior es peor.

Donde menos mejora es en los episodios de clima extremo. Las variables disponibles (calendario e historial) no contienen información sobre la temperatura, que es el principal determinante de la demanda, y los errores más altos se concentran en la tarde, en los meses de verano y en los cambios bruscos de condiciones.

Un MAPE de 5.89 % para un pronóstico con 24 horas de antelación es un resultado razonable y no hay señales de fuga de datos: un error cercano a cero habría sido sospechoso.

## 6. Limitaciones

- **Sin temperatura.** Es el principal determinante de la demanda y el dataset no la incluye. Los picos extremos son los más difíciles de pronosticar, y un residuo grande puede ser clima y no una anomalía de otro tipo.
- **Los árboles no extrapolan.** Un modelo de árboles no predice valores fuera del rango que vio en el entrenamiento, lo que podría explicar los errores en olas de frío intensas (hipótesis).
- **Pliegues de 12 meses.** La ventana móvil reduce la dependencia de un solo periodo, pero cada pliegue es un año concreto con su clima, y los primeros entrenan con menos historia que los últimos.
- **Una sola región.** El modelo y los residuos son de `PJME`, para otras regiones hay que repetir el proceso, y entrenar un modelo por región y pliegue es lento.
- **Festivos federales.** No se incluyen los festivos de cada estado.
- **Hiperparámetros por defecto.** XGBoost no se ajustó con búsqueda de parámetros.
- **Sesgo.** El modelo tiende a sobrepronosticar: la mediana del residuo diario es negativa (de −0.65 % a −1.74 % según el pliegue), coherente con la ligera baja de demanda de largo plazo.

## 7. Reproducibilidad

El código está en `notebooks/04_modelado.ipynb`, `src/modeling.py` y `src/features.py`. Los parámetros del experimento están en `src/config.py` (`HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `N_PLIEGUES`, `MESES_PLIEGUE`, `SEMILLA`). El notebook usa 6 pliegues, por encima del mínimo `N_PLIEGUES`. Salidas: `residuos_PJME.parquet` y `metricas_ventana_movil_PJME.parquet` en `data/processed/`. Los pasos para ejecutarlo están en la [guía de usuario](09_guia_usuario.md).

---

# Parte B. Agrupamiento de perfiles diarios

> No confundir con la variable `tipo_dia` de los notebooks 03 y 04 (laborable, fin de semana, festivo), que se define por el calendario. Aquí el tipo de día lo descubre el agrupamiento a partir de la forma de la curva.

## 1. Datos de entrada

| Elemento | Detalle |
|---|---|
| Unidad de análisis | Un día de una región (45,430 perfiles de 12 regiones) |
| Perfil | 24 valores, uno por hora, del día operativo (`Datetime − 1 h`) |
| Normalización | Cada valor se divide entre el promedio de su día, para capturar la forma y no el tamaño |
| Magnitud | El consumo medio diario (`MW_medio_dia`) se guarda aparte |
| Días incluidos | Solo días completos (24 horas). Se descartó 1 día con menos de 24 horas |
| Alcance | Las 12 regiones juntas, de modo que los tipos de día son los mismos y se puede construir la matriz región por tipo de día (decisión D6) |

## 2. Diseño del experimento

| Elemento | Decisión |
|---|---|
| Algoritmos | K-medias y agrupamiento jerárquico (criterio de Ward) |
| Rango de k | 2 a 10 (`K_MIN`, `K_MAX`) |
| Muestra | La silueta y Ward se calculan sobre una muestra reproducible de 10,000 días (`MUESTRA_AGRUPAMIENTO`), porque escalan de forma cuadrática. Ward asigna el resto de los días al centro más cercano, k-medias usa todos |
| Selección de k | Mayor silueta media entre las combinaciones en que ningún grupo baja del 5 % de los días |
| Calidad de la estructura | El proyecto usa 0.50 como umbral de estructura razonable (`SILUETA_RAZONABLE`) y 0.26 como límite de la estructura débil (`SILUETA_DEBIL`), siguiendo a Kaufman y Rousseeuw. Por debajo de 0.26 no hay estructura sustancial. Se reporta tal como sale |
| Estabilidad | Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado). La repetición con distintas semillas queda por hacer |
| Alineación horaria | Parámetro `ALINEAR_HORA_CENTRAL`: con `True` se resta 1 h a las regiones de `REGIONES_HORA_CENTRAL` antes de calcular el día operativo. El notebook mide el desfase de cada región para decidir (decisión D7) |
| Interpretación | Curva media de cada grupo con banda de percentiles 10 a 90, frecuencia y composición por día de la semana, mes, estación y festivo |
| Días que no encajan | Distancia de cada día al centro de su grupo (`distancia_centroide`), insumo del notebook 06 |

## 3. Resultados

| Concepto | Valor |
|---|---|
| Algoritmo elegido | K-medias |
| k elegido | 2 |
| Silueta media (muestra) y su interpretación | 0.413, estructura débil |
| Concordancia entre k-medias y Ward (Rand ajustado) | 0.82 |
| Alineación de `COMED` y `NI` | No (`ALINEAR_HORA_CENTRAL = False`). El diagnóstico detecta +1 h en ambas y 0 en el resto. La decisión D7 sigue por tomar |

**Elección de k.** La mayor silueta con grupos de al menos el 5 % es k-medias con k = 2. Con k = 3 la silueta es 0.30 (débil) y con k ≥ 4 queda por debajo de 0.26 (sin estructura sustancial). Con Ward, k ≥ 7 tiene un grupo con menos del 5 % de los días.

| k | Silueta k-medias | Silueta Ward | Grupo más pequeño k-medias (%) | Grupo más pequeño Ward (%) |
|---|---|---|---|---|
| 2 | 0.413 | 0.373 | 38.2 | 46.3 |
| 3 | 0.301 | 0.238 | 26.8 | 22.7 |
| 4 | 0.240 | 0.189 | 17.6 | 15.9 |
| 5 | 0.245 | 0.174 | 16.7 | 12.6 |
| 6 | 0.226 | 0.164 | 6.4 | 6.0 |
| 7 | 0.220 | 0.159 | 8.0 | 4.0 |
| 8 | 0.205 | 0.152 | 5.7 | 4.0 |
| 9 | 0.198 | 0.141 | 5.0 | 4.0 |
| 10 | 0.194 | 0.132 | 5.7 | 4.0 |

**Descripción de cada grupo.**

| Grupo | Nombre | Días | % de los días | Hora pico | Hora mínima | Amplitud | % fin de semana | % festivo | Estación dominante |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Temporada fría (oct–may) | 28,299 | 62.3 | 19 h | 3 h | 0.2 | 28.9 | 3.2 | Invierno (38.1 %) |
| 2 | Verano (jun–sep) | 17,131 | 37.7 | 17 h | 4 h | 0.4 | 28.1 | 2.8 | Verano (63.0 %) |

- **Grupo 1:** reúne los días de octubre a mayo, con una meseta de mañana (7 a 11 h), un pico nocturno a las 19–20 h, un mínimo a las 3 h y una amplitud de ≈ 0.2 del promedio del día.
- **Grupo 2:** reúne los días de junio a septiembre, con una sola curva de pico a las 16–17 h (≈ 1.19 del promedio), un mínimo a las 4 h y una amplitud de ≈ 0.4.
- **Son tipos estacionales, no de calendario.** El 28.9 % y el 28.1 % de los días son sábado o domingo, casi igual que el 28.6 % esperado si no hubiera relación, y los festivos no se concentran. No hay un tipo de día de fin de semana. Una hipótesis, sin verificar, es que el efecto de fin de semana es sobre todo de nivel (cerca de −9 % según el notebook 03) y desaparece al dividir cada perfil entre el promedio del día.
- Los nombres automáticos del notebook («G1 · Invierno · mixto» y «G2 · Verano · mixto») se sustituyen por los nombres basados en el calendario. Esa sustitución todavía no llega a las tablas guardadas (el notebook 06 aún lee los nombres automáticos) y debe aplicarse antes de exportar.

**Mezcla de tipos de día y estacionalidad por región.** «Común» es el periodo común de las 10 regiones vigentes (2013-06-01 → 2018-08-02).

| Región | % grupo 1, historial | % grupo 2, historial | % grupo 1, común | % grupo 2, común | Razón invierno/verano (común) | Amplitud diaria (común) |
|---|---|---|---|---|---|---|
| AEP | 67.8 | 32.2 | 64.0 | 36.0 | 1.059 | 0.302 |
| COMED | 60.4 | 39.6 | 59.3 | 40.7 | 0.928 | 0.340 |
| DAYTON | 65.1 | 34.9 | 61.8 | 38.2 | 1.008 | 0.342 |
| DEOK | 60.2 | 39.8 | 58.3 | 41.7 | 0.945 | 0.347 |
| DOM | 55.2 | 44.8 | 55.3 | 44.7 | 0.985 | 0.400 |
| DUQ | 65.4 | 34.6 | 63.3 | 36.7 | 0.917 | 0.327 |
| EKPC | 55.2 | 44.8 | 55.2 | 44.8 | 1.196 | 0.440 |
| FE | 69.4 | 30.6 | 69.1 | 30.9 | 0.996 | 0.306 |
| NI | 52.3 | 47.7 | n. a. | n. a. | n. a. | n. a. |
| PJME | 59.9 | 40.1 | 60.0 | 40.0 | 0.950 | 0.369 |
| PJMW | 67.3 | 32.7 | 64.4 | 35.6 | 1.119 | 0.322 |
| PJM_Load | 55.7 | 44.3 | n. a. | n. a. | n. a. | n. a. |

- En el periodo común, la proporción de días de verano va de ≈ 31 % (`FE`) a ≈ 45 % (`DOM` y `EKPC`).
- Sigue a la amplitud diaria de cada región (`EKPC` 0.44, `DOM` 0.40, `FE` 0.31) y no al sesgo invernal o veraniego: `EKPC` tiene sesgo invernal (1.20) y aun así es de las regiones con más días de forma veraniega.
- Al comparar el historial completo con el periodo común cambian las mezclas de `AEP`, `DAYTON` y `PJMW` (entre 3 y 4 puntos), por eso conviene reportar ambas.

**Días que no encajan en su grupo.** La distancia al centro tiene una mediana de ≈ 0.21 en ambos grupos (media 0.226 y 0.223). El día más lejano es el 2008-09-14 de `DAYTON` (1.54), y `EKPC` aparece 6 veces entre los 10 primeros. La distancia no es comparable entre regiones y conviene normalizarla antes de usarla como insumo del notebook 06.

**Salidas** (`data/processed/`): `tipos_de_dia.parquet` (45,430 filas), `tipos_de_dia_curvas.parquet` (48 filas), `tipos_de_dia_resumen.parquet` (2 filas), `tipos_de_dia_mezcla_region.parquet` (24 filas) y `tipos_de_dia_silueta_k.parquet` (18 filas).

## 4. Limitaciones

- **Estructura débil.** La silueta de 0.413 indica que los perfiles diarios forman en parte un continuo, así que los tipos de día son una simplificación útil y no categorías naturalmente separadas.
- **k = 2 solo captura la estación.** Si se quiere separar el fin de semana hay que probar un k mayor y justificar la elección aunque la silueta baje (con k = 3 es 0.30 y con k ≥ 4 es menor de 0.26). Esta decisión está pendiente.
- K-medias asume grupos compactos con distancia euclidiana.
- Al normalizar por el promedio del día se pierde la información de magnitud.
- Las regiones cubren periodos distintos, y eso afecta a su mezcla de tipos de día, por eso se compara también en el periodo común.
- Sin alinear `COMED` y `NI` a hora central, su curva llega una hora más tarde y puede separarse por la hora y no por la forma. Falta repetir con `ALINEAR_HORA_CENTRAL = True` y comparar (D7).
- El agrupamiento es conjunto para las 12 regiones, lo que permite compararlas pero puede esconder formas propias de una región.
- La silueta y Ward se calculan sobre una muestra de días (grupo más pequeño: 38.2 % en la muestra y 37.7 % con todos los días).
- Sin temperatura, los tipos de día se interpretan por el calendario y no por el clima.

## 5. Reproducibilidad

El código está en `notebooks/05_agrupamiento.ipynb` y `src/profiles.py`. Los parámetros (`K_MIN`, `K_MAX`, `TAMANO_MIN_GRUPO`, `SILUETA_RAZONABLE`, `SILUETA_DEBIL`, `MUESTRA_AGRUPAMIENTO`, `SEMILLA`) están en `src/config.py`. `ALINEAR_HORA_CENTRAL` y `REGIONES_HORA_CENTRAL` deben tener el mismo valor en los notebooks 05 y 07.

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
| Base del cálculo | Todos los días de la región (decisión D8). La opción `Z_POR_ESTACION` queda como alternativa |
| Comprobaciones | Sensibilidad al umbral (3, 3.5, 4 y 5), concentración de atípicos por estación y pliegue, y tasa en festivos |
| Validación | Contraste con episodios externos (olas de calor o frío, huracán Sandy), cada uno con su fuente y marca de verificación. Los episodios fuera del rango de los residuos se marcan como no evaluados. Los datos no traen etiquetas de anomalías |
| Dirección esperada | Frío o calor extremo: residuos positivos, huracán Sandy: negativos |
| Complemento | Relación con la distancia de cada día al centro de su grupo (Parte B) |

## 3. Resultados

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

Los atípicos no se concentran en una estación (0.7 % a 1.3 %). El pliegue 2 tiene más (7 días, 1.9 %). En festivos la tasa es 1.54 % (1 de 65 días) frente a 0.99 % en no festivos.

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
| Vórtice polar de fines de enero de 2014 | 2014-01-23 → 01-29 | Coincide | 1 (2014-01-28) | 3.57 | Alta / Alta | Sí |
| Ola de frío de febrero de 2015 | 2015-02-14 → 02-21 | Coincide | 1 (2015-02-15) | 4.85 | Alta / Alta | Sí |
| Tormenta Jonas | 2016-01-22 → 01-24 | Sin coincidencia | 0 | n. a. | Por verificar | **No** |
| Ola de frío de enero de 2018 | 2018-01-01 → 01-07 | Sin coincidencia | 0 | n. a. | Alta / n. a. | Sí |

### Interpretación

- **El detector encuentra los eventos de mayor magnitud.** Sandy, el vórtice polar de enero de 2014 y la ola de frío de febrero de 2015 son los tres atípicos con mayor |z| entre los episodios, y en los 5 episodios detectados el signo coincide con el esperado: demanda por encima de lo esperable en frío y calor extremos y por debajo en Sandy.
- **Dónde falla.** No salen atípicos la ola de calor de julio de 2013, la ola de frío de enero de 2018 ni la tormenta Jonas (esta última con fechas sin verificar). Una posible explicación, a confirmar, es que en episodios largos los rezagos y medias móviles del modelo ya incorporan el nivel alto de demanda y el residuo no se dispara.
- **Predominan los atípicos altos** (15 de 22). El modelo tiende además a sobrepronosticar, un sesgo coherente con la ligera baja de demanda de largo plazo del notebook 03.
- **Los casos hora a hora apuntan al clima.** En Sandy la demanda real cayó a unos 15,000 MW frente a unos 30,000 esperados. El 2014-01-07 llegó a cerca de 50,000 MW con un pronóstico muy inferior. Sin temperatura en el dataset, esto es una hipótesis.
- **16 de los 22 atípicos no coinciden con ningún episodio de la tabla.** Son días a revisar contra el clima y el calendario. Dos de ellos caen el día siguiente a un festivo (2016-07-05 y 2018-05-29), un patrón compatible con que el rezago de 24 h hereda la baja demanda del festivo, a verificar.
- **Forma frente a nivel.** La correlación de Spearman es 0.02, pero los días extremos en nivel tienden a serlo también en forma (36 % frente a ≈ 5 %), aunque no de manera lineal. Por tipo de día, la tasa es 0.8 % en el grupo 1 (11 de 1,350 días) y 1.3 % en el grupo 2 (11 de 841).

### Criterios de cierre

| Criterio | Estado |
|---|---|
| Lista contrastada con al menos un episodio externo, con fuente | Cumplido: 5 episodios con fuente y fechas verificadas coinciden con días atípicos y con la dirección esperada |
| Sensibilidad del umbral reportada | Cumplido |
| Revisión de concentración por estación y pliegue | Cumplido |

**Salidas** (`data/processed/`): `anomalias_PJME_diario.parquet` (2,191 filas), `anomalias_PJME_lista.parquet` (22 filas) y `anomalias_PJME_episodios.parquet` (10 filas).

## 4. Limitaciones

- Sin temperatura, las anomalías solo pueden interpretarse por coincidencia con eventos. Un día extremo por clima puede no salir atípico si los rezagos y medias móviles del modelo ya lo incorporaban.
- Lo atípico depende del modelo: otro pronóstico daría otros residuos y otra lista.
- Un residuo grande también puede deberse a un error de los datos, por eso se revisan las horas vecinas antes de concluir.
- Solo hay residuos de `PJME`, y cubren los últimos seis años, los episodios anteriores (2006 y 2011) quedan fuera de rango y no se evalúan.
- El umbral de 3.5 es el valor convencional para el z modificado y no garantiza una tasa de falsos positivos concreta. Los residuos no son normales, por eso se muestra la sensibilidad.
- Los primeros pliegues entrenan con menos historia. En la práctica el pliegue 2 concentra más atípicos (7 de 22) y el pliegue 1 solo 3.
- Los días de cambio de horario tienen una hora estimada o promediada en la limpieza, si resultan atípicos hay que descartar ese efecto.
- La tabla de episodios no es exhaustiva: que un atípico no coincida con un episodio no lo hace una falsa alarma. Solo recoge 10 eventos, uno de ellos sin verificar.
- No hay verdad de referencia con la que medir la detección.

## 5. Reproducibilidad

El código está en `notebooks/06_anomalias.ipynb` y `src/anomalies.py`. Los parámetros (`UMBRAL_Z_MODIFICADO`, `TOLERANCIA_EPISODIO_DIAS`) están en `src/config.py`. La tabla de episodios, con sus fuentes, está en el notebook 06 y reemplaza a `EPISODIOS_CONOCIDOS` de `src/anomalies.py`, que no incluye fuentes: conviene actualizar ese archivo con la misma tabla.