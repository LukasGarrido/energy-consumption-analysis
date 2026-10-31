# 11 · Conceptos teóricos

Este documento reúne los conceptos usados en el proyecto y explica qué papel juega cada uno aquí. Cada concepto puede incluir cuatro apartados:

- **Qué es:** la definición general.
- **Cómo funciona:** el procedimiento o la fórmula.
- **En el proyecto:** cómo se aplica, con cifras de los notebooks cuando ayudan.
- **Cuidado:** limitaciones y errores frecuentes.

Los conceptos de componentes que aún no tienen resultados (agrupamiento, anomalías, ventana móvil y panel) se marcan como *por hacer* y solo describen el diseño previsto.

## Mapa: qué conceptos usa cada pregunta

| Pregunta | Conceptos principales |
|---|---|
| P1. Tipos de día | Perfil diario, normalización, k-medias, agrupamiento jerárquico, silueta, estabilidad, mapa de calor de calendario |
| P2. Diferencias entre regiones | Normalización relativa, coeficiente de variación, correlación, mezcla de tipos de día, periodo común |
| P3. Días atípicos | Residuo, validación en ventana móvil, z modificado, MAD, validación sin etiquetas |
| P4. Error del pronóstico | Rezagos, fuga de datos, XGBoost, MAE, RMSE, MAPE, MASE, análisis por segmento |

## Contenido

1. Dominio: el sistema eléctrico
2. Series de tiempo
3. El tiempo en los datos
4. Calidad de datos y limpieza
5. Estadística descriptiva y comparación
6. Tendencia y estacionalidad
7. Agrupamiento de perfiles diarios (aprendizaje no supervisado)
8. Detección de anomalías
9. Pronóstico (aprendizaje supervisado)
10. Métricas de evaluación
11. Visualización de datos
12. Herramientas y buenas prácticas
13. Glosario de siglas

---

## 1. Dominio: el sistema eléctrico

### Demanda (o carga) eléctrica

**Qué es.** Cantidad de electricidad que los consumidores piden a la red en un momento dado. Cambia con la hora, el día, la estación y el clima.

**En el proyecto.** La columna `MW` es la demanda horaria de cada región. Es la variable que se analiza, se agrupa y se pronostica.

### Potencia (MW) y energía (MWh)

**Qué es.** La potencia indica cuánta electricidad se usa *en un instante* y se mide en vatios (1 MW = 1,000,000 W). La energía indica cuánta se usó *durante un tiempo*: 100 MW sostenidos durante una hora son 100 MWh. Es la diferencia entre la velocidad de un coche y los kilómetros recorridos.

**En el proyecto.** Los datos vienen en MW, con un valor por hora. Como cada fila cubre exactamente una hora, el valor en MW coincide numéricamente con los MWh de esa hora, por lo que se puede promediar sin conversión.

### PJM Interconnection y sus regiones

**Qué es.** PJM es una organización regional que coordina la red eléctrica de 13 estados del este de EE. UU. y Washington D.C. Reporta la demanda por zonas o regiones.

**En el proyecto.** Hay 12 regiones (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load). Tienen tamaños muy distintos (`PJME` promedia unos 32,080 MW y `DUQ` unos 1,659 MW) y algunas son subzonas de otras (`PJMW` no es una continuación de `PJM_Load`).

### Pico y valle de demanda

**Qué es.** El pico es el momento de mayor consumo y el valle el de menor consumo. Los picos son los que más exigen a la red.

**En el proyecto.** El valle diario ocurre de madrugada (hacia las 4–5 h, con cerca del 83 % del promedio) y el pico entre las 18 y las 20 h. El máximo histórico de `PJME` fue de 62,009 MW el 2 de agosto de 2006.

### Factores que determinan la demanda

**Qué es.** La demanda depende de tres grupos de factores: el **clima** (el calor dispara el aire acondicionado y el frío la calefacción), el **calendario** (hora, día de la semana, festivos) y la **actividad económica** de largo plazo.

**En el proyecto.** Los datos solo permiten usar el calendario y el propio historial del consumo. El dataset **no incluye temperatura**, así que la influencia del clima solo se infiere a partir de la estacionalidad. Esa ausencia limita la precisión del pronóstico en olas de calor y de frío, y obliga a interpretar los días atípicos por coincidencia con eventos.

---

## 2. Series de tiempo

### Serie de tiempo

**Qué es.** Conjunto de observaciones ordenadas en el tiempo. El orden importa: cada valor depende de los anteriores, y por eso los datos no se pueden mezclar al azar.

**En el proyecto.** Cada región es una serie con una observación por hora. Por eso la división entre entrenamiento y prueba es cronológica y los rezagos se calculan por región.

### Frecuencia y regularidad

**Qué es.** Una serie es regular cuando entre observaciones consecutivas pasa siempre el mismo tiempo. Muchas herramientas (rezagos, medias móviles, STL) suponen esa regularidad.

**En el proyecto.** La limpieza garantiza una fila por hora, sin saltos ni repeticiones. `validar_limpieza` lo comprueba restando cada fecha a la anterior: la diferencia debe ser siempre de una hora.

### Estacionalidad

**Qué es.** Patrón que se repite en un periodo fijo. Una serie puede tener varias estacionalidades a la vez.

**En el proyecto.** La demanda tiene tres niveles:

| Nivel | Periodo | Qué se observa |
|---|---|---|
| Diaria | 24 horas | Valle de madrugada y pico entre las 18 y las 20 h, en varias regiones, un segundo pico hacia las 8 h |
| Semanal | 7 días | El fin de semana consume entre un 4 % y un 14 % menos que un laborable |
| Anual | 12 meses | Picos en verano e invierno y valles en abril y octubre |

**Cuidado.** El nivel de demanda cambia entre regiones: `EKPC` consume más en invierno (razón invierno/verano de 1.20) y `DUQ` más en verano (0.92).

### Tendencia

**Qué es.** Movimiento lento y de largo plazo de la serie, una vez descontada la estacionalidad.

**En el proyecto.** No hay crecimiento sostenido, sino estabilidad o ligera baja: `PJME` pasó de 33,611 MW (2007) a 30,652 MW (2017), un −9 %, y `AEP` bajó un −13 %.

### Residuo (o ruido)

**Qué es.** Lo que queda de la serie después de quitar la tendencia y la estacionalidad: variaciones puntuales, como las que provoca el clima extremo.

