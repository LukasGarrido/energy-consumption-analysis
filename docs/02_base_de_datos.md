# Base de datos (dataset)

## Fuente y contenido

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)
- **Autor:** Rob Mulla
- **Origen de los datos:** sitio web de PJM Interconnection, organización regional de transmisión eléctrica que opera la red de todo o parte de 13 estados del este de EE. UU. y Washington D.C.
- **Contenido:** consumo horario en megavatios (MW), entre 1998-04-01 y 2018-08-03.
- **Regiones:** AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load.
- **Formato:** un archivo CSV por región con las columnas `Datetime` y `<REGION>_MW`, más un archivo combinado (`pjm_hourly_est.csv`) que no se utiliza.
- **Volumen:** 1,090,167 filas en total, entre 32,896 (`PJM_Load`) y 145,366 (`PJME`) por región.

### Periodos distintos por región

Las regiones no cubren los mismos años, por lo que **no existe un periodo común a las 12**:

- `PJM_Load` cubre 1998-04 → 2002-01 y `NI` 2004-05 → 2011-01.
- Las otras 10 regiones llegan hasta 2018-08-03 y se denominan *vigentes*. Comparten el periodo **2013-06-01 → 2018-08-03**.
- `NI` termina en 2011-01 cuando empieza `COMED`, y `PJM_Load` termina en 2002-01 cuando empiezan `PJME` y `PJMW`. Podrían ser la misma zona en periodos consecutivos, pero no está comprobado.

Las comparaciones entre regiones se hacen sobre las 10 vigentes en su periodo común, `NI` y `PJM_Load` se analizan por separado.

---

## Calidad de los datos

Resultados de `01_exploracion.ipynb`. Ninguna región tiene valores nulos y todas tienen una cobertura de entre 99.98 % y 99.99 % de las horas de su periodo.

| Región   | Inicio           | Fin              | Filas   | Duplicados | Horas faltantes | Cobertura (%) | Ceros |
| -------- | ---------------- | ---------------- | ------- | ---------- | --------------- | ------------- | ----- |
| AEP      | 2004-10-01 01:00 | 2018-08-03 00:00 | 121,273 | 4          | 27              | 99.98         | 0     |
| COMED    | 2011-01-01 01:00 | 2018-08-03 00:00 | 66,497  | 4          | 11              | 99.98         | 0     |
| DAYTON   | 2004-10-01 01:00 | 2018-08-03 00:00 | 121,275 | 4          | 25              | 99.98         | 0     |
| DEOK     | 2012-01-01 01:00 | 2018-08-03 00:00 | 57,739  | 4          | 9               | 99.98         | 0     |
| DOM      | 2005-05-01 01:00 | 2018-08-03 00:00 | 116,189 | 4          | 23              | 99.98         | 0     |
| DUQ      | 2005-01-01 01:00 | 2018-08-03 00:00 | 119,068 | 4          | 24              | 99.98         | 0     |
| EKPC     | 2013-06-01 01:00 | 2018-08-03 00:00 | 45,334  | 4          | 6               | 99.99         | 0     |
| FE       | 2011-06-01 01:00 | 2018-08-03 00:00 | 62,874  | 4          | 10              | 99.98         | 1     |
| NI       | 2004-05-01 01:00 | 2011-01-01 00:00 | 58,450  | 0          | 14              | 99.98         | 0     |
| PJM_Load | 1998-04-01 01:00 | 2002-01-01 00:00 | 32,896  | 0          | 8               | 99.98         | 0     |
| PJME     | 2002-01-01 01:00 | 2018-08-03 00:00 | 145,366 | 4          | 30              | 99.98         | 0     |
| PJMW     | 2002-04-01 01:00 | 2018-08-03 00:00 | 143,206 | 4          | 30              | 99.98         | 0     |

---
Casi todo se explica por el cambio de horario de EE. UU. (desde 2007, del segundo domingo de marzo al primer domingo de noviembre antes, del primer domingo de abril al último de octubre).

- **Duplicados:** 4 fechas (2014-11-02, 2015-11-01, 2016-11-06 y 2017-11-05) a las 02:00 en 10 regiones (no en `NI` ni en `PJM_Load`), con valores distintos. Son el primer domingo de noviembre: la hora que se repite en el cambio de otoño.
- **Horas faltantes (217 en total, entre 6 y 30 por región):**
  - La hora que no existe en el cambio de primavera, a las 03:00.
  - Hasta 2013, también la hora repetida de otoño (02:00). Desde 2014 esa hora aparece duplicada, lo que explica «2 faltantes por año hasta 2013 y 1 después».
  - Excepción en `PJME`: 2010-12-10 00:00, que no corresponde a un cambio de horario. La clasificación del resto de las regiones se confirma con la tabla de la sección 3.3 del notebook 01.

### Valores sospechosos y atípicos

