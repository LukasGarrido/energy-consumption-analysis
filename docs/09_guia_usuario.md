# Guía de usuario

Esta guía explica cómo instalar el proyecto, obtener los datos y reproducir el análisis desde cero, así como explorar los resultados tanto en el prototipo interactivo de Streamlit como en el panel de Power BI.

> Los pasos marcados como *(por crear)* corresponden a componentes que aún no existen en el repositorio.

---

## 1. Requisitos

| Requisito | Detalle |
|---|---|
| Python | 3.10, 3.11 o 3.12. Las versiones más recientes pueden dar problemas de instalación con algunas dependencias |
| Git | Para clonar el repositorio |
| Cuenta de Kaggle | Solo si se descarga el dataset con la API (opcional) |
| Sistema operativo | Windows, Linux o macOS |
| Power BI Desktop | Solo para ver el panel de Power BI (requiere Windows) |
| Navegador web | Para interactuar con el prototipo de Streamlit (Chrome, Edge, Firefox, etc.) |

Para verificar la versión de Python:

```bash
python --version
```

---

## 2. Instalación

### 2.1 Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/energy-consumption-analysis.git
cd energy-consumption-analysis
```

### 2.2 Crear el entorno virtual

```bash
python -m venv .venv
```

### 2.3 Activar el entorno virtual

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Linux / macOS | `source .venv/bin/activate` |

Cuando el entorno está activo, el terminal muestra `(.venv)` al inicio de la línea.

### 2.4 Instalar las dependencias

```bash
pip install -r requirements.txt
```

Incluye todas las librerías analíticas (`pandas`, `numpy`, `scikit-learn`, `xgboost`, `statsmodels`), de visualización (`matplotlib`, `seaborn`, `plotly`) y el motor de la aplicación interactiva (`streamlit`).

### 2.5 Instalar el proyecto en modo editable

Esto permite que los notebooks y módulos encuentren la carpeta `src/`:

```bash
pip install -e .
```

Solo se hace una vez. Gracias al modo editable, los cambios en los archivos de `src/` se reflejan sin reinstalar.

### 2.6 Parámetros del proyecto

Los parámetros están centralizados en `src/config.py`:

| Parámetro | Uso | Valor por defecto |
|---|---|---|
| `HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `SEMILLA` | Pronóstico | 24 h, [24, 48, 168], [24, 168], "2017-01-01", 42 |
| `K_MIN`, `K_MAX`, `TAMANO_MIN_GRUPO`, `SILUETA_RAZONABLE`, `SILUETA_DEBIL`, `MUESTRA_AGRUPAMIENTO` | Agrupamiento de perfiles diarios | 2 a 10 grupos, 5 %, 0.50, 0.26, 10,000 días |
| `UMBRAL_Z_MODIFICADO`, `TOLERANCIA_EPISODIO_DIAS` | Valores atípicos, días atípicos y contraste con episodios | 3.5 (Iglewicz y Hoaglin); la tolerancia está en `src/config.py` |
| `N_PLIEGUES`, `MESES_PLIEGUE` | Validación temporal en ventana móvil | 3 pliegues como mínimo (el notebook 04 usa 6), 12 meses por pliegue |

`REZAGOS_HORAS` no puede contener valores menores que `HORIZONTE_HORAS`: el código lanza un error para evitar usar información futura que no se tendría disponible al momento de pronosticar.

---

## 3. Obtención de los datos

Los datos crudos **no se incluyen en el repositorio**. Hay dos formas de obtenerlos y ambas dejan los archivos en `data/raw/`.

### Opción A: con la API de Kaggle

1. En Kaggle, ir a *Settings → API* y generar las credenciales siguiendo las instrucciones de la página.
2. Guardarlas donde indique Kaggle (normalmente en la carpeta `.kaggle` del usuario).
3. Ejecutar desde la raíz del proyecto:

```bash
kaggle datasets download -d robikscube/hourly-energy-consumption -p data/raw --unzip
```

### Opción B: descarga manual

1. Entrar a [Hourly Energy Consumption (Kaggle)](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption).
2. Descargar el conjunto de datos (botón *Download*).
3. Descomprimir los archivos CSV dentro de `data/raw/`.

### Verificación

`data/raw/` debe contener los 12 archivos por región (`PJME_hourly.csv`, `AEP_hourly.csv`, etc.) y el archivo combinado `pjm_hourly_est.csv`, que no se utiliza directamente.

---

## 4. Estructura del proyecto

