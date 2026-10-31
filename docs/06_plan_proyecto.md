# Plan del proyecto

## 1. Objetivos y alcance

Los objetivos y el alcance están en [01_objetivo.md](01_objetivo.md). Las decisiones de diseño están en [04_metodologia_desarrollo.md](04_metodologia_desarrollo.md#decisiones-de-diseño).

## 2. Métricas de evaluación

### Del proyecto

| Criterio | Cómo se verifica | Estado |
|---|---|---|
| Datos limpios y documentados | Las 12 regiones superan la validación y las filas finales cuadran (1,090,343) | Cumplido |
| Tipos de día identificados | Silueta media ≥ 0.50 (razonable) o entre 0.26 y 0.50 (débil, reportada como tal), grupos de al menos el 5 % de los días e interpretables con el calendario | Implementado (notebook 05) |
| Comparación entre regiones | Cada región caracterizada por su mezcla de tipos de día, en el historial completo y en el periodo común | Parcial |
| Días atípicos detectados | z modificado del residuo > 3.5 y contraste con episodios externos, con fuente y fecha verificada | Implementado (notebook 06) |
| Panel interactivo | Seis páginas, cada vista justificada por una tarea y un canal perceptual; filtros por región, fecha y estación | Tablas listas (notebook 07); panel por hacer |
| Reproducibilidad | Un tercero reproduce el análisis con la guía de usuario | Por comprobar |

### Del agrupamiento

| Métrica | Regla |
|---|---|
| Silueta media | Estructura razonable si es ≥ 0.50; débil entre 0.26 y 0.50, y se reporta como tal |
| Tamaño de los grupos | Ninguno con menos del 5 % de los días |
| Estabilidad | Concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado), reportada en el notebook 05. La repetición con distintas semillas queda por hacer |

### Del pronóstico (`PJME`)

Partición única (corte en 2017-01-01). Cifras calculadas con `Datetime` como hora de fin, **por recalcular** con el día operativo.

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) | MASE |
|---|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 | `[completar]` |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 | `[completar]` |
| XGBoost | 1,862.27 | 2,513.11 | 5.89 | `[completar]` |

Validación en ventana móvil (6 pliegues de 12 meses, mínimo 3): XGBoost debe superar al base en todos los pliegues y su MASE debe ser menor que 1. Resultados: `[completar]`.

### De los días atípicos

| Métrica | Regla |
|---|---|
| Umbral | \|z modificado\| > 3.5, con la sensibilidad a 3, 4 y 5 reportada |
| Episodios | Al menos uno coincide con la lista, los episodios fuera del rango de los residuos se marcan como no evaluados |
| Dirección | Las olas de frío y de calor deben dar residuos positivos y el huracán Sandy, negativos |

Herramientas: las de [03_metodos_y_herramientas.md](03_metodos_y_herramientas.md). Datos: *Hourly Energy Consumption* (Kaggle).

## 3. Cronograma

| Fase  | Actividades                                      | Entregable        | Estado                                    |
|-------|--------------------------------------------------|-------------------|-------------------------------------------|
| 1 a 3 | Exploración, limpieza y análisis descriptivo     | Notebooks 01 a 03 | Hecho, 03 por recalcular                  |
| 4     | Pronóstico de referencia, MASE y ventana móvil   | Notebook 04       | Implementado                              |
| 5     | Agrupamiento de perfiles diarios                 | Notebook 05       | Implementado                              |
| 6     | Detección de anomalías                           | Notebook 06       | Implementado                              |
| 7     | Exportación y panel en Power BI                  | Notebook 07 y panel | Notebook 07 implementado, panel por hacer |
| 8     | Documentación e informe final                    | `docs/`           | En curso                                  |

## 4. Presupuesto

Sin costo económico: las librerías son de código abierto y el dataset es de acceso libre.

## 5. Riesgos

| Riesgo | Impacto | Mitigación | Estado |
|---|---|---|---|
| Las regiones cubren periodos distintos | Comparaciones poco justas | Comparar las 10 regiones vigentes en su periodo común | Se materializó y está mitigado |
| Horas duplicadas o faltantes por cambios de horario | Errores en agregaciones y en el modelo | Limpieza con reglas y validación | Se materializó y está resuelto |
| La convención de hora de fin desplaza el día de la fila de las 00:00 | Pequeño (1 de cada 24 horas) | Día operativo (D1) en `features.py` | Mitigado en el código; falta repetir los notebooks 03 y 04 |
| Las cifras ya publicadas (horas, fin de semana, pronóstico) quedan desactualizadas | Medio | Marcarlas como por recalcular y reemplazarlas tras repetir los notebooks | Abierto |
| Valores bajos candidatos a error en `DOM` y `PJMW` | Pequeño | Se conservan; regla del z modificado en la limpieza por hacer (D2) | Aceptado |
| `DEOK` con mínimos y lecturas duplicadas inconsistentes | Pequeño | Revisar con la tabla de valores aislados del notebook 01 | Abierto |
| La hora de `COMED` y `NI` llega una hora más tarde que el resto | Medio: los tipos de día podrían separarse por la hora y no por la forma | Medir el desfase en el notebook 05 y alinear a hora central si hace falta (D7) | Abierto |
| La estructura de los grupos resulta débil | Medio | Reportarla como tal y apoyarla con el calendario | Abierto |
| Entrenar un modelo por región y pliegue es lento | Medio | Empezar con `PJME` (6 modelos en la ventana móvil) y ampliar a las demás | Abierto |
| Las anomalías solo se evalúan en `PJME`, la única región con residuos | Medio | Documentarlo, repetir el notebook 04 con otras regiones si hay tiempo | Abierto |
| Fechas de episodios sin fuente (por ejemplo, la tormenta Jonas) | Pequeño | Cada episodio lleva su fuente y una marca de verificación | Parcialmente mitigado |
| El pronóstico falla en olas de calor y de frío por no usar temperatura | Medio | Documentarlo como limitación, los residuos se usan para detectar anomalías | Abierto |
| Dependencia de Power BI y de su licencia | Medio | Verificar la licencia, Streamlit queda como alternativa (D4) | Abierto |