**En el proyecto.** Se usa de dos maneras. En la descomposición STL, los residuos grandes señalan días fuera de lo esperable. En el pronóstico, el residuo del modelo (observado menos pronosticado) es la señal para detectar días atípicos (sección 8).

### Descomposición aditiva

**Qué es.** Modelo que expresa la serie como la suma de tres partes: *serie = tendencia + estacionalidad + residuo*.

**En el proyecto.** Se aplica a la serie diaria de `PJME` con STL (sección 6).

### Autocorrelación

**Qué es.** Relación de una serie consigo misma desplazada en el tiempo. Si el consumo de hoy se parece al de ayer a la misma hora, la serie tiene autocorrelación en el rezago de 24 horas.

**En el proyecto.** Es la razón por la que los rezagos funcionan como variables de pronóstico: `MW_lag_24` concentra el 71.1 % de la importancia del modelo. También explica por qué un modelo tan simple como "igual que ayer" es una referencia exigente.

### Efecto calendario

**Qué es.** Influencia de los fines de semana y festivos en el consumo, independiente del clima.

**En el proyecto.** Un festivo consume en promedio cerca de un 5 % menos que un laborable y un fin de semana cerca de un 9 % menos. Por eso `es_festivo` y `es_fin_de_semana` son variables del modelo.

---

## 3. El tiempo en los datos

### Hora de fin de intervalo (*hour ending*)

**Qué es.** Convención que etiqueta cada hora con el instante en que **termina**: la hora 1 va de 00:00 a 01:00 y la hora 24 es la última del día. PJM la usa en sus reportes.

**En el proyecto.** `Datetime` parece seguir esta convención. Los indicios son que todas las series empiezan a las 01:00 y terminan a las 00:00, que en primavera falta la fila de las 03:00 (no la de las 02:00) y que en otoño se repite la de las 02:00.

**Consecuencias:**

- La fila de las 00:00 es la última hora del día anterior.
- Un "pico a las 19 h" corresponde al intervalo 18:00–19:00.
- Para la fila de las 00:00, `dia_semana`, `es_fin_de_semana` y `es_festivo` quedan desplazados un día (1 de cada 24 horas).
- Un indicio visible: entre el 4 % y el 5 % de los días de `COMED` y `NI` tienen su pico en la hora 0, algo poco plausible, que se explica porque esa fila pertenece al día anterior.

### Día operativo (por decidir)

**Qué es.** El día definido según la convención de los datos, no según el calendario civil.

**Cómo funciona.** El día operativo va de la hora 1 a la 24, lo que equivale a restar una hora a `Datetime` antes de calcular la fecha: la fila de las 00:00 pasa a ser la hora 24 del día anterior.

**En el proyecto.** Corrige las variables de calendario y es la base de los perfiles diarios del agrupamiento. Adoptarlo exige repetir los notebooks 03 y 04.

### Hora local y EPT

**Qué es.** EPT (*Eastern Prevailing Time*) es la hora civil del este de EE. UU., que cambia entre horario estándar y de verano.

**En el proyecto.** Los datos parecen estar todos en EPT, aunque algunas regiones operen en hora central.

### Horario de verano (cambio de hora)

**Qué es.** Dos veces al año se adelanta o se retrasa el reloj una hora. En primavera una hora **no existe**, en otoño una hora **ocurre dos veces**.

**En el proyecto.** Explica casi todas las horas faltantes y los duplicados. En `PJME`, 17 de las 30 horas faltantes son de primavera (siempre a las 03:00) y 12 de otoño (a las 02:00, de 2002 a 2013). Desde 2014 la hora de otoño aparece duplicada: 4 fechas repetidas por región (2014 a 2017).

### Hora faltante y hora repetida

**Qué es.** Una fila que debería existir y no está, o una fecha que aparece dos veces con valores distintos.

**En el proyecto.** Se detectan comparando con el calendario ideal y se corrigen reindexando (las faltantes) y promediando (las repetidas).

### Desfase entre regiones

**Qué es.** Diferencia de hora entre perfiles que deberían parecerse.

**En el proyecto.** `COMED` aparece retrasada 1 hora (error de 0.014 con ese desplazamiento frente a 0.024 sin él). Es coherente con que todas las series estén en hora del este mientras `COMED`, en la zona de Chicago, opera en hora central: su actividad ocurre una hora más tarde en el reloj del este. No requiere corrección, porque tener todas las regiones en un mismo reloj facilita compararlas.

### Día completo

**Qué es.** Día con sus 24 horas. El primer y el último día de una serie pueden tener menos.

**En el proyecto.** El último día de cada serie solo tiene la hora 00:00, y su promedio sería el de un solo punto. Por eso los promedios diarios, el análisis de los peores días y los perfiles del agrupamiento usan solo días completos.

---

## 4. Calidad de datos y limpieza

### Regla de preprocesamiento

**Qué es.** Criterio explícito, con un umbral y un fundamento, que decide cómo se trata un problema de los datos. Reemplaza las decisiones implícitas y permite que otra persona reproduzca el proceso.

**En el proyecto.** Cada decisión de limpieza está documentada con su umbral (por ejemplo, interpolar hasta 2 horas seguidas) y su fundamento (todos los huecos observados son de 2 horas o menos). Las reglas están en `02_base_de_datos.md`.

### Valor nulo

**Qué es.** Dato que falta en una celda (`NaN`).

**En el proyecto.** El dataset original no tiene nulos. Aparecen al reindexar (las horas nuevas) o al marcar errores, y la interpolación los rellena.

**Cuidado.** Un vacío no es lo mismo que un cero: sustituir un dato faltante por 0 distorsiona los promedios.

### Duplicado

**Qué es.** Registro repetido para una misma fecha.

**En el proyecto.** Hay 40 en total (4 por región en 10 regiones), con valores de MW distintos. Se unifican promediando las dos lecturas.

### Calendario ideal y reindexación

**Qué es.** El calendario ideal es la lista de todas las horas entre la primera y la última fecha de una serie. Reindexar es forzar a la serie a tener una fila por cada una de esas horas: las que faltaban se crean con valor vacío.

**En el proyecto.** En `AEP`, el calendario tiene 121,296 horas y el archivo traía 121,269 distintas, así que se agregaron 27 filas. En total se agregaron 217 horas en las 12 regiones.

**Cuidado.** Requiere fechas sin repetir: por eso la unificación de duplicados va antes que la reindexación.

### Cobertura

**Qué es.** Porcentaje de las horas esperadas que realmente existen: horas distintas ÷ horas del calendario ideal.

