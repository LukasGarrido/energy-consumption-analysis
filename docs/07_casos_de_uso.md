# Casos de uso

Formato: *Como* [parte interesada], *quiero* [qué lograr], *para* [motivo].

## Partes interesadas

| Parte interesada | Descripción |
|---|---|
| Analista de planeación energética | Necesita entender cuándo y cuánto se consume para planificar la capacidad |
| Operador de red | Necesita anticipar la demanda y detectar regiones y días con comportamientos distintos |
| Estudiante o investigador | Necesita reproducir y validar el análisis |

## Historias de usuario

Las historias HU-01 a HU-04 se cumplieron con el notebook 03 y sus cifras se recalculan con el día operativo.

| N.º | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-01 | Como analista, quiero ver el consumo por hora del día y día de la semana, para anticipar los momentos de mayor demanda | Mapa de calor por región, se indica en qué horas y días se concentra el consumo | Cumplida (notebook 03) |
| HU-02 | Como analista, quiero conocer la estacionalidad y la tendencia, para distinguir los efectos estacionales de la evolución de largo plazo | Gráficos de consumo por mes y de tendencia, meses de mayor y menor consumo | Cumplida (notebook 03) |
| HU-03 | Como operador, quiero comparar el consumo entre regiones, para identificar cuáles tienen más variabilidad y cómo reparten sus tipos de día | Comparación sobre un periodo común, diferencias y similitudes señaladas, y mezcla de tipos de día por región | Cumplida (notebooks 03 y 05) |
| HU-04 | Como operador, quiero identificar los días y horas de máximo consumo, para entender cuándo la red está más exigida | Máximos por región y su ubicación en el tiempo | Cumplida (notebook 03) |
| HU-05 | Como operador, quiero conocer cuándo y cuánto falla un pronóstico a 24 horas, para saber cuánto confiar en él | MAE, RMSE, MAPE y MASE comparados con un modelo base, en una ventana móvil de al menos 3 pliegues, y error por hora, mes y tipo de día | Cumplida (notebook 04), cifras por documentar |
| HU-06 | Como investigador, quiero reproducir el análisis desde cero, para validar los resultados | Pasos documentados en la guía de usuario, notebooks ejecutables en orden (01 a 07), semilla fija y parámetros en `src/config.py` | Parcial (falta actualizar la guía de usuario) |
| HU-07 | Como analista, quiero ver qué tipos de día existen y cuándo ocurre cada uno, para entender las formas de la demanda más allá de laborable y fin de semana | Grupos con silueta reportada, curva de cada grupo con su banda de dispersión y su ubicación en el calendario | Cumplida (notebook 05), resultados por documentar |
| HU-08 | Como operador, quiero ver qué días se desvían de lo esperable, para identificar episodios de demanda inusual | Lista de días con z modificado > 3.5, su magnitud y dirección, y contraste con episodios conocidos con fuente | Cumplida (notebook 06), resultados por documentar |
| HU-09 | Como analista, quiero explorar los resultados en un panel interactivo, para filtrar por región, fecha y estación sin programar | Panel de seis páginas con filtros y selección cruzada entre vistas | Parcial: tablas listas (notebook 07), panel por hacer (Power BI) |
| HU-10 | Como analista, quiero tablas con un modelo de datos coherente, para construir el panel sin reprocesar los datos | Dimensiones y hechos con claves sin huérfanos, y diccionario de datos | Cumplida (notebook 07) |

## Trazabilidad

| Historia | Pregunta | Objetivo específico |
|---|---|---|
| HU-01, HU-02, HU-04 | P1 | OE3 (indicadores) |
| HU-03 | P2 | OE3 |
| HU-05 | P4 | Referencia |
| HU-07 | P1 | OE2 |
| HU-08 | P3 | OE4 |
| HU-09, HU-10 | P1 a P4 | OE5 |
| HU-06 | Transversal | OE1 |