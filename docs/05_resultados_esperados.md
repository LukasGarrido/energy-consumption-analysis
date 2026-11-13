# Resultados esperados

> Las cifras de este documento salen de la ejecución de los notebooks 01 a 06 con el día operativo (decisión D1). Las horas son horas de inicio (0 = 00:00–01:00). El notebook 07 y el panel están pendientes de verificación.

| N.º        | Resultado esperado                                                                    | Estado                            | Qué se ha obtenido                                                                                                                                                                                  |
| ---------- | ------------------------------------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OE1        | Base horaria limpia y documentada                                                     | Cumplido                          | 1,090,343 filas en 12 regiones, validadas. Se unificaron 40 duplicados, se interpolaron 217 horas (0.02 %) y se recortó 1 fila (el cero inicial de `FE`)                                              |
| OE2        | Catálogo de tipos de día, con su curva, su frecuencia y su ubicación en el calendario | Cumplido con salvedad             | 2 tipos de día (k-medias, k = 2), silueta 0.413 (estructura débil): temporada fría (62.3 % de los días) y verano (37.7 %). Son estacionales y no separan laborables de fines de semana                |
| OE3        | Tipología de regiones y matriz región por tipo de día                                 | Cumplido                          | Variabilidad (CV) de 17 % a 26 %, razón invierno/verano de 0.92 (`DUQ`) a 1.20 (`EKPC`), correlaciones diarias de 0.56 a 0.96. Los días de verano van de 31 % (`FE`) a 45 % (`DOM` y `EKPC`) en el periodo común |
| OE4        | Lista de días atípicos con su magnitud y coincidencia con episodios                   | Cumplido                          | 22 días atípicos de 2,191 en `PJME` (15 altos y 7 bajos). De 10 episodios, 5 coinciden con el signo esperado, 3 no coinciden y 2 están fuera del rango de los residuos                              |
| OE5        | Panel interactivo con seis páginas (resumen, patrones, tipos de día, regiones, anomalías y pronóstico) | Parcial                           | Las 17 tablas del modelo de datos las genera el notebook 07. El archivo de Power BI está por construir                                                                                              |
| Referencia | Pronóstico a 24 horas contra modelos base, con MASE y ventana móvil                   | Cumplido                          | XGBoost: MAE 1,862 MW frente a 2,300 MW del modelo base de 24 h (−19.1 %), MASE 0.86. En la ventana móvil supera al base en los 6 pliegues, con MASE de 0.72 a 0.87                                  |

## Hallazgos del análisis descriptivo (notebooks 01 y 03)

- **Periodo:** no existe un periodo común a las 12 regiones, 10 comparten 2013-06-01 → 2018-08-03 (días operativos hasta el 2018-08-02).
- **Ciclo diario:** mínimo entre las 3 y las 4 h, subida desde las 5–6 h y máximo entre las 17 y las 19 h (18 h en 7 de 10 regiones, `DUQ` y `PJME` a las 17 h, `EKPC` a las 19 h).
- **Forma por estación:** en verano hay una sola curva con máximo por la tarde (hasta 1.2–1.4 del promedio) y en invierno hay dos picos, uno hacia las 7 h y otro hacia las 18–19 h.
- **Calendario:** el fin de semana consume entre un 3.9 % (`EKPC`) y un 13.9 % (`DAYTON`) menos que un laborable (≈ −9 % en promedio). Un festivo consume cerca de un 5 % menos (de −0.7 % en `DOM` a −8.8 % en `DAYTON`; `EKPC` es la excepción con +1.7 %).
- **Estacionalidad:** dos máximos anuales (verano e invierno) con valles en abril y octubre. `EKPC` (1.20) y `PJMW` (1.12) son invernales, `COMED` (0.93), `DUQ` (0.92), `DEOK` y `PJME` (0.95), veraniegas.
- **Tendencia:** estabilidad o ligera baja (`PJME` −9 % entre 2007 y 2017, de 33,612 a 30,653 MW; `AEP` −13 %; `DUQ` −10 %). `DOM` sube cerca de un 6 % desde 2006.
- **Picos:** `PJME` alcanzó 62,009 MW el 2006-08-02. `DOM`, `EKPC` y `PJMW` tienen su récord el 2015-02-20 a las 7 h. Ambas fechas coinciden con episodios documentados por PJM: el récord de demanda de verano y el de invierno. El máximo de `AEP` (2008-10-20) es inusual y debe verificarse.
- **Correlaciones:** de 0.56 a 0.96. Los pares más parecidos son `AEP`–`PJMW` y `DAYTON`–`FE` (0.96), y la región más distinta es `EKPC`.
- **Hora de `COMED` y `NI`:** su curva diaria llega una hora más tarde que la del resto (error de 0.014 con +1 h frente a 0.024 sin desplazar). Es lo esperable si las series están en hora del este y esas zonas son de hora central. No se corrige (ver D7).
- **`NI` y `COMED`:** cociente de niveles 1.00 y empalme el 2011-01-01, lo que permite tratarlas como la misma zona (decisión D3, por confirmar).

