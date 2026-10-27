# Metodología de desarrollo

El proyecto avanza por fases, con un notebook por fase y las funciones reutilizables en `src/`. En cada fase se formulan hipótesis a partir de los resultados y se contrastan con los datos antes de aceptarlas. Por ejemplo, la sospecha de que las horas faltantes eran cambios de horario se confirmó con las fechas exactas, y la de que el cero de `FE` era un error se confirmó al ver que era su primer registro.

## Fases

| Fase | Actividades | Entregable | Estado |
|---|---|---|---|
| 1. Exploración y calidad | Estructura, cobertura, duplicados, horas faltantes y valores sospechosos | Notebook 01 | Hecho |
| 2. Preparación | Limpieza con reglas explícitas y validación | Notebook 02 y `data/processed/` | Hecho |
| 3. Análisis descriptivo | Patrones por hora, día y estación; tendencia; comparación; picos | Notebook 03 | Hecho |
| 4. Pronóstico de referencia | Modelo a 24 horas contra modelos base; validación en ventana móvil | Notebook 04 | Hecho; ampliación por hacer |
| 5. Agrupamiento de perfiles diarios | Perfiles normalizados, elección de k y caracterización con el calendario | Notebook 05 | Por hacer |
| 6. Detección de anomalías | Residuos fuera de muestra y contraste con episodios conocidos | Notebook 06 | Por hacer |
| 7. Visualización | Exportación de tablas y construcción del panel | Notebook 07 y panel en Power BI | Por hacer |
| 8. Documentación | Informe, conclusiones y orden del repositorio | Documentación en `docs/` | En curso |

## Flujo de notebooks

| Notebook | Entrada | Salida |
|---|---|---|
| 01 Exploración | `data/raw/*.csv` | Hallazgos y decisiones de limpieza |
| 02 Limpieza | `data/raw/*.csv` | `data/processed/` (un archivo por región y `consumo_horario.parquet`) |
| 03 Análisis | `consumo_horario.parquet` | Patrones, tendencia, comparación y picos |
| 04 Modelado | `consumo_horario.parquet` | Métricas y residuos del pronóstico |
| 05 Agrupamiento | `consumo_horario.parquet` | Perfiles, grupos y mezcla por región |
| 06 Anomalías | Residuos del notebook 04 | Lista de días atípicos |
| 07 Exportación | Resultados de los notebooks 03 a 06 | Tablas para Power BI |

## Criterios de avance

Una fase se considera cerrada cuando cumple su criterio de logro:

- **Preparación:** las 12 regiones superan `validar_limpieza`.
- **Agrupamiento:** silueta media reportada y grupos con al menos el 5 % de los días.
- **Pronóstico:** el modelo supera al base en todos los pliegues de la ventana móvil.
- **Anomalías:** lista contrastada con al menos un episodio externo.
- **Panel:** cada vista justificada por una tarea y filtros funcionando.