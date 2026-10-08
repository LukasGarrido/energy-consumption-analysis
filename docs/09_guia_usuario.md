# Guía de usuario

Esta guía explica cómo instalar el proyecto, obtener los datos y reproducir el análisis desde cero.

> Los apartados marcados como *(pendiente)* se completarán cuando avance el proyecto.

---

## 1. Requisitos

- **Python:** se recomienda la versión 3.10, 3.11 o 3.12. Las versiones más recientes pueden dar problemas de instalación con algunas dependencias (por ejemplo, `prophet`).
- **Git:** para clonar el repositorio.
- **Cuenta de Kaggle:** solo si se desea descargar el dataset con la API (opcional).
- **Sistema operativo:** Windows, Linux o macOS.

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

Después de la descarga, `data/raw/` debe contener los archivos CSV por región (`PJME_hourly.csv`, `AEP_hourly.csv`, etc.) y el archivo combinado `pjm_hourly_est.csv`.

---

## 4. Estructura del proyecto

| Carpeta | Contenido |
|---|---|
| `data/raw/` | Datos originales de Kaggle (no se versionan) |
| `data/interim/` | Datos parcialmente procesados |
| `data/processed/` | Datos finales listos para analizar y visualizar |
| `notebooks/` | Notebooks de Jupyter, numerados en orden de ejecución |
| `src/` | Código Python reutilizable (carga de datos, variables, gráficos) |
| `app/` | Visualización final *(pendiente)* |
| `reports/figures/` | Imágenes exportadas |
| `docs/` | Documentación del proyecto |

---

## 5. Cómo reproducir el análisis

Con el entorno activado, abrir Jupyter desde la raíz del proyecto:

```bash
jupyter lab
```

Ejecutar los notebooks **en orden numérico**, de arriba abajo (*Run → Run All Cells*):

| Orden | Notebook | Qué hace |
|---|---|---|
| 1 | `01_exploracion.ipynb` | Revisa la estructura, nulos, duplicados y rangos de fechas |
| 2 | `02_limpieza.ipynb` | Limpia los datos y genera los archivos de `data/processed/` |
| 3 | `03_analisis.ipynb` | Analiza patrones, estacionalidad, tendencia y regiones |
| 4 | `04_modelado.ipynb` | Pronóstico de la demanda *(pendiente)* |

Cada notebook depende de los resultados del anterior, por lo que no conviene saltarse pasos.

---

## 6. Cómo ver la visualización

*(pendiente: se completará cuando se defina la herramienta de visualización)*

---

## 7. Solución de problemas

**El comando `pip install` falla con un mensaje sobre versiones de Python.**
Alguna dependencia no soporta la versión de Python instalada. Usar Python 3.10 a 3.12 o comentar en `requirements.txt` el paquete que falla (suele ser `prophet`).

**Error `No matching distribution found for ...`.**
Revisar que el nombre del paquete en `requirements.txt` esté bien escrito y que la línea no empiece con `#`.

**En PowerShell no se activa el entorno virtual ("la ejecución de scripts está deshabilitada").**
Ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Los notebooks no encuentran los archivos de datos.**
Verificar que los CSV estén en `data/raw/` y que Jupyter se haya iniciado desde la raíz del proyecto.

**`kaggle` no se reconoce como comando.**
Confirmar que el entorno virtual está activo y que las dependencias se instalaron. Si persiste, usar la descarga manual (Opción B).

**El kernel de Jupyter no usa el entorno del proyecto.**
Registrarlo con:

```bash
python -m ipykernel install --user --name energy-consumption --display-name "Python (energy-consumption)"
```

y seleccionarlo desde *Kernel → Change Kernel*.