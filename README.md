# Análisis visual de la demanda eléctrica horaria de la red PJM: tipos de día, regiones y episodios atípicos

---

## Resumen

Se propone un análisis visual de la demanda eléctrica horaria de 12 regiones de la red PJM (Estados Unidos, 1998–2018), apoyado en aprendizaje automático para extraer información que las visualizaciones por sí solas no entregan. El proyecto responde cuatro preguntas concretas: qué **tipos de día** existen en la demanda, en qué se diferencian las **regiones**, qué **días se desvían de lo esperable** y cuándo falla un pronóstico a 24 horas. Los perfiles diarios se agrupan con técnicas de agrupamiento, los días atípicos se detectan a partir de los residuos de un modelo de pronóstico, y los resultados se comunican en un panel interactivo en Power BI cuyo diseño se justifica con principios de percepción visual. El aporte diferencial respecto de los trabajos previos revisados, centrados en pronosticar una sola región, es la caracterización comparada de las 12 regiones con un tratamiento documentado de la calidad de los datos.

---

## 1. Contexto y problema

### 1.1 Contexto

El pronóstico de la demanda eléctrica es un problema fundamental desde los inicios de la industria eléctrica (Hong y Fan, 2016), y de él dependen la operación y la planificación de las empresas del sector. PJM Interconnection es una organización regional de transmisión que opera la red de todo o parte de 13 estados del este de EE. UU. y Washington D.C. (Mulla, 2018) y publica su demanda horaria en megavatios (MW).

La demanda horaria es una serie con estructura en varias escalas de tiempo a la vez: un ciclo diario (valle de madrugada y pico por la tarde-noche), uno semanal (el fin de semana consume menos) y uno anual (picos en verano e invierno). Además, cada región tiene un tamaño y un comportamiento distintos: en los resultados preliminares del proyecto, el consumo medio va de unos 1,464 MW (`EKPC`) a unos 31,478 MW (`PJME`), y algunas regiones tienen su mayor consumo en invierno y otras en verano.

### 1.2 Problema

En los trabajos revisados (sección 2), el dataset *Hourly Energy Consumption* se usa sobre todo para **pronosticar** la demanda de una sola región. Estos trabajos prestan menos atención a **caracterizar** cómo es la demanda: qué formas de día existen, cómo se reparten entre regiones y qué días se alejan de lo esperable. Responder estas preguntas exige comparar 12 series con más de un millón de observaciones en total, a varias escalas temporales.

### 1.3 Por qué la visualización es pertinente

La visualización es pertinente por tres razones:

1. **Volumen y estructura.** El dataset limpio tiene 1,090,343 filas (≈ 45,000 días-región). Un resumen numérico por región, como un promedio, oculta la *forma* del consumo a lo largo del día, la semana y el año.
2. **Tareas visuales.** Las preguntas del proyecto son tareas típicas del análisis visual: descubrir patrones cíclicos, comparar formas entre regiones y localizar valores atípicos en el tiempo. Un mapa de calor de hora por día de la semana comunica 168 valores de un vistazo; una tabla equivalente exige leerlos uno a uno.
3. **Decisiones.** Quien planifica o opera una red necesita identificar cuándo y dónde se concentra la demanda. El diseño de cada gráfico, y no solo su contenido, determina si esa lectura es rápida y precisa.

El proyecto se vincula con los resultados de aprendizaje de la asignatura así:

| Resultado de aprendizaje | Cómo se aborda |
|---|---|
| RDA1. Métodos de percepción visual y calidad de los gráficos | Cada gráfico se justifica por el canal de codificación que usa (sección 6) |
| RDA2. Selección de gráficos adecuados | Cada pregunta se asocia a una tarea y a un gráfico, con criterios explícitos (secciones 6 y 7) |
| RDA3. Examinar los datos con técnicas visuales | Exploración visual inicial de calidad, cobertura y distribución (sección 5) |

### 1.4 Preguntas de investigación

