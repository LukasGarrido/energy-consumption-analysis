# Análisis visual de la demanda eléctrica horaria de la red PJM

Análisis de la demanda eléctrica horaria de 12 regiones de la red PJM (Estados Unidos, 1998–2018): tipos de día, diferencias entre regiones y episodios atípicos, apoyado en aprendizaje automático y comunicado mediante visualizaciones.

---

## Descripción

El dataset *Hourly Energy Consumption* suele usarse para pronosticar la demanda de una sola región. Este proyecto se centra en **caracterizar** cómo es la demanda: qué formas de día existen, en qué se diferencian las regiones y qué días se desvían de lo esperable. El pronóstico pasa a ser una referencia de lo esperable, y los resultados se comunican en un panel interactivo.

### Preguntas de investigación

| N.º | Pregunta | Tarea visual |
|---|---|---|
| P1 | ¿Qué tipos de día (formas de perfil diario) existen y cómo se distribuyen en el calendario? | Descubrir patrones |
| P2 | ¿En qué se diferencian las regiones por su mezcla de tipos de día y su estacionalidad? | Comparar |
| P3 | ¿Qué días se desvían de la demanda esperable y a qué episodios corresponden? | Localizar anomalías |
| P4 | ¿Cuándo y cuánto falla un pronóstico a 24 horas? | Evaluar |

### Aporte diferencial

1. **De pronosticar a caracterizar:** el aprendizaje automático (agrupamiento de perfiles diarios y detección de anomalías) se usa para obtener información, no solo precisión de pronóstico.
2. **Comparación entre 12 regiones con calidad de datos documentada:** periodos desiguales, hora de fin de intervalo, cambios de horario y continuidad entre regiones.
3. **Diseño de visualización justificado:** cada gráfico se asocia a una tarea y a un canal perceptual, y se entrega en un panel interactivo en Power BI.

---

## Datos

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption), de Rob Mulla, con datos de PJM Interconnection.
- **Contenido:** demanda horaria en MW de 12 regiones (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load), entre 1998-04-01 y 2018-08-03.
- **Volumen:** 1,090,167 filas originales, 1,090,343 tras la limpieza.
- **Periodo común:** no existe uno para las 12 regiones, 10 comparten 2013-06-01 → 2018-08-03.

