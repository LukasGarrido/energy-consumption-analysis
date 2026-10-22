# 11 · Conceptos teóricos

Este documento reúne los conceptos usados en el proyecto, agrupados por tema. Cada concepto se define de forma general y se explica **qué papel juega aquí**, con cifras de los notebooks cuando ayudan a entenderlo.

**Contenido**

1. Dominio: el sistema eléctrico
2. Series de tiempo
3. El tiempo en los datos
4. Calidad de datos y limpieza
5. Estadística descriptiva y comparación
6. Tendencia y estacionalidad
7. Modelado y pronóstico
8. Métricas de evaluación
9. Herramientas y buenas prácticas
10. Glosario de siglas

---

## 1. Dominio: el sistema eléctrico

**Demanda (o carga) eléctrica.** Cantidad de electricidad que los consumidores piden a la red en un momento dado. Cambia con la hora, el día, la estación y el clima.
*En el proyecto:* la columna `MW` es la demanda horaria de cada región. Es la variable que se analiza y se pronostica.

**Potencia (MW) y energía (MWh).** La potencia indica cuánta electricidad se usa *en un instante* y se mide en vatios (1 MW = 1,000,000 W). La energía indica cuánta se usó *durante un tiempo*: 100 MW sostenidos durante una hora son 100 MWh. Es la diferencia entre la velocidad de un coche y los kilómetros recorridos.
*En el proyecto:* los datos vienen en MW, con un valor por hora. Como cada fila cubre exactamente una hora, el valor en MW coincide numéricamente con los MWh de esa hora, por lo que se puede promediar sin conversión.

**PJM Interconnection y sus regiones.** PJM es una organización regional que coordina la red eléctrica de 13 estados del este de EE. UU. y Washington D.C. Reporta la demanda por zonas o regiones.
*En el proyecto:* hay 12 regiones (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load). Tienen tamaños muy distintos (`PJME` promedia unos 32,080 MW y `DUQ` unos 1,659 MW) y algunas son subzonas de otras (`PJMW` no es una continuación de `PJM_Load`).

**Pico y valle de demanda.** El pico es el momento de mayor consumo; el valle, el de menor consumo. Los picos son los que exigen más a la red.
*En el proyecto:* el valle diario ocurre de madrugada (hacia las 4–5 h, con cerca del 83 % del promedio) y el pico entre las 18 y las 20 h. El máximo histórico de `PJME` fue de 62,009 MW el 2 de agosto de 2006.

**Temperatura como factor de la demanda.** El clima es el principal determinante de la demanda: el calor dispara el aire acondicionado y el frío la calefacción.
*En el proyecto:* el dataset **no incluye temperatura**. Solo puede inferirse a partir de la estacionalidad, y su ausencia limita la precisión del pronóstico, sobre todo en olas de calor y de frío.

---

## 2. Series de tiempo

**Serie de tiempo.** Conjunto de observaciones ordenadas en el tiempo. El orden importa: cada valor depende de los anteriores y no se pueden mezclar al azar.
*En el proyecto:* cada región es una serie con una observación por hora. Por eso la división entre entrenamiento y prueba es cronológica y los rezagos se calculan por región.

**Frecuencia y regularidad.** Una serie es regular cuando entre observaciones consecutivas pasa siempre el mismo tiempo. Muchas herramientas (medias móviles, rezagos, STL) suponen esa regularidad.
*En el proyecto:* la limpieza garantiza una fila por hora, sin saltos ni repeticiones. `validar_limpieza` lo comprueba comparando cada fecha con la anterior.

**Estacionalidad.** Patrón que se repite en un periodo fijo. En demanda eléctrica hay tres niveles: diaria (24 horas), semanal (7 días) y anual.
*En el proyecto:* se observan los tres. El ciclo diario tiene valle de madrugada y pico por la tarde-noche; el fin de semana consume entre un 4 % y un 14 % menos que un laborable; y el ciclo anual tiene picos en verano e invierno con valles en abril y octubre.

**Tendencia.** Movimiento lento y de largo plazo de la serie, una vez descontada la estacionalidad.
*En el proyecto:* no hay crecimiento sostenido, sino estabilidad o ligera baja: `PJME` pasó de 33,611 MW (2007) a 30,652 MW (2017), un −9 %, y `AEP` bajó un −13 %.