| Carpeta o archivo | Contenido |
|---|---|
| `data/raw/` | Datos originales de Kaggle (no se versionan) |
| `data/processed/` | Datos limpios y series consolidadas en formato Parquet |
| `data/processed/powerbi/` | 17 tablas CSV normalizadas exportadas para Power BI y Streamlit |
| `notebooks/` | Notebooks de Jupyter, numerados en orden de ejecución (01 a 07) |
| `src/config.py` | Rutas y parámetros globales |
| `src/data_loader.py` | Lectura segura y validación de datos crudos y procesados |
| `src/cleaning.py` | Funciones de limpieza, deduplicación e interpolación |
| `src/features.py` | Día operativo, variables de calendario, rezagos y medias móviles |
| `src/modeling.py` | Particiones temporales, modelos basales y XGBoost, métricas (MASE) y ventana móvil |
| `src/profiles.py` | Extracción de perfiles diarios, normalización, silueta y agrupamiento |
| `src/anomalies.py` | Cálculo de residuos diarios, z modificado y contraste con episodios históricos |
| `src/plots.py` | Funciones auxiliares de graficado y estilos |
| `app/streamlit_app.py` | Punto de entrada del prototipo interactivo en Streamlit |
| `app/config.py` | Constantes, paleta Okabe-Ito y rutas de la app |
| `app/data_loader.py` | Carga con caché y tipado de datos para la app |
| `app/filtros.py` | Helpers de filtrado por región, estación y rango de fechas |
| `app/graficos.py` | Helpers de visualización y compatibilidad con Plotly |
| `app/paginas/` | Módulos individuales por página (resumen, patrones, tipos de día, regiones, anomalías, pronóstico) |
| `app/panel_pjm.pbix` | Archivo del panel de Power BI *(por crear)* |
| `reports/figures/` | Figuras y gráficos exportados listos para publicación |
| `docs/` | Documentación técnica modular del proyecto |

---

## 5. Orden de ejecución

Con el entorno activado, abre Jupyter desde la raíz del proyecto:

```bash
jupyter lab
```

Ejecuta los notebooks **en orden numérico estricto**, con *Restart & Run All*. Cada uno depende de los datos generados por los anteriores.

| Orden | Notebook | Qué hace | Archivos que genera | Estado |
|---|---|---|---|---|
| 1 | `01_exploracion.ipynb` | Revisa la estructura, calidad y convención horaria | Ninguno | Disponible |
| 2 | `02_limpieza.ipynb` | Limpia, interpola DST y valida formalmente | `data/processed/<REGION>_clean.parquet` y `consumo_horario.parquet` | Disponible |
| 3 | `03_analisis.ipynb` | Analiza patrones horarios, estacionalidad y comparativas | Figuras exploratorias | Disponible |
| 4 | `04_modelado.ipynb` | Entrena pronóstico de referencia a 24 h (XGBoost vs base) | `residuos_PJME.parquet` y `metricas_ventana_movil_PJME.parquet` | Disponible |
| 5 | `05_agrupamiento.ipynb` | Normaliza perfiles, evalúa silueta y agrupa tipos de día | `tipos_de_dia*.parquet` | Disponible |
| 6 | `06_anomalias.ipynb` | Detecta anomalías con z modificado y contrasta con eventos | `anomalias_*.parquet` | Disponible |
| 7 | `07_exportacion.ipynb` | Exporta dimensiones y tablas de hechos normalizadas | 17 archivos CSV en `data/processed/powerbi/` | Disponible |

> **Importante:** los parámetros `ALINEAR_HORA_CENTRAL` y `REGIONES_HORA_CENTRAL` deben mantener el mismo valor en los notebooks 05 y 07 para conservar la coherencia en las formas de los perfiles.

### Comprobaciones tras ejecutar

| Notebook | Qué debe verse |
|---|---|
| 02 | Las 12 regiones en `OK`, con 1,090,343 filas en total y cero vacíos |
| 02 | `AEP`: 121,273 filas originales, 4 duplicados unificados y 121,296 filas finales |
| 03 | 10 regiones vigentes en el periodo común 2013-06-01 → 2018-08-03 |
| 04 | XGBoost supera al base en los 6 pliegues de 12 meses, con MASE entre 0.72 y 0.87 (0.86 en la partición única) |
| 05 | Silueta evaluada para $k \in [2, 10]$ con umbrales 0.26 y 0.50. Con la configuración por defecto resulta k-medias con k = 2 y silueta 0.413 |
| 06 | 22 días atípicos de 2,191 y detección del huracán Sandy (2012-10-30) y del vórtice polar de 2014 |
| 07 | 17 archivos `.csv` presentes en `data/processed/powerbi/` junto con `diccionario_datos.csv` |

---

## 6. Cómo ver los resultados

El proyecto ofrece dos vías de visualización analítica que consumen las mismas tablas calculadas en `data/processed/powerbi/`: el prototipo interactivo en Streamlit y el panel en Power BI.

### 6.1 Prototipo interactivo en Streamlit

El prototipo en Streamlit permite explorar de inmediato los resultados en cualquier navegador web, sin requerir Power BI Desktop ni licencias propietarias.

#### Ejecución

1. Activa el entorno virtual:
   - En Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - En Linux / macOS: `source .venv/bin/activate`
2. Lanza la aplicación desde la raíz del proyecto:

```bash
streamlit run app/streamlit_app.py
```

La app se abrirá automáticamente en tu navegador predeterminado (por defecto en `http://localhost:8501`).

