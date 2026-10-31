# Guía de usuario

Esta guía explica cómo instalar el proyecto, obtener los datos y reproducir el análisis desde cero.

> Los pasos marcados como *(por crear)* corresponden a componentes que aún no existen en el repositorio.

---

## 1. Requisitos

| Requisito | Detalle |
|---|---|
| Python | 3.10, 3.11 o 3.12. Las versiones más recientes pueden dar problemas de instalación con algunas dependencias |
| Git | Para clonar el repositorio |
| Cuenta de Kaggle | Solo si se descarga el dataset con la API (opcional) |
| Sistema operativo | Windows, Linux o macOS |
| Power BI Desktop | Solo para ver el panel (requiere Windows) |

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

### 2.5 Instalar el proyecto en modo editable

Esto permite que los notebooks encuentren la carpeta `src/`:

```bash
pip install -e .
```

Solo se hace una vez. Gracias al modo editable, los cambios en los archivos de `src/` se reflejan sin reinstalar.

### 2.6 Parámetros del proyecto

Los parámetros están en `src/config.py`:

| Parámetro | Uso | Estado |
|---|---|---|
| `HORIZONTE_HORAS`, `REZAGOS_HORAS`, `VENTANAS_HORAS`, `FECHA_CORTE`, `SEMILLA` | Pronóstico | Disponibles |
| `K_RANGO`, `TAMANO_MIN_GRUPO` | Agrupamiento de perfiles diarios | Por añadir |
| `UMBRAL_Z_MODIFICADO` | Valores atípicos y días atípicos | Por añadir |

Los parámetros del pronóstico deben ser:

```python
HORIZONTE_HORAS = 24            # se pronostica con 24 horas de antelación
REZAGOS_HORAS = [24, 48, 168]   # consumo de hace 1 día, 2 días y 1 semana
VENTANAS_HORAS = [24, 168]      # ventanas de las medias móviles
FECHA_CORTE = "2017-01-01"      # antes: entrenamiento, desde esta fecha: prueba
SEMILLA = 42                    # para que los resultados sean reproducibles
```

`REZAGOS_HORAS` no puede contener valores menores que `HORIZONTE_HORAS`: el código lanza un error para evitar usar información que no se tendría al pronosticar.

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

`data/raw/` debe contener los 12 archivos por región (`PJME_hourly.csv`, `AEP_hourly.csv`, etc.) y el archivo combinado `pjm_hourly_est.csv`, que no se utiliza.

---

## 4. Estructura del proyecto

| Carpeta o archivo | Contenido |
|---|---|
| `data/raw/` | Datos originales de Kaggle (no se versionan) |
| `data/processed/` | Datos limpios y tablas para el panel |
| `notebooks/` | Notebooks de Jupyter, numerados en orden de ejecución |
| `src/config.py` | Rutas y parámetros |
| `src/data_loader.py` | Lectura de los datos |
| `src/cleaning.py` | Funciones de limpieza |
| `src/features.py` | Variables de calendario, rezagos y medias móviles |
| `src/modeling.py` | División, modelos, métricas y comparación |
| `src/profiles.py` | Perfiles diarios y agrupamiento *(por crear)* |
| `src/anomalies.py` | Residuos y días atípicos *(por crear)* |
| `app/` | Panel de Power BI *(por crear)* |
| `reports/figures/` | Imágenes exportadas |
| `docs/` | Documentación del proyecto |

---

## 5. Orden de ejecución

Con el entorno activado, abre Jupyter desde la raíz del proyecto:

```bash
jupyter lab
```

Ejecuta los notebooks **en orden numérico**, con *Restart & Run All*. Cada uno depende de los anteriores.

