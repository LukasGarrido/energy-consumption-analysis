# Métodos y herramientas

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
| Power BI Desktop | Panel interactivo final, importa los CSV de `data/processed/powerbi/` (decisión D4) |
| Streamlit | Prototipo opcional (`app/streamlit_app.py`) |
| Jupyter Notebook | Desarrollo y documentación del análisis |
| VS Code y Antigravity IDE | Edición de código |
| GitHub | Control de versiones y gestión de tareas |
| Obsidian | Registro de la documentación técnica y de las decisiones |

La reproducibilidad se apoya en una semilla fija (`SEMILLA = 42` en `src/config.py`) y en que todos los parámetros (rango de k, umbrales, pliegues) viven en ese mismo archivo.

## Métodos de ciencia de datos

| Método | Descripción | Estado |
|---|---|---|
| Limpieza de series de tiempo | Unificación de horas repetidas (promedio), reindexado a calendario horario, recorte de extremos, interpolación lineal de huecos de hasta 2 horas y validación (`src/cleaning.py`) | Hecho |
| Detección de valores atípicos aislados | z modificado de la desviación respecto del patrón esperado (> 3.5) con criterio de continuidad. Los valores de `DOM` y `PJMW` se conservan (decisión D2) | Por hacer |
| Análisis exploratorio | Estadística descriptiva, cobertura, duplicados, horas faltantes (con su causa), valores aislados frente a rachas y distribución | Hecho |
| Variables de calendario | Día operativo (`Datetime − 1 h`): fecha, hora (0 a 23), día de la semana, mes, estación, fin de semana y festivo (`src/features.py`, decisión D1) | Hecho |
| Normalización relativa | Consumo dividido entre el promedio de su región (`MW_rel`), para comparar formas | Hecho |
| Tendencia y estacionalidad | Media móvil de 365 días y descomposición STL | Hecho |
| Correlación entre regiones | Correlación de Pearson sobre el promedio diario (solo días de 24 horas) | Hecho |
| Agrupamiento de perfiles diarios | Cada día se representa con 24 valores divididos entre el promedio del día. Se comparan k-medias y Ward para k entre 2 y 10, con la silueta media sobre una muestra reproducible de 10,000 días. Se elige la mayor silueta entre las combinaciones con grupos de al menos el 5 % de los días. Se reporta la concordancia entre ambos métodos (índice de Rand ajustado) y la distancia de cada día al centro de su grupo (`src/profiles.py`) | Implementado (notebook 05), por ejecutar |
| Detección de días atípicos | Residuo diario en % de la predicción, a partir de los residuos fuera de muestra del pronóstico, se marca el día con z modificado > 3.5 (0.6745 · (x − mediana) / MAD). Incluye sensibilidad al umbral, comparación por estación y pliegue, y contraste con episodios con fuente (`src/anomalies.py`) | Implementado (notebook 06),por ejecutar |
| Pronóstico a 24 horas | XGBoost con variables de calendario, rezagos (24, 48 y 168 h) y medias móviles desplazadas, frente a dos modelos base | Hecho |
| Validación | División cronológica con control de fuga de datos y ventana móvil con entrenamiento creciente: 6 pliegues de 12 meses (mínimo 3), sin solapamiento, de modo que cada hora se predice una sola vez fuera de muestra | Implementada (notebook 04), por ejecutar |
| Métricas | MAE, RMSE y MAPE, MASE con la escala del pronóstico ingenuo estacional de 24 h (Hyndman y Koehler), menor que 1 si el modelo mejora al ingenuo | Implementadas |
| Exportación para el panel | Modelo en estrella en CSV (4 dimensiones, hechos y resultados de los notebooks 04 a 06) con validación de claves y diccionario de datos | Implementada (notebook 07), por ejecutar |

## Métodos de visualización

| Pregunta | Gráfico | Justificación perceptual |
|---|---|---|
| P1. Patrón hora por día de la semana | Mapa de calor 7 × 24, con la misma escala en todas las regiones | 168 valores de un vistazo, el color se complementa con líneas por tipo de calendario (laborable, fin de semana, festivo) para mayor precisión |
| P1. Elección de k | Líneas de la silueta frente a k, con los umbrales 0.26 y 0.50 | Posición sobre escala común, los k que no cumplen el tamaño mínimo se marcan |
| P1. Forma de cada tipo de día | Líneas con banda de dispersión (percentiles 10 y 90), en paneles con la misma escala | Posición sobre escala común, el canal más preciso |
| P1. Dónde cae cada tipo de día | Mapa de calor de calendario (año por día del año) con color categórico, y composición de cada grupo por día de la semana y mes | Muestra la ubicación de cada grupo en el año |
| P2. Mezcla de tipos de día por región | Barras apiladas al 100 %, en el historial completo y en el periodo común | Longitud sobre una línea base común, se evitan los gráficos circulares |
| P2. Comparación de regiones | Gráfico de dispersión con etiquetas: razón invierno/verano frente a amplitud diaria | Posición en dos ejes comunes |
| Tendencia y estacionalidad | Líneas en paneles múltiples con eje de tiempo compartido | Posición sobre escala común |
| P3. Días atípicos | Línea de tiempo con puntos resaltados y anotaciones, casos principales hora a hora (real frente a pronóstico) | Pocos puntos resaltados destacan sobre el resto |
| P3. Contraste con episodios | Tabla con el estado de cada episodio (coincide, sin coincidencia, fuera de rango), su fuente y si la fecha está verificada | Distingue lo no detectado de lo no evaluado |
| P4. Error del pronóstico | Barras del error por hora, mes y tipo de día, líneas del MAE por pliegue | Posición y longitud |
| Calidad de los datos | Barras de intervalos y mapa de calor | Muestran los periodos desiguales que condicionan las comparaciones |

### Páginas del panel (Power BI)

| Página | Pregunta | Contenido |
|---|---|---|
| Resumen | Panorama | Tarjetas (días, regiones, silueta, MAE y MASE, días atípicos) y tendencia anual |
| Patrones | P1, P2 | Mapa de calor 7 × 24, líneas por tipo de calendario y estacionalidad mensual |
| Tipos de día | P1 | Curvas con banda, calendario de color y frecuencia de cada tipo |
| Regiones | P2 | Mezcla de tipos de día y dispersión de regiones |
| Anomalías | P3 | Línea de tiempo, tabla de episodios y lista de días atípicos |
| Pronóstico | P4 | Error por hora, mes y tipo de día, y métricas por pliegue |

Filtros en todas las páginas: región, fecha y estación. La región y la estación actúan sobre todas las tablas la fecha, solo sobre las tablas diarias y horarias (las ya agregadas no responden a ella). El detalle del modelo de datos está en la sección 7 del notebook 07.

Principios de diseño: el canal de codificación se elige según la tarea (la posición sobre una escala común es el más preciso), las vistas en paneles múltiples comparten escala cuando el objetivo es comparar; el color es secuencial de un solo matiz para magnitudes y categórico de pocos colores (k ≤ 8) para los tipos de día.

## Métodos considerados y descartados

- **Prophet y modelos ARIMA/SARIMAX:** con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.
- **Redes neuronales (por ejemplo, LSTM):** quedan fuera del alcance por su costo y su menor interpretabilidad.