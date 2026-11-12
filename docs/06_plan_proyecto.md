# Plan del proyecto

## 1. Objetivos y alcance

Los objetivos y el alcance están en [01_objetivo.md](01_objetivo.md). Las decisiones de diseño están en [04_metodologia_desarrollo.md](04_metodologia_desarrollo.md#decisiones-de-diseño).

## 2. Métricas de evaluación

### Del proyecto

| Criterio | Cómo se verifica | Estado |
|---|---|---|
| Datos limpios y documentados | Las 12 regiones superan la validación y las filas finales cuadran (1,090,343) | Cumplido |
| Tipos de día identificados | Silueta media ≥ 0.50 (razonable) o entre 0.26 y 0.50 (débil, reportada como tal), grupos de al menos el 5 % de los días e interpretables con el calendario | Cumplido con salvedad: silueta 0.413 (débil), 2 grupos estacionales, grupo más pequeño 37.7 % |
| Comparación entre regiones | Cada región caracterizada por su mezcla de tipos de día, en el historial completo y en el periodo común | Cumplido |
| Días atípicos detectados | z modificado del residuo > 3.5 y contraste con episodios externos, con fuente y fecha verificada | Cumplido: 22 días, 5 episodios coinciden |
| Panel interactivo | Seis páginas, cada vista justificada por una tarea y un canal perceptual, filtros por región, fecha y estación | Tablas listas (notebook 07), panel por hacer |
| Reproducibilidad | Un tercero reproduce el análisis con la guía de usuario | Por comprobar |

### Del agrupamiento

| Métrica | Regla | Resultado |
|---|---|---|
| Silueta media | Estructura razonable si es ≥ 0.50, débil entre 0.26 y 0.50, y se reporta como tal | 0.413 (débil) con k-medias y k = 2 |
| Tamaño de los grupos | Ninguno con menos del 5 % de los días | Cumplido: 62.3 % y 37.7 % |
| Estabilidad | Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado), reportada en el notebook 05. La repetición con distintas semillas queda por hacer | Rand ajustado 0.82. Semillas por hacer |

### Del pronóstico (`PJME`)

Partición única (corte en 2017-01-01), calculada con el día operativo.

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) | MASE |
|---|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 | 1.06 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 | 1.63 |
| XGBoost | 1,861.58 | 2,512.52 | 5.89 | 0.86 |

Validación en ventana móvil (6 pliegues de 12 meses, mínimo 3): XGBoost debe superar al base en todos los pliegues y su MASE debe ser menor que 1. **Resultado: cumplido.** Supera al base en los 6 pliegues (mejora de MAE de 18.3 % a 28.3 %) y su MASE va de 0.72 a 0.87.

### De los días atípicos

| Métrica | Regla | Resultado |
|---|---|---|
| Umbral | \|z modificado\| > 3.5, con la sensibilidad a 3, 4 y 5 reportada | 22 días con 3.5. Con 3, 4 y 5: 52, 9 y 2 días. El corte es frágil entre 3.5 y 4 |
| Episodios | Al menos uno coincide con la lista, los episodios fuera del rango de los residuos se marcan como no evaluados | Cumplido: 5 coinciden, 3 sin coincidencia y 2 no evaluados (2006 y 2011) |
| Dirección | Las olas de frío y de calor deben dar residuos positivos y el huracán Sandy, negativos | Cumplido: 5 de 5 con el signo esperado |

Herramientas: las de [03_metodos_y_herramientas.md](03_metodos_y_herramientas.md). Datos: *Hourly Energy Consumption* (Kaggle).

## 3. Cronograma

| Fase  | Actividades                                      | Entregable        | Estado                                    |
|-------|--------------------------------------------------|-------------------|-------------------------------------------|
| 1 a 3 | Exploración, limpieza y análisis descriptivo     | Notebooks 01 a 03 | Hecho                                     |
| 4     | Pronóstico de referencia, MASE y ventana móvil   | Notebook 04       | Hecho                                     |
| 5     | Agrupamiento de perfiles diarios                 | Notebook 05       | Hecho, con decisiones pendientes (D7 y k) |
| 6     | Detección de anomalías                           | Notebook 06       | Hecho                                     |
| 7     | Exportación y panel en Power BI                  | Notebook 07 y panel | Notebook 07 implementado, panel por hacer |
| 8     | Documentación e informe final                    | `docs/`           | En curso                                  |

## 4. Presupuesto

Sin costo económico: las librerías son de código abierto y el dataset es de acceso libre.

## 5. Riesgos

| Riesgo | Impacto | Mitigación | Estado |
|---|---|---|---|
| Las regiones cubren periodos distintos | Comparaciones poco justas | Comparar las 10 regiones vigentes en su periodo común | Se materializó y está mitigado |
| Horas duplicadas o faltantes por cambios de horario | Errores en agregaciones y en el modelo | Limpieza con reglas y validación | Se materializó y está resuelto |
| Horas faltantes sin causa horaria (2010-12-10 en 7 regiones, más 2 de `AEP`) | Pequeño | Se interpolan como el resto | Aceptado, falla común de la fuente por confirmar |
| La convención de hora de fin desplaza el día de la fila de las 00:00 | Pequeño (1 de cada 24 horas) | Día operativo (D1) en `features.py` | Resuelto: los notebooks 03 a 06 se ejecutaron con el día operativo |
| Las cifras publicadas (horas, fin de semana, pronóstico) quedaron desactualizadas | Medio | Reemplazarlas tras repetir los notebooks | Cerrado: documentación actualizada |
| Valores bajos aislados en `DOM` y `PJMW` | Pequeño | Se conservan, regla del z modificado en la limpieza por hacer (D2) | Aceptado |
| `DEOK` con una racha baja (2018-04-22) y lecturas duplicadas inconsistentes (2017-11-05) | Pequeño | Revisar con la tabla de valores aislados del notebook 01 | Abierto |
| Máximo de `AEP` (2008-10-20) inusual | Pequeño | Verificar contra la fuente | Abierto |
| La hora de `COMED` y `NI` llega una hora más tarde que el resto | Medio: los tipos de día podrían separarse por la hora y no por la forma | Medido en el notebook 05 (+1 h). Repetir con `ALINEAR_HORA_CENTRAL = True` y comparar (D7) | Abierto |
| La estructura de los grupos resulta débil | Medio | Reportarla como tal y apoyarla con el calendario | Se materializó (silueta 0.413), reportada |
| Con k = 2 los tipos de día solo capturan la estación y no el fin de semana | Medio: P1 queda respondida solo en parte | Justificar un k mayor aunque baje la silueta, o reportarlo como limitación | Abierto |
| Entrenar un modelo por región y pliegue es lento | Medio | Empezar con `PJME` (6 modelos en la ventana móvil) y ampliar a las demás | Abierto |
| Las anomalías solo se evalúan en `PJME`, la única región con residuos | Medio | Documentarlo, repetir el notebook 04 con otras regiones si hay tiempo | Abierto |
| Fechas de episodios sin fuente (por ejemplo, la tormenta Jonas) | Pequeño | Cada episodio lleva su fuente y una marca de verificación | Parcialmente mitigado |
| El pronóstico falla en olas de calor y de frío por no usar temperatura | Medio | Documentarlo como limitación, los residuos se usan para detectar anomalías | Abierto |
| Dependencia de Power BI y de su licencia | Medio | Verificar la licencia, Streamlit queda como alternativa (D4) | Abierto |