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
| D2 | Conservar los atípicos aislados (`DOM` 1,253 MW y `PJMW` 487 MW) y dejar la regla del z modificado de la limpieza por hacer | Son 2 valores en más de 1 M de filas. Los de `PJMW` de 2012-04-01/02 (2,553 y 2,574 MW) no cumplen el criterio de aislado (0.98 y 0.77 frente a sus vecinos). La regla debe aplicarse a la desviación respecto del patrón esperado y no al MW crudo, porque marcaría los picos reales | Implementarla ahora en `cleaning.py` | **Por hacer** (`cleaning.py`, `01_datos`, `02_datos.md`) |
| D3 | Guardar `NI` y `COMED` por separado y documentar la continuidad | Unirlas supone asumir que son la misma serie. El cociente de niveles es 1.00 y se tocan el 2011-01-01 (`02_patrones`), lo que respalda unirlas | Unirlas en una sola serie | **Por confirmar** |
| D11 | Limpieza por pasos: promediar duplicados, reindexar a calendario horario, recortar extremos vacíos, interpolar hasta 2 horas y validar | Duplicados y huecos vienen del cambio de horario y todos los huecos son de 2 horas o menos | Eliminar filas incompletas o rellenar huecos largos | Aplicada |
| D12 | Los valores ≤ 0 pasan a vacío y el 0 inicial de `FE` (su primer registro) se recorta | La demanda no puede ser cero y sin dato vecino no se puede estimar | Interpolar el cero inicial | Aplicada |
| D13 | Conservar picos altos continuos y rachas bajas reales (`EKPC` 514 MW, 2013-09-29, madrugada de domingo) | Un extremo real se distingue de un error por su continuidad | Tratar como atípicos todos los valores fuera del IQR | Aplicada |
| D14 | `DEOK` queda por revisar: 34 atípicos bajos, una racha de 3 horas de 907, 912 y 921 MW (2018-04-22) y dos lecturas de 1,044 y 2,064 MW para la misma hora el 2017-11-05, que la limpieza promedia | Los mínimos son consecutivos pero la lectura duplicada es inconsistente | Descartarla o aceptarla sin revisar | **Por revisar** (se conserva por ahora) |
| D15 | Comparar regiones en el periodo común de las 10 vigentes (2013-06-01 → 2018-08-02 en días operativos), `NI` y `PJM_Load` aparte | No hay periodo común a las 12 regiones y la mezcla depende de los años cubiertos | Comparar cada región en todo su historial | Aplicada |
| D16 | Cobertura mínima de 99 % y año completo con al menos 8,700 horas | Evita que un año parcial parezca una caída | Sin umbral | Aplicada |
| D17 | Guardar la limpieza como `<REGION>_clean.parquet` y `consumo_horario.parquet` | `01_datos` usa ese nombre y `run_cleaning` guarda otro | Mantener ambos nombres | **Por hacer** (cambiar `run_cleaning` para guardar `_clean.parquet`) |

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
| D7 | Conservar la hora de la fuente de `COMED` y `NI`, salvo que `02_patrones` decida alinearlas a hora central (`ALINEAR_HORA_CENTRAL`) | El diagnóstico mide +1 h en ambas y 0 en el resto, coherente con hora central dentro de series en hora del este. Sin alinear, la forma puede separarse por la hora y la comparación con otras regiones podría distorsionarse | Alinearlas siempre o corregir en la limpieza | **Por decidir.** `02_patrones` se ejecutó con `ALINEAR_HORA_CENTRAL = False`, falta repetirlo con `True` y comparar la mezcla de tipos de día |
| D25 | Perfil de 24 valores divididos entre el promedio del día, solo días completos, magnitud aparte | Compara la forma y no el tamaño | Agrupar en MW | Aplicada |
| D26 | K-medias y Ward con k de 2 a 10, mayor silueta con grupos de al menos 5 % de los días, y si gana k = 2 se justifica un k mayor | Evita grupos ininterpretables y el sesgo hacia k = 2. Ganó k = 2 (0.413) y separa temporada fría y verano. Con k = 3 la silueta es 0.30 y con k ≥ 4 queda por debajo de 0.26 | Elegir solo por silueta | **Por decidir:** reportar k = 2 como resultado o justificar un k mayor para separar el fin de semana |
| D27 | Silueta y Ward sobre una muestra de 10,000 días | Escalan de forma cuadrática con unos 45,000 días | Usar todos los días | Aplicada |
| D28 | Cortes de silueta de Kaufman y Rousseeuw: 0.71, 0.51 y 0.26 | En la fuente el 0.50 cae en «débil». Hoy `config.py` y los notebooks usan 0.50 y 0.26, y el resultado (0.413, débil) no cambia con ninguno de los dos | Mantener el 0.50 | **Por decidir:** alinear `config.py`, `profiles.py` y la documentación |
| D29 | Estabilidad con el índice de Rand ajustado entre k-medias y Ward (0.82), la repetición con semillas queda por hacer | Es una medida barata de que el resultado no depende del algoritmo | Afirmarla sin medirla | Parcial: Rand ajustado medido, semillas por hacer |

