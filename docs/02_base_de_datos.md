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

---

## Reglas de preprocesamiento

Reglas explícitas que gobiernan la preparación de los datos. El z modificado se calcula como 0.6745 · (x − mediana) / MAD, donde MAD es la mediana de las desviaciones absolutas respecto de la mediana (Iglewicz y Hoaglin, 1993).

| Regla | Umbral o criterio | Fundamento | Estado |
|---|---|---|---|
| Comparabilidad entre regiones | Solo en el periodo común (10 regiones, 2013-06-01 → 2018-08-03) | Derivado de la cobertura observada | Aplicada |
| Cobertura mínima | Una región se excluye de una comparación si tiene menos del 99 % de las horas de su periodo | Criterio del proyecto; el valor observado es de 99.98 % o más | Cumplida |
| Horas repetidas | Se promedian las lecturas | Cambio de horario de otoño: dos lecturas para una hora | Aplicada |
| Valores imposibles | MW ≤ 0 pasa a vacío | Restricción física: la demanda no puede ser negativa | Aplicada |
| Valores atípicos aislados | z modificado de la desviación respecto del patrón esperado > 3.5 y horas vecinas normales | Iglewicz y Hoaglin (1993) | **Por implementar**: hoy solo se corrigen los valores ≤ 0 |
| Picos altos continuos | Se conservan | Son demanda real; se distinguen por su continuidad | Aplicada |
| Horas faltantes | Se reindexa a un calendario horario completo | Una serie regular es requisito de rezagos, medias móviles y descomposición | Aplicada |
| Interpolación | Lineal, hasta 2 horas seguidas | Todos los huecos observados son de 2 horas o menos | Aplicada |
| Vacíos en los extremos | Se recortan | No hay dato vecino para estimarlos | Aplicada |
| Año completo | Al menos 8,700 horas (99.3 %) | Criterio del proyecto | Aplicada |
| Día operativo | Del 01:00 al 24:00 (`Datetime` − 1 h) | Convención de hora de fin | **Por decidir** |