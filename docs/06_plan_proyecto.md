# Plan del proyecto

---

## 1. Objetivos y alcance

Los objetivos del proyecto se detallan en [01_objetivo.md](https://claude.ai/chat/01_objetivo.md). En resumen, se busca analizar el consumo eléctrico horario de la red PJM Interconnection para identificar patrones de demanda y diferencias entre regiones, y comunicar los hallazgos mediante visualizaciones.

### Dentro del alcance

- Exploración, limpieza y documentación de la calidad de los datos.
- Análisis de patrones por hora, día de la semana y mes.
- Estudio de estacionalidad y tendencia de largo plazo.
- Comparación entre regiones y detección de periodos de máxima demanda.
- Visualizaciones estáticas e interactivas.
- Modelo de pronóstico de la demanda.

### Fuera del alcance

- Incorporación de datos externos (por ejemplo, temperatura o precios de energía).
- Análisis en tiempo real o despliegue en producción.
- Datos posteriores a los incluidos en el dataset.

---

## 2. Métricas de evaluación

Se definen dos tipos de métricas: las del proyecto y las del modelo de pronóstico.

### 2.1 Métricas del proyecto

| Criterio                          | Cómo se verifica                                                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Datos limpios y documentados      | Existe un resumen de calidad por región (rango de fechas, nulos, duplicados, horas faltantes)                     |
| Patrones temporales identificados | Se describen los patrones por hora, día de la semana y mes, con su gráfico correspondiente                        |
| Comparación entre regiones        | Hay al menos una visualización y una interpretación comparativa                                                   |
| Visualizaciones completas         | Se entregan gráficos estáticos e interactivos que comunican los hallazgos                                         |
| Reproducibilidad                  | Un tercero puede reproducir el análisis siguiendo la [guía de usuario](https://claude.ai/chat/09_guia_usuario.md) |

### 2.2 Métricas del modelo de pronóstico

|Métrica|Descripción|
|---|---|
|MAE|Error absoluto medio, en MW|
|RMSE|Raíz del error cuadrático medio, en MW; penaliza más los errores grandes|
|MAPE|Error porcentual absoluto medio; facilita comparar entre regiones|

Los modelos se evaluarán sobre un periodo de prueba que no se use en el entrenamiento y se compararán contra un modelo base sencillo. El diseño completo se documenta en [08_modelo.md](https://claude.ai/chat/08_modelo.md).

---

## 3. Recursos

### 3.1 Herramientas

|Herramienta|Uso|
|---|---|
|Python (pandas, NumPy, Matplotlib, Seaborn, Plotly)|Procesamiento, análisis y visualización|
|Jupyter Notebook|Desarrollo y documentación del análisis|
|VS Code y Antigravity IDE|Edición de código|
|GitHub|Control de versiones y gestión del código|
|Obsidian|Documentación técnica y registro de decisiones|

### 3.2 Datos

Dataset _Hourly Energy Consumption_ (Kaggle), descrito en [02_base_de_datos.md](https://claude.ai/chat/02_base_de_datos.md).

---

## 4. Cronograma

| Fase                                       | Actividades                                                                 | Fechas        | Entregable                                      |
| ------------------------------------------ | --------------------------------------------------------------------------- | ------------- | ----------------------------------------------- |
| 1. Comprensión del problema y de los datos | Definir preguntas de análisis, descargar el dataset y revisar su estructura | `09-10-2026`  | Documento de proyecto y dataset descargado      |
| 2. Exploración y limpieza                  | EDA, tratamiento de nulos, duplicados y horas faltantes                     | `12-10-2026`  | Datos en `data/processed/` y resumen de calidad |
| 3. Análisis                                | Patrones temporales, estacionalidad, tendencia y comparación entre regiones | `[completar]` | Notebook de análisis                            |
| 4. Pronóstico                              | Diseño, entrenamiento y evaluación de modelos                               | `[completar]` | Notebook de modelado y resultados               |
| 5. Visualización                           | Diseño y construcción de gráficos y de la presentación final                | `[completar]` | Visualización final                             |
| 6. Documentación y cierre                  | Conclusiones, informe final y orden del repositorio                         | `[completar]` | Informe final y repositorio                     |

---

## 5. Presupuesto

El proyecto no tiene costo económico: todas las herramientas y librerías son gratuitas o de código abierto, y el dataset es de acceso libre en Kaggle. El recurso principal es el tiempo del equipo.

---

## 6. Riesgos

|Riesgo|Impacto|Mitigación|
|---|---|---|
|Las regiones cubren periodos distintos|Comparaciones poco justas|Comparar sobre rangos de fechas comunes y documentar el rango de cada región|
|Horas duplicadas o faltantes por cambios de horario|Errores en agregaciones y en el modelo|Revisar duplicados y huecos en el EDA y documentar el tratamiento|
|Dependencias difíciles de instalar (por ejemplo, `prophet`)|Retrasos en el entorno|Usar versiones de Python compatibles o prescindir del paquete|
|Poco tiempo para el pronóstico|Resultados incompletos|Empezar con un modelo base sencillo y ampliar solo si hay tiempo|
|Indefinición de la herramienta de visualización|Retrasos en la fase final|Decidirla antes de iniciar la fase de visualización|