| Orden | Notebook | Qué hace | Archivos que genera | Estado |
|---|---|---|---|---|
| 1 | `01_exploracion.ipynb` | Revisa la estructura y calidad de los datos | Ninguno | Disponible |
| 2 | `02_limpieza.ipynb` | Limpia los datos | `data/processed/<REGION>_clean.parquet` y `consumo_horario.parquet` | Disponible |
| 3 | `03_analisis.ipynb` | Analiza patrones, regiones y picos | Ninguno | Disponible |
| 4 | `04_modelado.ipynb` | Entrena y evalúa el pronóstico | Residuos fuera de muestra (cuando se amplíe) | Disponible |
| 5 | `05_agrupamiento.ipynb` | Agrupa los perfiles diarios | Grupos por día | Por crear |
| 6 | `06_anomalias.ipynb` | Detecta los días atípicos | Lista de días atípicos | Por crear |
| 7 | `07_exportacion.ipynb` | Reúne las tablas para el panel | Tablas en `data/processed/` | Por crear |

### Comprobaciones tras ejecutar

Sirven para confirmar que el resultado es el esperado. Los valores pueden variar ligeramente según las versiones de las librerías.

| Notebook | Qué debe verse |
|---|---|
| 02 | Las 12 regiones en `OK`, con 1,090,343 filas en total y cero vacíos |
| 02 | `AEP`: 121,273 filas originales, 4 duplicados unificados y 121,296 filas finales |
| 03 | 10 regiones vigentes y periodo común 2013-06-01 → 2018-08-03 |
| 04 | Entrenamiento hasta 2016-12-31 y prueba desde 2017-01-01 (13,897 filas) |
| 04 | MAE de XGBoost cercano a 1,862 MW, frente a 2,300 MW del modelo base de 24 h |

---

## 6. Cómo ver el panel

El panel se construye en Power BI a partir de las tablas que genera el notebook 07 *(por crear)*. Para abrirlo:

1. Instalar Power BI Desktop (requiere Windows).
2. Abrir el archivo del panel desde `app/`.
3. Si las rutas de los datos no se encuentran, actualizar el origen de datos hacia la carpeta `data/processed/` del repositorio.

El panel tendrá cinco páginas: resumen, patrones, tipos de día, regiones y anomalías con pronóstico. Hay que verificar qué licencia se necesita para publicarlo o compartirlo.

---

## 7. Solución de problemas

**`pip install` falla con un mensaje sobre versiones de Python.**
Alguna dependencia no soporta la versión de Python instalada. Usar Python 3.10 a 3.12 o comentar en `requirements.txt` el paquete que falla.

**Error `No matching distribution found for ...`.**
Revisar que el nombre del paquete en `requirements.txt` esté bien escrito y que la línea no empiece con `#`.

**En PowerShell no se activa el entorno virtual ("la ejecución de scripts está deshabilitada").**
Ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**`ModuleNotFoundError: No module named 'src'`.**
Falta instalar el proyecto en modo editable (`pip install -e .`) o el kernel de Jupyter no usa el entorno del proyecto. Después de instalarlo, reinicia el kernel.

**`ImportError` al importar `src.features` o `src.modeling`.**
Faltan los parámetros del modelado en `src/config.py` (ver la sección 2.6).

**`ModuleNotFoundError` por `holidays`, `statsmodels`, `xgboost` o `sklearn`.**
Instalar las dependencias con `pip install -r requirements.txt`.

**Los notebooks no encuentran los archivos de datos.**
Verificar que los CSV estén en `data/raw/` y que Jupyter se haya iniciado desde la raíz del proyecto.

**Los notebooks 03 a 06 no encuentran `consumo_horario.parquet`.**
Ejecutar antes `02_limpieza.ipynb`.

**`kaggle` no se reconoce como comando.**
Confirmar que el entorno virtual está activo y que las dependencias se instalaron. Si persiste, usar la descarga manual (Opción B).

**El kernel de Jupyter no usa el entorno del proyecto.**
Registrarlo con:

```bash
python -m ipykernel install --user --name energy-consumption --display-name "Python (energy-consumption)"
```

y seleccionarlo desde *Kernel → Change Kernel*.

**El notebook 02 deja una región en `ERROR`.**
La región no se guarda. La celda de diagnóstico muestra los vacíos que quedaron: si son un hueco de más de 2 horas seguidas, se puede subir `LIMITE_HORAS` o dejarlo vacío y documentarlo, si están en el primer o último registro, `recortar_extremos_vacios` debería eliminarlos.