**En el proyecto.** Entre 99.98 % y 99.99 % en todas las regiones, es decir, casi no hay huecos.

### Periodo común y regiones vigentes

**Qué es.** El periodo común es el intervalo en el que *todas* las regiones comparadas tienen datos: empieza en el inicio más tardío y termina en el final más temprano. Las regiones vigentes son las que llegan hasta el final del dataset.

**En el proyecto.** No existe periodo común a las 12 regiones. Las 10 vigentes comparten 2013-06-01 → 2018-08-03, y las comparaciones entre regiones se hacen en ese intervalo.

### Valor atípico y rango intercuartil (IQR)

**Qué es.** Un valor atípico se aleja mucho del resto. La regla del IQR considera atípico lo que queda fuera de [Q1 − 1.5·IQR, Q3 + 1.5·IQR], donde Q1 y Q3 son el primer y el tercer cuartil e IQR = Q3 − Q1. La regla procede del análisis exploratorio de Tukey.

**En el proyecto.** En `AEP`, Q1 = 13,630, Q3 = 17,200 e IQR = 3,570, así que los límites son 8,275 y 22,555 MW. En todo el dataset hay 19,693 valores altos y solo 51 bajos.

**Cuidado.** La regla supone una distribución más o menos simétrica. La demanda tiene picos de verano e invierno, por lo que muchos "atípicos" altos son simplemente temporadas de alta demanda.

### Error de medición frente a valor extremo real

**Qué es.** Un valor extremo puede ser un error del medidor o consumo real. El criterio usado es la **continuidad**: varias horas seguidas extremas sugieren un evento real, un valor aislado entre horas normales sugiere un error.

**En el proyecto.** Los picos altos forman una nube continua y se conservan. El 0 de `FE` (su primer registro) y los 1,253 MW de `DOM` (el siguiente mínimo es 5,518) son aislados y sospechosos.

### MAD y z modificado

**Qué es.** El MAD (desviación absoluta mediana) es la mediana de las distancias de cada valor a la mediana de los datos. El z modificado mide cuántas "desviaciones robustas" se aleja un valor de la mediana.

**Cómo funciona.** `z modificado = 0.6745 · (x − mediana) / MAD`. La constante 0.6745 hace que el MAD sea comparable con la desviación estándar cuando los datos son aproximadamente normales. Un valor se considera atípico si el z modificado supera 3.5 (Iglewicz y Hoaglin, 1993).

**Por qué no el z clásico.** El z clásico usa la media y la desviación estándar, que se distorsionan justamente por los valores extremos que se quieren detectar. La mediana y el MAD casi no cambian por unos pocos extremos, por lo que son *robustos*.

**En el proyecto.** Es la regla prevista para los valores atípicos aislados (*por implementar*) y para los días atípicos (sección 8). Hoy la limpieza solo corrige los valores menores o iguales a 0.

### Interpolación lineal

**Qué es.** Estimar un valor faltante con la recta que une el valor anterior y el siguiente.

**Cómo funciona.** Si entre 105 (02:00) y 110 (05:00) hay dos horas vacías, valen 106.7 y 108.3, repartidas en línea recta.

**En el proyecto.** Se rellenan huecos de hasta 2 horas seguidas con valor válido a cada lado (por ejemplo, `FE` el 2012-03-11 a las 03:00 se estimó en 5,929.5 MW). Los huecos más largos no se rellenan, porque estimar muchas horas seguidas sería fabricar datos. Se interpoló el 0.02 % de las horas.

**Cuidado.** La hora de primavera, que no existió en la hora local, se rellena igualmente: esa hora es un dato inventado. Afecta a 1 o 2 horas por año.

### Recorte de extremos

**Qué es.** Eliminar los vacíos al inicio o al final de una serie, que no se pueden interpolar porque falta un vecino.

**En el proyecto.** Se aplicó a `FE`, cuyo primer registro era el valor en 0 MW: ahora empieza a las 02:00.

### Validación de datos

**Qué es.** Comprobaciones automáticas de que el resultado cumple lo esperado.

**En el proyecto.** `validar_limpieza` exige fechas sin repetir, orden cronológico, una hora exacta entre filas, sin vacíos y sin valores menores o iguales a 0. Si algo falla, lanza un error en lugar de dejar pasar datos sucios.

### Formato largo y formato ancho

**Qué es.** En el largo cada observación es una fila (`Datetime`, `region`, `MW`), en el ancho hay una columna por región.

**En el proyecto.** El análisis usa el formato largo porque facilita agrupar y comparar regiones. El archivo `pjm_hourly_est.csv` es ancho y no se utiliza.

### Archivo parquet

**Qué es.** Formato binario por columnas, más compacto y rápido que el CSV, que conserva los tipos de dato (como las fechas).

**En el proyecto.** La limpieza guarda sus resultados en parquet.

---

## 5. Estadística descriptiva y comparación

### Media, mediana y desviación estándar

**Qué es.** La media es el promedio, la mediana, el valor central, la desviación estándar mide cuánto se dispersan los datos alrededor de la media.

**En el proyecto.** En `PJME`, la media es 32,080 MW y la mediana 31,421: la media es mayor porque los picos altos la arrastran hacia arriba (distribución asimétrica a la derecha).

### Cuartiles, percentiles y diagrama de caja

**Qué es.** Los cuartiles dividen los datos ordenados en cuatro partes, los percentiles generalizan la idea (el percentil 10 deja el 10 % de los datos por debajo). El diagrama de caja dibuja el 50 % central (la caja), la mediana (la línea) y los valores atípicos (los puntos).

**En el proyecto.** El diagrama de caja se usó para comparar la distribución de las 12 regiones. Los percentiles 10 y 90 delimitarán la banda de dispersión de cada tipo de día.

**Cuidado.** Las regiones grandes aplastan visualmente a las pequeñas en un mismo eje.

### Coeficiente de variación (CV)

**Qué es.** Desviación estándar ÷ media, en porcentaje. Permite comparar la variabilidad entre series de distinto tamaño.

**En el proyecto.** Va de 16.9 % (`AEP`, `FE`) a 25.9 % (`EKPC`).

### Razón pico/media

**Qué es.** Máximo ÷ media: cuánto se dispara el pico respecto a lo habitual.

**En el proyecto.** Va de 1.66 (`AEP`) a 2.38 (`EKPC`), la región con los picos más extremos.

### Normalización relativa (`MW_rel`)

**Qué es.** Dividir cada valor entre el promedio de su región. Un valor de 1.2 significa un 20 % por encima de lo habitual para esa región.

