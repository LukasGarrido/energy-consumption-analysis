# Base de datos (dataset)

## Fuente y contenido

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)
- **Autor:** Rob Mulla
- **Origen de los datos:** sitio web de PJM Interconnection, organización regional de transmisión eléctrica que opera la red de todo o parte de 13 estados del este de EE. UU. y Washington D.C.
- **Contenido:** consumo horario en megavatios (MW), entre 1998-04-01 y 2018-08-03.
- **Regiones:** AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load.
- **Formato:** un archivo CSV por región con las columnas `Datetime` y `<REGION>_MW`, más un archivo combinado (`pjm_hourly_est.csv`) que no se utiliza.
- **Volumen:** 1,090,167 filas en total; entre 32,896 (`PJM_Load`) y 145,366 (`PJME`) por región.

### Periodos distintos por región

Las regiones no cubren los mismos años, por lo que **no existe un periodo común a las 12**:

- `PJM_Load` cubre 1998-04 → 2002-01 y `NI` 2004-05 → 2011-01.
- Las otras 10 regiones llegan hasta 2018-08-03 y se denominan *vigentes*. Comparten el periodo **2013-06-01 → 2018-08-03**.
- `NI` termina en 2011-01 cuando empieza `COMED`, y `PJM_Load` termina en 2002-01 cuando empiezan `PJME` y `PJMW`. Podrían ser la misma zona en periodos consecutivos, pero no está comprobado.

Las comparaciones entre regiones se hacen sobre las 10 vigentes en su periodo común; `NI` y `PJM_Load` se analizan por separado.

---

## Diccionario de datos

### Archivos por región (`data/raw/`)

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `Datetime` | Fecha y hora | Hora | Momento de la medición. Llega como texto y se convierte a fecha. Ver *Convención horaria* |
| `<REGION>_MW` | Numérico | MW | Consumo eléctrico de la región en esa hora (por ejemplo, `AEP_MW`, `PJME_MW`) |

### Tabla unificada (`data/processed/consumo_horario.parquet`)

Resultado de la limpieza, con todas las regiones en formato largo. Los MW son los originales: no se normalizan.

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `Datetime` | Fecha y hora | Hora | Momento de la medición, una fila por hora sin saltos |
| `MW` | Numérico | MW | Consumo eléctrico de la región en esa hora |
| `region` | Texto | N/A | Nombre de la región |

También se genera un archivo limpio por región (`<REGION>_clean.parquet`) con las columnas `Datetime` y `MW`.

### Variables derivadas (`src/features.py`)

Se calculan al momento de analizar y no se guardan en los archivos.

| Variable | Descripción |
|---|---|
| `anio`, `mes`, `hora` | Partes de la fecha |
| `dia_semana` | 0 = lunes, 6 = domingo |
| `es_fin_de_semana` | Sábado o domingo |
| `estacion` | Estación meteorológica del hemisferio norte, por meses completos |
| `es_festivo` | Festivo federal de EE. UU. |
| `MW_rel` | Consumo dividido entre el promedio de su región |

### Convención horaria

`Datetime` parece indicar el **final** de la hora y estar expresada en hora local del este de EE. UU. (EPT), no el inicio. Tres indicios en los datos lo sostienen:

1. Todas las series empiezan a las 01:00 y terminan a las 00:00.
2. En el cambio de horario de primavera falta la fila de las **03:00**, no la de las 02:00.
3. En el cambio de otoño la hora que se repite es la de las **02:00**.

Esto coincide con la documentación de PJM, que reporta sus datos horarios con "hora de fin" (hora 1 la primera del día y hora 24 la última) y en el cambio de marzo omite la hora de fin 3.

**Consecuencias:**

- La fila de las `00:00` corresponde a la última hora del día anterior.
- La variable `hora` de los perfiles refleja el final de la hora: un pico "a las 18 h" corresponde al intervalo 17:00–18:00.
- Para la fila de las `00:00`, `dia_semana`, `es_fin_de_semana` y `es_festivo` quedan desplazadas un día (1 de cada 24 horas).
- Que todas las regiones usen hora del este explicaría por qué `COMED`, que sirve a la zona de Chicago, aparece desfasada alrededor de una hora respecto a las demás (por confirmar en `03_analisis.ipynb`).

---

## Calidad de los datos

Resultados de `01_exploracion.ipynb`. Ninguna región tiene valores nulos y todas tienen una cobertura de entre 99.98 % y 99.99 % de las horas de su periodo.