| N.º | Pregunta | Tarea visual |
|---|---|---|
| P1 | ¿Qué tipos de día (formas de perfil diario) existen en la demanda de PJM y cómo se distribuyen en el calendario? | Descubrir patrones |
| P2 | ¿En qué se diferencian las regiones por su mezcla de tipos de día y por su estacionalidad? | Comparar |
| P3 | ¿Qué días se desvían de la demanda esperable y a qué episodios corresponden? | Localizar anomalías |
| P4 | ¿Cuándo y cuánto falla un pronóstico a 24 horas, y cómo comunicar ese error? | Evaluar |

### 1.5 Evidencia preliminar que motiva las preguntas

Resultados obtenidos en la fase exploratoria del proyecto (notebooks 01 a 04):

| Hallazgo | Implicación para la propuesta |
|---|---|
| No existe un periodo común a las 12 regiones; 10 de ellas comparten 2013-06-01 → 2018-08-03 | Las comparaciones entre regiones se hacen sobre ese grupo (P2) |
| `Datetime` marca el final de la hora y 29 de las 30 horas faltantes de `PJME` coinciden con cambios de horario | Hay que definir un día operativo (hora 1 a 24) y reglas de limpieza explícitas |
| La forma del día es común (pico entre las 18 y las 20 h), pero hay diferencias: `EKPC` consume más en invierno (razón invierno/verano de 1.20) y varias regiones muestran un segundo pico hacia las 8 h | Hay estructura de "tipos de día" por descubrir (P1, P2) |
| El fin de semana consume entre un 4 % y un 14 % menos que un laborable, y un festivo cerca de un 5 % menos | El calendario explica parte de la variación, pero no toda |
| Un modelo XGBoost reduce el MAE un 19.0 % frente al modelo base de 24 h, con los mayores errores en olas de calor y de frío | Los residuos del modelo son una señal para detectar días atípicos (P3, P4) |
| Los máximos de varias regiones coinciden en episodios concretos (agosto de 2006, julio de 2011, febrero de 2015) | Existen anomalías compartidas entre regiones (P3) |

---

## 2. Antecedentes y aporte diferencial

### 2.1 Trabajos previos con este dataset

| Tipo de trabajo | Qué hace | Límite respecto de este proyecto |
|---|---|---|
| Pronóstico de `PJME` con XGBoost (por ejemplo, Cordova Pou, s. f.; pranavsp108, s. f.) | Construye variables de tiempo y rezagos y entrena un regresor XGBoost sobre `PJME_MW` | Una sola región, el objetivo es la precisión del pronóstico |
| Proyecto con CRISP-DM (panambY, s. f.) | Plantea pronosticar el consumo de los próximos 12 meses y usa XGBoost con validación cruzada | La pregunta es predictiva; no caracteriza patrones |
| Tutorial con Prophet y modelos supervisados (Towards Data Science, s. f.) | Clasifica el consumo diario de `PJME` en cuatro niveles definidos por cuartiles y compara modelos | Una sola serie; los niveles dependen de cuartiles y no de la forma del día |
| Tareas sugeridas en la descripción del dataset (Mulla, 2018) | Predecir el último año y buscar tendencias por hora, festivos y largo plazo | Son tareas generales, sin una metodología ni criterios de evaluación |

### 2.2 Literatura relacionada

- **Agrupamiento de curvas de carga.** Chicco (2012) revisa las técnicas de agrupamiento para patrones de carga eléctrica y evalúa su desempeño con indicadores de validez; concluye que los métodos capaces de aislar los valores atípicos obtienen el mejor desempeño. Este resultado respalda tanto el uso del agrupamiento para descubrir tipos de día como su relación con la detección de anomalías.
- **Visualización de patrones diarios.** van Wijk y van Selow (1999) agrupan los patrones diarios de una serie de consumo eléctrico y los muestran en vistas enlazadas: curvas representativas de cada grupo y un calendario donde cada día se colorea según su grupo.
- **Pronóstico de carga.** Hong y Fan (2016) presentan una revisión de los métodos y las formas de evaluar los pronósticos de carga eléctrica.

### 2.3 Aporte del proyecto