**En el proyecto.** En `AEP`, el primer registro (12,379 MW) equivale a 0.80. Permite comparar la **forma** del consumo entre regiones y no su tamaño.

**Cuidado.** Usa el promedio de todo el historial de la región, incluido el futuro, por lo que no debe entrar como variable de un modelo de pronóstico.

### Perfil

**Qué es.** Promedio del consumo agrupado por una categoría (hora, día de la semana, mes o estación).

**En el proyecto.** Los perfiles muestran el ciclo diario, semanal y anual y cómo cambian con la estación.

### Correlación de Pearson

**Qué es.** Medida entre −1 y 1 de cuánto suben y bajan juntas dos series. Cerca de 1, se mueven en la misma dirección, cerca de 0, no hay relación lineal.

**En el proyecto.** Se calcula sobre el promedio diario de las 10 regiones vigentes. Los valores van de 0.56 (`EKPC`–`COMED`) a 0.96 (`AEP`–`PJMW`, `DAYTON`–`FE`).

**Cuidado.** Son altos en buena parte porque todas comparten la estacionalidad anual, así que no significan que se parezcan en todo. Además, correlación no implica causalidad.

---

## 6. Tendencia y estacionalidad

### Media móvil

**Qué es.** Promedio de una ventana de observaciones que se desplaza a lo largo de la serie, y suaviza las variaciones cortas.

**En el proyecto.** Una ventana de 365 días cancela la estacionalidad anual, porque cada ventana contiene un invierno y un verano completos. Lo que queda es la tendencia.

### Media móvil centrada y efecto de borde

**Qué es.** En una media móvil centrada, cada promedio se coloca en el centro de su ventana. A cambio, no se puede calcular en los extremos de la serie, y las estimaciones cercanas a ellos son poco fiables.

**En el proyecto.** Explica por qué la línea gruesa de las gráficas de tendencia es más corta que la serie, y por qué la subida que muestra la tendencia STL de `PJME` al final de 2017 no es fiable.

### Descomposición STL

**Qué es.** *Seasonal-Trend decomposition using LOESS* (Cleveland et al., 1990). Separa una serie en tendencia, estacionalidad y residuo.

**Cómo funciona.** LOESS es una regresión local: para estimar cada punto, ajusta una recta usando solo los puntos cercanos, con más peso a los más próximos. STL aplica este suavizado de forma iterativa a la tendencia y al ciclo estacional.

**En el proyecto.** Se aplica con `period=365` a la serie diaria de `PJME`. La opción `robust=True` reduce la influencia de los valores extremos. La tendencia se mueve entre unos 30,500 y 33,300 MW, con su máximo en 2007–2008 y el mínimo en 2016–2017.

**Cuidado.** El periodo fijo de 365 días ignora los años bisiestos, por lo que es una aproximación.

### Año completo

**Qué es.** Año con (casi) todas sus horas. Se usa para evitar que un año parcial parezca una caída.

**En el proyecto.** Se considera completo con al menos 8,700 de las 8,760 horas (99.3 %). 114 de las 134 combinaciones región-año lo cumplen.

---

## 7. Agrupamiento de perfiles diarios (aprendizaje no supervisado) — por hacer

### Aprendizaje supervisado y no supervisado

**Qué es.** En el aprendizaje **supervisado** hay una variable objetivo conocida que el modelo aprende a predecir (el pronóstico). En el **no supervisado** no hay objetivo: el algoritmo busca estructura en los datos por sí solo (el agrupamiento).

**En el proyecto.** El pronóstico (sección 9) es supervisado, el agrupamiento de perfiles diarios es no supervisado y responde a P1 y P2.

### Perfil diario

**Qué es.** La curva de consumo de un día, representada como un vector de 24 valores, uno por hora.

**Cómo funciona.** Cada día de cada región se convierte en un vector de 24 números. El proyecto tiene unos 45,000 días-región, es decir, unos 45,000 vectores.

### Normalización del perfil: forma frente a tamaño

**Qué es.** Dividir cada valor del perfil entre el promedio de su día, para que el vector tenga media 1.

**Cómo funciona.** Un día con valores 20, 30 y 40 (promedio 30) queda en 0.67, 1.00 y 1.33. Dos días que sigan el mismo patrón pero con distinto tamaño quedan idénticos.

**En el proyecto.** Así el agrupamiento captura la *forma* del día y no el tamaño de la región ni la temporada. La magnitud (el promedio diario) se guarda aparte y se analiza por separado.

**Cuidado.** Se pierde la información de magnitud: un día de calor extremo y un día normal con la misma forma quedarían juntos.

### Distancia euclidiana

**Qué es.** La distancia "en línea recta" entre dos vectores: la raíz de la suma de las diferencias al cuadrado, hora a hora.

**En el proyecto.** Mide cuán parecidos son dos perfiles diarios, y es la distancia que usan k-medias y la silueta.

### Agrupamiento (*clustering*)

**Qué es.** Dividir los datos en grupos de modo que los elementos de un mismo grupo se parezcan entre sí más que a los de otros grupos.

**En el proyecto.** Cada grupo de perfiles diarios es un **tipo de día**.

**Cuidado.** No confundir con la variable `tipo_dia` de los notebooks 03 y 04 (laborable, fin de semana, festivo), que se define por el calendario. Aquí el tipo de día lo descubre el algoritmo a partir de la forma de la curva, y después se compara con el calendario.

### K-medias

**Qué es.** Algoritmo que agrupa los datos en *k* grupos, cada uno representado por su centro (centroide).

**Cómo funciona.**

1. Se eligen *k* centroides iniciales.
2. Cada perfil se asigna al centroide más cercano.
3. Cada centroide se recalcula como el promedio de los perfiles asignados.
4. Se repiten los pasos 2 y 3 hasta que los grupos dejan de cambiar.

El algoritmo minimiza la suma de las distancias al cuadrado entre cada perfil y el centro de su grupo.

**En el proyecto.** El centroide de cada grupo es la **curva representativa** del tipo de día.

**Cuidado.** El resultado depende de los centroides iniciales, por lo que se repite con distintas semillas. Además, supone grupos compactos y de forma redondeada: los perfiles diarios forman en parte un continuo, y la estructura puede resultar débil.

### Agrupamiento jerárquico y criterio de Ward

**Qué es.** Algoritmo que parte de cada perfil como un grupo propio y va fusionando los dos grupos más parecidos hasta quedar uno solo. El criterio de Ward elige, en cada paso, la fusión que menos aumenta la dispersión dentro de los grupos.

