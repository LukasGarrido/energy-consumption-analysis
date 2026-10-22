# Resultados Esperados del Análisis

---

[← Volver al Índice](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md)

---

- Un conjunto de datos limpio y documentado, con un resumen bien redactado de la información por región.
- La identificación de los patrones de consumo por hora, día y mes, y de su estacionalidad.
- La descripción de la tendencia de largo plazo y de los periodos de mayor demanda.
- Una comparación entre regiones, con sus similitudes y diferencias.
- Un conjunto de visualizaciones (estáticas e interactivas) que comuniquen los hallazgos.
- Un repositorio en GitHub ordenado, con notebooks y documentación.
- Un informe final con conclusiones.

---

# Resultados obtenidos

|Resultado esperado|Estado|Qué se obtuvo|
|---|---|---|
|Conjunto de datos limpio y documentado, con resumen por región|Cumplido|`consumo_horario.parquet` (1,090,343 filas, 12 regiones) y un archivo limpio por región. Se unificaron 40 duplicados e interpolaron 217 horas (0.02 %). La calidad por región está en `02_base_de_datos.md`|
|Patrones de consumo por hora, día y mes, y estacionalidad|Cumplido|Mínimo hacia las 4–5 h, máximo entre las 18 y las 20 h (19 h en 7 de 10 regiones). El fin de semana consume entre 4 % y 14 % menos que un laborable. Doble estacionalidad anual (verano e invierno) con valles en abril y octubre|
|Tendencia de largo plazo y periodos de mayor demanda|Cumplido|Sin crecimiento: estabilidad o ligera baja (`PJME` −9 % entre 2007 y 2017, `AEP` −13 %). Máximos casi siempre en olas de calor de verano (`PJME` 62,009 MW el 2006-08-02); `DOM`, `EKPC` y `PJMW` tienen su récord el 2015-02-20|
|Comparación entre regiones|Cumplido|Variabilidad (CV) de 17 % a 26 %; regiones de verano (`COMED`, `DUQ`, `DEOK`, `PJME`) e invernales (`EKPC`, `PJMW`). Correlaciones diarias de 0.56 a 0.96|
|Visualizaciones estáticas e interactivas|Parcial|Las estáticas están en los notebooks; las interactivas dependen del dashboard en Streamlit (pendiente)|
|Repositorio ordenado, con notebooks y documentación|En curso|Estructura y cuatro notebooks listos; falta cerrar la documentación|
|Informe final con conclusiones|Pendiente|Se redactará con los resultados de los notebooks|
|Modelo de pronóstico de la demanda|Cumplido|XGBoost reduce el MAE un 19.0 % frente al modelo base de 24 h (1,862 frente a 2,300 MW) en `PJME`|