La técnica de agrupar días y mostrarlos en un calendario no es nueva (van Wijk y van Selow, 1999). El aporte de este proyecto es su aplicación y combinación:

1. **De pronosticar a caracterizar.** El pronóstico deja de ser el producto final y pasa a ser una referencia de lo esperable, y el aprendizaje automático (agrupamiento y detección de anomalías) se usa para obtener información sobre la demanda.
2. **Comparación entre 12 regiones con calidad de datos documentada.** Se trata el periodo desigual de las regiones, la convención de hora de fin, los cambios de horario y la continuidad entre regiones (por ejemplo, `NI` termina el 2011-01-01 a las 00:00 y `COMED` empieza a las 01:00, con niveles casi idénticos), aspectos que, hasta donde alcanzó la revisión, no se documentan en esos trabajos.
3. **Diseño de visualización justificado.** Cada vista se asocia a una tarea y a un canal de codificación con fundamento perceptual, y se entrega en un panel interactivo en Power BI.

---

## 3. Objetivos y resultados esperados

### 3.1 Objetivo general

Caracterizar, mediante análisis visual apoyado en aprendizaje automático, los patrones de demanda eléctrica horaria de 12 regiones de la red PJM, identificando tipos de día, diferencias entre regiones y episodios atípicos, y comunicarlos en un panel interactivo.

### 3.2 Objetivos específicos y criterios de logro

| N.º | Objetivo específico | Criterio de logro |
|---|---|---|
| OE1 | Preparar una base horaria regular y documentada | Las 12 regiones superan la validación (fechas sin repetir, una hora entre filas, sin vacíos). *Logrado* |
| OE2 | Identificar tipos de día agrupando los perfiles diarios | Silueta media ≥ 0.50 (estructura razonable); cada grupo con al menos el 5 % de los días; grupos interpretables con el calendario |
| OE3 | Comparar las regiones por su mezcla de tipos de día y su estacionalidad | Cada región queda caracterizada por su distribución de tipos de día y sus indicadores (variabilidad, razón invierno/verano, caída de fin de semana) |
| OE4 | Detectar días atípicos respecto de la demanda esperada | Días con z modificado del residuo > 3.5; al menos una contrastación con episodios externos (olas de calor o frío, huracanes) |
| OE5 | Diseñar y construir un panel interactivo en Power BI | Cada vista justificada por una tarea y un canal perceptual; filtros por región, fecha y estación |

### 3.3 Resultados esperados

| Objetivo | Resultado esperado |
|---|---|
| OE1 | Base limpia en `data/processed/` y documentación de calidad por región *(disponible)* |
| OE2 | Catálogo de tipos de día, con su curva representativa, su frecuencia y su ubicación en el calendario |
| OE3 | Tipología de regiones y matriz región por tipo de día |
| OE4 | Lista de días atípicos con su magnitud y su coincidencia con episodios conocidos |
| OE5 | Panel con cinco páginas: resumen, patrones, tipos de día, regiones y anomalías con pronóstico |

---

## 4. Datos

| Elemento | Detalle |
|---|---|
| Fuente | *Hourly Energy Consumption* (Mulla, 2018), con datos de PJM |
| Contenido | Demanda horaria en MW de 12 regiones, entre 1998-04-01 y 2018-08-03 |
| Volumen | 1,090,167 filas originales; 1,090,343 tras la limpieza |
| Convención horaria | `Datetime` parece marcar el final de la hora en hora del este de EE. UU. (PJM Interconnection, s. f.) |

La calidad de los datos se documentó en la fase exploratoria: sin valores nulos, cobertura de entre 99.98 % y 99.99 %, 40 fechas duplicadas (cambio de horario de otoño) y 217 horas faltantes, casi todas explicadas por los cambios de horario.

---

## 5. Metodología

### 5.1 Fases