#### Estructura y navegación

La aplicación cuenta con una barra lateral izquierda de filtros globales y seis páginas:

1. **Resumen:** tarjetas de indicadores clave (regiones seleccionadas, días en el filtro, consumo medio, tipos de día, MAE y MASE medios de XGBoost), advertencia de días atípicos de PJME y línea de tendencia anual por región (solo años completos).
2. **Patrones:** mapa de calor 7 × 24 de consumo relativo (`MW_rel_medio`) con escala común para comparar regiones, perfiles diarios por tipo de calendario (laborable, fin de semana, festivo) y estacionalidad mensual.
3. **Tipos de día:** curvas horarias medias con bandas de dispersión interpercentil, calendario anual en mapa de dispersión, barras de porcentaje de días por tipo, línea de silueta frente a $k$ y tabla resumen de grupos.
4. **Regiones:** comparativa regional mediante gráfico de barras apiladas al 100 % (con interruptor entre historial completo y periodo común) y dispersión de indicadores estructurales (razón invierno/verano frente a amplitud diaria).
5. **Anomalías:** línea de tiempo de residuos porcentuales con eventos históricos sombreados, **deslizador interactivo de umbral $z$-score modificado** (recalcula en tiempo real sin modificar datos en disco), ranking de días con mayor desvío, tabla de episodios históricos y selector para ver el perfil horario real vs pronóstico en una ventana de $\pm 3$ días.
6. **Pronóstico:** métricas de validación por pliegue, gráfico comparativo de MAE por modelo, selector interactivo de métrica (MAE / MAPE) para desglosar el error por hora, mes y tipo de día, y gráfico temporal de real frente a pronóstico.

#### Comportamiento de los filtros

- **Filtro de región y estación:** aplican a todas las tablas que disponen de dichas dimensiones.
- **Filtro de fecha:** actúa sobre `hechos_diario`, `pronostico_horario` y `anomalias_dias`. Los gráficos que consumen tablas agregadas muestran una nota aclaratoria: *"Este gráfico no responde al filtro de fecha."*
- **Botón "Restablecer filtros":** restaura instantáneamente la selección de todas las regiones, las cuatro estaciones y el rango temporal completo.

---

### 6.2 Panel en Power BI Desktop

El panel interactivo en Power BI consume las tablas exportadas por el notebook 07 *(por crear)*:

1. Instalar Power BI Desktop (requiere Windows).
2. Abrir el archivo `app/panel_pjm.pbix`.
3. Si los orígenes de datos no se detectan automáticamente, actualizar la ruta de origen en *Transformar datos → Configuración del origen de datos* apuntando a la carpeta `data/processed/powerbi/` de tu repositorio local.

---

## 7. Solución de problemas

**`pip install` falla con un mensaje sobre versiones de Python.**
Alguna dependencia no soporta la versión de Python instalada. Usar Python 3.10 a 3.12.

**Error `No matching distribution found for ...`.**
Revisar que el nombre del paquete en `requirements.txt` esté bien escrito y que la línea no comience con un espacio o carácter inválido.

**En PowerShell no se activa el entorno virtual ("la ejecución de scripts está deshabilitada").**
Ejecutar una sola vez en una terminal con permisos estándar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**`ModuleNotFoundError: No module named 'app'` al ejecutar Streamlit.**
El archivo `app/streamlit_app.py` añade automáticamente la raíz del proyecto al `sys.path`. Asegúrate de lanzar el comando desde la raíz del repositorio (`streamlit run app/streamlit_app.py`).

**Aviso en Streamlit: "Faltan los siguientes archivos CSV en la carpeta de datos...".**
La aplicación se detiene si faltan tablas en `data/processed/powerbi/`. Ejecuta el notebook `07_exportacion.ipynb` con *Restart & Run All* para exportar las 17 tablas requeridas.

**El puerto 8501 de Streamlit ya está en uso.**
Puedes especificar otro puerto agregando la bandera `--server.port`:

```bash
streamlit run app/streamlit_app.py --server.port 8502
```

**`ModuleNotFoundError: No module named 'src'`.**
Falta instalar el proyecto en modo editable (`pip install -e .`) o el kernel de Jupyter no usa el entorno del proyecto.

**Los notebooks no encuentran los archivos de datos crudos.**
Verificar que los CSV estén descomprimidos en `data/raw/` y que Jupyter se haya abierto desde la raíz del proyecto.

**Los notebooks 03 a 06 no encuentran `consumo_horario.parquet`.**
Ejecutar previamente `02_limpieza.ipynb`.

**El notebook 06 no encuentra `residuos_PJME.parquet`.**
Ejecutar previamente `04_modelado.ipynb`.

**El kernel de Jupyter no usa el entorno del proyecto.**
Registrarlo ejecutando:

```bash
python -m ipykernel install --user --name energy-consumption --display-name "Python (energy-consumption)"
```

y seleccionarlo en Jupyter desde *Kernel → Change Kernel*.