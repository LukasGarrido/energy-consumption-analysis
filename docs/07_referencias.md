<div align="center">

# Referencias

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [Qué respalda cada referencia](#qué-respalda-cada-referencia)
- [Estado de la verificación](#estado-de-la-verificación)

---


Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. CRISP-DM Consortium.

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794). ACM. https://doi.org/10.1145/2939672.2939785

Chicco, G. (2012). Overview and performance assessment of the clustering methods for electrical load pattern grouping. *Energy, 42*(1), 68-80. https://doi.org/10.1016/j.energy.2011.12.031

Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics, 6*(1), 3-73.

Cleveland, W. S., & McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. *Journal of the American Statistical Association, 79*(387), 531-554. https://doi.org/10.2307/2288400

Cordova Pou, G. (s. f.). *EnergyConsumptionForecast* [Repositorio de GitHub]. https://github.com/gonzalo-cordova-pou/EnergyConsumptionForecast

Heer, J., & Bostock, M. (2010). Crowdsourcing graphical perception: Using Mechanical Turk to assess visualization design. En *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems* (pp. 203-212). ACM.

Hong, T., & Fan, S. (2016). Probabilistic electric load forecasting: A tutorial review. *International Journal of Forecasting, 32*(3), 914-938. https://doi.org/10.1016/j.ijforecast.2015.11.011

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/

Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting, 22*(4), 679-688.

Iglewicz, B., & Hoaglin, D. C. (1993). *How to detect and handle outliers*. ASQC Quality Press.

Kaufman, L., & Rousseeuw, P. J. (1990). *Finding groups in data: An introduction to cluster analysis*. Wiley.

Mulla, R. (2018). *Hourly Energy Consumption* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption

Munzner, T. (2014). *Visualization analysis and design*. CRC Press.

panambY. (s. f.). *Hourly_Energy_Consumption* [Repositorio de GitHub]. https://github.com/panambY/Hourly_Energy_Consumption

PJM Interconnection. (s. f.). *MSRS report format documentation: Hourly load data*. https://www.pjm.com/-/media/markets-ops/settlements/msrs/desc/msrs-customer-report-documentation-hourly-load-data.ashx

pranavsp108. (s. f.). *time-series-forcasting* [Repositorio de GitHub]. https://github.com/pranavsp108/time-series-forcasting

Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics, 20*, 53-65.

*Towards Data Science.* (s. f.). *How to forecast time series data using any supervised learning model* [Artículo en línea]. https://towardsdatascience.com/how-to-forecast-time-series-data-using-any-supervised-learning-model-02dd62cd4bda

Tukey, J. W. (1977). *Exploratory data analysis*. Addison-Wesley.

van Wijk, J. J., & van Selow, E. R. (1999). Cluster and calendar based visualization of time series data. En *Proceedings of the IEEE Symposium on Information Visualization (InfoVis '99)* (pp. 4-9). IEEE.

## Qué respalda cada referencia

| Referencia | Afirmación que respalda |
|---|---|
| Hong y Fan (2016) | Importancia del pronóstico de la demanda eléctrica, revisión de métodos |
| Mulla (2018), PJM Interconnection (s. f.) | Descripción del dataset y convención de hora de fin |
| Cordova Pou, pranavsp108, panambY, Towards Data Science | Trabajos previos con el dataset |
| Chicco (2012) | Agrupamiento de curvas de carga y desempeño de los métodos |
| van Wijk y van Selow (1999) | Agrupamiento de perfiles diarios con vista de calendario |
| Cleveland y McGill (1984), Heer y Bostock (2010) | Precisión relativa de los canales visuales |
| Munzner (2014) | Marco de datos, tarea y codificación para diseñar vistas |
| Rousseeuw (1987), Kaufman y Rousseeuw (1990) | Silueta y su interpretación |
| Iglewicz y Hoaglin (1993) | Umbral de z modificado para valores atípicos |
| Tukey (1977) | Regla de 1.5 veces el rango intercuartil para valores atípicos |
| Cleveland et al. (1990) | Descomposición STL |
| Hyndman y Koehler (2006), Hyndman y Athanasopoulos (2021) | Métricas de error, MASE y pronóstico ingenuo como referencia |
| Chen y Guestrin (2016) | Algoritmo de pronóstico |
| Chapman et al. (2000) | Estructura por fases del proyecto |

## Estado de la verificación

Revisión de la decisión D38. «Comprobado» indica contra qué se contrastó; no implica haber leído la obra completa.

**Cifras y umbrales que usa el proyecto**

| Afirmación | Comprobado en | Resultado |
|---|---|---|
| Silueta: 0.71–1.00 fuerte, 0.51–0.70 razonable, 0.26–0.50 débil, hasta 0.25 sin estructura | [Struyf, Hubert y Rousseeuw (1997)](https://www.jstatsoft.org/article/view/v001i04), artículo en acceso abierto con un coautor de la obra citada, tabla 2 | Coincide. El libro de 1990 no se consultó |
| z modificado 0.6745 · (x − mediana) / MAD, umbral 3.5 | [Manual de NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm), que lo atribuye a Iglewicz y Hoaglin | Coincide. El libro no se consultó |
| Límites a 1.5 veces el rango intercuartílico | [Manual de NIST](https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm) | Coincide. El libro de Tukey no se consultó |
| Error escalado con el pronóstico ingenuo estacional | [Hyndman y Athanasopoulos, sección 5.8](https://otexts.com/fpp3/accuracy.html) | Coincide |

**Datos bibliográficos**

| Referencias | Comprobado en | Resultado |
|---|---|---|
| Artículos y libros con DOI | Crossref | Autores, título y año coinciden, y volumen y páginas cuando Crossref los registra |
| Cleveland et al. (1990), STL | [Documentación de R](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/stl.html) | Volumen 6 y páginas 3–73 coinciden. El número 1 no se confirmó |
| Chapman et al. (2000), CRISP-DM | [Copia de la guía](https://www.kde.cs.uni-kassel.de/wp-content/uploads/lehre/ws2012-13/kdd/files/CRISPWP-0800.pdf) para título, año y las seis fases; autores en índices bibliográficos | Coincide. La portada de la copia consultada no permitió leer los autores |
| Enlaces de Kaggle, GitHub, Towards Data Science, OTexts y PJM | Consulta directa | Responden |

**Afirmaciones atribuidas a los artículos**

| Referencia | Comprobado en | Resultado |
|---|---|---|
| van Wijk y van Selow (1999): agrupamiento con vista de calendario | Resumen | Respaldada |
| Cleveland y McGill (1984), Heer y Bostock (2010): precisión de los canales visuales | Resúmenes | Respaldada |
| Chen y Guestrin (2016): XGBoost | Resumen | Respaldada |
| Wang et al. (2019): analítica de mediciones de alta resolución | Resumen | Respaldada en lo general; el resumen no detalla segmentación, agrupamiento ni anomalías |
| Himeur et al. (2021): detección de anomalías comparando con un modelo de predicción | Resumen y fragmentos | El artículo revisa la detección de anomalías; la familia basada en predicción solo se vio en fragmentos |
| Chicco (2012), Rajabi et al. (2020): k-medias y métodos jerárquicos | Resúmenes indirectos | Se confirman los métodos y el uso de índices de validación; la dependencia de la normalización no se confirmó |
| Hong y Fan (2016): importancia del pronóstico y de la temperatura | Sin resumen disponible | Sin confirmar |
| Munzner (2014): marco de datos, tarea y codificación | Solo datos bibliográficos | Sin confirmar |

Para cerrar las filas sin confirmar hace falta el texto completo de esas obras.