| Fase | Actividades | Entregable |
|---|---|---|
| 1. Exploración y calidad | Revisión de estructura, cobertura, duplicados, horas faltantes y valores sospechosos | Notebook 01 *(hecho)* |
| 2. Preparación | Limpieza con reglas explícitas y validación | Notebook 02 y `data/processed/` *(hecho)* |
| 3. Análisis descriptivo | Patrones por hora, día y estación; tendencia; comparación; picos; festivos | Notebook 03 *(hecho)* |
| 4. Pronóstico de referencia | Modelo a 24 h contra modelos base | Notebook 04 *(hecho; se ampliará)* |
| 5. Agrupamiento de perfiles diarios | Construcción de perfiles, selección de k y caracterización | Notebook 05 |
| 6. Detección de anomalías | Residuos del pronóstico en ventana móvil y contraste con episodios | Notebook 06 |
| 7. Visualización | Diseño y construcción del panel en Power BI | Panel |
| 8. Documentación | Informe y conclusiones | Documentación en `docs/` |

### 5.2 Reglas de exploración y preprocesamiento

| Regla | Umbral o criterio | Fundamento |
|---|---|---|
| Comparabilidad entre regiones | Solo se comparan en su periodo común (10 regiones, 2013-06-01 → 2018-08-03) | Derivado de la cobertura observada |
| Cobertura mínima | Una región se excluye de una comparación si tiene menos del 99 % de las horas de su periodo | Criterio del proyecto; el valor observado es de 99.98 % o más |
| Horas repetidas | Se promedian las lecturas | Cambio de horario de otoño: dos lecturas para una hora |
| Valores imposibles | MW ≤ 0 pasa a vacío | Restricción física: la demanda no puede ser negativa |
| Valores atípicos aislados | Se marcan si el z modificado de su desviación respecto del patrón esperado es > 3.5 y las horas vecinas son normales | Iglewicz y Hoaglin (1993) |
| Valores atípicos altos y continuos | Se conservan | Picos de demanda reales; se distinguen por su continuidad |
| Horas faltantes | Se reindexa a un calendario horario completo | Una serie regular es requisito de rezagos, medias móviles y descomposición |
| Interpolación | Lineal y solo hasta 2 horas seguidas | Todos los huecos observados son de 2 horas o menos |
| Vacíos en los extremos | Se recortan | No hay dato vecino para estimarlos |
| Año completo | Al menos 8,700 horas (99.3 %) | Criterio del proyecto, para evitar que un año parcial parezca una caída |
| Día operativo | Del 01:00 al 24:00 (`Datetime` − 1 h) | Convención de hora de fin |

El z modificado se calcula como 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana (Iglewicz y Hoaglin, 1993).

### 5.3 Diseño analítico

**Agrupamiento de perfiles diarios (P1 y P2).** Cada día de cada región se representa con 24 valores normalizados por el promedio del día, de modo que el agrupamiento capture la *forma* y no el tamaño. La magnitud (consumo medio diario) se analiza aparte. Se compararán k-medias y agrupamiento jerárquico (criterio de Ward) para k entre 2 y 10, siguiendo la práctica de la literatura (Chicco, 2012). Cada grupo se describe con su curva media y su distribución en el calendario, según el esquema de van Wijk y van Selow (1999).

**Pronóstico de referencia y anomalías (P3 y P4).** Se pronostica la demanda a 24 horas con variables de calendario, rezagos y medias móviles desplazadas, usando XGBoost (Chen y Guestrin, 2016) y se compara con modelos base. Para obtener residuos fuera de muestra en todo el historial, la validación se hace en ventana móvil por años. Un día se considera atípico si su residuo diario supera el umbral de z modificado de la sección 5.2.

---

## 6. Plan de visualización

### 6.1 Principios de diseño

- **Canal de codificación según la tarea.** Cleveland y McGill (1984) ordenaron las tareas perceptuales elementales por la precisión con que las personas las realizan: la posición sobre una escala común se juzga con mayor exactitud que la longitud, el ángulo, el área o el color. Su ordenamiento fue replicado con participantes en línea por Heer y Bostock (2010). Por eso las comparaciones precisas usan posición y longitud, y el color se reserva para ver patrones globales o para categorías.
- **Marco de diseño.** Cada vista se define por sus datos, su tarea y su codificación, siguiendo el marco de Munzner (2014).
- **Escalas comparables.** Las vistas en paneles múltiples comparten la escala de color o de eje cuando el objetivo es comparar.
- **Color.** Paleta secuencial de un solo matiz para magnitudes y paleta categórica de pocos colores (k ≤ 8) para los tipos de día.
- **Interacción.** Resumen primero y detalle bajo demanda: filtros por región, fecha y estación, y selección cruzada entre vistas.

