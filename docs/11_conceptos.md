Los conceptos de componentes ya implementados (agrupamiento, anomalías, ventana móvil y exportación al panel) describen el diseño aplicado, y sus resultados se documentan en `08_modelo.md` cuando se completen. Las cifras marcadas como «por recalcular» se calcularon con `Datetime` como hora de fin y se actualizan con el día operativo.

## Mapa: qué conceptos usa cada pregunta

| Pregunta | Conceptos principales |
|---|---|
| P1. Tipos de día | Perfil diario, normalización, k-medias, agrupamiento jerárquico, silueta, índice de Rand ajustado, distancia al centroide, mapa de calor de calendario |
| P2. Diferencias entre regiones | Normalización relativa, coeficiente de variación, correlación, mezcla de tipos de día, periodo común, desfase entre regiones |
| P3. Días atípicos | Residuo, validación en ventana móvil, z modificado, MAD, sensibilidad al umbral, validación sin etiquetas |
| P4. Error del pronóstico | Rezagos, fuga de datos, XGBoost, MAE, RMSE, MAPE, MASE, análisis por segmento |

---

### Hora de fin de intervalo (*hour ending*)

**Qué es.** Convención que etiqueta cada hora con el instante en que **termina**: la hora 1 va de 00:00 a 01:00 y la hora 24 es la última del día. PJM la usa en sus reportes.

**En el proyecto.** `Datetime` sigue esta convención. Los indicios: todas las series empiezan a las 01:00 y terminan a las 00:00, en primavera falta la fila de las 03:00 (no la de las 02:00) y en otoño se repite la de las 02:00. El notebook 01 lo comprueba contra la regla del cambio de horario de EE. UU.

**Consecuencias:**

- La fila de las 00:00 es la última hora del día anterior.
- Un «pico a las 19 h» en `Datetime` corresponde al intervalo 18:00–19:00.
- Si el calendario se calcula directamente desde `Datetime`, `dia_semana`, `es_fin_de_semana` y `es_festivo` quedan desplazados un día en la fila de las 00:00 (1 de cada 24 horas). Se corrige con el día operativo.
- Un indicio visible antes de la corrección: entre el 4 % y el 5 % de los días de `COMED` y `NI` tenían su pico en la hora 0, algo poco plausible. Debe desaparecer al recalcular con el día operativo.

### Día operativo

**Qué es.** El día definido según la convención de los datos, no según el calendario civil.

**Cómo funciona.** Se resta una hora a `Datetime` antes de calcular la fecha: la fila de las 00:00 pasa a ser la hora 23 (23:00–24:00) del día anterior, y `hora` va de 0 a 23.

**En el proyecto.** Decisión D1, aplicada en `src/features.py` (columna `fecha`). Es la base de los promedios diarios, de los perfiles del agrupamiento y de los residuos diarios. Las cifras de los notebooks 03 y 04 se recalculan con él.

### Hora local y EPT

**Qué es.** EPT (*Eastern Prevailing Time*) es la hora civil del este de EE. UU., que cambia entre horario estándar y de verano.

**En el proyecto.** Los datos parecen estar todos en EPT, aunque algunas regiones operen en hora central. Falta confirmarlo en la documentación de PJM.

### Desfase entre regiones

**Qué es.** Diferencia de hora entre perfiles que deberían parecerse.

**En el proyecto.** `COMED` aparece retrasada 1 hora (error de 0.014 con ese desplazamiento frente a 0.024 sin él). Es coherente con que todas las series estén en hora del este mientras `COMED`, en la zona de Chicago, opera en hora central. No se corrige en la limpieza. El notebook 05 mide el desfase de cada región y su parámetro `ALINEAR_HORA_CENTRAL` permite restar 1 h a `COMED` y `NI` antes de comparar formas de día (decisión D7).

### Día completo

**Qué es.** Día con sus 24 horas.