**Residuo (o ruido).** Lo que queda de la serie después de quitar la tendencia y la estacionalidad: variaciones puntuales, como las que provoca el clima extremo.
*En el proyecto:* los residuos grandes de la descomposición STL señalan días fuera de lo esperable.

**Descomposición aditiva.** Modelo que expresa la serie como la suma de tres partes: *tendencia + estacionalidad + residuo*.
*En el proyecto:* se aplica a la serie diaria de `PJME` con STL.

**Efecto calendario.** Influencia de los fines de semana y festivos en el consumo, independiente del clima.
*En el proyecto:* un festivo consume en promedio cerca de un 5 % menos que un laborable y un fin de semana cerca de un 9 % menos. Por eso `es_festivo` y `es_fin_de_semana` son variables del modelo.

---

## 3. El tiempo en los datos

**Hora de fin de intervalo (*hour ending*).** Convención que etiqueta cada hora con el instante en que termina: la hora 1 es la que va de 00:00 a 01:00 y la hora 24 es la última del día. PJM la usa en sus reportes.
*En el proyecto:* `Datetime` parece seguir esta convención: todas las series empiezan a las 01:00 y terminan a las 00:00. Consecuencias: la fila de las 00:00 es la última hora del día anterior, el "pico a las 19 h" corresponde al intervalo 18:00–19:00, y `dia_semana`, `es_fin_de_semana` y `es_festivo` quedan desplazados un día en esa fila (1 de cada 24 horas).

**Hora local y EPT.** EPT (*Eastern Prevailing Time*) es la hora civil del este de EE. UU., que cambia entre horario estándar y de verano.
*En el proyecto:* los datos parecen estar todos en EPT, aunque algunas regiones operen en hora central.

**Horario de verano (cambio de hora).** Dos veces al año se adelanta o se retrasa el reloj una hora. En primavera una hora **no existe**; en otoño una hora **ocurre dos veces**.
*En el proyecto:* explica casi todas las horas faltantes y los duplicados. En `PJME`, 17 de las 30 horas faltantes son de primavera (siempre a las 03:00) y 12 de otoño (a las 02:00, de 2002 a 2013). Desde 2014 la hora de otoño aparece duplicada: 4 fechas repetidas por región (2014 a 2017).

**Hora faltante y hora repetida.** Una fila que debería existir y no está, o una fecha que aparece dos veces con valores distintos.
*En el proyecto:* se detectan comparando con el calendario ideal y se corrigen reindexando (las faltantes) y promediando (las repetidas).

**Desfase entre regiones.** Diferencia de hora entre perfiles que deberían parecerse.
*En el proyecto:* `COMED` aparece retrasada 1 hora (error de 0.014 con ese desplazamiento frente a 0.024 sin él). Es coherente con que todas las series estén en hora del este mientras `COMED`, en la zona de Chicago, opera en hora central: su actividad ocurre una hora más tarde en el reloj del este. No requiere corrección: tener todas las regiones en un mismo reloj facilita compararlas.

**Día completo.** Día con sus 24 horas. El primer y el último día de una serie pueden tener menos.
*En el proyecto:* el último día de cada serie solo tiene la hora 00:00, y su promedio sería el de un solo punto. Por eso los promedios diarios y el análisis de los peores días usan solo días completos.

---

## 4. Calidad de datos y limpieza

**Valor nulo.** Dato que falta en una celda (`NaN`).
*En el proyecto:* el dataset original no tiene nulos. Aparecen al reindexar (las horas nuevas) o al marcar errores, y la interpolación los rellena.

**Duplicado.** Registro repetido para una misma fecha.
*En el proyecto:* hay 40 en total (4 por región en 10 regiones), con valores de MW distintos. Se unifican promediando.

**Calendario ideal y reindexación.** El calendario ideal es la lista de todas las horas entre la primera y la última fecha de una serie. Reindexar es forzar a la serie a tener una fila por cada una de esas horas: las que faltaban se crean con valor vacío.
*En el proyecto:* en `AEP`, el calendario tiene 121,296 horas y el archivo traía 121,269 distintas, así que se agregaron 27 filas. En total se agregaron 217 horas en las 12 regiones.

**Cobertura.** Porcentaje de las horas esperadas que realmente existen: horas distintas ÷ horas del calendario ideal.
*En el proyecto:* entre 99.98 % y 99.99 % en todas las regiones, es decir, casi no hay huecos.