## Tipos de día (notebook 05)

| Indicador | Valor |
|---|---|
| Días agrupados | 45,430 días de 12 regiones |
| Método y k | k-medias, k = 2 (la mayor silueta con grupos de al menos el 5 %) |
| Silueta media (muestra de 10,000 días) | 0.413, estructura débil |
| Silueta con otros k | 0.30 con k = 3 y entre 0.19 y 0.25 con k de 4 a 10 |
| Concordancia con Ward (Rand ajustado) | 0.82 |

| Grupo | Nombre | % de los días | Hora pico | Hora mínima | Amplitud | % fin de semana |
|---|---|---|---|---|---|---|
| 1 | Temporada fría (oct–may) | 62.3 | 19 h | 3 h | 0.2 | 28.9 |
| 2 | Verano (jun–sep) | 37.7 | 17 h | 4 h | 0.4 | 28.1 |

- Los dos tipos son **estacionales**, no de calendario: el porcentaje de fines de semana en cada grupo es casi igual al 28.6 % esperado sin relación, y los festivos no se concentran (3.2 % y 2.8 %).
- Una hipótesis, sin verificar: el efecto de fin de semana es sobre todo de nivel, y al dividir cada perfil entre el promedio del día ese efecto desaparece del agrupamiento.
- **Mezcla por región (periodo común):** la proporción de días de verano va de 31 % (`FE`) a 45 % (`DOM` y `EKPC`). Sigue a la amplitud diaria de cada región (`EKPC` 0.44, `DOM` 0.40, `FE` 0.31) y no al sesgo invernal o veraniego.
- **Distancia al centro:** es similar en ambos grupos (mediana ≈ 0.21). Los días más alejados se concentran en regiones pequeñas (`EKPC` aparece 6 veces entre los 10 primeros), por lo que la distancia no es comparable entre regiones sin normalizar.

## Días atípicos (notebook 06, `PJME`)

| Indicador | Valor |
|---|---|
| Periodo cubierto por los residuos | 2012-08-03 → 2018-08-02 (6 pliegues de 12 meses) |
| Días evaluados | 2,191 |
| Días atípicos (z modificado > 3.5) | 22 (1.0 %): 15 altos y 7 bajos |
| Sensibilidad al umbral | 52 días con 3.0, 22 con 3.5, 9 con 4.0 y 2 con 5.0 |
| Concentración | Por estación de 0.7 % a 1.3 %. El pliegue 2 concentra más (7 días, 1.9 %) |
| Episodios | 5 coinciden, 3 sin coincidencia y 2 fuera de rango (de 10) |
| Dirección | 5 de 5 coinciden con el signo esperado |