**En el proyecto.** Con el día operativo, el primer registro de cada serie (01:00) y el último (00:00) cierran días completos. Aun así se exigen las 24 horas por día y región en los promedios diarios, los perfiles del agrupamiento y los residuos diarios. Los bordes de los pliegues de la ventana móvil sí pueden dejar días incompletos, que se descartan.

### Error de medición frente a valor extremo real

**Qué es.** Un valor extremo puede ser un error del medidor o consumo real. El criterio es la **continuidad**: varias horas seguidas extremas sugieren un evento real, un valor aislado entre horas normales sugiere un error.

**En el proyecto.** Los picos altos forman una nube continua y se conservan. Aislados y sospechosos: el 0 de `FE` (su primer registro, se recorta), `DOM` (1,253 MW) y `PJMW` (487, 2,553 y 2,574 MW), que se conservan hasta aplicar el z modificado (D2). El mínimo de `EKPC` (514 MW) es una racha de varias horas en la madrugada de un domingo: un valle real. El notebook 01 los distingue con el cociente entre el valor y el promedio de sus horas vecinas.

### Periodo común y regiones vigentes

**Qué es.** El periodo común es el intervalo en el que *todas* las regiones comparadas tienen datos: empieza en el inicio más tardío y termina en el final más temprano. Las regiones vigentes son las que llegan hasta el final del dataset.

**En el proyecto.** No existe periodo común a las 12 regiones. Las 10 vigentes comparten 2013-06-01 → 2018-08-03 (días operativos hasta el 2018-08-02), y las comparaciones entre regiones se hacen en ese intervalo.

### Media móvil centrada y efecto de borde

**En el proyecto.** Explica por qué la línea gruesa de las gráficas de tendencia es más corta que la serie, y por qué el tramo final de la tendencia STL de `PJME` no es fiable y no se interpreta.

### Descomposición STL

**En el proyecto.** Se aplica con `period=365` a la serie diaria de `PJME` (solo días completos). La opción `robust=True` reduce la influencia de los valores extremos. La tendencia se movía entre unos 30,500 y 33,300 MW, con su máximo en 2007–2008 y el mínimo en 2016–2017 (por recalcular).

**Cuidado.** El periodo fijo de 365 días ignora los años bisiestos, por lo que el componente estacional es una aproximación.

---

## 7. Agrupamiento de perfiles diarios (aprendizaje no supervisado)

### Silueta

**Cómo se interpreta.** Siguiendo a Kaufman y Rousseeuw, una silueta media de 0.71 a 1.00 indica una estructura fuerte, de 0.51 a 0.70 una estructura razonable, de 0.26 a 0.50 una estructura débil que podría ser artificial, y de 0.25 o menos que no hay estructura sustancial. El proyecto usa estos cortes (`SILUETA_FUERTE = 0.71`, `SILUETA_RAZONABLE = 0.51`, `SILUETA_DEBIL = 0.26`) y reporta como «débil» lo que quede entre 0.26 y 0.50.

**En el proyecto.** Se calcula para cada *k* entre 2 y 10, con k-medias y con Ward, sobre una muestra reproducible de 10,000 días.

### Elección del número de grupos (*k*)

**En el proyecto.** Se prueba cada *k* de 2 a 10 con ambos métodos y se elige la mayor silueta entre las combinaciones en que ningún grupo tiene menos del 5 % de los días.

**Cuidado.** Con frecuencia k = 2 gana en silueta (por ejemplo, laborable frente a fin de semana). Si ocurre, se justifica en el informe un k mayor cuando sus grupos son más interpretables, aunque la silueta baje algo.

### Agrupamiento jerárquico y criterio de Ward

**Cuidado.** Es costoso en memoria con decenas de miles de elementos. Por eso se ajusta sobre una muestra de 10,000 días y el resto se asigna al centro más cercano.

### Estabilidad del agrupamiento