**Periodo común y regiones vigentes.** El periodo común es el intervalo en el que *todas* las regiones comparadas tienen datos: empieza en el inicio más tardío y termina en el final más temprano. Las regiones vigentes son las que llegan hasta el final del dataset.
*En el proyecto:* no existe periodo común a las 12 regiones. Las 10 vigentes comparten 2013-06-01 → 2018-08-03, y las comparaciones entre regiones se hacen en ese intervalo.

**Valor atípico y rango intercuartil (IQR).** Un valor atípico se aleja mucho del resto. La regla del IQR considera atípico lo que queda fuera del intervalo [Q1 − 1.5·IQR, Q3 + 1.5·IQR], donde Q1 y Q3 son el primer y el tercer cuartil y IQR = Q3 − Q1.
*En el proyecto:* en `AEP`, Q1 = 13,630, Q3 = 17,200 y IQR = 3,570, así que los límites son 8,275 y 22,555 MW. En todo el dataset hay 19,693 valores altos y solo 51 bajos.

**Error de medición frente a valor extremo real.** Un valor extremo puede ser un error del sensor o consumo real. El criterio usado es la **continuidad**: varias horas seguidas extremas sugieren un evento real; un valor aislado entre horas normales sugiere un error.
*En el proyecto:* los picos altos forman una nube continua y se conservan. El 0 de `FE` (su primer registro) y los 1,253 MW de `DOM` (el siguiente mínimo es 5,518) son aislados y sospechosos.

**Interpolación lineal.** Estimar un valor faltante con la recta que une el valor anterior y el siguiente. Si entre 105 y 110 hay dos huecos, valen 106.7 y 108.3.
*En el proyecto:* se rellenan huecos de hasta 2 horas seguidas con valor válido a cada lado (por ejemplo, `FE` el 2012-03-11 a las 03:00 se estimó en 5,929.5 MW). Los huecos más largos no se rellenan, porque estimar muchas horas seguidas sería fabricar datos. Se interpoló el 0.02 % de las horas.

**Recorte de extremos.** Eliminar los vacíos al inicio o al final de una serie, que no se pueden interpolar porque falta un vecino.
*En el proyecto:* se aplicó a `FE`, cuyo primer registro era el valor en 0 MW: ahora empieza a las 02:00.

**Validación de datos.** Comprobaciones automáticas de que el resultado cumple lo esperado.
*En el proyecto:* `validar_limpieza` exige fechas sin repetir, orden cronológico, una hora exacta entre filas, sin vacíos y sin valores menores o iguales a 0. Si algo falla, lanza un error.

**Formato largo y formato ancho.** En el largo cada observación es una fila (`Datetime`, `region`, `MW`); en el ancho hay una columna por región.
*En el proyecto:* el análisis usa el formato largo porque facilita agrupar y comparar regiones. El archivo `pjm_hourly_est.csv` es ancho y no se utiliza.

**Archivo parquet.** Formato binario por columnas, más compacto y rápido que el CSV, que conserva los tipos de dato (como las fechas).
*En el proyecto:* la limpieza guarda sus resultados en parquet.

---

## 5. Estadística descriptiva y comparación

**Media, mediana y desviación estándar.** La media es el promedio; la mediana, el valor central; la desviación estándar mide cuánto se dispersan los datos alrededor de la media.
*En el proyecto:* en `PJME`, la media es 32,080 MW y la mediana 31,421: la media es mayor porque los picos altos la arrastran hacia arriba.

**Cuartiles y diagrama de caja (*boxplot*).** Los cuartiles dividen los datos ordenados en cuatro partes. El diagrama de caja dibuja el 50 % central (la caja), la mediana (la línea) y los valores atípicos (los puntos).
*En el proyecto:* se usó para comparar la distribución de las 12 regiones. Su límite es que las regiones grandes aplastan visualmente a las pequeñas.

**Coeficiente de variación (CV).** Desviación estándar ÷ media, en porcentaje. Permite comparar la variabilidad entre series de distinto tamaño.
*En el proyecto:* va de 16.9 % (`AEP`, `FE`) a 25.9 % (`EKPC`).

**Razón pico/media.** Máximo ÷ media: cuánto se dispara el pico respecto a lo habitual.
*En el proyecto:* va de 1.66 (`AEP`) a 2.38 (`EKPC`), la región con los picos más extremos.

**Normalización relativa (`MW_rel`).** Dividir cada valor entre el promedio de su región. Un valor de 1.2 significa un 20 % por encima de lo habitual para esa región.
*En el proyecto:* en `AEP`, el primer registro (12,379 MW) equivale a 0.80. Permite comparar la **forma** del consumo entre regiones y no su tamaño.

