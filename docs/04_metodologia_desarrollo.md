# Metodología de desarrollo

El proyecto avanza por fases, con un notebook por fase y las funciones reutilizables en `src/`. En cada fase se formulan hipótesis a partir de los resultados y se contrastan con los datos antes de aceptarlas. Por ejemplo:

- La sospecha de que las horas faltantes eran cambios de horario se confirmó con las fechas exactas, comparadas con la regla del cambio de horario de EE. UU. Quedaron 9 faltantes sin explicación horaria (ver `02_base_de_datos.md`).
- La de que el cero de `FE` era un error se confirmó al ver que era su primer registro.
- La de que el mínimo de `EKPC` (514 MW) era un error se descartó: es una racha de varias horas en la madrugada de un domingo.
- El desfase de una hora de `COMED` (y de `NI`) se midió en los notebooks 03 y 05 y no se corrigió: es lo esperable si las series están en hora del este y esas zonas son de hora central.
- La expectativa de que el agrupamiento separaría laborables y fines de semana no se cumplió: con k = 2 los grupos son estacionales (notebook 05).

## Fases

| Fase | Actividades | Entregable | Estado |
|---|---|---|---|
| 1. Exploración y calidad | Estructura, convención horaria, cobertura, duplicados, horas faltantes y valores sospechosos | Notebook 01 | Hecho |
| 2. Preparación | Limpieza con reglas explícitas y validación | Notebook 02 y `data/processed/` | Hecho |
| 3. Análisis descriptivo | Patrones por hora, día y estación, tendencia, comparación, picos | Notebook 03 | Hecho (con el día operativo) |
| 4. Pronóstico de referencia | Modelo a 24 horas contra modelos base, MASE, validación en ventana móvil, residuos fuera de muestra | Notebook 04 | Hecho |
| 5. Agrupamiento de perfiles diarios | Perfiles normalizados, elección de k, caracterización con el calendario, mezcla por región y distancia al centro | Notebook 05 | Hecho, con decisiones pendientes (D7 y justificación de k) |
| 6. Detección de anomalías | Residuo diario, z modificado y contraste con episodios conocidos | Notebook 06 | Hecho |
| 7. Visualización | Exportación de tablas y construcción del panel | Notebook 07 y panel en Power BI | Notebook 07 implementado, panel por hacer |
| 8. Documentación | Informe, conclusiones y orden del repositorio | Documentación en `docs/` | En curso |

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
| D1 | Calcular las variables de calendario desde `Datetime − 1 h` (día operativo) | `Datetime` marca el final de la hora, sin el ajuste, la hora 24 de cada día cae en el día siguiente y los perfiles de 24 horas quedan desfasados | Usar `Datetime` directamente | `src/features.py`, notebooks 01 a 07. Los notebooks 03 a 06 ya se ejecutaron con el día operativo | Aplicada |
| D2 | Conservar los atípicos aislados (`DOM` 1,253 MW y `PJMW` 487 MW) y dejar la regla del z modificado de la limpieza por hacer | Son 2 valores en más de 1 M de filas. Los valores de `PJMW` de 2012-04-01/02 (2,553 y 2,574 MW) no cumplen el criterio de aislado. La regla debe aplicarse a la desviación respecto del patrón esperado y no al MW crudo, porque marcaría los picos reales | Implementarla ahora en `cleaning.py` | `cleaning.py`, notebook 02, `02_base_de_datos.md` | Por hacer |
| D3 | Guardar `NI` y `COMED` por separado por ahora | Unirlas supone asumir que son la misma serie. El cociente de niveles es 1.00 y se tocan el 2011-01-01 (notebook 03, sección 6.2), lo que respalda unirlas | Unirlas en una sola serie | Notebooks 02, 05 y 07 | Por confirmar |
| D4 | Panel en Power BI, Streamlit queda como prototipo opcional | Lo pide la rúbrica | Solo Streamlit | Notebook 07, `app/` | Confirmada |
| D5 | Residuos con ventana móvil de 6 pliegues de 12 meses (mínimo 3) | Cubren 2012-08 → 2018-08, que incluye el huracán Sandy, el vórtice polar de 2014 y el frío de 2015 | 3 pliegues | Notebooks 04 y 06 | Aplicada |
| D6 | Un solo agrupamiento para las 12 regiones | Los perfiles están normalizados, así que los tipos de día son los mismos y se puede construir la matriz región por tipo de día | Un agrupamiento por región | Notebook 05 | Aplicada |
| D7 | Conservar la hora de la fuente de `COMED` y `NI`, salvo que el notebook 05 decida alinearlas a hora central | El diagnóstico del notebook 05 mide +1 h en ambas y 0 en el resto. Si no se alinea, la comparación de formas con otras regiones podría distorsionarse | Alinearlas siempre | Notebooks 05 y 07 | Por decidir: el notebook 05 se ejecutó con `ALINEAR_HORA_CENTRAL = False`, falta repetirlo con `True` y comparar la mezcla de tipos de día |
| D8 | Calcular el z modificado con todos los días de la región | Es simple y comparable. El notebook 06 comprobó que los atípicos no se concentran en una estación (0.7 % a 1.3 %) | Calcularlo por estación | Notebook 06 | Aplicada |

### Pendiente de decisión (sin ID asignado)

**Elección de k.** La mayor silueta con grupos de al menos el 5 % es k-medias con k = 2 (0.413, débil). Esos dos grupos separan temporada fría (oct–may) y verano (jun–sep), no laborables y fines de semana. Con k = 3 la silueta es 0.30 y con k ≥ 4 queda por debajo de 0.26. Hay que decidir si se reporta k = 2 como resultado o se justifica un k mayor, y registrarlo en la bitácora.

## Criterios de avance

Una fase se considera cerrada cuando cumple su criterio de logro:

| Fase | Criterio | Estado |
|---|---|---|
| Preparación | Las 12 regiones superan `validar_limpieza` y las filas finales cuadran (1,090,343) | Cumplido |
| Agrupamiento | Silueta media reportada y grupos con al menos el 5 % de los días | Cumplido: silueta 0.413 (débil), grupo más pequeño 37.7 % |
| Pronóstico | El modelo supera al base en todos los pliegues de la ventana móvil y su MASE es menor que 1 | Cumplido: 6 de 6 pliegues, MASE de 0.72 a 0.87 |
| Anomalías | Lista contrastada con al menos un episodio externo, con fuente | Cumplido: 5 episodios coinciden |
| Panel | Cada vista justificada por una tarea y filtros por región, fecha y estación funcionando | Pendiente |