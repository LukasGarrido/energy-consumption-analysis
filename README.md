# Análisis de Consumo Horario de Energía

Proyecto de ciencia de datos enfocado en el análisis, exploración y modelado del consumo eléctrico horario de la red de transmisión eléctrica **PJM Interconnection** (EE. UU.), abarcando múltiples regiones y series temporales históricas (2002–2018).

---

## Visión General del Proyecto

El objetivo principal es identificar patrones temporales en la demanda de energía (por hora, día de la semana y estacionalidad anual), evaluar tendencias de largo plazo, detectar periodos críticos de demanda pico y comparar el comportamiento entre distintas regiones geográficas.

### Aspectos Clave

- **Conjunto de Datos:** Registros horarios de consumo de energía en megavatios (MW) procedentes de PJM Interconnection (Kaggle).
- **Enfoque Metodológico:** Análisis exploratorio de datos (EDA), tratamiento de series de tiempo (limpieza de horas duplicadas/faltantes por cambios de huso horario), agregaciones temporales, descomposición de estacionalidad/tendencia y pronósticos de demanda.
- **Visualización:** Generación de gráficos analíticos e interactivos para facilitar la interpretación de patrones y anomalías en la red.
- **Herramientas Principales:** Python (`pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`), Jupyter Notebooks y Obsidian para documentación técnica.

---

## Documentación Detallada

La documentación modular del proyecto se encuentra organizada en el directorio [`docs/`](docs/00_indice.md):

- [Índice de Documentación](docs/00_indice.md)
- [01. Objetivo del Análisis](docs/01_objetivo.md)
- [02. Base de Datos (Dataset)](docs/02_base_de_datos.md)
- [03. Métodos y Herramientas](docs/03_metodos_y_herramientas.md)
- [04. Metodología para el Desarrollo](docs/04_metodologia_desarrollo.md)
- [05. Resultados Esperados](docs/05_resultados_esperados.md)
- [06. Referencias](docs/06_referencias.md)

---

## Estructura del Repositorio

```text
├── data/          # Datos crudos y procesados
├── notebooks/     # Cuadernos Jupyter para exploración y análisis
├── src/           # Módulos y scripts de soporte en Python
├── app/           # Aplicación o dashboard de visualización
├── reports/       # Reportes generados y figuras
├── docs/          # Documentación detallada del proyecto (compatible con Obsidian)
├── requirements.txt
└── README.md
```