**Perfil.** Promedio del consumo agrupado por una categoría (hora, día de la semana, mes o estación).
*En el proyecto:* los perfiles muestran el ciclo diario, semanal y anual y cómo cambian con la estación.

**Correlación de Pearson.** Medida entre −1 y 1 de cuánto suben y bajan juntas dos series. Cerca de 1, se mueven en la misma dirección.
*En el proyecto:* se calcula sobre el promedio diario de las 10 regiones vigentes. Los valores van de 0.56 (`EKPC`–`COMED`) a 0.96 (`AEP`–`PJMW`, `DAYTON`–`FE`). Son altos en buena parte porque todas comparten la estacionalidad anual, así que no significan que se parezcan en todo.

**Mapa de calor.** Gráfico que representa un valor con un color en una tabla de dos dimensiones.
*En el proyecto:* se usa para el consumo por hora y día de la semana, las horas faltantes por año y región, la correlación entre regiones y el mes del pico anual.

---

## 6. Tendencia y estacionalidad

**Media móvil.** Promedio de una ventana de observaciones que se desplaza a lo largo de la serie, y suaviza las variaciones cortas.
*En el proyecto:* una ventana de 365 días cancela la estacionalidad anual, porque cada ventana contiene un invierno y un verano completos. Lo que queda es la tendencia.

**Media móvil centrada y efecto de borde.** En una media móvil centrada, cada promedio se coloca en el centro de su ventana. A cambio, no se puede calcular en los extremos de la serie, y las estimaciones cercanas a ellos son poco fiables.
*En el proyecto:* explica por qué la línea gruesa de las gráficas de tendencia es más corta que la serie. También por qué la subida que muestra la tendencia STL de `PJME` al final de 2017 no es fiable.

**Descomposición STL.** *Seasonal-Trend decomposition using LOESS* (Cleveland et al., 1990). Separa una serie en tendencia, estacionalidad y residuo usando regresiones locales (LOESS).
*En el proyecto:* se aplica con `period=365` a la serie diaria de `PJME`. La opción `robust=True` reduce la influencia de los valores extremos. La tendencia se mueve entre unos 30,500 y 33,300 MW, con su máximo en 2007–2008 y el mínimo en 2016–2017. Como el periodo fijo de 365 días ignora los años bisiestos, es una aproximación.

**Año completo.** Año con (casi) todas sus horas. Se usa para evitar que un año parcial parezca una caída.
*En el proyecto:* se considera completo con al menos 8,700 de las 8,760 horas. 114 de las 134 combinaciones región-año lo cumplen.

---

## 7. Modelado y pronóstico

**Pronóstico y horizonte.** Pronosticar es predecir valores futuros. El horizonte es cuánto tiempo hacia adelante se predice.
*En el proyecto:* el horizonte es de 24 horas: para predecir la hora *t* solo se usa información hasta *t − 24*.

**Variable objetivo y variables explicativas.** La objetivo es lo que se quiere predecir; las explicativas (*features*) son los datos con los que se predice.
*En el proyecto:* la objetivo es `MW`. Las explicativas son el calendario, los rezagos y las medias móviles.

**Ingeniería de variables.** Crear variables informativas a partir de los datos originales.
*En el proyecto:* se derivan de la fecha (hora, día de la semana, mes, fin de semana, festivo) y del propio historial del consumo (rezagos y medias móviles).

**Rezago (*lag*).** Valor de la serie de hace *k* pasos.
*En el proyecto:* `MW_lag_24` es el consumo de hace 24 horas (ayer a la misma hora), `MW_lag_48` el de hace 2 días y `MW_lag_168` el de hace una semana. Se calculan por región, para no mezclar series.

**Media móvil desplazada.** Promedio de las horas previas, desplazado para que termine antes del momento a predecir.
*En el proyecto:* `MW_media_24h` y `MW_media_168h` promedian las 24 y 168 horas que terminan 24 horas antes de *t*.

**Fuga de datos (*data leakage*).** Usar para entrenar información que no estaría disponible al momento de pronosticar. Produce resultados engañosamente buenos.
*En el proyecto:* un rezago de 1 hora sería una fuga con un horizonte de 24 horas. Por eso todos los rezagos son de 24 horas o más y `agregar_rezagos` lanza un error si se pide uno menor. También se excluyen `MW_rel` (usa el promedio de toda la región, incluido el futuro) y `anio`.

