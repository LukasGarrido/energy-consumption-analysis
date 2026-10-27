# Métodos y herramientas

## Herramientas

| Herramienta | Uso |
|---|---|
| Python (pandas, NumPy) | Procesamiento de los datos y cálculo de indicadores |
| scikit-learn | Agrupamiento de perfiles diarios y métricas de validación (silueta) |
| XGBoost | Modelo de pronóstico de referencia |
| statsmodels | Descomposición STL de la serie |
| holidays | Festivos federales de EE. UU. para la variable `es_festivo` |
| pyarrow | Lectura y escritura de archivos parquet |
| Matplotlib y Seaborn | Gráficos exploratorios en los notebooks |
| Power BI | Panel interactivo final |
| Jupyter Notebook | Desarrollo y documentación del análisis |
| VS Code y Antigravity IDE | Edición de código |
| GitHub | Control de versiones y gestión de tareas |
| Obsidian | Registro de la documentación técnica y de las decisiones |

## Métodos de ciencia de datos

| Método | Descripción | Estado |
|---|---|---|
| Limpieza de series de tiempo | Unificación de horas repetidas (promedio), reindexado a calendario horario, recorte de extremos, interpolación lineal de huecos de hasta 2 horas y validación | Hecho |
| Detección de valores atípicos aislados | z modificado de la desviación respecto del patrón esperado (> 3.5) con criterio de continuidad | Por hacer |
| Análisis exploratorio | Estadística descriptiva, cobertura, duplicados, horas faltantes y distribución | Hecho |
| Variables de calendario | Hora, día de la semana, mes, estación, fin de semana y festivo | Hecho |
| Normalización relativa | Consumo dividido entre el promedio de su región (`MW_rel`), para comparar formas | Hecho |
| Tendencia y estacionalidad | Media móvil de 365 días y descomposición STL | Hecho |
| Correlación entre regiones | Correlación de Pearson sobre el promedio diario | Hecho |
| Agrupamiento de perfiles diarios | Cada día se representa con 24 valores normalizados por el promedio del día. Se comparan k-medias y agrupamiento jerárquico (Ward) para k entre 2 y 10, y se elige k con la silueta media | Por hacer |
| Detección de días atípicos | Residuos fuera de muestra del pronóstico; se marca el día con z modificado > 3.5 | Por hacer |
| Pronóstico a 24 horas | XGBoost con variables de calendario, rezagos (24, 48 y 168 h) y medias móviles desplazadas, frente a dos modelos base | Hecho (una partición); la validación en ventana móvil queda por hacer |
| Validación | División cronológica con control de fuga de datos; ampliación a ventana móvil con al menos 3 pliegues | Parcial |
| Métricas | MAE, RMSE y MAPE; MASE para comparar con el pronóstico ingenuo | MAE, RMSE y MAPE hechos; MASE por hacer |

## Métodos de visualización

| Pregunta | Gráfico | Justificación perceptual |
|---|---|---|
| P1. Patrón hora por día de la semana | Mapa de calor 7 × 24, con la misma escala en todas las regiones | 168 valores de un vistazo; el color se complementa con líneas para mayor precisión |
| P1. Forma de cada tipo de día | Líneas con banda de dispersión | Posición sobre escala común, el canal más preciso |
| P1. Dónde cae cada tipo de día | Mapa de calor de calendario con color categórico | Muestra la ubicación de cada grupo en el año |
| P2. Mezcla de tipos de día por región | Barras apiladas al 100 % | Longitud sobre una línea base común; se evitan los gráficos circulares |
| P2. Comparación de regiones | Gráfico de dispersión con etiquetas | Posición en dos ejes comunes |
| Tendencia y estacionalidad | Líneas en paneles múltiples con eje de tiempo compartido | Posición sobre escala común |
| P3. Días atípicos | Línea de tiempo con puntos resaltados y anotaciones | Pocos puntos resaltados destacan sobre el resto |
| P4. Error del pronóstico | Líneas y barras por hora, mes y tipo de día | Posición y longitud |
| Calidad de los datos | Barras de intervalos y mapa de calor | Muestran los periodos desiguales que condicionan las comparaciones |

Principios de diseño: el canal de codificación se elige según la tarea (la posición sobre una escala común es el más preciso); las vistas en paneles múltiples comparten escala cuando el objetivo es comparar; el color es secuencial de un solo matiz para magnitudes y categórico de pocos colores (k ≤ 8) para los tipos de día.

## Métodos considerados y descartados

- **Prophet y modelos ARIMA/SARIMAX:** con datos horarios y varias estacionalidades simultáneas son lentos y complejos de ajustar, y el pronóstico es una referencia y no el producto final.
- **Redes neuronales (por ejemplo, LSTM):** quedan fuera del alcance por su costo y su menor interpretabilidad.