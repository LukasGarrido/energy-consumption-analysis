<div align="center">

# Metodología

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [Enfoque](#enfoque)
- [Fases y criterios de cierre](#fases-y-criterios-de-cierre)
- [Flujo de notebooks](#flujo-de-notebooks)
- [Herramientas](#herramientas)
- [Métodos de ciencia de datos](#métodos-de-ciencia-de-datos)
- [Métodos de visualización](#métodos-de-visualización)
  - [Páginas del panel (Streamlit)](#páginas-del-panel-streamlit)
- [Métodos considerados y descartados](#métodos-considerados-y-descartados)

---

## Enfoque

El proyecto avanza por fases, con un notebook por bloque de trabajo y las funciones reutilizables en `src/`. En cada fase se formulan hipótesis a partir de los resultados y se contrastan con los datos antes de aceptarlas (las hipótesis contrastadas están en la sección 8 de [05_decisiones.md](05_decisiones.md)). Las decisiones de diseño se escriben una sola vez en ese mismo documento, aquí solo se enlazan.

## Fases y criterios de cierre

Una fase se considera cerrada cuando cumple su criterio de logro.

| Fase | Actividades | Entregable | Criterio de cierre | Estado |
|---|---|---|---|---|
| 1. Exploración y calidad | Estructura, convención horaria, cobertura, duplicados, horas faltantes y valores sospechosos | `01_datos.ipynb` | Hallazgos y decisiones de limpieza documentados | Hecho |
| 2. Preparación | Limpieza con reglas explícitas y validación | `01_datos.ipynb` y `data/processed/` | Las 12 regiones superan `validar_limpieza` y las filas finales cuadran (1,090,343) | Hecho |
| 3. Análisis descriptivo | Patrones por hora, día y estación, tendencia, comparación, picos | `02_patrones.ipynb` | Patrones y comparación sobre el periodo común, con el día operativo | Hecho |
| 4. Pronóstico de referencia | Modelo a 24 horas contra modelos base, MASE, validación en ventana móvil, residuos fuera de muestra | `03_pronostico_anomalias.ipynb` | El modelo supera al base en todos los pliegues y su MASE es menor que 1 | Hecho: 6 de 6 pliegues, MASE de 0.72 a 0.87 |
| 5. Agrupamiento de perfiles diarios | Perfiles normalizados, elección de k, caracterización con el calendario, mezcla por región y distancia al centro | `02_patrones.ipynb` | Silueta media reportada y grupos con al menos el 5 % de los días | Hecho (D7 y D26): k = 2, silueta 0.413 (débil), grupo más pequeño 37.7 % |
| 6. Detección de anomalías | Residuo diario, z modificado y contraste con episodios conocidos | `03_pronostico_anomalias.ipynb` | Lista contrastada con al menos un episodio externo, con fuente | Hecho: 5 episodios coinciden |
| 7. Visualización | Exportación de tablas y construcción del panel | `src/export.py` y panel en Streamlit (`app/streamlit_app.py`) | Tablas con claves coherentes y diccionario de datos. Panel con cada vista justificada por una tarea y filtros por región, fecha y estación funcionando | Hecho: 17 tablas con claves validadas, 109 columnas documentadas y panel de seis páginas con filtros |
| 8. Documentación | Informe, conclusiones y orden del repositorio | `docs/` | Documentación al día con los resultados | En curso |

## Flujo de notebooks

Ejecutar en orden numérico, cada uno con *Restart & Run All*. El detalle de instalación y ejecución está en [06_guia_usuario.md](06_guia_usuario.md).

| Paso | Entrada | Salida |
|---|---|---|
| `01_datos.ipynb` (exploración y limpieza) | `data/raw/*.csv` | Hallazgos y decisiones de limpieza. `data/processed/<REGION>_clean.parquet` y `consumo_horario.parquet` |
| `02_patrones.ipynb` (análisis y agrupamiento) | `consumo_horario.parquet` | Patrones, tendencia, comparación y picos. `tipos_de_dia.parquet`, `tipos_de_dia_curvas.parquet`, `tipos_de_dia_resumen.parquet`, `tipos_de_dia_mezcla_region.parquet` y `tipos_de_dia_silueta_k.parquet` |
| `03_pronostico_anomalias.ipynb` (modelado y anomalías) | `consumo_horario.parquet` y, si existe, `tipos_de_dia.parquet` | `residuos_PJME.parquet` (fuera de muestra), `metricas_ventana_movil_PJME.parquet`, `anomalias_PJME_diario.parquet`, `anomalias_PJME_lista.parquet` y `anomalias_PJME_episodios.parquet` |
| `src/export.py` (exportación) | `consumo_horario.parquet` y las salidas de los notebooks 02 y 03 | `data/processed/panel/*.csv` (17 tablas) y `diccionario_datos.csv`, que lee el panel de Streamlit. La ruta se define una vez en `PANEL_DIR` (`src/config.py`) |

`02_patrones.ipynb` y `src/export.py` usan la hora de la fuente para todas las regiones (D7 y D41). `ALINEAR_HORA_CENTRAL` queda en el notebook para repetir el análisis de sensibilidad; si se adoptara la alineación, la exportación tendría que aplicarla también.

## Herramientas

| Herramienta | Uso |
|---|---|
| Python (pandas, NumPy) | Procesamiento de los datos y cálculo de indicadores |
| scikit-learn | Agrupamiento de perfiles diarios (k-medias y Ward), silueta e índice de Rand ajustado |
| XGBoost | Modelo de pronóstico de referencia |
| statsmodels | Descomposición STL de la serie |
| holidays | Festivos federales de EE. UU. para la variable `es_festivo` |
| pyarrow | Lectura y escritura de archivos parquet |
| Matplotlib y Seaborn | Gráficos exploratorios en los notebooks |
| Streamlit y Plotly | Panel interactivo (`app/streamlit_app.py`), lee los CSV de `data/processed/panel/` (D4) |
| Docker Compose | Ejecución opcional del panel sin entorno de Python (`compose.yaml`) |
| Jupyter Notebook | Desarrollo y documentación del análisis |
| VS Code y Antigravity IDE | Edición de código |
| GitHub | Control de versiones y gestión de tareas |
| Obsidian | Registro de la documentación técnica y de las decisiones |

La reproducibilidad se apoya en una semilla fija (`SEMILLA = 42` en `src/config.py`) y en que todos los parámetros (rango de k, umbrales, pliegues) viven en ese mismo archivo.

## Métodos de ciencia de datos

| Método | Descripción | Estado |
|---|---|---|
| Limpieza de series de tiempo | Unificación de horas repetidas (promedio), reindexado a calendario horario, recorte de extremos, interpolación lineal de huecos de hasta 2 horas y validación (`src/cleaning.py`) | Hecho |
| Detección de valores atípicos aislados | Desviación respecto de las horas vecinas, z modificado frente al patrón de mes y hora (> 3.5) y criterio de continuidad (`marcar_atipicos_aislados`). Marca 3 valores en `AEP`, `DOM` y `PJMW` (D2) | Hecho (`01_datos`) |
| Análisis exploratorio | Estadística descriptiva, cobertura, duplicados, horas faltantes (con su causa) y valores aislados frente a rachas y distribución | Hecho (`01_datos`) |
| Variables de calendario | Día operativo (`Datetime − 1 h`): fecha, hora (0 a 23), día de la semana, mes, estación, fin de semana y festivo (`src/features.py`, D1) | Hecho |
| Normalización relativa | Consumo dividido entre el promedio de su región (`MW_rel`), para comparar formas | Hecho |
| Tendencia y estacionalidad | Media móvil de 365 días y descomposición STL (`period = 365` sobre la serie diaria, por lo que el componente estacional es aproximado y el tramo final de la tendencia no se interpreta por el efecto de borde) | Hecho (`02_patrones`) |
| Correlación entre regiones | Correlación de Pearson sobre el promedio diario (solo días de 24 horas) | Hecho (`02_patrones`) |
| Continuidad entre regiones | Comparación de las medias de 30 días a cada lado del empalme (`NI` → `COMED`, `PJM_Load` → `PJME` y `PJMW`) y medición del desfase horario de cada región entre −3 y +3 h | Hecho (`02_patrones`) |
| Agrupamiento de perfiles diarios | Cada día se representa con 24 valores divididos entre el promedio del día. Se comparan k-medias y Ward para k entre 2 y 10, con la silueta media sobre una muestra reproducible de 10,000 días. Se elige la mayor silueta entre las combinaciones con grupos de al menos el 5 % de los días. Se reporta la concordancia entre ambos métodos (índice de Rand ajustado) y la distancia de cada día al centro de su grupo (`src/profiles.py`) | Hecho (`02_patrones`): k-medias con k = 2, silueta 0.413 |
| Detección de días atípicos | Residuo diario en % de la predicción, a partir de los residuos fuera de muestra del pronóstico, se marca el día con z modificado > 3.5 (0.6745 · (x − mediana) / MAD). Incluye sensibilidad al umbral, comparación por estación y pliegue, y contraste con episodios con fuente (`src/anomalies.py`) | Hecho (`03_pronostico_anomalias`): 22 días atípicos |
| Pronóstico a 24 horas | XGBoost con variables de calendario, rezagos (24, 48 y 168 h) y medias móviles desplazadas, frente a dos modelos base | Hecho |
| Validación | División cronológica con control de fuga de datos y ventana móvil con entrenamiento creciente: 6 pliegues de 12 meses (mínimo 3), sin solapamiento, de modo que cada hora se predice una sola vez fuera de muestra | Hecho (`03_pronostico_anomalias`) |
| Métricas | MAE, RMSE y MAPE, MASE con la escala del pronóstico ingenuo estacional de 24 h (Hyndman y Koehler), menor que 1 si el modelo mejora al ingenuo | Hecho |
| Exportación para el panel | Modelo en estrella en CSV (4 dimensiones, hechos y resultados de los notebooks 02 y 03) y diccionario de datos (`src/export.py`) | Hecho: 17 tablas, diccionario de 110 columnas y validación de claves (la exportación se detiene si alguna clave no tiene su fila en la dimensión) |

## Métodos de visualización

| Pregunta | Gráfico | Justificación perceptual |
|---|---|---|
| P1. Patrón hora por día de la semana | Mapa de calor 7 × 24, con la misma escala en todas las regiones | 168 valores de un vistazo, el color se complementa con líneas por tipo de calendario (laborable, fin de semana, festivo) para mayor precisión |
| P1. Elección de k | Líneas de la silueta frente a k, con los umbrales 0.26 y 0.51 | Posición sobre escala común, los k que no cumplen el tamaño mínimo se marcan |
| P1. Forma de cada tipo de día | Líneas con banda de dispersión (percentiles 10 y 90), en paneles con la misma escala | Posición sobre escala común, el canal más preciso |
| P1. Dónde cae cada tipo de día | Mapa de calor de calendario (año por día del año) con color categórico, y composición de cada grupo por día de la semana y mes | Muestra la ubicación de cada grupo en el año |
| P2. Mezcla de tipos de día por región | Barras apiladas al 100 %, en el historial completo y en el periodo común | Longitud sobre una línea base común, se evitan los gráficos circulares |
| P2. Comparación de regiones | Gráfico de dispersión con etiquetas: razón invierno/verano frente a amplitud diaria | Posición en dos ejes comunes |
| Tendencia y estacionalidad | Líneas en paneles múltiples con eje de tiempo compartido | Posición sobre escala común |
| P3. Días atípicos | Línea de tiempo con puntos resaltados y anotaciones, casos principales hora a hora (real frente a pronóstico) | Pocos puntos resaltados destacan sobre el resto |
| P3. Contraste con episodios | Tabla con el estado de cada episodio (coincide, sin coincidencia, fuera de rango), su fuente y si la fecha está verificada | Distingue lo no detectado de lo no evaluado |
| P4. Error del pronóstico | Barras del error por hora, mes y tipo de día, líneas del MAE por pliegue | Posición y longitud |
| Calidad de los datos | Barras de intervalos y mapa de calor | Muestran los periodos desiguales que condicionan las comparaciones |

### Páginas del panel (Streamlit)

| Página | Pregunta | Contenido |
|---|---|---|
| Resumen | Panorama | Tarjetas (días, regiones, silueta, MAE y MASE, días atípicos) y tendencia anual |
| Patrones | P1, P2 | Mapa de calor 7 × 24, líneas por tipo de calendario y estacionalidad mensual |
| Tipos de día | P1 | Curvas con banda, calendario de color y frecuencia de cada tipo |
| Regiones | P2 | Mezcla de tipos de día y dispersión de regiones |
| Anomalías | P3 | Línea de tiempo, tabla de episodios y lista de días atípicos |
| Pronóstico | P4 | Error por hora, mes y tipo de día, y métricas por pliegue |

Filtros en todas las páginas: región, fecha y estación. La región y la estación actúan sobre todas las tablas; la fecha, solo sobre las tablas diarias y horarias (las ya agregadas no responden a ella, D44). El modelo de datos exportado se describe en [04_modelo_y_resultados.md](04_modelo_y_resultados.md#exportación-para-el-panel).

Principios de diseño: el canal de codificación se elige según la tarea (la posición sobre una escala común es el más preciso), las vistas en paneles múltiples comparten escala cuando el objetivo es comparar, el color es secuencial de un solo matiz para magnitudes y categórico de pocos colores (k ≤ 8) para los tipos de día (D36).

## Métodos considerados y descartados

- **Prophet y modelos ARIMA/SARIMAX:** con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final (D23).
- **Redes neuronales (por ejemplo, LSTM):** quedan fuera del alcance por su costo y su menor interpretabilidad (D23).
