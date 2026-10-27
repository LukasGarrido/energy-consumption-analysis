# Resultados esperados

| N.º        | Resultado esperado                                                                    | Estado    | Qué se ha obtenido                                                                                                                                |
| ---------- | ------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| OE1        | Base horaria limpia y documentada                                                     | Cumplido  | 1,090,343 filas en 12 regiones, validadas. Se unificaron 40 duplicados y se interpolaron 217 horas (0.02 %)                                       |
| OE2        | Catálogo de tipos de día, con su curva, su frecuencia y su ubicación en el calendario | Por hacer | Evidencia previa de estructura: segundo pico hacia las 8 h en varias regiones y fin de semana entre un 4 % y un 14 % menor                        |
| OE3        | Tipología de regiones y matriz región por tipo de día                                 | Parcial   | Indicadores calculados: variabilidad de 17 % a 26 %, razón invierno/verano de 0.92 (`DUQ`) a 1.20 (`EKPC`) y correlaciones diarias de 0.56 a 0.96 |
| OE4        | Lista de días atípicos con su magnitud y coincidencia con episodios                   | Por hacer | Máximos coincidentes entre regiones en agosto de 2006, julio de 2011 y febrero de 2015, menor consumo de `PJME` el 2012-10-30                     |
| OE5        | Panel interactivo con cinco páginas                                                   | Por hacer | Las vistas estáticas están en los notebooks                                                                                                       |
| Referencia | Pronóstico a 24 horas contra modelos base                                             | Cumplido  | XGBoost: MAE 1,862 MW frente a 2,300 MW del modelo base de 24 h (−19.0 %)                                                                         |

## Hallazgos del análisis descriptivo

- **Periodo:** no existe un periodo común a las 12 regiones; 10 comparten 2013-06-01 → 2018-08-03.
- **Ciclo diario:** mínimo hacia las 4 y 5 h y máximo entre las 18 y las 20 h (19 h en 7 de 10 regiones).
- **Calendario:** el fin de semana consume entre un 4 % y un 14 % menos que un laborable, y un festivo cerca de un 5 % menos.
- **Estacionalidad:** dos máximos anuales (verano e invierno) con valles en abril y octubre. `EKPC` y `PJMW` son invernales; `COMED`, `DUQ`, `DEOK` y `PJME`, veraniegas.
- **Tendencia:** estabilidad o ligera baja (`PJME` −9 % entre 2007 y 2017; `AEP` −13 %).
- **Picos:** `PJME` alcanzó 62,009 MW el 2006-08-02; `DOM`, `EKPC` y `PJMW` tienen su récord el 2015-02-20.