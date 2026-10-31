# Resultados esperados

> Las cifras horarias (hora del mínimo y del máximo, diferencias entre fin de semana y festivo) y los resultados del pronóstico se calcularon con `Datetime` como hora de fin. Con el día operativo (decisión D1) las horas bajan 1 h y las demás cifras pueden cambiar: se marcan como **por recalcular** hasta repetir los notebooks 03 y 04.

| N.º        | Resultado esperado                                                                    | Estado                            | Qué se ha obtenido                                                                                                                                                                                  |
| ---------- | ------------------------------------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OE1        | Base horaria limpia y documentada                                                     | Cumplido                          | 1,090,343 filas en 12 regiones, validadas. Se unificaron 40 duplicados, se interpolaron 217 horas (0.02 %) y se recortó 1 fila (el cero inicial de `FE`)                                              |
| OE2        | Catálogo de tipos de día, con su curva, su frecuencia y su ubicación en el calendario | Implementado (notebook 05) | Evidencia previa de estructura: segundo pico hacia las 8 h en varias regiones y fin de semana entre un 4 % y un 14 % menor (por recalcular)                                                  |
| OE3        | Tipología de regiones y matriz región por tipo de día                                 | Parcial                           | Indicadores calculados: variabilidad de 17 % a 26 %, razón invierno/verano de 0.92 (`DUQ`) a 1.20 (`EKPC`) y correlaciones diarias de 0.56 a 0.96. La matriz región por tipo de día sale del notebook 05 |
| OE4        | Lista de días atípicos con su magnitud y coincidencia con episodios                   | Implementado (notebook 06) | Máximos coincidentes entre regiones en agosto de 2006, julio de 2011 y febrero de 2015, y menor consumo de `PJME` el 2012-10-30 (huracán Sandy). El contraste con episodios usa fuentes públicas   |
| OE5        | Panel interactivo con seis páginas (resumen, patrones, tipos de día, regiones, anomalías y pronóstico) | Parcial                           | Las 17 tablas del modelo de datos las genera el notebook 07. El archivo de Power BI está por construir                                                                                              |
| Referencia | Pronóstico a 24 horas contra modelos base, con MASE y ventana móvil                   | Cumplido (partición única), ventana móvil por ejecutar | XGBoost: MAE 1,862 MW frente a 2,300 MW del modelo base de 24 h (−19.0 %), por recalcular con el día operativo. Ventana móvil de 6 pliegues y MASE implementados en el notebook 04 |

## Hallazgos del análisis descriptivo

- **Periodo:** no existe un periodo común a las 12 regiones, 10 comparten 2013-06-01 → 2018-08-03 (días operativos hasta el 2018-08-02).
- **Ciclo diario:** mínimo hacia las 4 y 5 h y máximo entre las 18 y las 20 h (19 h en 7 de 10 regiones). Cifras en hora de fin, **por recalcular** (con la hora de inicio deberían bajar 1 h).
- **Calendario:** el fin de semana consume entre un 4 % y un 14 % menos que un laborable, y un festivo cerca de un 5 % menos (por recalcular).
- **Estacionalidad:** dos máximos anuales (verano e invierno) con valles en abril y octubre. `EKPC` y `PJMW` son invernales, `COMED`, `DUQ`, `DEOK` y `PJME`, veraniegas.
- **Tendencia:** estabilidad o ligera baja (`PJME` −9 % entre 2007 y 2017, `AEP` −13 %).
- **Picos:** `PJME` alcanzó 62,009 MW el 2006-08-02, `DOM`, `EKPC` y `PJMW` tienen su récord el 2015-02-20. Ambas fechas coinciden con episodios documentados por PJM: el récord de demanda de verano (2 de agosto de 2006) y el de invierno (20 de febrero de 2015).
- **Hora de `COMED`:** su curva diaria llega una hora más tarde que la del resto. Es lo esperable si las series están en hora del este y `COMED` es una zona de hora central, y no se corrige (ver D7).
- **`NI` y `COMED`:** niveles casi iguales (cociente 1.00) y empalme el 2011-01-01, lo que permite tratarlas como la misma zona (decisión D3, por confirmar).