**En el proyecto.** Se compara con k-medias para el mismo rango de *k*. Se elige el algoritmo con mayor silueta media y grupos interpretables.

**Cuidado.** Es más costoso en memoria cuando hay decenas de miles de elementos, por lo que puede requerir una muestra.

### Silueta

**Qué es.** Medida de qué tan bien separado está cada perfil de los demás grupos.

**Cómo funciona.** Para cada perfil, `s = (b − a) / max(a, b)`, donde *a* es la distancia media a los perfiles de su propio grupo y *b* la distancia media al grupo vecino más cercano. Va de −1 a 1: cerca de 1, el perfil está bien asignado, cerca de 0, está en la frontera entre dos grupos, negativo, probablemente está en el grupo equivocado. La silueta media es el promedio de todos los perfiles (Rousseeuw, 1987).

**Cómo se interpreta.** Siguiendo a Kaufman y Rousseeuw (1990), una silueta media de 0.51 a 0.70 indica una estructura razonable, de 0.26 a 0.50 una estructura débil que podría ser artificial, y menor de 0.25 que no hay estructura sustancial. El proyecto usa el umbral de 0.50 y reporta como "débil" lo que quede entre 0.26 y 0.50.

**En el proyecto.** Se calcula para cada *k* entre 2 y 10 y se elige el *k* con mayor silueta media.

### Elección del número de grupos (*k*)

**Qué es.** El número de grupos no lo conoce el algoritmo: hay que decidirlo.

**En el proyecto.** Se prueba cada *k* de 2 a 10, se calcula la silueta media y se elige el máximo. Se exige además que ningún grupo tenga menos del 5 % de los días, para evitar grupos tan pequeños que no se puedan interpretar.

**Cuidado.** El *k* que maximiza una métrica no siempre es el más útil para interpretar. Por eso se revisa que los grupos tengan sentido con el calendario.

### Estabilidad del agrupamiento

**Qué es.** Que la solución se mantenga al repetir el procedimiento con otras condiciones (otra semilla, otra muestra).

**En el proyecto.** Se repite con distintas semillas y se comprueba que los grupos y la silueta no cambian de forma apreciable. Una solución que cambia mucho no es confiable.

### Interpretación de los grupos con el calendario

**Qué es.** Describir cada grupo con información que el algoritmo no usó.

**Cómo funciona.** Para cada grupo se calcula su curva media, su banda de dispersión (percentiles 10 a 90), su frecuencia y la distribución de sus días según día de la semana, mes y festivo. Con esa tabla se puede nombrar cada tipo (por ejemplo, "laborable de invierno").

**En el proyecto.** Permite además detectar días que el calendario no explica, como un lunes con forma de domingo.

### Mezcla de tipos de día por región

**Qué es.** El porcentaje de días de cada grupo en cada región.

**En el proyecto.** Es la base de P2: dos regiones se parecen si reparten sus días en los mismos tipos en proporciones similares. Se muestra como barras apiladas al 100 %.

---

## 8. Detección de anomalías — por hacer

### Atípico, anomalía y error

**Qué es.** Tres ideas cercanas pero distintas:

| Concepto | Definición | Dónde se trata en el proyecto |
|---|---|---|
| Valor atípico | Un valor lejano al resto, a nivel de hora | Limpieza (sección 4) |
| Día atípico o anomalía | Un día cuyo comportamiento se aleja de lo esperable dado su contexto | Este apartado |
| Error de datos | Un valor erróneo por falla de medición o registro | Limpieza |

**En el proyecto.** Un día atípico puede deberse a un evento real (ola de calor, huracán) o a un error, por eso se revisan las horas vecinas antes de concluir.

### Demanda esperada y residuo

**Qué es.** El modelo de pronóstico captura lo previsible a partir del calendario y del historial. La diferencia entre lo observado y lo pronosticado es el **residuo**: lo que el modelo no pudo anticipar.

**Cómo funciona.** `residuo = observado − pronosticado`. Un residuo grande en un día significa que ese día fue más (o menos) demanda de lo esperable.

**En el proyecto.** El residuo es la señal que se usa para detectar días atípicos.

### Residuo fuera de muestra

**Qué es.** El residuo calculado con datos que el modelo no vio al entrenarse.

**Por qué importa.** Con los datos de entrenamiento, el modelo se ajusta y los residuos salen artificialmente pequeños, por lo que ocultan las anomalías. Solo los residuos fuera de muestra reflejan lo inesperado.

**En el proyecto.** Para obtener residuos fuera de muestra en todo el historial, se usa la validación en ventana móvil (sección 9).

### Residuo diario

**Qué es.** El resumen de los 24 residuos horarios de un día en un solo número.

**En el proyecto.** Se define como el error absoluto medio de las 24 horas, para evaluar el día completo y no una hora aislada.

### Umbral de z modificado

**Qué es.** La regla para decidir qué residuos diarios son atípicos: z modificado > 3.5 (ver MAD y z modificado, sección 4).

**Ejemplo ilustrativo.** Con una mediana de residuos de 1,500 MW y un MAD de 600 MW, un día con un residuo de 5,000 MW tiene `z = 0.6745 · (5,000 − 1,500) / 600 ≈ 3.9`, mayor que 3.5, así que se marca. Las cifras son inventadas para ilustrar el cálculo.

**Cuidado.** El umbral es una convención. Un valor más bajo marca más días, con más falsos positivos, uno más alto marca menos, con más falsos negativos.

### Validación sin etiquetas

**Qué es.** Los datos no traen una lista de días anómalos reales, así que no se puede calcular una exactitud directa.

**Cómo funciona.** Se contrastan los días marcados con episodios externos conocidos (olas de calor o frío, huracanes) y se reporta cuántos de esos episodios se recuperan y cuántos días marcados no corresponden a ningún evento conocido.

**En el proyecto.** Los resultados preliminares dan pistas de qué buscar: máximos coincidentes entre regiones en agosto de 2006, julio de 2011 y febrero de 2015, y el menor consumo de `PJME` el 2012-10-30. La atribución a eventos concretos es una hipótesis hasta contrastarla con registros meteorológicos.

### Distancia al centroide (complemento)

**Qué es.** Qué tan lejos queda el perfil de un día del centro de su grupo.

**En el proyecto.** Un día muy lejos de su centroide tiene una forma inusual dentro de su tipo. Complementa la detección por residuos: una mira el tamaño del error del pronóstico y la otra la forma de la curva.