**En el proyecto.** Se mide la concordancia entre k-medias y Ward con el mismo k (índice de Rand ajustado). La repetición con distintas semillas queda por hacer.

### Índice de Rand ajustado (nuevo)

**Qué es.** Medida de cuánto coinciden dos agrupamientos de los mismos elementos, corregida por el azar. Vale 1 si son idénticos y cerca de 0 si no tienen relación, no depende de cómo se numeren los grupos.

**En el proyecto.** Compara k-medias con Ward para el k elegido: un valor alto indica que la solución no depende del algoritmo.

### Distancia al centroide

**En el proyecto.** Es la raíz de la suma de las diferencias al cuadrado, hora a hora, entre el perfil de un día y la curva media de su grupo. El notebook 05 la guarda en `tipos_de_dia.parquet`.

---

## 8. Detección de anomalías

### Residuo diario

**Qué es.** El resumen de los 24 residuos horarios de un día en un solo número.

**En el proyecto.** Es el residuo medio de las 24 horas, **con signo**, en porcentaje de la predicción media del día. El signo permite distinguir los días `alta` (más demanda de la esperable) de los `baja`, y el porcentaje permite comparar épocas con niveles distintos. Solo se usan días completos.

### Umbral de z modificado

**Ejemplo ilustrativo.** Con una mediana del residuo diario de 0.1 % y un MAD de 1.0 punto porcentual, un día con un residuo de +6 % tiene `z = 0.6745 · (6 − 0.1) / 1.0 ≈ 4.0`, mayor que 3.5, así que se marca como `alta`. Las cifras son inventadas para ilustrar el cálculo.

**Cuidado.** El 3.5 se calibró para datos normales (Iglewicz y Hoaglin) y es una convención: un valor más bajo marca más días, con más falsos positivos, uno más alto marca menos, con más falsos negativos.

### Sensibilidad al umbral (nuevo)

**Qué es.** Repetir la detección con varios umbrales (3, 3.5, 4 y 5) para ver cuánto cambia el número de días marcados.

**En el proyecto.** Si el número cambia mucho entre 3.5 y 4, el corte es frágil y se reporta. El notebook 06 también compara la concentración de atípicos por estación y por pliegue, porque un error del modelo desigual produciría atípicos que reflejan al modelo y no al día.

### Validación sin etiquetas

**En el proyecto.** Cada episodio de la tabla del notebook 06 (huracán Sandy, vórtices polares de 2014, frío de 2015, olas de calor de 2013, entre otros) lleva su fuente y una marca de verificación. Se reporta cuántos se recuperan, si la dirección coincide con la esperada (frío y calor: `alta`, Sandy: `baja`) y cuántos atípicos no corresponden a ningún episodio. Los episodios fuera del rango de los residuos (2006 y 2011) se marcan como **fuera de rango**, distinto de **sin coincidencia**. La atribución a eventos sigue siendo una hipótesis sin datos de temperatura.

### Distancia al centroide (complemento)

**En el proyecto.** Una mira el tamaño del error del pronóstico (el nivel) y la otra la forma de la curva: un día puede ser raro en una, en la otra o en ambas. El notebook 06 mide su correlación.

---

## 9. Pronóstico (aprendizaje supervisado)

### División cronológica entrenamiento/prueba

**En el proyecto.** Se entrena con 2002-01-01 → 2016-12-31 y se prueba con 2017-01-01 → 2018-08-03 (cifras por recalcular con el día operativo). Con la hora de fin, el primer día de la prueba empieza en su hora 23 y queda incompleto.

### Validación en ventana móvil (*rolling-origin*)

**Qué es.** Repetir la evaluación con varias particiones cronológicas: el modelo se entrena con el pasado hasta un punto, se evalúa en el periodo siguiente, y el punto de corte avanza para el pliegue siguiente.

