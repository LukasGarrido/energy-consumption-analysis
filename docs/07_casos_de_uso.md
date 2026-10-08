# Casos de uso

Historias de usuario que describen qué necesitaría lograr cada parte interesada con este análisis y por qué. Cada historia incluye criterios de aceptación para verificar que se cumplió.

**Formato:** _Como_ [parte interesada], _quiero_ [qué lograr], _para_ [motivo].

---

## Partes interesadas

| Parte interesada                  | Descripción                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------- |
| Analista de planeación energética | Necesita entender cuándo y cuánto se consume para planificar la capacidad       |
| Operador de red                   | Necesita anticipar la demanda y detectar regiones con comportamientos distintos |
| Estudiante o investigador         | Necesita reproducir y validar el análisis, o usarlo como base para otro trabajo |

---

## Historias de usuario

### HU-01. Patrones por hora y día de la semana

**Como** analista de planeación energética, **quiero** ver el consumo promedio por hora del día y día de la semana, **para** anticipar los momentos de mayor demanda.

**Criterios de aceptación:**

- Existe un mapa de calor de hora por día de la semana para cada región analizada.
- Se indica en qué horas y días se concentra el mayor consumo.

### HU-02. Estacionalidad y tendencia

**Como** analista de planeación energética, **quiero** conocer cómo cambia el consumo a lo largo del año y de los años, **para** distinguir los efectos estacionales de la tendencia de largo plazo.

**Criterios de aceptación:**

- Hay un gráfico de consumo por mes y otro con la tendencia de largo plazo.
- Se describen los meses o estaciones de mayor y menor consumo.

### HU-03. Comparación entre regiones

**Como** operador de red, **quiero** comparar el consumo entre regiones, **para** identificar cuáles tienen más variabilidad o picos más marcados.

**Criterios de aceptación:**

- La comparación se hace sobre un periodo común para todas las regiones.
- Se señalan las diferencias y similitudes más relevantes.

### HU-04. Periodos de máxima demanda

**Como** operador de red, **quiero** identificar los días y horas de máximo consumo, **para** entender cuándo la red está más exigida.

**Criterios de aceptación:**

- Se listan los periodos de mayor demanda por región.
- Se muestran en una visualización que permita ubicarlos en el tiempo.

### HU-05. Pronóstico de la demanda

**Como** operador de red, **quiero** una estimación de la demanda futura con su error asociado, **para** apoyar la planificación a corto plazo.

**Criterios de aceptación:**

- El modelo se evalúa sobre un periodo de prueba con MAE, RMSE y MAPE.
- Se compara contra un modelo base y se explica la diferencia.

### HU-06. Reproducibilidad

**Como** estudiante o investigador, **quiero** reproducir el análisis desde cero, **para** validar los resultados o reutilizarlos.

**Criterios de aceptación:**

- Los pasos de instalación, descarga de datos y ejecución están en la [guía de usuario](https://claude.ai/chat/09_guia_usuario.md).
- Los notebooks se ejecutan en orden sin errores.

---

## Trazabilidad con los objetivos

|Historia|Objetivo específico relacionado|
|---|---|
|HU-01|Identificar patrones por hora del día, día de la semana y mes del año|
|HU-02|Estudiar la estacionalidad y la tendencia de largo plazo|
|HU-03|Comparar el comportamiento de las distintas regiones|
|HU-04|Detectar los periodos de máxima demanda|
|HU-05|Pronóstico de la demanda (método)|
|HU-06|Repositorio ordenado, con notebooks y documentación|