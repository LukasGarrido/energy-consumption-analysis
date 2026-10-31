# Metodología de desarrollo

El proyecto avanza por fases, con un notebook por fase y las funciones reutilizables en `src/`. En cada fase se formulan hipótesis a partir de los resultados y se contrastan con los datos antes de aceptarlas. Por ejemplo:

- La sospecha de que las horas faltantes eran cambios de horario se confirmó con las fechas exactas, comparadas con la regla del cambio de horario de EE. UU.
- La de que el cero de `FE` era un error se confirmó al ver que era su primer registro.
- La de que el mínimo de `EKPC` (514 MW) era un error se descartó: es una racha de varias horas en la madrugada de un domingo.
- El desfase de una hora de `COMED` no se corrigió: es lo esperable si las series están en hora del este y `COMED` es una zona de hora central.

## Fases

| Fase | Actividades | Entregable | Estado |
|---|---|---|---|
| 1. Exploración y calidad | Estructura, convención horaria, cobertura, duplicados, horas faltantes y valores sospechosos | Notebook 01 | Hecho |
| 2. Preparación | Limpieza con reglas explícitas y validación | Notebook 02 y `data/processed/` | Hecho |
| 3. Análisis descriptivo | Patrones por hora, día y estación, tendencia, comparación, picos | Notebook 03 | Hecho, recalcular con el día operativo |
| 4. Pronóstico de referencia | Modelo a 24 horas contra modelos base, MASE, validación en ventana móvil, residuos fuera de muestra | Notebook 04 | Implementado|
| 5. Agrupamiento de perfiles diarios | Perfiles normalizados, elección de k, caracterización con el calendario, mezcla por región y distancia al centro | Notebook 05 | Implementado |
| 6. Detección de anomalías | Residuo diario, z modificado y contraste con episodios conocidos | Notebook 06 | Implementado |
| 7. Visualización | Exportación de tablas y construcción del panel | Notebook 07 y panel en Power BI | Notebook 07 implementado, panel por hacer |
| 8. Documentación | Informe, conclusiones y orden del repositorio | Documentación en `docs/` | Hecho |

## Flujo de notebooks

Ejecutar en orden numérico, cada uno con *Restart & Run All*.

| Notebook | Entrada | Salida |
|---|---|---|
| 01 Exploración | `data/raw/*.csv` | Hallazgos y decisiones de limpieza |
| 02 Limpieza | `data/raw/*.csv` | `data/processed/` (`<REGION>_clean.parquet` por región y `consumo_horario.parquet`) |
| 03 Análisis | `consumo_horario.parquet` | Patrones, tendencia, comparación y picos |
| 04 Modelado | `consumo_horario.parquet` | `residuos_PJME.parquet` (fuera de muestra) y `metricas_ventana_movil_PJME.parquet` |
| 05 Agrupamiento | `consumo_horario.parquet` | `tipos_de_dia.parquet`, `tipos_de_dia_curvas.parquet`, `tipos_de_dia_resumen.parquet`, `tipos_de_dia_mezcla_region.parquet` y `tipos_de_dia_silueta_k.parquet` |
| 06 Anomalías | `residuos_PJME.parquet` y, si existe, `tipos_de_dia.parquet` | `anomalias_PJME_diario.parquet`, `anomalias_PJME_lista.parquet` y `anomalias_PJME_episodios.parquet` |
| 07 Exportación | `consumo_horario.parquet` y las salidas de los notebooks 04 a 06 | `data/processed/powerbi/*.csv` (17 tablas) y `diccionario_datos.csv` |

Los parámetros `ALINEAR_HORA_CENTRAL` y `REGIONES_HORA_CENTRAL` deben tener el mismo valor en los notebooks 05 y 07.

## Decisiones de diseño

Cada decisión se escribe aquí una vez, los demás documentos la enlazan.

| ID | Decisión | Motivo | Alternativa descartada | Impacto | Estado |
|---|---|---|---|---|---|
| D1 | Calcular las variables de calendario desde `Datetime − 1 h` (día operativo) | `Datetime` marca el final de la hora, sin el ajuste, la hora 24 de cada día cae en el día siguiente y los perfiles de 24 horas quedan desfasados | Usar `Datetime` directamente | `src/features.py`, notebooks 01 a 07, las cifras horarias deben recalcularse | Aplicada |
| D2 | Conservar los atípicos aislados (`DOM` 1,253 MW, `PJMW` 487, 2,553 y 2,574 MW) y dejar la regla del z modificado de la limpieza por hacer | Son 4 valores en más de 1 M de filas. La regla debe aplicarse a la desviación respecto del patrón esperado y no al MW crudo, porque marcaría los picos reales | Implementarla ahora en `cleaning.py` | `cleaning.py`, notebook 02, `02_base_de_datos.md` | Por hacer |
| D3 | Guardar `NI` y `COMED` por separado por ahora | Unirlas supone asumir que son la misma serie. El cociente de niveles es 1.00 y se tocan el 2011-01-01, lo que respalda unirlas | Unirlas en una sola serie | Notebooks 02, 05 y 07 | Por confirmar |
| D4 | Panel en Power BI, Streamlit queda como prototipo opcional | Lo pide la rúbrica | Solo Streamlit | Notebook 07, `app/` | Confirmada |
| D5 | Residuos con ventana móvil de 6 pliegues de 12 meses (mínimo 3) | Cubren 2012-08 → 2018-08, que incluye el huracán Sandy, el vórtice polar de 2014 y el frío de 2015 | 3 pliegues | Notebooks 04 y 06 | Aplicada |
| D6 | Un solo agrupamiento para las 12 regiones | Los perfiles están normalizados, así que los tipos de día son los mismos y se puede construir la matriz región por tipo de día | Un agrupamiento por región | Notebook 05 | Aplicada |
| D7 | Conservar la hora de la fuente de `COMED` y `NI`, salvo que el notebook 05 decida alinearlas a hora central | Su curva llega una hora más tarde, si no se alinea, la comparación de formas con otras regiones se distorsiona | Alinearlas siempre | Notebooks 05 y 07 | Por decidir |
| D8 | Calcular el z modificado con todos los días de la región | Es simple y comparable, el notebook 06 comprueba la concentración por estación y ofrece `Z_POR_ESTACION` | Calcularlo por estación | Notebook 06 | Aplicada |

## Criterios de avance

Una fase se considera cerrada cuando cumple su criterio de logro:

- **Preparación:** las 12 regiones superan `validar_limpieza` y las filas finales cuadran (1,090,343).
- **Agrupamiento:** silueta media reportada y grupos con al menos el 5 % de los días.
- **Pronóstico:** el modelo supera al base en todos los pliegues de la ventana móvil y su MASE es menor que 1.
- **Anomalías:** lista contrastada con al menos un episodio externo, con fuente.
- **Panel:** cada vista justificada por una tarea y filtros por región, fecha y estación funcionando.