| Región | Inicio | Fin | Filas | Duplicados | Horas faltantes | Cobertura (%) | Ceros |
|---|---|---|---|---|---|---|---|
| AEP | 2004-10-01 01:00 | 2018-08-03 00:00 | 121,273 | 4 | 27 | 99.98 | 0 |
| COMED | 2011-01-01 01:00 | 2018-08-03 00:00 | 66,497 | 4 | 11 | 99.98 | 0 |
| DAYTON | 2004-10-01 01:00 | 2018-08-03 00:00 | 121,275 | 4 | 25 | 99.98 | 0 |
| DEOK | 2012-01-01 01:00 | 2018-08-03 00:00 | 57,739 | 4 | 9 | 99.98 | 0 |
| DOM | 2005-05-01 01:00 | 2018-08-03 00:00 | 116,189 | 4 | 23 | 99.98 | 0 |
| DUQ | 2005-01-01 01:00 | 2018-08-03 00:00 | 119,068 | 4 | 24 | 99.98 | 0 |
| EKPC | 2013-06-01 01:00 | 2018-08-03 00:00 | 45,334 | 4 | 6 | 99.99 | 0 |
| FE | 2011-06-01 01:00 | 2018-08-03 00:00 | 62,874 | 4 | 10 | 99.98 | 1 |
| NI | 2004-05-01 01:00 | 2011-01-01 00:00 | 58,450 | 0 | 14 | 99.98 | 0 |
| PJM_Load | 1998-04-01 01:00 | 2002-01-01 00:00 | 32,896 | 0 | 8 | 99.98 | 0 |
| PJME | 2002-01-01 01:00 | 2018-08-03 00:00 | 145,366 | 4 | 30 | 99.98 | 0 |
| PJMW | 2002-04-01 01:00 | 2018-08-03 00:00 | 143,206 | 4 | 30 | 99.98 | 0 |

### Duplicados

Hay 4 fechas repetidas en 10 de las 12 regiones (no en `NI` ni `PJM_Load`): las **02:00** del 2014-11-02, 2015-11-01, 2016-11-06 y 2017-11-05. Las dos filas de cada fecha traen valores de MW distintos: en `AEP`, la región revisada en detalle, el 2014-11-02 son 12,994 y 13,190 MW, y la tabla global confirma que cada una de las 4 fechas tiene valores distintos al menos en una región. Coinciden con el cambio de horario de otoño.

### Horas faltantes

Faltan entre 6 y 30 horas por región, de 1 a 3 por año. Ninguna región pierde más de 3 horas en un año: no hay apagones de datos. Las fechas de las 30 horas faltantes de `PJME` se explican casi en su totalidad por el cambio de horario:

| Causa | Horas | Detalle |
|---|---|---|
| Primavera (cambio de horario) | 17 | Siempre a las 03:00, de 2002 a 2018 |
| Otoño (cambio de horario) | 12 | Siempre a las 02:00, de 2002 a 2013. Desde 2014 esa hora aparece duplicada en lugar de faltar |
| Otra causa | 1 | 2010-12-10 a las 00:00 |

Las fechas de primavera y otoño coinciden con las fechas oficiales del cambio de horario de EE. UU., incluido el adelanto de las fechas a partir de 2007.

**Excepciones:**

- **2010-12-10 00:00:** hace que 2010 tenga 3 horas faltantes en todas las regiones con datos ese año (`AEP`, `DAYTON`, `DOM`, `DUQ`, `NI`, `PJME` y `PJMW`).
- **`AEP`:** tiene una hora extra en 2012 (3 frente a 2 en las demás) y otra en 2014 (2 frente a 1). Sus fechas están por identificar.
- **Años de arranque:** las regiones que empiezan a mitad de año tienen una hora menos ese año, porque solo ven uno de los dos cambios de horario.

### Valores bajos y atípicos

Con la regla del rango intercuartil hay **19,693 valores altos y solo 51 bajos** en todo el dataset (los bajos están en `DEOK` 34, `PJMW` 10, `PJME` 5, `DOM` 1 y `FE` 1). Los valores altos forman una nube continua hasta el máximo de cada región: son picos de demanda reales y se conservan. Los valores bajos se revisaron por separado:

| Región | Valor (MW) | Fecha | Lectura |
|---|---|---|---|
| `FE` | 0 | 2011-06-01 01:00 (primer registro) | Error casi seguro |
| `DOM` | 1,253 | 2009-12-12 00:00 | Aislado: el siguiente mínimo es 5,518. Candidato a error |
| `PJMW` | 487 | 2003-05-29 00:00 | Aislado: el siguiente mínimo es 2,553. Candidato a error |
| `PJMW` | 2,553 y 2,574 | 2012-04-02 00:00 y 2012-04-01 16:00 | Muy por debajo de su media (5,602), sobre todo el de la tarde. Candidato a error |
| `DEOK` | 907, 912 y 921 | 2018-04-22 03:00–05:00 | Tres horas seguidas, lejos de su media (3,105). Por revisar |
| `PJME` | 14,544 | 2012-10-30 03:00–05:00 | Varias horas seguidas; coincide con el paso del huracán Sandy (hipótesis sin verificar) |
| `DAYTON` | 982 | 2008-09-14 18:00 | Coincide con la tormenta de viento del huracán Ike (hipótesis sin verificar) |
| `EKPC` | 514, 519 y 519 | 2013-09-29 03:00–07:00 | Varias horas el mismo día: probable demanda real |
| `AEP`, `DUQ` | 9,581 (`AEP`), 1,014 (`DUQ`) | 2016-10-02 y 2015-04-27 | Madrugadas de bajo consumo: probable demanda real |
| `COMED`, `NI`, `PJM_Load` | 7,237, 7,003 y 17,461 | 2014-05-25, 2005-05-29 y 1998-05-24 | Domingos del fin de semana largo del Memorial Day: probable demanda real |