---

## 9. Pronóstico (aprendizaje supervisado)

### Pronóstico y horizonte

**Qué es.** Pronosticar es predecir valores futuros. El horizonte es cuánto tiempo hacia adelante se predice.

**En el proyecto.** El horizonte es de 24 horas: para predecir la hora *t* solo se usa información hasta *t − 24*.

### Variable objetivo y variables explicativas

**Qué es.** La objetivo es lo que se quiere predecir, las explicativas (*features*) son los datos con los que se predice.

**En el proyecto.** La objetivo es `MW`. Las explicativas son el calendario, los rezagos y las medias móviles.

### Ingeniería de variables

**Qué es.** Crear variables informativas a partir de los datos originales.

**En el proyecto.** Se derivan de la fecha (hora, día de la semana, mes, fin de semana, festivo) y del propio historial del consumo (rezagos y medias móviles).

### Rezago (*lag*)

**Qué es.** Valor de la serie de hace *k* pasos.

**En el proyecto.** `MW_lag_24` es el consumo de hace 24 horas (ayer a la misma hora), `MW_lag_48` el de hace 2 días y `MW_lag_168` el de hace una semana. Se calculan por región, para no mezclar series.

### Media móvil desplazada

**Qué es.** Promedio de las horas previas, desplazado para que termine antes del momento a predecir.

**En el proyecto.** `MW_media_24h` y `MW_media_168h` promedian las 24 y 168 horas que terminan 24 horas antes de *t*.

### Fuga de datos (*data leakage*)

**Qué es.** Usar para entrenar información que no estaría disponible al momento de pronosticar. Produce resultados engañosamente buenos que no se repiten en la práctica.

**En el proyecto.** Se previene de tres maneras:

- Todos los rezagos son de 24 horas o más, y `agregar_rezagos` lanza un error si se pide uno menor.
- Se excluyen `MW_rel` (usa el promedio de toda la región, incluido el futuro) y `anio`.
- La división es cronológica.

**Cómo detectarla.** Un error sospechosamente bajo (por ejemplo, un MAPE cercano a cero en demanda horaria con 24 horas de antelación) es una señal de alerta. El MAPE de 5.89 % obtenido no lo es.

### División cronológica entrenamiento/prueba

**Qué es.** El conjunto de entrenamiento se usa para que el modelo aprenda, el de prueba, para evaluarlo con datos que no ha visto. En series de tiempo, la división respeta el orden: el entrenamiento es anterior a la prueba.

**En el proyecto.** Se entrena con 2002-01-01 → 2016-12-31 (131,495 filas) y se prueba con 2017-01-01 → 2018-08-03 (13,897 filas). Una división al azar mezclaría horas contiguas y produciría una fuga.

**Cuidado.** Con una sola partición, el resultado depende del periodo elegido para la prueba.

### Validación en ventana móvil (*rolling-origin*) — por hacer

**Qué es.** Repetir la evaluación con varias particiones cronológicas: el modelo se entrena con el pasado hasta un punto, se evalúa en el periodo siguiente, y el punto de corte avanza para el pliegue siguiente.

**Cómo funciona.** Por ejemplo, con pliegues por año: entrenar hasta 2014 y evaluar 2015, entrenar hasta 2015 y evaluar 2016, y así sucesivamente. El entrenamiento crece en cada pliegue (ventana expansiva).

**En el proyecto.** Cumple dos funciones: dar una evaluación más estable que una sola partición (al menos 3 pliegues, y el modelo debe superar al base en todos) y producir residuos fuera de muestra para todo el historial, que alimentan la detección de anomalías.

**Cuidado.** Exige entrenar un modelo por pliegue (y por región), por lo que se empieza con `PJME`.

### Modelo base (*baseline*)

**Qué es.** Pronóstico simple contra el cual comparar. Un modelo complejo solo se justifica si lo supera.

**En el proyecto.** El base de 24 horas predice "como ayer a la misma hora" (MAE de 2,300 MW) y el de 168 horas "como la semana pasada" (MAE de 3,511 MW). Es el llamado pronóstico ingenuo estacional.

### Árbol de decisión

**Qué es.** Modelo que predice dividiendo los datos con reglas sucesivas, por ejemplo: "si la hora es mayor que 7 y es laborable, entonces...". Cada hoja del árbol da un valor de predicción.

**Cuidado.** Un árbol solo puede predecir valores del rango que vio en el entrenamiento, y un árbol solo tiende a sobreajustarse.

### Gradient boosting y XGBoost

**Qué es.** El *gradient boosting* construye muchos árboles pequeños en secuencia, y cada árbol nuevo se entrena para corregir los errores de los anteriores. La predicción final es la suma de las contribuciones de todos los árboles. XGBoost (Chen y Guestrin, 2016) es una implementación eficiente que además penaliza la complejidad de los árboles para reducir el sobreajuste.

**En el proyecto.** Es el modelo de pronóstico. Funciona bien con datos tabulares y captura relaciones no lineales entre variables.

### Hiperparámetros

**Qué es.** Ajustes del modelo que se fijan antes de entrenar, a diferencia de los parámetros que el modelo aprende.

**En el proyecto.**

| Hiperparámetro | Valor | Qué controla |
|---|---|---|
| `n_estimators` | 500 | Número de árboles |
| `learning_rate` | 0.05 | Cuánto corrige cada árbol (más bajo, más lento y más estable) |
| `max_depth` | 6 | Profundidad máxima de cada árbol (más profundo, más complejo) |
| `subsample` | 0.8 | Fracción de filas que usa cada árbol |
| `colsample_bytree` | 0.8 | Fracción de variables que usa cada árbol |

No se ajustaron con una búsqueda de parámetros.

### Sobreajuste (*overfitting*)

**Qué es.** Cuando un modelo memoriza los datos de entrenamiento y generaliza mal a datos nuevos.

**En el proyecto.** Se evalúa solo con datos de prueba que el modelo no vio para detectarlo.

### Extrapolación de los árboles

**Qué es.** Un modelo de árboles no predice valores fuera del rango que vio al entrenar.

**En el proyecto.** Podría explicar por qué, en olas de frío intensas, el modelo base supera a XGBoost en 4 de los 10 peores días. Es una hipótesis que no se verificó.

### Importancia de variables

**Qué es.** Medida de cuánto contribuye cada variable a las predicciones del modelo. En XGBoost suele calcularse como la mejora del error que aporta cada variable cuando se usa para dividir los árboles.

