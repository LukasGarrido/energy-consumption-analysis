# Análisis de Consumo Horario de Energía

---
### Objetivo 
#### General
Analizar el consumo eléctrico horario de la red PJM Interconnection (EE. UU.) para identificar patrones de demanda en el tiempo y diferencias entre regiones, y comunicar los hallazgos mediante visualizaciones.

#### Específicos
- Explorar y depurar el conjunto de datos, documentando su calidad (nulos, duplicados, horas faltantes y rangos de fechas por región).
- Identificar patrones por hora del día, día de la semana y mes del año.
- Estudiar la estacionalidad y la tendencia de largo plazo del consumo.
- Comparar el comportamiento de las distintas regiones y detectar los periodos de máxima demanda.
- Construir visualizaciones que presenten los resultados de forma comprensible.

---
### Base de datos (dataset)

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)
- **Autor:** Rob Mulla
- **Origen de los datos:** sitio web de PJM Interconnection, organización regional de transmisión eléctrica que opera la red de todo o parte de 13 estados del este de EE. UU. y Washington D.C.
- **Contenido:** consumo horario en megavatios (MW), aproximadamente entre 2002 y 2018.
- **Regiones:** AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load.
- **Formato:** un archivo CSV por región con las columnas `Datetime` y `<REGION>_MW`.
- **Volumen:** entre unas 33 mil y 145 mil filas por archivo, según la región.
- **Consideración importante:** las regiones han cambiado con los años, por lo que no todas cubren el mismo periodo. Las comparaciones deberán hacerse sobre rangos de fechas comunes.

---
### Métodos y herramientas para visualización y ciencia de datos.

#### Herramientas
- **Obsidian:** registro de la documentación técnica y de las decisiones del análisis.
- **VS Code y Antigravity IDE:** editores de código para el desarrollo del proyecto.
- **Python:** lenguaje principal para el procesamiento y análisis de los datos, por su ecosistema de librerías (pandas, NumPy, Matplotlib, Seaborn y Plotly).
- **Jupyter Notebook:** desarrollo y documentación del análisis paso a paso.
- **GitHub:** control de versiones y gestión del código del proyecto.
#### Métodos
- **Análisis exploratorio de datos (EDA):** estadística descriptiva, detección de nulos, duplicados y valores atípicos.
- **Preparación de series de tiempo:** conversión de fechas, ordenamiento, tratamiento de horas faltantes y duplicadas por cambios de horario.
- **Ingeniería de variables temporales:** hora, día de la semana, mes, estación del año y día festivo.
- **Agregaciones temporales:** promedios diarios, mensuales y anuales para resumir y visualizar.
- **Análisis de estacionalidad y tendencia:** medias móviles y descomposición de la serie.
- **Visualización:** gráficos de líneas, mapas de calor (hora por día de la semana), diagramas de caja y comparaciones entre regiones, en versiones estáticas e interactivas.
- **Pronóstico:** modelo de predicción de la demanda.

---
### Metodología para el desarrollo 
Se seguirá un flujo de trabajo por fases, con avances registrados en GitHub y Obsidian.

| Fase                                       | Actividades                                                                             |
| ------------------------------------------ | --------------------------------------------------------------------------------------- |
| 1. Comprensión del problema y de los datos | Definir preguntas de análisis, descargar el dataset y revisar su estructura             |
| 2. Exploración y limpieza                  | EDA, tratamiento de nulos, duplicados y horas faltantes, generación de datos procesados |
| 3. Análisis                                | Patrones temporales, estacionalidad, tendencia y comparación entre regiones             |
| 4. Visualización                           | Diseño y construcción de gráficos y de la presentación final de resultados              |
| 5. Documentación y cierre                  | Conclusiones, informe final, orden del repositorio y presentación                       |

---
### Resultados esperados del análisis 

- Un conjunto de datos limpio y documentado, con un resumen bien redactado  de la información por región.
- La identificación de los patrones de consumo por hora, día y mes, y de su estacionalidad.
- La descripción de la tendencia de largo plazo y de los periodos de mayor demanda.
- Una comparación entre regiones, con sus similitudes y diferencias.
- Un conjunto de visualizaciones (estáticas e interactivas) que comuniquen los hallazgos.
- Un repositorio en GitHub ordenado, con notebooks y documentación.
- Un informe final con conclusiones.

---

### Referencias

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). _CRISP-DM 1.0: Step-by-step data mining guide_. CRISP-DM Consortium.

Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. _Journal of Official Statistics, 6_(1), 3-73.

Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. _Nature, 585_, 357-362. [https://doi.org/10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2)

Hong, T., & Fan, S. (2016). Probabilistic electric load forecasting: A tutorial review. _International Journal of Forecasting, 32_(3), 914-938.

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. _Computing in Science & Engineering, 9_(3), 90-95.

Hyndman, R. J., & Athanasopoulos, G. (2021). _Forecasting: Principles and practice_ (3rd ed.). OTexts. [https://otexts.com/fpp3/](https://otexts.com/fpp3/)

Kluyver, T., Ragan-Kelley, B., Pérez, F., et al. (2016). Jupyter Notebooks: A publishing format for reproducible computational workflows. En F. Loizides & B. Schmidt (Eds.), _Positioning and Power in Academic Publishing_ (pp. 87-90). IOS Press.

McKinney, W. (2010). Data structures for statistical computing in Python. _Proceedings of the 9th Python in Science Conference_, 56-61.

Mulla, R. (2018). _Hourly Energy Consumption_. Kaggle. [https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)

Plotly Technologies Inc. (2015). _Collaborative data science_. [https://plot.ly](https://plot.ly)

Tukey, J. W. (1977). _Exploratory data analysis_. Addison-Wesley.

Waskom, M. L. (2021). seaborn: Statistical data visualization. _Journal of Open Source Software, 6_(60), 3021. [https://doi.org/10.21105/joss.03021](https://doi.org/10.21105/joss.03021)

| Parte del documento                                                        | Referencia                                               |
| -------------------------------------------------------------------------- | -------------------------------------------------------- |
| Base de datos (Kaggle, Rob Mulla)                                          | Mulla (2018)                                             |
| Herramientas: Python con pandas                                            | McKinney (2010)                                          |
| Herramientas: NumPy                                                        | Harris et al. (2020)                                     |
| Herramientas: Matplotlib                                                   | Hunter (2007)                                            |
| Herramientas: Seaborn                                                      | Waskom (2021)                                            |
| Herramientas: Plotly                                                       | Plotly Technologies Inc. (2015)                          |
| Herramientas: Jupyter Notebook                                             | Kluyver et al. (2016)                                    |
| Método: análisis exploratorio de datos (EDA)                               | Tukey (1977)                                             |
| Método: análisis de estacionalidad y tendencia, descomposición de la serie | Hyndman y Athanasopoulos (2021), Cleveland et al. (1990) |
| Método: pronóstico                                                         | Hyndman y Athanasopoulos (2021), Hong y Fan (2016)       |
| Metodología por fases                                                      | Chapman et al. (2000)                                    |
