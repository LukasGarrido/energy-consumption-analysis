<div align="center">

# Análisis visual de la demanda eléctrica horaria de la red PJM

Análisis de la demanda eléctrica horaria de 12 regiones de la red PJM (Estados Unidos, 1998–2018): tipos de día, diferencias entre regiones y episodios atípicos, apoyado en aprendizaje automático y comunicado mediante visualizaciones.

</div>

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
3. **Diseño de visualización justificado:** cada gráfico se asocia a una tarea y a un canal perceptual, y se entrega en un panel interactivo en Power BI complementado por un prototipo en Streamlit.

---

## Datos

- **Fuente:** [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption), de Rob Mulla, con datos de PJM Interconnection.
- **Contenido:** demanda horaria en MW de 12 regiones (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW y PJM_Load), entre 1998-04-01 y 2018-08-03.
- **Volumen:** 1,090,167 filas originales, 1,090,343 tras la limpieza.
- **Convención horaria:** `Datetime` marca el **final** de la hora. Las variables de calendario se calculan desde `Datetime − 1 h` (día operativo).
- **Periodo común:** no existe uno para las 12 regiones, 10 comparten 2013-06-01 → 2018-08-03.

Los datos crudos **no se incluyen en el repositorio**, se descargan desde Kaggle (ver [inicio rápido](#inicio-rápido)).

---

## Resultados

Las cifras horarias y las del pronóstico se calcularon con `Datetime` como hora de fin y se actualizan con el día operativo.

| Hallazgo | Resultado |
|---|---|
| Calidad de los datos | Sin nulos, cobertura de 99.98 % a 99.99 %, 40 duplicados y 217 horas faltantes, casi todos por cambios de horario |
| Limpieza | Las 12 regiones superan la validación (1,090,343 filas), se interpoló el 0.02 % de las horas |
| Convención horaria | `Datetime` marca el final de la hora, el calendario usa el día operativo |
| Hora de `COMED` | Su curva llega una hora más tarde que la del resto: es lo esperable si las series están en hora del este y `COMED` es una zona de hora central |
| Ciclo diario | Mínimo hacia las 3–4 h y máximo entre las 17 y las 19 h |
| Calendario | El fin de semana consume entre un 3.9 % y un 13.9 % menos que un laborable (≈ −9 % en promedio), un festivo cerca de un 5 % menos |
| Estacionalidad | Dos máximos anuales (verano e invierno), `EKPC` y `PJMW` son invernales, `COMED`, `DUQ`, `DEOK` y `PJME` veraniegas |
| Pronóstico a 24 h (`PJME`) | XGBoost: MAE de 1,862 MW frente a 2,300 MW del modelo base (−19.1 %), MASE de 0.86 (0.72 a 0.87 en ventana móvil de 6 pliegues) |
| Tipos de día y anomalías | 2 tipos estacionales (k = 2, silueta 0.413: temporada fría y verano); 22 días atípicos en PJME (z modificado > 3.5), con 5 episodios contrastados |

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

Ejecuta los notebooks **en orden numérico (01 a 03)**, con *Restart & Run All*. Posteriormente, ejecuta el script de exportación (`python src/export.py`) para generar las 17 tablas requeridas por Power BI y Streamlit. La guía completa, con las comprobaciones esperadas y la solución de problemas, está en [docs/09_guia_usuario.md](docs/09_guia_usuario.md). Se recomienda Python 3.10 a 3.12.

### Ejecutar el prototipo de Streamlit

Una vez ejecutados los notebooks y el script de exportación, la app puede levantarse directamente desde la raíz del proyecto:

```bash
# Opción 1: Generar o actualizar las tablas analíticas
python src/export.py

# Opción 2: Lanzar la aplicación interactiva
streamlit run app/streamlit_app.py
```

La app lee las tablas de `data/processed/powerbi/` sin recalcular nada. Si algún CSV falta, indica cuál y recuerda ejecutar `python src/export.py`.

---

## Estructura del repositorio

```text
├── app/
│   ├── streamlit_app.py          # Punto de entrada del prototipo Streamlit
│   ├── config.py                 # Constantes, paleta Okabe-Ito y resolución de rutas
│   ├── data_loader.py            # Carga con caché y conversiones de tipo
│   ├── estilos.py                # Mejoras visuales y diseño adaptativo (modo claro/oscuro)
│   ├── filtros.py                # Helpers de filtrado local y por módulo
│   ├── graficos.py               # Helpers de color y compatibilidad de API de Streamlit
│   ├── paginas/
│   │   ├── __init__.py
│   │   ├── resumen.py            # Tarjetas de indicadores y tendencia anual
│   │   ├── patrones.py           # Mapa de calor, curvas por tipo y estacionalidad mensual
│   │   ├── tipos_de_dia.py       # Curvas con bandas, calendario, barras y silueta
│   │   ├── regiones.py           # Barras apiladas y dispersión de indicadores
│   │   ├── anomalias.py          # Línea de tiempo, episodios y caso hora a hora
│   │   └── pronostico.py         # Métricas, error desglosado y real vs. pronóstico
│   └── panel_pjm.pbix            # Panel en Power BI (en desarrollo)
├── data/
│   ├── raw/                      # Datos crudos (.gitkeep, excluidos por .gitignore)
│   └── processed/                # Datos limpios y resultados (.gitkeep)
│       └── powerbi/              # 17 tablas CSV y diccionario de datos (generadas por src/export.py)
├── docs/                         # Documentación técnica modular (compatible con Obsidian)
│   ├── 00_indice.md              # Índice general de la documentación
│   ├── 01_objetivo.md            # Problema, preguntas y objetivos
│   ├── 02_base_de_datos.md       # Dataset, calidad, reglas de preprocesamiento y limpieza
│   ├── 03_metodos_y_herramientas.md # Herramientas y métodos de datos y de visualización
│   ├── 04_metodologia_desarrollo.md # Fases, flujo de notebooks y decisiones de diseño
│   ├── 05_resultados_esperados.md # Entregables y resultados obtenidos
│   ├── 06_plan_proyecto.md       # Métricas, recursos, cronograma y riesgos
│   ├── 07_casos_de_uso.md        # Historias de usuario y estado
│   ├── 08_modelo.md              # Pronóstico, agrupamiento y detección de anomalías
│   ├── 09_guia_usuario.md        # Guía paso a paso de uso y reproducción
│   ├── 10_referencias.md         # Bibliografía y afirmaciones que respalda
│   ├── 11_conceptos.md           # Conceptos teóricos explicados para este proyecto
│   └── 12_bitacora_decisiones.md # Registro histórico de decisiones del proyecto
├── notebooks/                    # Cuadernos Jupyter en orden de ejecución
│   ├── 01_datos.ipynb            # Exploración inicial (EDA), calidad de datos, convención horaria y limpieza
│   ├── 02_patrones.ipynb         # Patrones horarios/estacionales y agrupamiento de tipos de día
│   └── 03_pronostico_anomalias.ipynb # Pronóstico de referencia (XGBoost vs base) y detección de anomalías
├── src/                          # Módulos Python reutilizables por los notebooks
│   ├── __init__.py               # Inicialización del paquete
│   ├── anomalies.py              # Residuo diario, z modificado y contraste con episodios
│   ├── cleaning.py               # Limpieza de series, deduplicación e interpolación
│   ├── config.py                 # Rutas y parámetros globales del proyecto
│   ├── data_loader.py            # Funciones de carga y lectura de datos
│   ├── export.py                 # Exportación del modelo dimensional (17 tablas CSV para Power BI)
│   ├── features.py               # Día operativo, variables de calendario, rezagos y medias móviles
│   ├── modeling.py               # Partición temporal, modelos XGBoost/base, métricas y ventana móvil
│   └── profiles.py               # Perfiles diarios, elección de k y agrupamiento
├── .env.example                  # Plantilla de variables de entorno
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
- [12. Bitácora de decisiones](docs/12_bitacora_decisiones.md)

---

## Tecnologías

El proyecto se desarrolla utilizando un ecosistema de análisis de datos, modelado, visualización y gestión:

- **Procesamiento y Análisis de Datos:** Python, `pandas`, `numpy`, `scipy`, `pyarrow`.
- **Aprendizaje Automático y Modelado:** `scikit-learn` (agrupamiento k-medias y Ward, métricas), `xgboost` (pronóstico de referencia a 24 horas), `statsmodels` (descomposición STL).
- **Utilidades y Datos:** `holidays` (festivos federales de EE. UU.), `kagglehub` (descarga y gestión de datasets).
- **Visualización y Presentación:** `Plotly`, `Matplotlib`, `Seaborn`, Streamlit (prototipo interactivo), Power BI Desktop (panel analítico en modelo en estrella).
- **Entorno y Documentación:** Jupyter Notebook / JupyterLab, Git y GitHub (control de versiones), Obsidian (documentación técnica y bitácora de decisiones).

El detalle completo de métodos y herramientas está en [docs/03_metodos_y_herramientas.md](docs/03_metodos_y_herramientas.md).

---

## Limitaciones

- El dataset no incluye temperatura, el principal determinante de la demanda: los episodios atípicos se interpretan por coincidencia con eventos.
- Los tipos de día pueden resultar con una estructura débil, porque los perfiles diarios forman en parte un continuo.
- El pronóstico y la detección de anomalías se hacen solo para `PJME`.
- La curva de `COMED` llega una hora más tarde que la del resto, la comparación de formas de día entre regiones depende de si se alinea (parámetro `ALINEAR_HORA_CENTRAL`).
- Los datos llegan hasta 2018 y pueden no representar la demanda actual.

---

## Licencia

Este proyecto está bajo la licencia indicada en el archivo [LICENSE](LICENSE). Los datos pertenecen a PJM Interconnection y a sus autores.