**En el proyecto.** `MW_lag_24` concentra el 71.1 % y le siguen `MW_lag_168` (9.1 %) y `es_fin_de_semana` (8.1 %). El modelo es esencialmente "ayer" con correcciones por tipo de día.

**Cuidado.** No implica causalidad, y cuando varias variables están muy correlacionadas, el modelo reparte la importancia entre ellas de forma arbitraria.

### Pronóstico puntual y probabilístico

**Qué es.** Un pronóstico puntual entrega un solo valor por hora, uno probabilístico entrega una distribución o un intervalo (Hong y Fan, 2016).

**En el proyecto.** El pronóstico es puntual. El intervalo queda fuera del alcance.

### Semilla aleatoria

**Qué es.** Número que fija la parte aleatoria de un algoritmo, para que dé el mismo resultado en cada ejecución.

**En el proyecto.** `SEMILLA = 42` en `config.py`. También se usa en el agrupamiento.

---

## 10. Métricas de evaluación

### Error de pronóstico

**Qué es.** Diferencia entre el valor predicho y el real: `error = predicho − real`.

### MAE (error absoluto medio)

**Cómo funciona.** `MAE = promedio de |predicho − real|`. Se expresa en MW y es fácil de interpretar.

**En el proyecto.** XGBoost tiene un MAE de 1,862 MW: se equivoca, en promedio, en esa cantidad de megavatios (cerca del 6 % del consumo medio).

### RMSE (raíz del error cuadrático medio)

**Cómo funciona.** `RMSE = raíz del promedio de (predicho − real)²`. Al elevar al cuadrado, penaliza más los errores grandes. Siempre es mayor o igual que el MAE, y una diferencia grande entre ambos indica que hay errores muy altos puntuales.

**En el proyecto.** 2,513 MW frente a un MAE de 1,862.

### MAPE (error porcentual absoluto medio)

**Cómo funciona.** `MAPE = promedio de |predicho − real| / real × 100`. Expresa el error como porcentaje, lo que permite comparar series de distinto tamaño.

**En el proyecto.** 5.89 %. No hay problema de ceros porque la limpieza eliminó los valores menores o iguales a 0.

**Cuidado.** Se vuelve inestable si el valor real se acerca a cero, y penaliza más los errores por exceso que por defecto.

### MASE (error absoluto medio escalado) — por hacer

**Qué es.** El MAE del modelo dividido entre el MAE del pronóstico ingenuo calculado sobre los datos de entrenamiento (Hyndman y Koehler, 2006).

**Cómo se interpreta.** Un MASE menor que 1 significa que el modelo supera al pronóstico ingenuo, mayor que 1, que lo empeora. No depende de la escala, así que sirve para comparar entre regiones.

**En el proyecto.** Se exigirá MASE < 1 en todos los pliegues de la ventana móvil, tomando como referencia el pronóstico de "ayer a la misma hora".

### Mejora relativa

**Qué es.** Reducción del error de un modelo frente a otro: `1 − error del modelo / error de la referencia`.

**En el proyecto.** XGBoost reduce el MAE un 19.0 % frente al modelo base de 24 horas y un 47.0 % frente al semanal.

### Análisis de errores por segmento

**Qué es.** Calcular el error por hora, mes o tipo de día para ver dónde falla el modelo.

**En el proyecto.** El error es menor de madrugada y mayor por la tarde-noche. La mayor ganancia frente al modelo base está en los festivos (30.9 %) y fines de semana (25.3 %), y la menor en los laborables (15.4 %).

**Cuidado.** Los segmentos pueden tener tamaños muy distintos: los festivos son solo 408 de 13,897 horas de prueba.

---

## 11. Visualización de datos

### Tarea visual

**Qué es.** Lo que quiere hacer quien mira un gráfico: descubrir patrones, comparar, localizar un valor, resumir o evaluar.

**En el proyecto.** Cada pregunta se asocia a una tarea (P1 descubrir, P2 comparar, P3 localizar, P4 evaluar), y el gráfico se elige según ella. Es una forma de elegir gráficos con un criterio y no por costumbre.

### Datos, tarea y codificación

**Qué es.** Un marco para diseñar una visualización (Munzner, 2014): qué datos hay, qué tarea se quiere apoyar y cómo se codifican los datos en formas y colores.

**En el proyecto.** La tabla del plan de visualización de la propuesta sigue este esquema.

### Marca y canal de codificación

**Qué es.** Una marca es el elemento gráfico (punto, línea, barra, celda). Un canal es el atributo visual con que se codifica un dato: posición, longitud, ángulo, área o color.

### Precisión de los canales

**Qué es.** Cleveland y McGill (1984) ordenaron las tareas perceptuales por la precisión con que las personas las realizan. De más a menos preciso: posición sobre una escala común, posición sobre escalas no alineadas, longitud, ángulo y pendiente, área, y por último color (saturación y sombreado). Su ordenamiento fue replicado con participantes en línea por Heer y Bostock (2010).

**En el proyecto.** Las comparaciones precisas usan posición y longitud (líneas, barras, puntos), y el color se reserva para ver patrones globales (mapas de calor) o para categorías (tipos de día).

### Mapa de calor

**Qué es.** Tabla de dos dimensiones donde cada celda se colorea según un valor.

**En el proyecto.** Se usa para el consumo por hora y día de la semana (7 × 24 celdas), las horas faltantes por año y región, la correlación entre regiones y el mes del pico anual.

**Cuidado.** Como el color es un canal poco preciso, un mapa de calor sirve para ver patrones globales, no para leer valores exactos. Por eso se complementa con líneas.

### Mapa de calor de calendario

**Qué es.** Mapa de calor donde las celdas son los días del año, dispuestos en semanas, y el color indica una categoría o un valor del día.

**En el proyecto.** Cada día se colorea según su tipo de día. Es el esquema de van Wijk y van Selow (1999) y muestra cuándo ocurre cada forma de día.

### Escalas de color

**Qué es.** Tres tipos de escala según el dato:

| Tipo | Cuándo se usa |
|---|---|
| Secuencial | Una magnitud ordenada de menor a mayor (por ejemplo, el consumo relativo) |
| Divergente | Una desviación respecto de un valor central (por ejemplo, por encima o por debajo de 1) |
| Categórica | Grupos sin orden (por ejemplo, los tipos de día) |

**En el proyecto.** Paleta secuencial de un solo matiz para magnitudes y categórica de pocos colores (regla práctica del proyecto: no más de 8) para los tipos de día. Una escala divergente centrada en 1 es una alternativa para `MW_rel`.