## 5. Detección de anomalías

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D8 | z modificado con todos los días de la región, con comprobación por estación y opción `Z_POR_ESTACION` | Es simple y comparable. Los atípicos no se concentran en una estación (0.7 % a 1.3 %) | Calcularlo por estación desde el inicio | Aplicada (`03_pronostico_anomalias`) |
| D30 | Residuo = real − predicción, residuo diario con signo en % de la predicción, solo días completos | El signo da la dirección y el % permite comparar épocas | Error absoluto o MW | Aplicada |
| D31 | Umbral \|z\| > 3.5 con sensibilidad a 3, 4 y 5 y comparación por estación y pliegue | Es una convención calibrada para datos normales. Con 3, 3.5, 4 y 5 salen 52, 22, 9 y 2 días | Fijarlo sin comprobar | Aplicada |
| D32 | Contraste con episodios con fuente y verificación, «fuera de rango» distinto de «sin coincidencia», y dirección esperada (frío y calor `alta`, Sandy `baja`) | No hay etiquetas y hay que distinguir lo no detectado de lo no evaluado | Fechas sin fuente | Aplicada. Falta verificar la tormenta Jonas y sincronizar `EPISODIOS_CONOCIDOS` en `src/anomalies.py` |
| D33 | Anomalías solo para `PJME` | Es la única región con residuos | Repetir para las 12 | Aplicada |

## 6. Visualización y panel

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D4 | Panel en Power BI, Streamlit queda como prototipo opcional | Lo pide la rúbrica | Solo Streamlit | Confirmada. Archivo de Power BI por construir |
| D34 | Seis páginas: resumen, patrones, tipos de día, regiones, anomalías y pronóstico | Cada una responde a P1 a P4 y al panorama | Cinco páginas | Aplicada. Falta alinear el README con seis páginas |
| D35 | Modelo en estrella en CSV UTF-8 con BOM (17 tablas), fechas ISO, Sí/No, nombres sin `%` y validación de claves huérfanas | Power BI lo importa sin configuración y una clave huérfana aparece como fila en blanco. La exportación no encontró claves huérfanas | Importar parquet | Aplicada (`src/export.py`) |
| D36 | Gráficos elegidos por tarea y canal perceptual, color secuencial de un matiz y categórico de hasta 8 colores, sin gráficos circulares | Cleveland y McGill ordenan la precisión de los canales | Elegir por costumbre | Aplicada |
| D44 | Filtros por región, fecha y estación, las tablas agregadas no responden a la fecha | La rúbrica los pide y esas tablas no tienen fecha | Todo a nivel horario | Aplicada |

## 7. Documentación y reproducibilidad

