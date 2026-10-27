# Plan del proyecto

## 1. Objetivos y alcance

Los objetivos y el alcance están en [01_objetivo.md](01_objetivo.md).

## 2. Métricas de evaluación

### Del proyecto

| Criterio | Cómo se verifica | Estado |
|---|---|---|
| Datos limpios y documentados | Las 12 regiones superan la validación | Cumplido |
| Tipos de día identificados | Silueta media ≥ 0.50, grupos de al menos el 5 % de los días e interpretables con el calendario | Por hacer |
| Comparación entre regiones | Cada región caracterizada por su mezcla de tipos de día | Parcial |
| Días atípicos detectados | z modificado del residuo > 3.5 y contraste con episodios externos | Por hacer |
| Panel interactivo | Cada vista justificada por una tarea y un canal perceptual; filtros por región, fecha y estación | Por hacer |
| Reproducibilidad | Un tercero reproduce el análisis con la guía de usuario | Por comprobar |

### Del agrupamiento

| Métrica | Regla |
|---|---|
| Silueta media | Estructura razonable si es ≥ 0.50; débil entre 0.26 y 0.50, y se reporta como tal |
| Tamaño de los grupos | Ninguno con menos del 5 % de los días |
| Estabilidad | La solución se mantiene al repetir con distintas semillas |

### Del pronóstico (`PJME`)

| Modelo | MAE (MW) | RMSE (MW) | MAPE (%) |
|---|---|---|---|
| Base 24 h | 2,300.08 | 3,134.18 | 7.32 |
| Base 168 h | 3,511.18 | 4,793.98 | 10.99 |
| XGBoost | 1,862.27 | 2,513.11 | 5.89 |

Se añadirán MASE (debe ser menor que 1) y la validación en ventana móvil con al menos 3 pliegues.

Herramientas: las de [03_metodos_y_herramientas.md](03_metodos_y_herramientas.md). Datos: *Hourly Energy Consumption* (Kaggle).

## 3. Cronograma

| Fase | Actividades | Fechas | Entregable | Estado |
|---|---|---|---|---|
| 1 a 3 | Exploración, limpieza y análisis descriptivo | `[completar]` | Notebooks 01 a 03 | Hecho |
| 4 | Pronóstico de referencia y ventana móvil | `[completar]` | Notebook 04 | Parcial |
| 5 | Agrupamiento de perfiles diarios | `[completar]` | Notebook 05 | Por hacer |
| 6 | Detección de anomalías | `[completar]` | Notebook 06 | Por hacer |
| 7 | Exportación y panel en Power BI | `[completar]` | Notebook 07 y panel | Por hacer |
| 8 | Documentación e informe final | `[completar]` | `docs/` | En curso |

## 4. Presupuesto

Sin costo económico: las librerías son de código abierto y el dataset es de acceso libre.
## 5. Riesgos

| Riesgo | Impacto | Mitigación | Estado |
|---|---|---|---|
| Las regiones cubren periodos distintos | Comparaciones poco justas | Comparar las 10 regiones vigentes en su periodo común | Se materializó y está mitigado |
| Horas duplicadas o faltantes por cambios de horario | Errores en agregaciones y en el modelo | Limpieza con reglas y validación | Se materializó y está resuelto |
| La convención de hora de fin desplaza el día de la fila de las 00:00 | Pequeño (1 de cada 24 horas) | Adoptar el día operativo y repetir los notebooks 03 y 04 | Abierto |
| Valores bajos candidatos a error en `DOM` y `PJMW` | Pequeño | Implementar la regla del z modificado | Abierto |
| La estructura de los grupos resulta débil | Medio | Reportarla como tal y apoyarla con el calendario | Abierto |
| Entrenar un modelo por región y pliegue es lento | Medio | Empezar con `PJME` y ampliar a las demás | Abierto |
| El pronóstico falla en olas de calor y de frío por no usar temperatura | Medio | Documentarlo como limitación; los residuos se usan para detectar anomalías | Abierto |
| Dependencia de Power BI y de su licencia | Medio | Verificar la licencia; Streamlit queda como alternativa | Abierto |