### 6.2 Gráficos por pregunta

| Vista | Pregunta y tarea | Datos | Gráfico | Codificación y justificación |
|---|---|---|---|---|
| V1. Patrón semanal-diario | P1. Descubrir patrones | Consumo relativo promedio por día de la semana y hora | Mapa de calor 7 × 24 en paneles múltiples por región | Color secuencial en una matriz de 168 celdas, con la misma escala en todos los paneles. El color es menos preciso que la posición, así que se complementa con V2 |
| V2. Forma de cada tipo de día | P1. Comparar | Curva media de cada grupo y banda de dispersión (percentiles 10 a 90) | Líneas en paneles múltiples | Posición sobre escala común, el canal más preciso, para comparar formas |
| V3. Calendario de tipos de día | P1. Localizar | Grupo asignado a cada día | Mapa de calor de calendario | Color categórico sobre una malla de semanas y días, como en van Wijk y van Selow (1999) |
| V4. Mezcla de tipos de día por región | P2. Comparar | Porcentaje de días de cada grupo por región | Barras apiladas al 100 % | Longitud sobre una línea base común; se evitan los gráficos circulares, que dependen de ángulo y área |
| V5. Comparación de regiones | P2. Resumir | Variabilidad, razón invierno/verano, caída de fin de semana | Gráfico de dispersión con etiquetas | Posición en dos ejes comunes |
| V6. Tendencia y estacionalidad | P1. Descubrir | Media móvil de 365 días y descomposición STL | Líneas en paneles múltiples con eje de tiempo compartido | Posición sobre escala común |
| V7. Días atípicos | P3. Localizar | Residuo diario y marca de atipicidad | Línea de tiempo con puntos resaltados y anotaciones de eventos | Se resaltan pocos puntos con color; el perfil real y el esperado del día se muestran bajo demanda |
| V8. Pronóstico y error | P4. Evaluar | Real frente a pronóstico, y error por hora, mes y tipo de día | Líneas y barras | Posición y longitud sobre escalas comunes |
| V9. Calidad de los datos | Verificar | Cobertura por región y horas faltantes por año | Barras de intervalos y mapa de calor | Muestran los periodos desiguales, que condicionan las comparaciones |

### 6.3 Herramientas y estructura del panel

El procesamiento, el agrupamiento y los modelos se desarrollan en Python. Los resultados (perfiles, grupos, residuos y métricas) se exportan como tablas a `data/processed/` para ser consumidos desde **Power BI**, donde se construye el panel interactivo. El panel tiene cinco páginas:

1. **Resumen:** indicadores principales y filtros globales.
2. **Patrones:** V1, V6 y V9.
3. **Tipos de día:** V2 y V3.
4. **Regiones:** V4 y V5.
5. **Anomalías y pronóstico:** V7 y V8.

---

## 7. Criterios para seleccionar métodos y modelos

### 7.1 Agrupamiento (P1 y P2)

| Criterio | Regla de decisión | Fundamento |
|---|---|---|
| Número de grupos (k) | Se elige el k con mayor silueta media entre 2 y 10 | Silueta (Rousseeuw, 1987) |
| Calidad de la estructura | Silueta media ≥ 0.50: estructura razonable. Entre 0.26 y 0.50: estructura débil, se reporta como tal | Kaufman y Rousseeuw (1990) |
| Tamaño de los grupos | Ningún grupo con menos del 5 % de los días | Criterio del proyecto, para evitar grupos no interpretables |
| Estabilidad | La solución debe mantenerse al repetir el agrupamiento con distintas semillas | Verificación de robustez |
| Elección entre algoritmos | Mayor silueta media con grupos interpretables con el calendario | Chicco (2012) |

