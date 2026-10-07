# Análisis de Consumo Horario de Energía

Proyecto de ciencia y visualización de datos sobre el consumo eléctrico horario de la red PJM.

## Dataset

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)
- **Autor:** Rob Mulla
- **Contenido:** consumo horario en megavatios (MW) de distintas regiones de PJM Interconnection (Estados Unidos), aproximadamente entre 2002 y 2018.
- **Regiones:** AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load.
- **Formato:** un CSV por región con las columnas `Datetime` y `<REGION>_MW`.

## Estructura del repositorio

```
energy-consumption-analysis/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── raw/               # CSVs originales de Kaggle (ignorados por git)
│   ├── interim/           # Datos parcialmente procesados
│   └── processed/         # Datos finales listos para analizar/visualizar
│
├── notebooks/             # Jupyter notebooks, numerados en orden de lectura
│
├── src/                   # Código Python reutilizable
│
├── app/                   # Visualización final (por definir)
│
└── reports/
    └── figures/           # Imágenes exportadas
```