Los datos crudos **no se incluyen en el repositorio**, se descargan desde Kaggle (ver [inicio rápido](#inicio-rápido)).

---

## Resultados preliminares

| Hallazgo | Resultado |
|---|---|
| Calidad de los datos | Sin nulos, cobertura de 99.98 % a 99.99 %, 40 duplicados y 217 horas faltantes, casi todos por cambios de horario |
| Limpieza | Las 12 regiones superan la validación, se interpoló el 0.02 % de las horas |
| Ciclo diario | Mínimo hacia las 4–5 h y máximo entre las 18 y las 20 h |
| Calendario | El fin de semana consume entre un 4 % y un 14 % menos que un laborable, un festivo, cerca de un 5 % menos |
| Estacionalidad | Dos máximos anuales (verano e invierno), `EKPC` y `PJMW` son invernales, `COMED`, `DUQ`, `DEOK` y `PJME` veraniegas |
| Pronóstico a 24 h (`PJME`) | XGBoost: MAE de 1,862 MW frente a 2,300 MW del modelo base (−19.0 %) |

---

## Inicio rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/energy-consumption-analysis.git
cd energy-consumption-analysis

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/bin/activate         # Linux / macOS

# 3. Instalar dependencias y el proyecto
pip install -r requirements.txt
pip install -e .

# 4. Descargar los datos (requiere la API de Kaggle) o colocarlos a mano en data/raw/
kaggle datasets download -d robikscube/hourly-energy-consumption -p data/raw --unzip

# 5. Abrir los notebooks
jupyter lab
```

Ejecuta los notebooks **en orden numérico**, con *Restart & Run All*. La guía completa, con las comprobaciones esperadas y la solución de problemas, está en [docs/09_guia_usuario.md](docs/09_guia_usuario.md). Se recomienda Python 3.10 a 3.12.

---

## Estructura del repositorio

```text
├── app/
│   ├── streamlit_app.py          # Prototipo en Streamlit (opcional)
│   └── panel_pjm.pbix            # Panel en Power BI (por crear)
├── data/
│   ├── raw/                      # Datos crudos (.gitkeep; excluidos por .gitignore)
│   └── processed/                # Datos limpios y tablas para el panel (.gitkeep)
├── docs/                         # Documentación técnica modular (compatible con Obsidian)
│   ├── 00_indice.md              # Índice general de la documentación
│   ├── 01_objetivo.md            # Problema, preguntas y objetivos
│   ├── 02_base_de_datos.md       # Dataset, calidad, reglas de preprocesamiento y limpieza
│   ├── 03_metodos_y_herramientas.md # Herramientas y métodos de datos y de visualización
│   ├── 04_metodologia_desarrollo.md # Fases del proyecto y flujo de notebooks
│   ├── 05_resultados_esperados.md # Entregables y resultados obtenidos
│   ├── 06_plan_proyecto.md       # Métricas, recursos, cronograma y riesgos
│   ├── 07_casos_de_uso.md        # Historias de usuario y estado
│   ├── 08_modelo.md              # Pronóstico, agrupamiento y detección de anomalías
│   ├── 09_guia_usuario.md        # Guía paso a paso de uso y reproducción
│   ├── 10_referencias.md         # Bibliografía y afirmaciones que respalda
│   └── 11_conceptos.md           # Conceptos teóricos explicados para este proyecto
├── notebooks/                    # Cuadernos Jupyter en orden de ejecución
│   ├── 01_exploracion.ipynb      # Exploración inicial (EDA) y calidad de datos
│   ├── 02_limpieza.ipynb         # Limpieza y tratamiento de series de tiempo
│   ├── 03_analisis.ipynb         # Patrones, estacionalidad, regiones y picos
│   ├── 04_modelado.ipynb         # Pronóstico de referencia a 24 horas
│   ├── 05_agrupamiento.ipynb     # Agrupamiento de perfiles diarios
│   ├── 06_anomalias.ipynb        # Detección de días atípicos
│   └── 07_exportacion.ipynb      # Tablas para el panel
├── reports/
│   ├── figures/                  # Figuras y gráficos exportados
│   └── templates/                # Plantillas y formatos de informes (PDF, documentos)
├── src/                          # Módulos Python reutilizables
│   ├── __init__.py               # Inicialización del paquete
│   ├── anomalies.py              # Residuos y días atípicos
│   ├── cleaning.py               # Limpieza de datos
│   ├── config.py                 # Rutas y parámetros del proyecto
│   ├── data_loader.py            # Funciones de carga y lectura de datos
│   ├── features.py               # Variables de calendario, rezagos y medias móviles
│   ├── modeling.py               # División, modelos, métricas y comparación
│   ├── plots.py                  # Utilidades y funciones de graficado
│   └── profiles.py               # Perfiles diarios y agrupamiento
├── .gitignore                    # Configuración de exclusiones de Git
├── AGENTS.md                     # Directrices para agentes de IA y colaboradores
├── LICENSE                       # Licencia del proyecto
├── pyproject.toml                # Configuración de empaquetado del proyecto
├── README.md                     # Descripción general del repositorio
└── requirements.txt              # Dependencias del proyecto
```

---

## Documentación

La documentación completa está en [`docs/`](docs/00_indice.md):

- [Índice de documentación](docs/00_indice.md)
- [01. Objetivo del análisis](docs/01_objetivo.md)
- [02. Base de datos (dataset)](docs/02_base_de_datos.md)
- [03. Métodos y herramientas](docs/03_metodos_y_herramientas.md)
- [04. Metodología para el desarrollo](docs/04_metodologia_desarrollo.md)
- [05. Resultados esperados](docs/05_resultados_esperados.md)
- [06. Plan del proyecto](docs/06_plan_proyecto.md)
- [07. Casos de uso](docs/07_casos_de_uso.md)
- [08. Documentación del modelo](docs/08_modelo.md)
- [09. Guía de usuario](docs/09_guia_usuario.md)
- [10. Referencias](docs/10_referencias.md)
- [11. Conceptos teóricos](docs/11_conceptos.md)

---

## Tecnologías

Python (pandas, NumPy, scikit-learn, XGBoost, statsmodels), Jupyter, Power BI, Matplotlib y Seaborn, GitHub y Obsidian. El detalle está en [docs/03_metodos_y_herramientas.md](docs/03_metodos_y_herramientas.md).

---

## Limitaciones

- El dataset no incluye temperatura, el principal determinante de la demanda: los episodios atípicos se interpretan por coincidencia con eventos.
- Los tipos de día pueden resultar con una estructura débil, porque los perfiles diarios forman en parte un continuo.
- Los datos llegan hasta 2018 y pueden no representar la demanda actual.

---

## Licencia

Este proyecto está bajo la licencia indicada en el archivo [LICENSE](LICENSE). Los datos pertenecen a PJM Interconnection y a sus autores. 