### 7.2 Pronóstico (P3 y P4)

| Criterio | Regla de decisión | Fundamento |
|---|---|---|
| Métricas | MAE como principal; RMSE para los picos; MAPE para comparar entre regiones | Hyndman y Koehler (2006) |
| Referencia | Se exige superar al modelo de "mismo valor de ayer a la misma hora" | Hyndman y Athanasopoulos (2021) |
| Error escalado | MASE < 1: el modelo supera al pronóstico ingenuo | Hyndman y Koehler (2006) |
| Validación | Ventana móvil con al menos 3 pliegues; el modelo elegido debe superar al base en todos | Evita depender de una sola partición |
| Selección | Menor MAE medio entre los modelos que cumplen las reglas anteriores | Criterio del proyecto |
| Fuga de datos | Todo rezago es mayor o igual al horizonte | Se verifica por código |

### 7.3 Anomalías (P3)

| Criterio | Regla de decisión | Fundamento |
|---|---|---|
| Umbral | z modificado del residuo diario > 3.5 | Iglewicz y Hoaglin (1993) |
| Validación | Contraste con episodios externos (olas de calor o frío, huracanes) y reporte de cuántos se recuperan | Los datos no traen etiquetas de anomalías |

### 7.4 Gráficos

| Criterio | Regla |
|---|---|
| Ajuste a la tarea | Cada gráfico responde a una tarea definida (descubrir, comparar, localizar, evaluar) |
| Precisión | Se usa el canal más preciso disponible para la tarea (Cleveland y McGill, 1984) |
| Legibilidad | Número limitado de categorías, escalas comparables y sin solapamientos |
| Verificación | Revisión del panel con un grupo reducido de compañeros usando tareas definidas (opcional) |

---

## 8. Ventajas y limitaciones frente a soluciones existentes

### 8.1 Comparación

| Solución existente | Ventajas de esta propuesta | Limitaciones de esta propuesta |
|---|---|---|
| Proyectos de pronóstico de `PJME` con XGBoost o Prophet | Cubre 12 regiones, documenta la calidad de los datos y usa el modelo para obtener información (anomalías), no solo precisión | El pronóstico no se afina con búsqueda de hiperparámetros y no usa temperatura, por lo que su precisión no busca competir con ellos |
| Modelos de series de tiempo más complejos (SARIMA, redes LSTM) | Un modelo basado en árboles y variables explícitas es más interpretable y permite explicar los residuos | Puede ser menos preciso que modelos más elaborados |
| Agrupamiento y calendario original (van Wijk y van Selow, 1999) | Aplica la idea a 12 regiones y añade una capa de anomalías basada en un pronóstico y un panel interactivo moderno | No introduce una técnica nueva: el aporte es la aplicación y la combinación |
| Paneles descriptivos de BI sin modelos | Incorpora capas derivadas de aprendizaje automático (tipos de día y anomalías) | Requiere preparar y exportar datos desde Python, lo que añade pasos de mantenimiento |

### 8.2 Limitaciones de la metodología propuesta

- **Sin temperatura.** Es el principal determinante de la demanda y el dataset no la incluye; los episodios atípicos se interpretan por coincidencia con eventos, no se explican con datos meteorológicos.
- **Supuestos del agrupamiento.** K-medias asume grupos compactos con distancia euclidiana, y los perfiles diarios forman en parte un continuo; la estructura puede resultar débil (silueta entre 0.26 y 0.50).
- **Anomalías sin etiquetas.** No hay una verdad de referencia para medir la detección; la validación es por contraste con episodios conocidos.
- **Convención horaria.** La hora de fin desplaza el día de la fila de las 00:00; se corrige con el día operativo, pero depende de que la convención inferida sea correcta.
- **Datos de 2018 o anteriores.** Los patrones pueden no representar la demanda actual.
- **Herramienta propietaria.** El panel depende de Power BI; hay que verificar la licencia necesaria para publicarlo o compartirlo.

---

## 9. Estado actual y plan de trabajo

