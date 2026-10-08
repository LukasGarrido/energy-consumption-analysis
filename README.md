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
- [06. Plan del Proyecto](docs/06_plan_proyecto.md)
- [07. Casos de Uso](docs/07_casos_de_uso.md)
- [08. Documentación del Modelo](docs/08_modelo.md)
- [09. Guía de Usuario](docs/09_guia_usuario.md)
- [10. Referencias](docs/10_referencias.md)

---

## Estructura del Repositorio

```text
├── app/
│   └── index.html                # Aplicación o dashboard de visualización
├── data/
│   ├── raw/                      # Datos crudos (.gitkeep; excluidos por .gitignore)
│   ├── interim/                  # Datos en etapas intermedias de procesamiento
│   └── processed/                # Datos procesados y limpios para análisis
├── docs/                         # Documentación técnica modular (compatible con Obsidian)
│   ├── 00_indice.md              # Índice general de la documentación
│   ├── 01_objetivo.md            # Objetivos del análisis
│   ├── 02_base_de_datos.md       # Descripción y metadatos del dataset
│   ├── 03_metodos_y_herramientas.md # Herramientas, tecnologías y métodos
│   ├── 04_metodologia_desarrollo.md # Metodología y fases del proyecto
│   ├── 05_resultados_esperados.md # Entregables y expectativas
│   ├── 06_plan_proyecto.md       # Alcance, cronograma, recursos y riesgos
│   ├── 07_casos_de_uso.md        # Historias de usuario y criterios de aceptación
│   ├── 08_modelo.md              # Especificaciones y métricas del modelo
│   ├── 09_guia_usuario.md        # Guía paso a paso de uso y reproducción
│   └── 10_referencias.md         # Bibliografía y referencias bibliográficas
├── notebooks/                    # Cuadernos Jupyter en orden de ejecución
│   ├── 01_exploracion.ipynb      # Exploración inicial (EDA) y calidad de datos
│   ├── 02_limpieza.ipynb         # Limpieza y tratamiento de series de tiempo
│   ├── 03_analisis.ipynb         # Análisis de patrones, estacionalidad y regiones
│   └── 04_modelado.ipynb         # Modelado y pronóstico de demanda
├── reports/
│   └── figures/                  # Figuras y gráficos exportados
├── src/                          # Módulos Python reutilizables
│   ├── __init__.py
│   ├── data_loader.py            # Funciones de carga y lectura de datos
│   ├── features.py               # Extracción e ingeniería de características
│   └── plots.py                  # Utilidades y funciones de graficado
├── .gitignore                    # Configuración de exclusiones de Git
├── AGENTS.md                     # Directrices para agentes de IA y colaboradores
├── LICENSE                       # Licencia del proyecto
├── README.md                     # Descripción general del repositorio
└── requirements.txt              # Dependencias del proyecto
```

