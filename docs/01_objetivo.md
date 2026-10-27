# Objetivo

## Problema

El dataset *Hourly Energy Consumption* reúne la demanda horaria de 12 regiones de la red PJM (Estados Unidos) entre 1998 y 2018. En los trabajos revisados se usa sobre todo para pronosticar la demanda de una sola región. Este proyecto se centra en **caracterizar** cómo es la demanda: qué formas de día existen, en qué se diferencian las regiones y qué días se desvían de lo esperable, y en comunicarlo mediante visualizaciones.

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
| OE1 | Preparar una base horaria regular y documentada | Las 12 regiones superan la validación (fechas sin repetir, una hora entre filas, sin vacíos) | Hecho |
| OE2 | Identificar tipos de día agrupando los perfiles diarios | Silueta media ≥ 0.50; cada grupo con al menos el 5 % de los días; grupos interpretables con el calendario | Por hacer |
| OE3 | Comparar las regiones por su mezcla de tipos de día y su estacionalidad | Cada región caracterizada por su distribución de tipos de día y por indicadores de variabilidad, razón invierno/verano y caída de fin de semana | Parcial: los indicadores están calculados; falta la mezcla de tipos de día |
| OE4 | Detectar días atípicos respecto de la demanda esperada | Días con z modificado del residuo > 3.5; contraste con episodios externos | Por hacer |
| OE5 | Diseñar y construir un panel interactivo | Cada vista justificada por una tarea y un canal perceptual; filtros por región, fecha y estación | Por hacer |

## Alcance

**Dentro:** limpieza y documentación de la calidad de los datos, análisis descriptivo, agrupamiento de perfiles diarios, detección de anomalías, pronóstico de referencia a 24 horas y panel en Power BI.

**Fuera:** datos externos (temperatura, precios), análisis en tiempo real, despliegue en producción y búsqueda de hiperparámetros del pronóstico.