### Paneles múltiples (*small multiples*)

**Qué es.** Una serie de gráficos pequeños con el mismo formato, uno por categoría.

**En el proyecto.** Se usan para mostrar una región por panel con una escala común, lo que permite comparar sin superponer 10 series.

**Cuidado.** Si los ejes no son comunes, la comparación visual engaña.

### Elección del gráfico por pregunta

| Gráfico | Cuándo usarlo | En el proyecto |
|---|---|---|
| Líneas | Evolución o forma de una curva | Perfiles, tendencia, real frente a pronóstico |
| Barras apiladas al 100 % | Composición de un total, comparando entre categorías | Mezcla de tipos de día por región |
| Dispersión | Relación entre dos variables | Comparación de regiones |
| Diagrama de caja | Distribución de una variable | Consumo por región |
| Mapa de calor | Dos dimensiones con un valor en cada cruce | Hora por día de la semana |

**Gráficos circulares.** Se evitan porque dependen de ángulo y área, canales menos precisos que la longitud.

### Resumen primero, detalle bajo demanda

**Qué es.** Principio de interacción: se muestra primero una vista general y el detalle aparece al filtrar o seleccionar.

**En el proyecto.** El panel tiene una página de resumen y filtros por región, fecha y estación, el perfil real y el esperado de un día atípico se muestran al seleccionarlo.

---

## 12. Herramientas y buenas prácticas

### Notebook de Jupyter

**Qué es.** Documento que combina código, resultados y texto, ejecutado por celdas.

**En el proyecto.** Hay siete previstos, en orden: exploración, limpieza, análisis, modelado, agrupamiento, anomalías y exportación. Los cuatro primeros están hechos.

### Módulo reutilizable y paquete editable

**Qué es.** Una función que se usa en varios notebooks se mueve a un archivo `.py` en `src/` y se importa. Con `pip install -e .` y el archivo `pyproject.toml`, esa carpeta se registra como un paquete y se puede importar desde cualquier lugar.

**En el proyecto.** `src/` contiene `config.py` (rutas y parámetros), `data_loader.py`, `cleaning.py`, `features.py` y `modeling.py`, `profiles.py` y `anomalies.py` están por crear.

### Entorno virtual y dependencias

**Qué es.** Un entorno virtual aísla las librerías del proyecto, `requirements.txt` lista cuáles son.

**En el proyecto.** `python -m venv .venv` y `pip install -r requirements.txt`.

### Control de versiones

**Qué es.** Registro de los cambios del código a lo largo del tiempo, con Git y GitHub.

**En el proyecto.** El repositorio guarda el código, los notebooks y la documentación. Los datos crudos no se versionan (`data/raw` está ignorado). Las tareas pendientes se registran como issues.

### Reproducibilidad

**Qué es.** Que otra persona pueda obtener los mismos resultados siguiendo los pasos.

**En el proyecto.** Se apoya en el entorno virtual, la semilla fija, la guía de usuario y el orden numerado de los notebooks.

### Operaciones de pandas más usadas

| Operación | Qué hace |
|---|---|
| `groupby` | Agrupa filas por una o más columnas para calcular estadísticos por grupo |
| `unstack` | Convierte un nivel del índice en columnas, para armar tablas anchas |
| `transform` | Como `groupby`, pero repite el resultado en cada fila (sirve para normalizar por región) |
| `resample` | Agrupa una serie de tiempo por periodos (por ejemplo, por día) |
| `reindex` | Fuerza un índice nuevo, creando filas vacías donde faltan |
| `interpolate` | Estima valores faltantes a partir de los vecinos |
| `shift` y `rolling` | Desplazan la serie y calculan ventanas móviles (rezagos y medias móviles) |

### Power BI

**Qué es.** Herramienta de inteligencia de negocio (*BI*) para construir paneles interactivos a partir de tablas de datos.

**Cómo funciona.** Se importan las tablas, se construyen las vistas y se añaden segmentadores (filtros) que actualizan todas las vistas de la página. Al seleccionar un elemento de un gráfico, las demás vistas resaltan los datos relacionados (selección cruzada).

**En el proyecto.** Es la herramienta del panel final. Python genera las tablas (perfiles, grupos, residuos y métricas) y Power BI las muestra. Hay que verificar la licencia necesaria para publicarlo o compartirlo.

### Análisis exploratorio de datos (EDA)

**Qué es.** Revisión inicial de los datos con estadística y gráficos, antes de modelar (Tukey, 1977).

**En el proyecto.** Es el notebook 01, de donde salieron las decisiones de limpieza.

### CRISP-DM

**Qué es.** Metodología por fases para proyectos de minería de datos: comprensión del problema y de los datos, preparación, modelado, evaluación y despliegue (Chapman et al., 2000).

**En el proyecto.** Las fases siguen una lógica parecida: exploración, limpieza, análisis, modelado y visualización.

---

## 13. Glosario de siglas

| Sigla | Significado | Dónde aparece |
|---|---|---|
| MW | Megavatio, unidad de potencia | Todas las series |
| MWh | Megavatio-hora, unidad de energía | Diferencia entre potencia y energía |
| PJM | PJM Interconnection, operador de la red del este de EE. UU. | Origen de los datos |
| EPT | *Eastern Prevailing Time*, hora civil del este de EE. UU. | Zona horaria de los datos |
| HE | *Hour ending*, hora de fin de intervalo | Convención de `Datetime` |
| EDA | Análisis exploratorio de datos | Notebook 01 |
| IQR | Rango intercuartil | Detección de atípicos |
| MAD | Desviación absoluta mediana | z modificado |
| CV | Coeficiente de variación | Comparación entre regiones |
| STL | *Seasonal-Trend decomposition using LOESS* | Notebook 03 |
| LOESS | Regresión local ponderada | Base de STL |
| k | Número de grupos del agrupamiento | Notebook 05 |
| MAE | Error absoluto medio | Notebook 04 |
| RMSE | Raíz del error cuadrático medio | Notebook 04 |
| MAPE | Error porcentual absoluto medio | Notebook 04 |
| MASE | Error absoluto medio escalado | Notebook 04 (por hacer) |
| XGBoost | *eXtreme Gradient Boosting* | Modelo de pronóstico |
| BI | *Business intelligence*, inteligencia de negocio | Power BI |
| CRISP-DM | *Cross-Industry Standard Process for Data Mining* | Metodología |