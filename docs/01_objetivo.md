# Objetivo

## Problema

El dataset *Hourly Energy Consumption* reúne la demanda horaria de 12 regiones de la red PJM (Estados Unidos) entre 1998 y 2018. En los trabajos revisados se usa sobre todo para pronosticar la demanda de una sola región. Este proyecto se centra en **caracterizar** cómo es la demanda: qué formas de día existen, en qué se diferencian las regiones y qué días se desvían de lo esperable, y en comunicarlo mediante visualizaciones. El pronóstico a 24 horas no es el producto final: es la referencia de lo esperable contra la que se miden las desviaciones.

## Preguntas de investigación

| N.º | Pregunta | Tarea visual |
|---|---|---|
| P1 | ¿Qué tipos de día (formas de perfil diario) existen y cómo se distribuyen en el calendario? | Descubrir patrones |
| P2 | ¿En qué se diferencian las regiones por su mezcla de tipos de día y su estacionalidad? | Comparar |
| P3 | ¿Qué días se desvían de la demanda esperable y a qué episodios corresponden? | Localizar anomalías |
| P4 | ¿Cuándo y cuánto falla un pronóstico a 24 horas? | Evaluar |

## Objetivo general

Caracterizar, mediante análisis visual apoyado en aprendizaje automático, los patrones de demanda eléctrica horaria de 12 regiones de la red PJM, identificando tipos de día, diferencias entre regiones y episodios atípicos, y comunicarlos en un panel interactivo.

## Objetivos específicos

| N.º | Objetivo | Criterio de logro | Estado |
|---|---|---|---|
| OE1 | Preparar una base horaria regular y documentada | Las 12 regiones superan la validación (fechas sin repetir, una hora entre filas, sin vacíos) y las filas finales cuadran (1,090,343) | Hecho |
| OE2 | Identificar tipos de día agrupando los perfiles diarios | Silueta media reportada (mayor que 0.50, razonable, de 0.26 a 0.50, débil), cada grupo con al menos el 5 % de los días y grupos interpretables con el calendario | Implementado (notebook 05), resultados por documentar |
| OE3 | Comparar las regiones por su mezcla de tipos de día y su estacionalidad | Cada región caracterizada por su distribución de tipos de día (en el historial completo y en el periodo común) y por indicadores de variabilidad, razón invierno/verano y caída de fin de semana | Implementado (notebooks 03 y 05), resultados por documentar |
| OE4 | Detectar días atípicos respecto de la demanda esperada | Días con z modificado del residuo > 3.5, con su magnitud y dirección, y contraste con episodios externos con fuente | Implementado (notebook 06), resultados por documentar |
| OE5 | Diseñar y construir un panel interactivo | Seis páginas (resumen, patrones, tipos de día, regiones, anomalías y pronóstico), cada vista justificada por una tarea y un canal perceptual, y filtros por región, fecha y estación | Parcial: las tablas están listas (notebook 07), el panel en Power BI está por construir |
| Referencia | Pronóstico a 24 horas como referencia de lo esperable | Modelo que supera al base en todos los pliegues de una ventana móvil, con MASE menor que 1 | Implementado (notebook 04), resultados por documentar |

Las decisiones de diseño que condicionan estos objetivos (día operativo, atípicos aislados, `NI` y `COMED`, hora de `COMED`) están en [04_metodologia_desarrollo.md](04_metodologia_desarrollo.md#decisiones-de-diseño).

## Alcance

**Dentro:** limpieza y documentación de la calidad de los datos, análisis descriptivo con el día operativo, agrupamiento de perfiles diarios de las 12 regiones, pronóstico de referencia a 24 horas con validación en ventana móvil, detección de días atípicos a partir de los residuos fuera de muestra y panel en Power BI.

**Fuera:** datos externos (temperatura, precios), análisis en tiempo real, despliegue en producción y búsqueda de hiperparámetros del pronóstico. El pronóstico y la detección de anomalías se hacen solo para `PJME`.