**Cómo funciona.** En el proyecto, los pliegues son 6 bloques consecutivos de 12 meses que terminan el 2018-08-03. El entrenamiento crece en cada pliegue (ventana expansiva) y los bloques de prueba no se solapan, de modo que cada hora se predice una sola vez fuera de muestra.

**En el proyecto.** Cumple dos funciones: dar una evaluación más estable que una sola partición (al menos 3 pliegues, y el modelo debe superar al base en todos) y producir residuos fuera de muestra para 2012-08 → 2018-08, que alimentan la detección de anomalías.

**Cuidado.** Exige entrenar un modelo por pliegue (y por región), por lo que se hace con `PJME`. Cada pliegue es un año concreto con su clima.

### Extrapolación de los árboles

**En el proyecto.** Podría explicar por qué, en olas de frío intensas, el modelo base supera a XGBoost en 4 de los 10 peores días (cifra por recalcular). Es una hipótesis que no se verificó.

---

## 10. Métricas de evaluación

### MASE (error absoluto medio escalado)

**Qué es.** El MAE del modelo dividido entre el error del pronóstico ingenuo estacional medido sobre los datos de entrenamiento (Hyndman y Koehler, 2006).

**Cómo funciona.** El denominador es el error absoluto medio de «ayer a la misma hora» en el entrenamiento (`escala_ingenua`, estacionalidad de 24 h). No es lo mismo que dividir entre el MAE del base en la prueba: eso sería un error relativo.

**Cómo se interpreta.** Menor que 1: el modelo supera al pronóstico ingenuo, mayor que 1: lo empeora. No depende de la escala, así que sirve para comparar entre regiones.

**En el proyecto.** Se calcula en el notebook 04 para la partición única y para cada pliegue. Se exige MASE < 1 para XGBoost en todos los pliegues.

---

## 11. Visualización de datos

### Mapa de calor de calendario

**Qué es.** Mapa de calor donde las celdas son los días del año y el color indica una categoría o un valor del día.

**En el proyecto.** Cada fila es un año y cada columna un día del año, y el color indica el tipo de día. Es una variante del esquema de van Wijk y van Selow (1999) y muestra cuándo ocurre cada forma de día.

---

## 12. Herramientas y buenas prácticas

### Notebook de Jupyter

**En el proyecto.** Hay siete, en orden: exploración, limpieza, análisis, modelado, agrupamiento, anomalías y exportación. Todos están implementados.

### Módulo reutilizable y paquete editable

**En el proyecto.** `src/` contiene `config.py` (rutas y parámetros), `data_loader.py`, `cleaning.py`, `features.py`, `modeling.py`, `profiles.py` y `anomalies.py`.

### Modelo en estrella (nuevo)

**Qué es.** Forma de organizar tablas para un panel: **dimensiones** pequeñas, con una fila por valor de un filtro (región, fecha, estación, tipo de día), y **hechos** grandes, con una fila por observación. Cada hecho se relaciona con sus dimensiones por una clave, y un filtro sobre la dimensión actúa en todas las tablas relacionadas.

**En el proyecto.** El notebook 07 genera 4 dimensiones y las tablas de hechos y resultados, y comprueba que no haya claves huérfanas, que aparecerían como filas en blanco en los filtros. Las tablas ya agregadas no responden al filtro de fecha.

### Power BI

**En el proyecto.** Es la herramienta del panel final, de seis páginas. Python genera los CSV (dimensiones, hechos, residuos, tipos de día y anomalías) y Power BI los muestra. Hay que verificar la licencia necesaria para publicarlo o compartirlo.

---

## 13. Glosario de siglas

Cambia la fila de MASE y añade las nuevas:

| Sigla | Significado | Dónde aparece |
|---|---|---|
| MASE | Error absoluto medio escalado | Notebook 04 |
| ARI | Índice de Rand ajustado | Notebook 05 |
| D1 a D8 | Decisiones de diseño del proyecto | `04_metodologia_desarrollo.md` |