| Componente | Estado |
|---|---|
| Exploración y calidad de los datos | Hecho (notebook 01) |
| Limpieza y validación | Hecho (notebook 02): 12 de 12 regiones validadas |
| Análisis descriptivo | Hecho (notebook 03) |
| Pronóstico de referencia | Hecho (notebook 04): XGBoost reduce el MAE un 19.0 % frente al modelo base de 24 h |
| Documentación base | En curso |
| Agrupamiento de perfiles diarios | Por hacer |
| Anomalías con validación en ventana móvil | Por hacer |
| Panel en Power BI | Por hacer |

**Cronograma:** `[completar con las fechas del semestre]`

---

## Referencias

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. CRISP-DM Consortium.

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794). ACM. https://doi.org/10.1145/2939672.2939785

Chicco, G. (2012). Overview and performance assessment of the clustering methods for electrical load pattern grouping. *Energy, 42*(1), 68-80. https://doi.org/10.1016/j.energy.2011.12.031

Cleveland, W. S., & McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. *Journal of the American Statistical Association, 79*(387), 531-554. https://doi.org/10.2307/2288400

Cordova Pou, G. (s. f.). *EnergyConsumptionForecast* [Repositorio de GitHub]. https://github.com/gonzalo-cordova-pou/EnergyConsumptionForecast

Heer, J., & Bostock, M. (2010). Crowdsourcing graphical perception: Using Mechanical Turk to assess visualization design. En *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems* (pp. 203-212). ACM.

Hong, T., & Fan, S. (2016). Probabilistic electric load forecasting: A tutorial review. *International Journal of Forecasting, 32*(3), 914-938. https://doi.org/10.1016/j.ijforecast.2015.11.011

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/

Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting, 22*(4), 679-688.

Iglewicz, B., & Hoaglin, D. C. (1993). *How to detect and handle outliers*. ASQC Quality Press.

Kaufman, L., & Rousseeuw, P. J. (1990). *Finding groups in data: An introduction to cluster analysis*. Wiley.

Mulla, R. (2018). *Hourly Energy Consumption* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption

Munzner, T. (2014). *Visualization analysis and design*. CRC Press.

panambY. (s. f.). *Hourly_Energy_Consumption* [Repositorio de GitHub]. https://github.com/panambY/Hourly_Energy_Consumption

PJM Interconnection. (s. f.). *MSRS report format documentation: Hourly load data*. https://www.pjm.com/-/media/markets-ops/settlements/msrs/desc/msrs-customer-report-documentation-hourly-load-data.ashx

pranavsp108. (s. f.). *time-series-forcasting* [Repositorio de GitHub]. https://github.com/pranavsp108/time-series-forcasting

Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics, 20*, 53-65.

*Towards Data Science.* (s. f.). *How to forecast time series data using any supervised learning model* [Artículo en línea]. https://towardsdatascience.com/how-to-forecast-time-series-data-using-any-supervised-learning-model-02dd62cd4bda