| Fecha | Dirección | Residuo (%) | z | Episodio |
|---|---|---|---|---|
| 2012-10-30 | Baja | −27.9 | −5.74 | Huracán Sandy |
| 2014-01-07 | Alta | +25.0 | 5.55 | Vórtice polar de enero de 2014 |
| 2015-02-15 | Alta | +21.7 | 4.85 | Ola de frío de febrero de 2015 |
| 2017-05-20 | Baja | −23.6 | −4.81 | Ninguno conocido |
| 2016-09-10 | Alta | +20.7 | 4.64 | Ninguno conocido |
| 2013-09-10 | Alta | +20.5 | 4.58 | Calor de septiembre de 2013 |

- **No se detectan** la ola de calor de julio de 2013, la ola de frío de enero de 2018 ni la tormenta Jonas (esta última con fechas sin verificar). Una explicación posible, sin confirmar, es que en episodios largos los rezagos del modelo ya incorporan el nivel alto.
- **Fuera de rango:** las olas de calor de agosto de 2006 y julio de 2011 quedan antes del periodo de los residuos y no se evalúan.
- 16 de los 22 atípicos no coinciden con ningún episodio de la tabla. Dos caen el día siguiente a un festivo (2016-07-05 y 2018-05-29), un patrón compatible con que el rezago de 24 h hereda la baja demanda del festivo.
- El modelo tiende a sobrepronosticar: la mediana del residuo es negativa (de −0.65 % a −1.74 % según el pliegue).
- **Forma frente a nivel:** la correlación de Spearman entre |z| y la distancia al centro del grupo es 0.02, pero 8 de los 22 atípicos (36 %) tienen una forma lejana frente a cerca del 5 % del resto.

## Pronóstico a 24 horas (notebook 04, `PJME`)

Partición única (corte en 2017-01-01):

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) | MASE |
|---|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 | 1.06 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 | 1.63 |
| XGBoost | 1,861.58 | 2,512.52 | 5.89 | 0.86 |

XGBoost reduce el MAE un 19.1 % y el RMSE un 19.8 % respecto al modelo base de 24 h.

Ventana móvil (6 pliegues de 12 meses):

| Pliegue | Prueba | MAE XGBoost (MW) | MAE base (MW) | Mejora (%) | MASE XGBoost |
|---|---|---|---|---|---|
| 1 | 2012-08-03 → 2013-08-03 | 1,551 | 2,049 | 24.3 | 0.72 |
| 2 | 2013-08-03 → 2014-08-03 | 1,723 | 2,402 | 28.3 | 0.80 |
| 3 | 2014-08-03 → 2015-08-03 | 1,688 | 2,252 | 25.0 | 0.78 |
| 4 | 2015-08-03 → 2016-08-03 | 1,581 | 2,013 | 21.5 | 0.73 |
| 5 | 2016-08-03 → 2017-08-03 | 1,727 | 2,174 | 20.5 | 0.80 |
| 6 | 2017-08-03 → 2018-08-03 | 1,884 | 2,307 | 18.3 | 0.87 |

- **Mejora estable pero decreciente:** entre un 18 % y un 28 % según el pliegue.
- **Un modelo de «ayer con ajustes»:** `MW_lag_24` concentra el 71 % de la importancia, seguido de `MW_lag_168` (10 %) y `es_fin_de_semana` (8 %).
- **Dónde falla más:** en las horas de la tarde (≈ 2,350 MW a las 17 h frente a ≈ 1,500 MW de madrugada) y en verano e invierno (junio y julio ≈ 2,400 MW). Son los periodos más sensibles a la temperatura, que el modelo no tiene.
- **Dónde gana más al base:** en las horas de subida de la mañana (5–9 h, cerca de un 40 %). Por tipo de día, un 30 % en festivos, un 25 % en fines de semana y un 15 % en laborables.
- **Días de mayor error:** 2017-05-20 (MAE de 8,098 MW), 2018-06-03 y 2018-07-07. En 4 de los 10 peores días el modelo base obtiene menos error que XGBoost.