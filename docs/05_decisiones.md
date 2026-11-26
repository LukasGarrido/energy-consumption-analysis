<div align="center">

# Decisiones

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [1. Enfoque y alcance](#1-enfoque-y-alcance)
- [2. Datos y limpieza](#2-datos-y-limpieza)
- [3. Pronóstico de referencia](#3-pronóstico-de-referencia)
- [4. Agrupamiento de perfiles diarios](#4-agrupamiento-de-perfiles-diarios)
- [5. Detección de anomalías](#5-detección-de-anomalías)
- [6. Visualización y panel](#6-visualización-y-panel)
- [7. Documentación y reproducibilidad](#7-documentación-y-reproducibilidad)
- [8. Hipótesis contrastadas](#8-hipótesis-contrastadas)
- [9. Pendientes de decisión](#9-pendientes-de-decisión)

---

Fuente única de las decisiones del proyecto (D1 a D44): qué se decidió, por qué, qué se descartó y en qué estado está. Los demás documentos enlazan aquí en lugar de repetirlas. Las decisiones están agrupadas por área y conservan su ID. Las que siguen abiertas se resumen en la [sección 9](#9-pendientes-de-decisión).

Los notebooks se citan con su nombre actual: `01_datos` (exploración y limpieza), `02_patrones` (análisis y agrupamiento), `03_pronostico_anomalias` (modelado y anomalías) y `src/export.py` (exportación).

## 1. Enfoque y alcance

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D9 | Pasar de pronosticar a caracterizar la demanda con agrupamiento y detección de anomalías, el pronóstico es la referencia de lo esperable | La rúbrica pidió un aporte diferencial respecto de los trabajos previos, que pronostican `PJME` con XGBoost | Mantener el proyecto como pronóstico | Aplicada |
| D10 | Sin datos externos (temperatura), las anomalías se interpretan por coincidencia con eventos | El dataset no la incluye y el alcance se limita a los datos de PJM | Incorporar datos meteorológicos | Aplicada |

## 2. Datos y limpieza

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D1 | Calcular el calendario desde `Datetime − 1 h` (día operativo), `Datetime` no se modifica | `Datetime` marca el final de la hora, sin el ajuste la hora 24 de cada día cae en el día siguiente y los perfiles de 24 horas quedan desfasados | Usar `Datetime` directamente | Aplicada en `src/features.py` y en todos los notebooks |
| D2 | Marcar como vacío e interpolar los atípicos aislados de una hora: desviación > 50 % del promedio de las horas vecinas, vecinas que difieren ≤ 25 % entre sí y z modificado > 3.5 sobre la desviación respecto del patrón de mes y hora. Actúa en ambos sentidos y marca 3 valores (`AEP` 25,695 MW, `DOM` 1,253 MW y `PJMW` 487 MW) | Son saltos de una sola hora incompatibles con sus vecinas. El z por sí solo marca miles de saltos pequeños, por eso se exige además una desviación grande. Los valores de `PJMW` de 2012-04-01/02 (2,553 y 2,574 MW) no cumplen el criterio | Aplicar el z al MW crudo (marcaría los picos reales) o conservarlos como limitación | Aplicada (`src/cleaning.py`, `01_datos`) |
| D3 | Mantener `NI` y `COMED` como series separadas y documentar la continuidad | Unirlas supone asumir que son la misma serie. El cociente de niveles es 1.00 y se tocan el 2011-01-01 (`02_patrones`), lo que se reporta sin modificar los datos | Unirlas en una sola serie | Aplicada |
| D11 | Limpieza por pasos: promediar duplicados, reindexar a calendario horario, recortar extremos vacíos, interpolar hasta 2 horas y validar | Duplicados y huecos vienen del cambio de horario y todos los huecos son de 2 horas o menos | Eliminar filas incompletas o rellenar huecos largos | Aplicada |
| D12 | Los valores ≤ 0 pasan a vacío y el 0 inicial de `FE` (su primer registro) se recorta | La demanda no puede ser cero y sin dato vecino no se puede estimar | Interpolar el cero inicial | Aplicada |
| D13 | Conservar picos altos continuos y rachas bajas reales (`EKPC` 514 MW, 2013-09-29, madrugada de domingo) | Un extremo real se distingue de un error por su continuidad | Tratar como atípicos todos los valores fuera del IQR | Aplicada |
| D14 | Excluir los días 2018-04-22 y 2018-04-24 de `DEOK` y descartar la lectura de 1,044 MW del 2017-11-05 02:00 (`DIAS_EXCLUIDOS` y `LECTURAS_DESCARTADAS` en `src/config.py`) | En los dos días la demanda cae a menos de la mitad justo en la primera hora y se recupera al empezar el día siguiente, sin cambios en las regiones vecinas. La lectura descartada difiere un 98 % de su duplicada, frente a menos de 7 % en los otros cambios de hora, y no encaja con las horas vecinas. No se conoce la causa | Conservarlos y documentarlos como limitación, o interpolar 24 horas | Aplicada (`src/cleaning.py`, `01_datos`) |
| D15 | Comparar regiones en el periodo común de las 10 vigentes (2013-06-01 → 2018-08-02 en días operativos), `NI` y `PJM_Load` aparte | No hay periodo común a las 12 regiones y la mezcla depende de los años cubiertos | Comparar cada región en todo su historial | Aplicada |
| D16 | Cobertura mínima de 99 % y año completo con al menos 8,700 horas | Evita que un año parcial parezca una caída | Sin umbral | Aplicada |
| D17 | Guardar la limpieza como `<REGION>_clean.parquet` y `consumo_horario.parquet` | Es lo que guarda `01_datos`, el único paso que escribe la limpieza | Mantener dos nombres | Aplicada (`01_datos`; la mención a una función `run_cleaning` inexistente se quitó de `src/cleaning.py`) |

## 3. Pronóstico de referencia

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D5 | Ventana móvil con entrenamiento creciente, 6 pliegues de 12 meses (mínimo 3) | Con 6 pliegues los residuos cubren 2012-08 → 2018-08, que incluye el huracán Sandy, el vórtice polar de 2014 y el frío de 2015 | 3 pliegues | Aplicada (`03_pronostico_anomalias`) |
| D18 | XGBoost a 24 h con calendario, rezagos de 24, 48 y 168 h y medias móviles desplazadas 24 h, sin `anio`, `MW_rel` ni `estacion` | Todo rezago ≥ horizonte evita fuga, `anio` no se extrapola con árboles y `MW_rel` usa el futuro | Incluir `anio` o `MW_rel` | Aplicada |
| D19 | Mantener la partición única (corte 2017-01-01) como referencia junto a la ventana móvil | Permite comparar con los resultados previos | Reemplazarla | Aplicada |
| D20 | Modelos base de 24 y 168 horas | Un modelo complejo solo se justifica si los supera | Un solo base | Aplicada |
| D21 | MASE con la escala del ingenuo estacional de 24 h medida en el entrenamiento | Definición de Hyndman y Koehler | Error relativo contra el base en la prueba | Aplicada |
| D22 | Hiperparámetros por defecto, sin búsqueda | El pronóstico es una referencia, no el producto final | Búsqueda de hiperparámetros | Aplicada |
| D23 | Descartar Prophet, ARIMA/SARIMAX y LSTM | Son lentos y complejos con varias estacionalidades y las redes son menos interpretables | Usarlos como referencia | Aplicada |
| D24 | Pronosticar solo `PJME` | Mayor historial y tamaño, y entrenar por región y pliegue es lento | Un modelo por región | Aplicada |

## 4. Agrupamiento de perfiles diarios

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D6 | Un solo agrupamiento para las 12 regiones | Con perfiles normalizados los tipos son comunes y permite la matriz región por tipo de día | Uno por región | Aplicada |
| D7 | Conservar la hora de la fuente de `COMED` y `NI` (`ALINEAR_HORA_CENTRAL = False`) | El diagnóstico mide +1 h en ambas y 0 en el resto, coherente con hora central dentro de series en hora del este. Un [documento de liquidaciones de PJM](https://www.pjm.com/-/media/markets-ops/settlements/msrs/desc/msrs-customer-report-documentation-hourly-load-data.ashx) publica la carga horaria como «EPT Hour Ending» e incluye `COMED` entre sus zonas, pero no dice expresamente que esa zona venga en hora del este ni describe el conjunto de Kaggle. Sensibilidad medida: alinearlas cambiaría de grupo el 1.33 % de los días y subiría el grupo 1 de 60.4 % a 67.1 % en `COMED` y de 52.3 % a 64.3 % en `NI` (silueta 0.420) | Alinearlas siempre o corregir en la limpieza | Aplicada. La mezcla de tipos de día de `COMED` y `NI` se lee con esa cautela |
| D25 | Perfil de 24 valores divididos entre el promedio del día, solo días completos, magnitud aparte | Compara la forma y no el tamaño | Agrupar en MW | Aplicada |
| D26 | K-medias y Ward con k de 2 a 10, mayor silueta con grupos de al menos 5 % de los días. Se reporta k = 2 | Ganó k = 2 (0.413) y separa temporada fría y verano. Subir k no separa el fin de semana: sus grupos tienen de 25.5 % a 32.9 % de sábados y domingos con k = 3 y de 20.5 % a 32.6 % con k = 4 (28.6 % esperado sin relación), con silueta 0.304 y 0.242 | Justificar un k mayor para separar el fin de semana | Aplicada |
| D27 | Silueta y Ward sobre una muestra de 10,000 días | Escalan de forma cuadrática con unos 45,000 días | Usar todos los días | Aplicada |
| D28 | Cortes de silueta de Kaufman y Rousseeuw: 0.51 (razonable) y 0.26 (débil) | La fuente sitúa 0.26 a 0.50 como estructura débil y 0.51 a 0.70 como razonable. El resultado (0.413, débil) no cambia | Mantener el 0.50 | Aplicada (`SILUETA_RAZONABLE` en `src/config.py`, que usan `src/profiles.py`, `02_patrones` y el panel) |
| D29 | Estabilidad medida entre semillas y entre algoritmos | Entre semillas (`estabilidad_semillas`, `SEMILLAS_ESTABILIDAD`): con 20 semillas, el índice de Rand ajustado frente a la asignación de referencia va de 0.997 a 1.000, cambia de grupo como máximo el 0.08 % de los días, el grupo 1 reúne entre 62.2 % y 62.3 % y la silueta va de 0.408 a 0.414. Entre k-medias y Ward depende de la muestra de Ward: con la semilla 42 el índice es 0.95, y al ajustar Ward sobre las muestras de 20 semillas va de 0.69 a 0.99 (mediana 0.89). Por eso un cambio pequeño en los datos mueve mucho la cifra de una sola semilla (0.82, 0.73 y 0.95 en distintas versiones) | Afirmarla sin medirla | Aplicada (`02_patrones`) |

## 5. Detección de anomalías

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D8 | z modificado con todos los días de la región, con comprobación por estación y opción `Z_POR_ESTACION` | Es simple y comparable. Los atípicos no se concentran en una estación (0.7 % a 1.3 %) | Calcularlo por estación desde el inicio | Aplicada (`03_pronostico_anomalias`) |
| D30 | Residuo = real − predicción, residuo diario con signo en % de la predicción, solo días completos | El signo da la dirección y el % permite comparar épocas | Error absoluto o MW | Aplicada |
| D31 | Umbral \|z\| > 3.5 con sensibilidad a 3, 4 y 5 y comparación por estación y pliegue | Es una convención calibrada para datos normales. Con 3, 3.5, 4 y 5 salen 52, 22, 9 y 2 días | Fijarlo sin comprobar | Aplicada |
| D32 | Contraste con episodios con fuente y verificación, «fuera de rango» distinto de «sin coincidencia», y dirección esperada (frío y calor `alta`, Sandy `baja`) | No hay etiquetas y hay que distinguir lo no detectado de lo no evaluado | Fechas sin fuente | Aplicada, con una sola tabla en `EPISODIOS_CONOCIDOS` (`src/anomalies.py`). Las fuentes se revisaron y se sustituyeron las que no abrían; el episodio de fines de enero de 2014 pasó a los días 24 a 30, los de su fuente. En varios episodios la fuente confirma el día del pico y el intervalo que lo rodea es criterio del proyecto. Las fechas de la tormenta Jonas (22 a 24 de enero de 2016) se verificaron con [NOAA](https://www.noaa.gov/media-release/january-2016-blizzard-ranked-category-4-on-northeast-snowfall-scale); su dirección esperada queda «por verificar» porque no se halló una fuente sobre la demanda de PJM |
| D33 | Anomalías solo para `PJME` | Es la única región con residuos | Repetir para las 12 | Aplicada |

## 6. Visualización y panel

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D4 | Panel solo en Streamlit | Permite una visualización más dinámica, usa el mismo Python del análisis y no requiere licencias | Power BI, que era la opción inicial | Aplicada (`app/streamlit_app.py`) |
| D34 | Seis páginas: resumen, patrones, tipos de día, regiones, anomalías y pronóstico | Cada una responde a P1 a P4 y al panorama | Cinco páginas | Aplicada |
| D35 | Modelo en estrella en CSV UTF-8 con BOM (17 tablas), fechas ISO, Sí/No y nombres sin `%` | Formato legible por cualquier herramienta, y una clave sin su fila en la dimensión haría desaparecer filas al filtrar | Importar parquet | Aplicada (`src/export.py`), con validación de claves al final de la exportación |
| D36 | Gráficos elegidos por tarea y canal perceptual, color secuencial de un matiz y categórico de hasta 8 colores, sin gráficos circulares | Cleveland y McGill ordenan la precisión de los canales | Elegir por costumbre | Aplicada |
| D44 | Filtros por región, fecha y estación, las tablas agregadas no responden a la fecha | La rúbrica los pide y esas tablas no tienen fecha | Todo a nivel horario | Aplicada |

## 7. Documentación y reproducibilidad

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D37 | Las cifras con hora de fin se marcaron «por recalcular» y se borraron las salidas de las secciones afectadas de los notebooks. El análisis, el modelado, el agrupamiento, las anomalías y la exportación se volvieron a ejecutar con el día operativo | D1 las cambia | Dejarlas sin señalar | Aplicada |
| D38 | Verificar las referencias y alinear los umbrales con la fuente | Es una tarea de la issue | Citar sin verificar | Parcial: umbrales de silueta alineados (D28), metadatos de los artículos con DOI comprobados en Crossref y fuentes de los episodios revisadas. Falta contrastar Cleveland et al. (1990) y CRISP-DM, y comprobar en las obras los umbrales y las afirmaciones que se les atribuyen |
| D39 | Quitar `prophet`, añadir `jupyterlab` e `ipykernel`, Streamlit opcional y usar `kaggle` para la descarga | Prophet está descartado, y la guía descarga con el comando `kaggle`; ningún código usa `kagglehub` | `kagglehub`, que no aporta ese comando en las instrucciones | Aplicada |
| D40 | Parámetros en `src/config.py`, semilla 42 y notebooks 01 a 03 en orden | Reproducibilidad | Parámetros dentro de los notebooks | Aplicada |
| D41 | La exportación usa la misma hora que `02_patrones`: la de la fuente | Con D7 no hay alineación en ninguno de los dos | Un parámetro compartido | Aplicada. Si se cambiara D7, `src/export.py` tendría que aplicar la misma alineación |
| D42 | STL con `period=365` y sin interpretar el tramo final de la tendencia | Años bisiestos y efecto de borde | Interpretar la subida final | Aplicada |
| D43 | Festivos federales de EE. UU. con `holidays` | Criterio uniforme para las 12 regiones | Festivos estatales | Aplicada |

## 8. Hipótesis contrastadas

| Hipótesis | Resultado | Decisión |
|---|---|---|
| Las horas faltantes son cambios de horario | Confirmada en 208 de 217: 03:00 en primavera (126) y 02:00 en otoño (82). Quedan 9 sin causa horaria: el 2010-12-10 en 7 regiones y 2 de `AEP` | D1, D11 |
| El 0 de `FE` es un error | Confirmada: es su primer registro | D12 |
| El mínimo de `EKPC` es un error | Descartada: es una racha de varias horas en la madrugada de un domingo | D13 |
| `COMED` está desfasada una hora | Confirmada (error 0.014 con +1 h frente a 0.024), pero coherente con hora central dentro de series en hora del este. No se corrigió | D7 |
| `NI` y `COMED` son la misma zona | Soportada: cociente de 1.00 y empalme el 2011-01-01 | D3 |
| `PJMW` continúa a `PJM_Load` | Descartada: cociente 0.17. `PJM_Load` → `PJME` es compatible (1.05) | D3, D15 |
| La tendencia STL sube al final | Descartada: efecto de borde | D42 |
| El agrupamiento separará laborables y fines de semana | Descartada: con k = 2 los grupos son estacionales (28.9 % y 28.1 % de fines de semana) y con k = 3 o 4 tampoco aparece un grupo de fin de semana | D26 |
| XGBoost supera al base en todos los pliegues | Confirmada: 6 de 6, MASE de 0.72 a 0.87 | D5, D21 |
| Los atípicos se concentran en una estación o pliegue | Descartada: de 0.7 % a 1.3 % por estación y de 0.5 % a 1.9 % por pliegue | D8, D31 |
| Los episodios documentados aparecen como atípicos | Parcial: 5 de 8 evaluados, con el signo esperado en los 5 | D32 |
| Las filas cuadran | 1,090,167 − 1 − 39 + 217 − 1 − 48 = 1,090,295 | D11, D14 |

## 9. Pendientes de decisión

**Decisiones abiertas**

Ninguna.

**Tareas de cierre**

- **Hora de las series (D1 y D7):** PJM publica la carga como hora de fin en EPT (horas 1 a 24), lo que respalda D1. Falta una confirmación expresa de que `COMED` y `NI` vienen en hora del este en este conjunto de datos.
- **Reproducibilidad:** que un tercero siga la guía de usuario.

