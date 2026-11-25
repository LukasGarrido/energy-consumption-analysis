<div align="center">

# Guía de usuario

*Análisis de Consumo Horario de Energía (Red PJM)*

</div>

---

## Índice de contenidos

- [1. Requisitos](#1-requisitos)
- [2. Instalación](#2-instalación)
  - [2.1 Clonar el repositorio](#21-clonar-el-repositorio)
  - [2.2 Crear el entorno virtual](#22-crear-el-entorno-virtual)
  - [2.3 Activar el entorno virtual](#23-activar-el-entorno-virtual)
  - [2.4 Instalar las dependencias](#24-instalar-las-dependencias)
  - [2.5 Instalar el proyecto en modo editable](#25-instalar-el-proyecto-en-modo-editable)
  - [2.6 Parámetros del proyecto](#26-parámetros-del-proyecto)
- [3. Obtención de los datos](#3-obtención-de-los-datos)
  - [Opción A: con la API de Kaggle](#opción-a-con-la-api-de-kaggle)
  - [Opción B: descarga manual](#opción-b-descarga-manual)
  - [Verificación](#verificación)
- [4. Estructura del proyecto](#4-estructura-del-proyecto)
- [5. Orden de ejecución](#5-orden-de-ejecución)
  - [Comprobaciones tras ejecutar](#comprobaciones-tras-ejecutar)
- [6. Cómo ver los resultados](#6-cómo-ver-los-resultados)
  - [6.1 Prototipo interactivo en Streamlit](#61-prototipo-interactivo-en-streamlit)
  - [6.2 Panel en Power BI Desktop](#62-panel-en-power-bi-desktop)
- [7. Solución de problemas](#7-solución-de-problemas)

---


Esta guía explica cómo instalar el proyecto, obtener los datos y reproducir el análisis desde cero, así como explorar los resultados tanto en el prototipo interactivo de Streamlit como en el panel de Power BI.

> El archivo de Power BI (`app/panel_pjm.pbix`) está en desarrollo. El resto de los pasos corresponde a componentes que ya existen.

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
| `N_PLIEGUES`, `MESES_PLIEGUE` | Validación temporal en ventana móvil | 3 pliegues como mínimo (`03_pronostico_anomalias.ipynb` usa 6), 12 meses por pliegue |

`ALINEAR_HORA_CENTRAL` y `REGIONES_HORA_CENTRAL` (decisión D7) deben tener el mismo valor en `02_patrones.ipynb` y en `src/export.py` (decisión D41). Los cortes de silueta (0.50 y 0.26) siguen pendientes de alinear con Kaufman y Rousseeuw (D28).

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
| `data/processed/powerbi/` | 17 tablas CSV normalizadas y diccionario de datos exportados para Power BI y Streamlit |
| `notebooks/` | Notebooks de Jupyter, numerados en orden de ejecución (01 a 03) |
| `src/config.py` | Rutas y parámetros globales |
| `src/data_loader.py` | Lectura segura y validación de datos crudos y procesados |
| `src/cleaning.py` | Funciones de limpieza, deduplicación e interpolación |
| `src/features.py` | Día operativo, variables de calendario, rezagos y medias móviles |
| `src/modeling.py` | Particiones temporales, modelos basales y XGBoost, métricas (MASE) y ventana móvil |
| `src/profiles.py` | Extracción de perfiles diarios, normalización, silueta y agrupamiento |
| `src/anomalies.py` | Cálculo de residuos diarios, z modificado y contraste con episodios históricos |
| `src/export.py` | Script de exportación del modelo dimensional (17 tablas CSV para Power BI y Streamlit) |
| `src/plots.py` | Funciones auxiliares de graficado y estilos |
| `app/streamlit_app.py` | Punto de entrada del prototipo interactivo en Streamlit |
| `app/config.py` | Constantes, paleta Okabe-Ito y rutas de la app |
| `app/data_loader.py` | Carga con caché y tipado de datos para la app |
| `app/filtros.py` | Helpers de filtrado por región, estación y rango de fechas |
| `app/graficos.py` | Helpers de visualización y compatibilidad con Plotly |
| `app/paginas/` | Módulos individuales por página (resumen, patrones, tipos de día, regiones, anomalías, pronóstico) |
| `app/panel_pjm.pbix` | Archivo del panel de Power BI *(en desarrollo)* |
| `Dockerfile`, `compose.yaml`, `.dockerignore` | Contenedor de la app de Streamlit y su servicio de Docker Compose |
| `requirements-app.txt` | Dependencias fijadas de la imagen Docker |
| `public/report/` | Plantilla de informe final en PDF |
| `public/power_electric_plant.png` | Ilustración conceptual del proyecto |
| `docs/` | Documentación del proyecto: `01_proyecto`, `02_datos`, `03_metodologia`, `04_modelo_y_resultados`, `05_decisiones`, `06_guia_usuario` y `07_referencias` |

---

## 5. Orden de ejecución

Con el entorno activado, abre Jupyter desde la raíz del proyecto:

```bash
jupyter lab
```

Ejecuta los notebooks **en orden numérico estricto**, con *Restart & Run All*. Cada uno depende de los datos generados por los anteriores.

| Orden | Archivo | Qué hace | Archivos que genera | Estado |
|---|---|---|---|---|
| 1 | `01_datos.ipynb` | Revisa la estructura y calidad de las 12 regiones, convención horaria, duplicados e interpolación de saltos DST | `data/processed/<REGION>_clean.parquet` y `consumo_horario.parquet` | Disponible |
| 2 | `02_patrones.ipynb` | Analiza patrones horarios, estacionalidad, ciclo semanal, normaliza perfiles diarios y agrupa tipos de día | `data/processed/tipos_de_dia*.parquet` (resumen, curvas, mezcla, silueta) | Disponible |
| 3 | `03_pronostico_anomalias.ipynb` | Entrena pronóstico de referencia (XGBoost vs base a 24 h en ventana móvil) y detecta días atípicos con z modificado | `residuos_PJME.parquet`, `metricas_ventana_movil_PJME.parquet`, `anomalias_PJME_*.parquet` | Disponible |
| 4 | `src/export.py` (script) | Consolida los datos procesados y exporta el modelo dimensional de 17 tablas CSV junto al diccionario de datos | 17 archivos CSV en `data/processed/powerbi/` | Disponible |

Correspondencia con la numeración anterior de siete notebooks, útil para leer versiones anteriores de la documentación:

| Ahora | Antes |
|---|---|
| `01_datos.ipynb` | 01 Exploración y 02 Limpieza |
| `02_patrones.ipynb` | 03 Análisis y 05 Agrupamiento |
| `03_pronostico_anomalias.ipynb` | 04 Modelado y 06 Anomalías |
| `src/export.py` | 07 Exportación |

Para ejecutar la exportación directamente desde la terminal:
```bash
python src/export.py
```

### Comprobaciones tras ejecutar

| Paso | Qué debe verse |
|---|---|
| `01_datos.ipynb` | Las 12 regiones en `OK`, con 1,090,343 filas en total y cero vacíos tras interpolación. `AEP`: 121,273 filas originales, 4 duplicados unificados y 121,296 filas finales |
| `02_patrones.ipynb` | 10 regiones vigentes en el periodo común (2013-06-01 → 2018-08-03). Silueta evaluada para $k \in [2, 10]$ con umbrales 0.26 y 0.50 (k-medias con $k = 2$ y silueta 0.413) |
| `03_pronostico_anomalias.ipynb` | XGBoost supera al base en los 6 pliegues de 12 meses (MASE de 0.86 en la partición única, entre 0.72 y 0.87 por pliegue). 22 días atípicos de 2,191 en `PJME` (z modificado > 3.5) con detección del huracán Sandy (2012-10-30) y el vórtice polar de 2014 |
| `src/export.py` | 17 archivos `.csv` en `data/processed/powerbi/` junto con `diccionario_datos.csv` (118 columnas documentadas) y el mensaje «Exportación completada con éxito» |

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

#### Ejecución con Docker Compose

Es una alternativa que no necesita Python ni entorno virtual para levantar la app. Requiere Docker (en Windows, Docker Desktop en ejecución) y las tablas ya generadas en `data/processed/powerbi/`.

Desde la raíz del proyecto:

```bash
docker compose up --build -d
```

La app queda disponible en `http://localhost:8501`, accesible solo desde el propio equipo.

| Tarea | Comando |
|---|---|
| Ver el estado | `docker compose ps` |
| Ver los registros | `docker compose logs -f` |
| Detener y eliminar el contenedor | `docker compose down` |

- **Datos:** la carpeta `data/processed/powerbi/` se monta en solo lectura, no se copia en la imagen. Tras volver a ejecutar `src/export.py`, reinicia con `docker compose restart` para descartar los datos en caché.
- **Código:** los cambios en `app/`, `src/` o `.streamlit/` requieren repetir `docker compose up --build -d`.
- **Puerto:** si el 8501 está ocupado, define `STREAMLIT_PORT` en un archivo `.env` en la raíz (por ejemplo, `STREAMLIT_PORT=8502`).
- **Reinicio:** el contenedor vuelve a arrancar junto con Docker hasta que se detenga con `docker compose down`.
- **Dependencias:** la imagen usa las versiones fijadas en `requirements-app.txt`.

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

El panel interactivo en Power BI consume las tablas exportadas por `src/export.py` *(panel en desarrollo en `app/panel_pjm.pbix`)*:

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
La aplicación se detiene si faltan tablas en `data/processed/powerbi/`. Ejecuta el script `python src/export.py` para exportar las 17 tablas requeridas.

**El puerto 8501 de Streamlit ya está en uso.**
Puedes especificar otro puerto agregando la bandera `--server.port`:

```bash
streamlit run app/streamlit_app.py --server.port 8502
```

**`ModuleNotFoundError: No module named 'src'`.**
Falta instalar el proyecto en modo editable (`pip install -e .`) o el kernel de Jupyter no usa el entorno del proyecto.

**Los notebooks no encuentran los archivos de datos crudos.**
Verificar que los CSV estén descomprimidos en `data/raw/` y que Jupyter se haya abierto desde la raíz del proyecto.

**Los notebooks 02 o 03 no encuentran `consumo_horario.parquet`.**
Ejecutar previamente `01_datos.ipynb`.

**El script `src/export.py` falla por falta de archivos Parquet.**
Ejecutar previamente y en orden los notebooks `01_datos.ipynb`, `02_patrones.ipynb` y `03_pronostico_anomalias.ipynb` para generar todos los datos procesados requeridos.

**El kernel de Jupyter no usa el entorno del proyecto.**
Registrarlo ejecutando:

```bash
python -m ipykernel install --user --name energy-consumption --display-name "Python (energy-consumption)"
```

y seleccionarlo en Jupyter desde *Kernel → Change Kernel*.