**División cronológica entrenamiento/prueba.** El conjunto de entrenamiento se usa para que el modelo aprenda; el de prueba, para evaluarlo con datos que no ha visto. En series de tiempo, la división respeta el orden: el entrenamiento es anterior a la prueba.
*En el proyecto:* se entrena con 2002-01-01 → 2016-12-31 (131,495 filas) y se prueba con 2017-01-01 → 2018-08-03 (13,897 filas). Una división al azar mezclaría horas contiguas y produciría una fuga.

**Modelo base (*baseline*).** Pronóstico simple contra el cual comparar. Un modelo complejo solo se justifica si lo supera.
*En el proyecto:* el base de 24 horas predice "como ayer a la misma hora" (MAE de 2,300 MW) y el de 168 horas "como la semana pasada" (MAE de 3,511 MW).

**Árbol de decisión, *gradient boosting* y XGBoost.** Un árbol de decisión predice dividiendo los datos con reglas sucesivas ("si la hora es mayor que 7 y es laborable..."). El *gradient boosting* construye muchos árboles pequeños en secuencia, de modo que cada uno corrige los errores de los anteriores. XGBoost (Chen y Guestrin, 2016) es una implementación eficiente de esta técnica.
*En el proyecto:* es el modelo de pronóstico. Funciona bien con datos tabulares y captura relaciones no lineales entre variables.

**Hiperparámetros.** Ajustes del modelo que se fijan antes de entrenar.
*En el proyecto:* 500 árboles (`n_estimators`), tasa de aprendizaje 0.05 (cuánto corrige cada árbol), profundidad máxima 6 (`max_depth`), `subsample` 0.8 y `colsample_bytree` 0.8 (fracción de filas y de variables que usa cada árbol). No se ajustaron con búsqueda de parámetros.

**Sobreajuste (*overfitting*).** Cuando un modelo memoriza los datos de entrenamiento y generaliza mal.
*En el proyecto:* se evalúa solo con datos de prueba que el modelo no vio para detectarlo.

**Extrapolación de los árboles.** Un modelo de árboles no predice valores fuera del rango que vio al entrenar.
*En el proyecto:* podría explicar por qué en olas de frío intensas el modelo base supera a XGBoost en 4 de los 10 peores días. Es una hipótesis que no se verificó.

**Importancia de variables.** Medida de cuánto contribuye cada variable a las predicciones del modelo. No implica causalidad.
*En el proyecto:* `MW_lag_24` concentra el 71.1 % y le siguen `MW_lag_168` (9.1 %) y `es_fin_de_semana` (8.1 %). El modelo es esencialmente "ayer" con correcciones por tipo de día.

**Semilla aleatoria.** Número que fija la parte aleatoria de un algoritmo, para que dé el mismo resultado en cada ejecución.
*En el proyecto:* `SEMILLA = 42` en `config.py`.

---

## 8. Métricas de evaluación

**Error de pronóstico.** Diferencia entre el valor predicho y el real: *error = predicho − real*.

**MAE (error absoluto medio).** Promedio del valor absoluto de los errores: MAE = media de |predicho − real|. Se expresa en MW y es fácil de interpretar.
*En el proyecto:* XGBoost tiene un MAE de 1,862 MW: se equivoca, en promedio, en esa cantidad de megavatios (cerca del 6 % del consumo medio).

**RMSE (raíz del error cuadrático medio).** RMSE = raíz de la media de (predicho − real)². Al elevar al cuadrado, penaliza más los errores grandes. Siempre es mayor o igual que el MAE, y una diferencia grande entre ambos indica que hay errores muy altos puntuales.
*En el proyecto:* 2,513 MW frente a un MAE de 1,862.

**MAPE (error porcentual absoluto medio).** MAPE = media de |predicho − real| ÷ real × 100. Expresa el error como porcentaje, lo que permite comparar series de distinto tamaño. Se vuelve inestable si el valor real se acerca a cero.
*En el proyecto:* 5.89 %. No hay problema de ceros porque la limpieza eliminó los valores menores o iguales a 0.

**Mejora relativa.** Reducción del error de un modelo frente a otro: 1 − error del modelo ÷ error de la referencia.
*En el proyecto:* XGBoost reduce el MAE un 19.0 % frente al modelo base de 24 horas y un 47.0 % frente al semanal.