| Región | Valor | Fecha | Tipo | Tratamiento |
| ------ | ----- | ----- | ---- | ----------- |
| FE | 0 MW | 2011-06-01 01:00 | Primer registro de la serie | Se marca vacío y se recorta |
| DOM | 1,253 MW | 2009-12-12 00:00 | Aislado, el siguiente valor más bajo es 5,518 MW | Se conserva (D2) |
| PJMW | 487 MW | 2003-05-29 00:00 | Aislado | Se conserva (D2) |
| PJMW | 2,553 y 2,574 MW | 2012-04-01 y 2012-04-02 | Aislados | Se conserva (D2) |
| EKPC | 514 MW | 2013-09-29, de madrugada | Racha de varias horas en domingo: valle real, no error | Se conserva |
| DEOK | Mínimos de 907 MW y lecturas de 1,044 y 2,064 MW para una misma hora (2017-11-05) | 2018-04-22 y 2017-11-05 | **Por revisar** (sección 3.4 del notebook 01) | Se conserva por ahora |

Con el criterio del rango intercuartílico, los atípicos **altos** van de 567 (`PJM_Load`) a 3,450 por región (`PJME`) y son picos reales de demanda. Los atípicos **bajos** son 34 en `DEOK`, 10 en `PJMW`, 5 en `PJME` (entre ellos el 2012-10-30, huracán Sandy, un valle real), 1 en `DOM`, 1 en `FE` y ninguno en el resto.

---

## Reglas de preprocesamiento

Reglas explícitas que gobiernan la preparación de los datos. El z modificado se calcula como 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana (Iglewicz y Hoaglin, 1993).

| Regla                         | Umbral o criterio                                                                           | Fundamento                                                                 | Estado                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------- |
| Comparabilidad entre regiones | Solo en el periodo común (10 regiones, 2013-06-01 → 2018-08-02 en días operativos)          | Derivado de la cobertura observada                                         | Aplicada                                                  |
| Cobertura mínima              | Una región se excluye de una comparación si tiene menos del 99 % de las horas de su periodo | Criterio del proyecto, el valor observado es de 99.98 % o más              | Cumplida                                                  |
| Horas repetidas               | Se promedian las lecturas                                                                   | Cambio de horario de otoño (desde 2014): dos lecturas para una hora        | Aplicada                                                  |
| Valores imposibles            | MW ≤ 0 pasa a vacío                                                                         | Restricción física: la demanda no puede ser negativa                       | Aplicada                                                  |
| Valores atípicos aislados     | z modificado de la desviación respecto del patrón esperado > 3.5 y horas vecinas normales   | Iglewicz y Hoaglin (1993)                                                  | **Por hacer (D2)**: hoy solo se corrigen los valores ≤ 0, `DOM` y `PJMW` se conservan |
| Picos altos continuos         | Se conservan                                                                                | Son demanda real, se distinguen por su continuidad                         | Aplicada                                                  |
| Rachas bajas reales           | Se conservan                                                                                | Un valle de varias horas seguidas es consumo real (`EKPC`, 2013-09-29)     | Aplicada                                                  |
| Horas faltantes               | Se reindexa a un calendario horario completo                                                | Una serie regular es requisito de rezagos, medias móviles y descomposición | Aplicada                                                  |
| Interpolación                 | Lineal, hasta 2 horas seguidas                                                              | Todos los huecos observados son de 2 horas o menos                         | Aplicada                                                  |
| Vacíos en los extremos        | Se recortan                                                                                 | No hay dato vecino para estimarlos (por ejemplo, el 0 MW inicial de `FE`)  | Aplicada                                                  |
| Año completo                  | Al menos 8,700 horas (99.3 %)                                                               | Criterio del proyecto                                                      | Aplicada                                                  |
| Día operativo                 | Del 01:00 al 24:00 (`Datetime − 1 h`)                                                       | `Datetime` marca el final de la hora (decisión D1)                         | Aplicada en `src/features.py`                             |
| Día completo                  | 24 horas por día y región                                                                   | Requisito de los perfiles diarios y de los promedios diarios               | Aplicada en `src/profiles.py` y en el notebook 03         |
| Series `NI` y `COMED`         | Se guardan por separado y se documenta la continuidad                                       | La evidencia permite unirlas, pero la decisión no está tomada              | **Por confirmar (D3)**                                    |

### Salidas de la limpieza

`02_limpieza.ipynb` (o `run_cleaning` en `src/cleaning.py`) guarda en `data/processed/`:

- Un archivo `<REGION>_clean.parquet` por región.
- `consumo_horario.parquet`: las 12 regiones en formato largo (`Datetime`, `MW`, `region`), con 1,090,343 filas.

Las 12 regiones superan `validar_limpieza`: fechas sin repetir, orden cronológico, una hora exacta entre filas consecutivas, sin vacíos y sin valores menores o iguales a 0.