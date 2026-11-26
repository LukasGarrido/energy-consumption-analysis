<div align="center">

# Proyecto

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [Problema](#problema)
- [Preguntas de investigación](#preguntas-de-investigación)
- [Objetivo general](#objetivo-general)
- [Objetivos y estado](#objetivos-y-estado)
- [Alcance](#alcance)
- [Partes interesadas e historias de usuario](#partes-interesadas-e-historias-de-usuario)
- [Riesgos](#riesgos)
- [Presupuesto](#presupuesto)

---

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

## Objetivos y estado

Una sola tabla reúne el criterio de logro de cada objetivo, su estado y el resultado obtenido. Los detalles y las cifras completas están en [04_modelo_y_resultados.md](04_modelo_y_resultados.md).

| N.º | Objetivo | Criterio de logro | Estado y resultado |
|---|---|---|---|
| OE1 | Preparar una base horaria regular y documentada | Las 12 regiones superan la validación (fechas sin repetir, una hora entre filas, sin vacíos) y las filas finales cuadran (1,090,295) | **Cumplido.** 1,090,295 filas: se descartó 1 lectura errónea, se unificaron 39 duplicados, se interpolaron 220 horas (217 faltantes y 3 atípicos aislados, 0.02 %), se recortó 1 fila y se excluyeron 2 días de `DEOK` (48 horas) |
| OE2 | Identificar tipos de día agrupando los perfiles diarios | Silueta media reportada (desde 0.51, razonable; de 0.26 a 0.50, débil), cada grupo con al menos el 5 % de los días y grupos interpretables con el calendario | **Cumplido con salvedad.** 2 tipos de día estacionales (temporada fría 62.3 % y verano 37.7 %), silueta 0.413 (débil). No separan laborables de fines de semana |
| OE3 | Comparar las regiones por su mezcla de tipos de día y su estacionalidad | Cada región caracterizada por su distribución de tipos de día (historial completo y periodo común) y por indicadores de variabilidad, razón invierno/verano y caída de fin de semana | **Cumplido** (`02_patrones.ipynb`). Variabilidad (CV) de 17 % a 26 %, razón invierno/verano de 0.92 a 1.20, días de verano de 31 % a 45 % |
| OE4 | Detectar días atípicos respecto de la demanda esperada | Días con z modificado del residuo > 3.5, con su magnitud y dirección, y contraste con episodios externos con fuente | **Cumplido** (`03_pronostico_anomalias.ipynb`). 22 días atípicos de `PJME`, 5 episodios con coincidencia y 5 de 5 con el signo esperado |
| OE5 | Diseñar y construir un panel interactivo | Seis páginas (resumen, patrones, tipos de día, regiones, anomalías y pronóstico), cada vista justificada por una tarea y un canal perceptual, y filtros por región, fecha y estación | **Cumplido.** Panel en Streamlit (`app/streamlit_app.py`) con las seis páginas y filtros por región, estación y fecha, alimentado por las 17 tablas de `src/export.py` |
| Referencia | Pronóstico a 24 horas como referencia de lo esperable | Modelo que supera al base en todos los pliegues de una ventana móvil, con MASE menor que 1 | **Cumplido.** Supera al base en los 6 pliegues, MASE de 0.72 a 0.87 (MAE 1,862 MW frente a 2,300 MW del base de 24 h) |
| Reproducibilidad | Un tercero reproduce el análisis con la guía de usuario | Pasos documentados, notebooks ejecutables en orden, semilla fija y parámetros en `src/config.py` | **Por comprobar.** La guía está actualizada, falta que un tercero la siga |

Las decisiones de diseño que condicionan estos objetivos (día operativo, atípicos aislados, `NI` y `COMED`, hora de `COMED`) están en [05_decisiones.md](05_decisiones.md).

## Alcance

**Dentro:** limpieza y documentación de la calidad de los datos, análisis descriptivo con el día operativo, agrupamiento de perfiles diarios de las 12 regiones, pronóstico de referencia a 24 horas con validación en ventana móvil, detección de días atípicos a partir de los residuos fuera de muestra y panel interactivo en Streamlit.

**Fuera:** datos externos (temperatura, precios), análisis en tiempo real, despliegue en producción y búsqueda de hiperparámetros del pronóstico. El pronóstico y la detección de anomalías se hacen solo para `PJME`.

## Partes interesadas e historias de usuario

Formato: *Como* [parte interesada], *quiero* [qué lograr], *para* [motivo].

| Parte interesada | Descripción |
|---|---|
| Analista de planeación energética | Necesita entender cuándo y cuánto se consume para planificar la capacidad |
| Operador de red | Necesita anticipar la demanda y detectar regiones y días con comportamientos distintos |
| Estudiante o investigador | Necesita reproducir y validar el análisis |

Las columnas *Pregunta* y *Objetivo* dan la trazabilidad de cada historia. HU-01 a HU-04 se cumplieron con `02_patrones.ipynb`, ejecutado con el día operativo.

| N.º | Historia | Criterios de aceptación | Pregunta | Objetivo | Estado |
|---|---|---|---|---|---|
| HU-01 | Como analista, quiero ver el consumo por hora del día y día de la semana, para anticipar los momentos de mayor demanda | Mapa de calor por región, se indica en qué horas y días se concentra el consumo | P1 | OE3 | Cumplida: mínimo a las 3–4 h y máximo a las 17–19 h |
| HU-02 | Como analista, quiero conocer la estacionalidad y la tendencia, para distinguir los efectos estacionales de la evolución de largo plazo | Gráficos de consumo por mes y de tendencia, meses de mayor y menor consumo | P1 | OE3 | Cumplida: dos máximos anuales y tendencia estable o a la baja |
| HU-03 | Como operador, quiero comparar el consumo entre regiones, para identificar cuáles tienen más variabilidad y cómo reparten sus tipos de día | Comparación sobre un periodo común, diferencias y similitudes señaladas, y mezcla de tipos de día por región | P2 | OE3 | Cumplida |
| HU-04 | Como operador, quiero identificar los días y horas de máximo consumo, para entender cuándo la red está más exigida | Máximos por región y su ubicación en el tiempo | P1 | OE3 | Cumplida |
| HU-05 | Como operador, quiero conocer cuándo y cuánto falla un pronóstico a 24 horas, para saber cuánto confiar en él | MAE, RMSE, MAPE y MASE comparados con un modelo base, en una ventana móvil de al menos 3 pliegues, y error por hora, mes y tipo de día | P4 | Referencia | Cumplida: MASE 0.86 y 6 pliegues superados |
| HU-06 | Como investigador, quiero reproducir el análisis desde cero, para validar los resultados | Pasos documentados en la guía de usuario, notebooks ejecutables en orden (01 a 03), semilla fija y parámetros en `src/config.py` | Transversal | OE1 | Parcial: la guía está actualizada, falta que un tercero la compruebe |
| HU-07 | Como analista, quiero ver qué tipos de día existen y cuándo ocurre cada uno, para entender las formas de la demanda más allá de laborable y fin de semana | Grupos con silueta reportada, curva de cada grupo con su banda de dispersión y su ubicación en el calendario | P1 | OE2 | Cumplida con salvedad: 2 tipos estacionales, silueta 0.413 (débil). No distingue laborable de fin de semana |
| HU-08 | Como operador, quiero ver qué días se desvían de lo esperable, para identificar episodios de demanda inusual | Lista de días con z modificado > 3.5, su magnitud y dirección, y contraste con episodios conocidos con fuente | P3 | OE4 | Cumplida: 22 días y 5 episodios coincidentes |
| HU-09 | Como analista, quiero explorar los resultados en un panel interactivo, para filtrar por región, fecha y estación sin programar | Panel de seis páginas con filtros por región, fecha y estación | P1 a P4 | OE5 | Cumplida: panel en Streamlit con seis páginas y filtros. No tiene selección cruzada entre vistas |
| HU-10 | Como analista, quiero tablas con un modelo de datos coherente, para construir el panel sin reprocesar los datos | Dimensiones y hechos con claves sin huérfanos, y diccionario de datos | P1 a P4 | OE5 | Cumplida: 17 tablas, diccionario de 109 columnas y validación de claves en `src/export.py`, que se detiene si alguna clave no tiene su fila en la dimensión |

## Riesgos

| Riesgo | Impacto | Mitigación | Estado |
|---|---|---|---|
| Las regiones cubren periodos distintos | Comparaciones poco justas | Comparar las 10 regiones vigentes en su periodo común | Se materializó y está mitigado |
| Horas duplicadas o faltantes por cambios de horario | Errores en agregaciones y en el modelo | Limpieza con reglas y validación | Se materializó y está resuelto |
| Horas faltantes sin causa horaria (2010-12-10 en 7 regiones, más 2 de `AEP`) | Pequeño | Se interpolan como el resto | Aceptado, falla común de la fuente por confirmar |
| La convención de hora de fin desplaza el día de la fila de las 00:00 | Pequeño (1 de cada 24 horas) | Día operativo (D1) en `features.py` | Resuelto: el análisis, el modelado, el agrupamiento y la exportación se ejecutaron con el día operativo |
| Las cifras publicadas (horas, fin de semana, pronóstico) quedaron desactualizadas | Medio | Reemplazarlas tras repetir los notebooks | Cerrado |
| Atípicos aislados en `AEP`, `DOM` y `PJMW` | Pequeño | Se marcan como vacío y se interpolan en la limpieza (D2) | Resuelto |
| `DEOK` con dos días erróneos (2018-04-22 y 2018-04-24) y una lectura duplicada inconsistente (2017-11-05) | Pequeño | Se excluyen los dos días y se descarta la lectura (D14) | Resuelto |
| Máximo de `AEP` (2008-10-20) inusual | Pequeño | Se trata como atípico aislado (D2), sin contraste con la fuente | Resuelto |
| La hora de `COMED` y `NI` llega una hora más tarde que el resto | Medio: la mezcla de tipos de día de esas dos regiones depende de la alineación | Medido en `02_patrones.ipynb` (+1 h) y su efecto cuantificado: alinearlas cambiaría de grupo el 1.33 % de los días y subiría el grupo 1 de 60.4 % a 67.1 % en `COMED` y de 52.3 % a 64.3 % en `NI` (silueta 0.420). Se conserva la hora de la fuente (D7) | Aceptado y reportado |
| La estructura de los grupos resulta débil | Medio | Reportarla como tal y apoyarla con el calendario | Se materializó (silueta 0.413), reportada |
| Con k = 2 los tipos de día solo capturan la estación y no el fin de semana | Medio: P1 queda respondida solo en parte | Se reporta como limitación: con k = 3 o 4 tampoco se separa el fin de semana (D26) | Aceptado y reportado |
| Los nombres de los grupos exportados al panel podrían seguir siendo los automáticos («G1 · Invierno · mixto») | Pequeño | `02_patrones` guarda «Temporada fría» y «Verano», y `src/export.py` los exporta así en `dim_tipo_dia.csv` | Cerrado |
| Entrenar un modelo por región y pliegue es lento | Medio | Empezar con `PJME` (6 modelos en la ventana móvil) y ampliar a las demás | Abierto |
| Las anomalías solo se evalúan en `PJME`, la única región con residuos | Medio | Documentarlo, repetir el pronóstico con otras regiones si hay tiempo (D33) | Abierto |
| Fechas de episodios sin fuente | Pequeño | Cada episodio lleva su fuente y una marca de verificación (D32). Solo queda sin definir la dirección esperada de la tormenta Jonas | Mitigado |
| El pronóstico falla en olas de calor y de frío por no usar temperatura | Medio | Documentarlo como limitación, los residuos se usan para detectar anomalías | Abierto |
| Tablas del panel con errores de exportación (`pronostico_horario`, `indicadores_region`) | Medio: el panel muestra cifras distintas de las de los notebooks | `src/export.py` usa el día operativo y el periodo común, y valida las claves | Resuelto |

## Presupuesto

Sin costo económico: las librerías son de código abierto y el dataset es de acceso libre.