**Análisis de errores por segmento.** Calcular el error por hora, mes o tipo de día para ver dónde falla el modelo.
*En el proyecto:* el error es menor de madrugada y mayor por la tarde-noche. La mayor ganancia frente al modelo base está en los festivos (30.9 %) y fines de semana (25.3 %), y la menor en los laborables (15.4 %).

---

## 9. Herramientas y buenas prácticas

**Notebook de Jupyter.** Documento que combina código, resultados y texto, ejecutado por celdas.
*En el proyecto:* hay cuatro, en orden: exploración, limpieza, análisis y modelado.

**Módulo reutilizable y paquete editable.** Una función que se usa en varios notebooks se mueve a un archivo `.py` en `src/` y se importa. Con `pip install -e .` y el archivo `pyproject.toml`, esa carpeta se registra como un paquete y se puede importar desde cualquier lugar.
*En el proyecto:* `src/` contiene `config.py` (rutas y parámetros), `data_loader.py`, `cleaning.py`, `features.py` y `modeling.py`.

**Entorno virtual y dependencias.** Un entorno virtual aísla las librerías del proyecto; `requirements.txt` lista cuáles son.
*En el proyecto:* `python -m venv .venv` y `pip install -r requirements.txt`.

**Control de versiones.** Registro de los cambios del código a lo largo del tiempo, con Git y GitHub.
*En el proyecto:* el repositorio guarda el código, los notebooks y la documentación. Los datos crudos no se versionan (`data/raw` está ignorado).

**Reproducibilidad.** Que otra persona pueda obtener los mismos resultados siguiendo los pasos.
*En el proyecto:* se apoya en el entorno virtual, la semilla fija, la guía de usuario y el orden numerado de los notebooks.

**Operaciones de pandas más usadas.**

| Operación | Qué hace |
|---|---|
| `groupby` | Agrupa filas por una o más columnas para calcular estadísticos por grupo |
| `unstack` | Convierte un nivel del índice en columnas, para armar tablas anchas |
| `transform` | Como `groupby`, pero repite el resultado en cada fila (sirve para normalizar por región) |
| `resample` | Agrupa una serie de tiempo por periodos (por ejemplo, por día) |
| `reindex` | Fuerza un índice nuevo, creando filas vacías donde faltan |
| `interpolate` | Estima valores faltantes a partir de los vecinos |
| `shift` y `rolling` | Desplazan la serie y calculan ventanas móviles (rezagos y medias móviles) |

**Dashboard con Streamlit.** Streamlit es una librería de Python para construir aplicaciones web interactivas con pocas líneas de código.
*En el proyecto:* es la herramienta elegida para la visualización final (pendiente), con filtros por región y fechas.

**Análisis exploratorio de datos (EDA).** Revisión inicial de los datos con estadística y gráficos, antes de modelar (Tukey, 1977).
*En el proyecto:* es el notebook 01, de donde salieron las decisiones de limpieza.

**CRISP-DM.** Metodología por fases para proyectos de minería de datos: comprensión del problema y de los datos, preparación, modelado, evaluación y despliegue (Chapman et al., 2000).
*En el proyecto:* las fases del proyecto siguen una lógica parecida: comprensión y exploración, limpieza, análisis, modelado y visualización.

---

## 10. Glosario de siglas

| Sigla | Significado | Dónde aparece |
|---|---|---|
| MW | Megavatio, unidad de potencia | Todas las series |
| MWh | Megavatio-hora, unidad de energía | Diferencia entre potencia y energía |
| PJM | PJM Interconnection, operador de la red del este de EE. UU. | Origen de los datos |
| EPT | *Eastern Prevailing Time*, hora civil del este de EE. UU. | Zona horaria de los datos |
| HE | *Hour ending*, hora de fin de intervalo | Convención de `Datetime` |
| EDA | Análisis exploratorio de datos | Notebook 01 |
| IQR | Rango intercuartil | Detección de atípicos |
| CV | Coeficiente de variación | Comparación entre regiones |
| STL | *Seasonal-Trend decomposition using LOESS* | Notebook 03 |
| LOESS | Regresión local ponderada | Base de STL |
| MAE | Error absoluto medio | Notebook 04 |
| RMSE | Raíz del error cuadrático medio | Notebook 04 |
| MAPE | Error porcentual absoluto medio | Notebook 04 |
| XGBoost | *eXtreme Gradient Boosting* | Modelo de pronóstico |
| CRISP-DM | *Cross-Industry Standard Process for Data Mining* | Metodología |
