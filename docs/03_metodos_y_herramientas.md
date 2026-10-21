# Métodos y Herramientas para Visualización y Ciencia de Datos

---

[← Volver al Índice](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md)

---

### Herramientas
- **Obsidian:** registro de la documentación técnica y de las decisiones del análisis.
- **VS Code y Antigravity IDE:** editores de código para el desarrollo del proyecto.
- **Python:** Lenguaje principal para el procesamiento, análisis y modelado de datos, aprovechando su ecosistema de librerías (`pandas`, `NumPy`, `Matplotlib`, `Seaborn`, `Plotly`, `statsmodels`, `holidays`, `XGBoost` y `Streamlit`).
- **Jupyter Notebook:** desarrollo y documentación del análisis paso a paso.
- **GitHub:** control de versiones y gestión del código del proyecto.

### Métodos
- **Análisis exploratorio de datos (EDA):** estadística descriptiva, detección de nulos, duplicados y valores atípicos.
- **Preparación de series de tiempo:** conversión de fechas, ordenamiento, tratamiento de horas faltantes y duplicadas por cambios de horario.
- **Ingeniería de variables temporales:** hora, día de la semana, mes, estación del año y día festivo.
- **Agregaciones temporales:** promedios diarios, mensuales y anuales para resumir y visualizar.
- **Análisis de estacionalidad y tendencia:** medias móviles y descomposición de la serie (utilizando `statsmodels`).
- **Visualización:** gráficos de líneas, mapas de calor (hora por día de la semana), diagramas de caja y comparaciones entre regiones, en versiones estáticas e interactivas.
- **Pronóstico:** Implementación y ajuste de un modelo predictivo supervisado basado en **XGBoost** (_Extreme Gradient Boosting_) evaluado sobre las características temporales e históricas extraídas.

---

[← Volver al Índice](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md)