van Wijk, J. J., & van Selow, E. R. (1999). Cluster and calendar based visualization of time series data. En *Proceedings of the IEEE Symposium on Information Visualization (InfoVis '99)* (pp. 4-9). IEEE.

### Qué respalda cada referencia

| Referencia | Afirmación que respalda |
|---|---|
| Hong y Fan (2016) | Importancia del análisis y pronóstico de carga; revisión de métodos |
| Mulla (2018); PJM Interconnection (s. f.) | Descripción del dataset y convención de hora de fin |
| Cordova Pou; pranavsp108; panambY; Towards Data Science | Trabajos previos con el dataset |
| Chicco (2012) | Agrupamiento de curvas de carga y desempeño de los métodos |
| van Wijk y van Selow (1999) | Agrupamiento de perfiles diarios con vista de calendario |
| Cleveland y McGill (1984); Heer y Bostock (2010) | Precisión relativa de los canales visuales |
| Munzner (2014) | Marco de datos, tarea y codificación para diseñar vistas |
| Rousseeuw (1987); Kaufman y Rousseeuw (1990) | Silueta y su interpretación |
| Iglewicz y Hoaglin (1993) | Umbral de z modificado para valores atípicos |
| Hyndman y Koehler (2006); Hyndman y Athanasopoulos (2021) | Métricas de error, MASE y pronóstico ingenuo como referencia |
| Chen y Guestrin (2016) | Algoritmo de pronóstico |
| Chapman et al. (2000) | Estructura por fases del proyecto |

---

## Documentación

La documentación del proyecto se encuentra organizada en el directorio [`docs/`](docs/00_indice.md):

- [Índice de Documentación](docs/00_indice.md)
- [01. Objetivo del Análisis](docs/01_objetivo.md)
- [02. Base de Datos (Dataset)](docs/02_base_de_datos.md)
- [03. Métodos y Herramientas](docs/03_metodos_y_herramientas.md)
- [04. Metodología para el Desarrollo](docs/04_metodologia_desarrollo.md)
- [05. Resultados Esperados](docs/05_resultados_esperados.md)
- [06. Plan del Proyecto](docs/06_plan_proyecto.md)
- [07. Casos de Uso](docs/07_casos_de_uso.md)
- [08. Documentación del Modelo](docs/08_modelo.md)
- [09. Guía de Usuario](docs/09_guia_usuario.md)
- [10. Referencias](docs/10_referencias.md)

---

## Estructura del Repositorio

```text
├── app/
│   └── streamlit_app.py          # Aplicación o dashboard interactivo (Streamlit)
├── data/
│   ├── raw/                      # Datos crudos (.gitkeep; excluidos por .gitignore)
│   └── processed/                # Datos procesados y limpios para análisis (.gitkeep)
├── docs/                         # Documentación técnica modular (compatible con Obsidian)
│   ├── 00_indice.md              # Índice general de la documentación
│   ├── 01_objetivo.md            # Objetivos del análisis
│   ├── 02_base_de_datos.md       # Descripción y metadatos del dataset
│   ├── 03_metodos_y_herramientas.md # Herramientas, tecnologías y métodos
│   ├── 04_metodologia_desarrollo.md # Metodología y fases del proyecto
│   ├── 05_resultados_esperados.md # Entregables y expectativas
│   ├── 06_plan_proyecto.md       # Alcance, cronograma, recursos y riesgos
│   ├── 07_casos_de_uso.md        # Historias de usuario y criterios de aceptación
│   ├── 08_modelo.md              # Especificaciones y métricas del modelo
│   ├── 09_guia_usuario.md        # Guía paso a paso de uso y reproducción
│   └── 10_referencias.md         # Bibliografía y referencias bibliográficas
├── notebooks/                    # Cuadernos Jupyter en orden de ejecución
│   ├── 01_exploracion.ipynb      # Exploración inicial (EDA) y calidad de datos
│   ├── 02_limpieza.ipynb         # Limpieza y tratamiento de series de tiempo
│   ├── 03_analisis.ipynb         # Análisis de patrones, estacionalidad y regiones
│   └── 04_modelado.ipynb         # Modelado y pronóstico de demanda
├── reports/
│   ├── figures/                  # Figuras y gráficos exportados
│   └── templates/                # Plantillas y formatos de informes (PDF, documentos)
├── src/                          # Módulos Python reutilizables
│   ├── __init__.py               # Inicialización del paquete
│   ├── cleaning.py               # Limpieza de datos
│   ├── config.py                 # Configuración del proyecto
│   ├── data_loader.py            # Funciones de carga y lectura de datos
│   ├── features.py               # Extracción e ingeniería de características
│   ├── modeling.py               # Entrenamiento, evaluación y métricas de modelos
│   └── plots.py                  # Utilidades y funciones de graficado
├── .gitignore                    # Configuración de exclusiones de Git
├── AGENTS.md                     # Directrices para agentes de IA y colaboradores
├── LICENSE                       # Licencia del proyecto
├── pyproject.toml                # Configuración de empaquetado del proyecto
├── README.md                     # Descripción general del repositorio
└── requirements.txt              # Dependencias del proyecto
```