| ID | Decisión | Motivo | Alternativa descartada | Estado |
|---|---|---|---|---|
| D37 | Las cifras con hora de fin se marcaron «por recalcular» y se borraron las salidas de las secciones afectadas de los notebooks. El análisis, el modelado, el agrupamiento, las anomalías y la exportación se volvieron a ejecutar con el día operativo | D1 las cambia | Dejarlas sin señalar | Aplicada |
| D38 | Verificar las referencias y alinear los umbrales con la fuente | Es una tarea de la issue | Citar sin verificar | En curso (ver D28) |
| D39 | Quitar `prophet`, añadir `jupyterlab` e `ipykernel`, Streamlit opcional | Prophet está descartado | Dejar las dependencias sin revisar | Parcial: falta elegir entre `kaggle` y `kagglehub` |
| D40 | Parámetros en `src/config.py`, semilla 42 y notebooks 01 a 03 en orden | Reproducibilidad | Parámetros dentro de los notebooks | Aplicada |
| D41 | `ALINEAR_HORA_CENTRAL` con el mismo valor en `02_patrones` y en la exportación | Si difiere, los días de `COMED` y `NI` no coinciden | Archivo compartido | Aplicada |
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
| El agrupamiento separará laborables y fines de semana | Descartada: con k = 2 los grupos son estacionales (28.9 % y 28.1 % de fines de semana) | D26 |
| XGBoost supera al base en todos los pliegues | Confirmada: 6 de 6, MASE de 0.72 a 0.87 | D5, D21 |
| Los atípicos se concentran en una estación o pliegue | Descartada: de 0.7 % a 1.3 % por estación y de 0.5 % a 1.9 % por pliegue | D8, D31 |
| Los episodios documentados aparecen como atípicos | Parcial: 5 de 8 evaluados, con el signo esperado en los 5 | D32 |
| Las filas cuadran | 1,090,167 − 40 + 217 − 1 = 1,090,343 | D11 |

## 9. Pendientes de decisión

**Decisiones abiertas**

- **D3:** unir o no `NI` y `COMED`.
- **D7:** alinear o no `COMED` y `NI` a hora central. Falta repetir `02_patrones` con `ALINEAR_HORA_CENTRAL = True` y comparar la mezcla de tipos de día.
- **D26:** decidir si se reporta k = 2 (silueta 0.413, grupos estacionales) o se justifica un k mayor para separar el fin de semana, y registrarlo aquí.
- **D28:** decidir si se pasan los cortes a 0.51 y 0.71 en `config.py` y `profiles.py`. No cambia el resultado actual.
- **D2:** implementar la regla del z modificado en la limpieza o dejarla como limitación.
- **D14:** revisar `DEOK` con la tabla de valores aislados de `01_datos`.
- **D17:** cambiar `run_cleaning` para guardar `_clean.parquet`.
- **D29:** repetir el agrupamiento con varias semillas.
- **D32:** verificar la tormenta Jonas y sincronizar `EPISODIOS_CONOCIDOS` en `src/anomalies.py`.
- **D39:** elegir entre `kaggle` y `kagglehub`.

**Tareas de cierre**

- **Nombres de los grupos:** aplicar «Temporada fría» y «Verano» a `nombre_grupo` antes de exportar, porque las tablas guardadas y `src/export.py` usan los nombres automáticos «G1 · Invierno · mixto» y «G2 · Verano · mixto».
- **`02_patrones`:** completar los 5 marcadores `[completar]` (decisión D7, justificación de k y tres interpretaciones).
- **`03_pronostico_anomalias`:** la interpretación habla de 15 atípicos sin episodio y el resultado dice 16.
- **`AEP`:** verificar el máximo del 2008-10-20 (25,695 MW).
- **Hora de las series (D1 y D7):** confirmar en la documentación de PJM que todas las series están en hora del este.
- **D34:** alinear el README con seis páginas.
- **Panel (D4, D34):** construir el archivo de Power BI y verificar la licencia.
- **Reproducibilidad:** que un tercero siga la guía de usuario.