El criterio general es la continuidad: varias horas bajas seguidas sugieren un evento real, mientras que un valor aislado entre horas normales sugiere un error de medición.

---

## Limpieza aplicada

Realizada en `02_limpieza.ipynb` con las funciones de `src/cleaning.py`, en este orden:

| # | Problema | Decisión |
|---|---|---|
| 1 | Horas repetidas (cambio de horario de otoño) | Una fila por hora, promediando las lecturas repetidas |
| 2 | Valores menores o iguales a 0 | Se marcan como vacío |
| 3 | Horas ausentes | Se reindexa a un calendario horario completo (las horas nuevas quedan vacías) |
| 4 | Vacíos en el primer o último registro | Se recortan (no hay dato vecino para estimarlos) |
| 5 | Vacíos cortos | Interpolación lineal, hasta 2 horas seguidas (`LIMITE_HORAS = 2`) |
| 6 | Vacíos largos | No se rellenan; la validación los reporta |
| 7 | Picos altos de demanda | Se conservan (consumo real) |

Cada región se valida al final: sin fechas repetidas, en orden cronológico, una hora exacta entre filas consecutivas, sin vacíos y sin valores menores o iguales a 0.

### Resultados de la limpieza

| Región | Filas originales | Duplicados unificados | Valores marcados | Horas agregadas | Filas recortadas | Huecos interpolados | Filas finales |
|---|---|---|---|---|---|---|---|
| AEP | 121,273 | 4 | 0 | 27 | 0 | 27 | 121,296 |
| COMED | 66,497 | 4 | 0 | 11 | 0 | 11 | 66,504 |
| DAYTON | 121,275 | 4 | 0 | 25 | 0 | 25 | 121,296 |
| DEOK | 57,739 | 4 | 0 | 9 | 0 | 9 | 57,744 |
| DOM | 116,189 | 4 | 0 | 23 | 0 | 23 | 116,208 |
| DUQ | 119,068 | 4 | 0 | 24 | 0 | 24 | 119,088 |
| EKPC | 45,334 | 4 | 0 | 6 | 0 | 6 | 45,336 |
| FE | 62,874 | 4 | 1 | 10 | 1 | 10 | 62,879 |
| NI | 58,450 | 0 | 0 | 14 | 0 | 14 | 58,464 |
| PJM_Load | 32,896 | 0 | 0 | 8 | 0 | 8 | 32,904 |
| PJME | 145,366 | 4 | 0 | 30 | 0 | 30 | 145,392 |
| PJMW | 143,206 | 4 | 0 | 30 | 0 | 30 | 143,232 |
| **Total** | **1,090,167** | **40** | **1** | **217** | **1** | **217** | **1,090,343** |

- Las 12 regiones pasaron la validación y quedaron con cero vacíos. Ningún hueco superó las 2 horas seguidas.
- Se interpoló el 0.02 % de las horas (217 de 1,090,343) y se unificó el 0.004 % de las filas originales (40 duplicados).
- `FE` ahora empieza el 2011-06-01 a las 02:00: su primer registro era el valor en 0 MW y se recortó.
- El resultado se guarda en `data/processed/` (un archivo limpio por región y uno combinado).

### Limitaciones de la limpieza

- **La hora de primavera se inventa.** Esa hora no existió en la hora local; al reindexar aparece como faltante y se rellena por interpolación. Afecta a 1 o 2 horas por año.
- **Las dos lecturas de otoño se promedian**, aunque corresponden a horas distintas. Afecta a 4 fechas por región.
- **Solo se corrigen los valores menores o iguales a 0.** Los candidatos a error de `DOM` y `PJMW` siguen en los datos limpios.

---

## Puntos abiertos

1. **Valores bajos candidatos a error** (`DOM` 1,253; `PJMW` 487, 2,553 y 2,574): decidir si se marcan como vacío y se interpolan, y con qué criterio.
2. **`DEOK` el 2018-04-22:** revisar si las tres horas bajas son consumo real.
3. **Horas faltantes sin explicación:** confirmar las fechas de las horas extra de `AEP` (2012 y 2014).
4. **Convención horaria:** decidir si se corrigen las variables de calendario restando una hora a `Datetime`, o si se documenta la simplificación.
5. **Continuidad entre regiones** (`NI`→`COMED`, `PJM_Load`→`PJME`/`PJMW`): se comprueba en `03_analisis.ipynb`.
