# Directrices para Agentes y Desarrolladores de IA (AGENTS.md)

Este documento establece las directrices, reglas de contexto, convenciones de código y estándares de documentación para cualquier agente de IA o colaborador que opere en este repositorio.

---

## 1. Contexto del Repositorio y Enfoque del Proyecto

- **Propósito del Proyecto:** Caracterización visual y cuantitativa de la demanda eléctrica horaria de 12 regiones de la red de transmisión PJM Interconnection (EE. UU., 1998–2018).
- **Aporte Diferencial (De Pronosticar a Caracterizar):** El objetivo central no es competir por décimas de precisión en pronóstico, sino caracterizar cómo es la demanda: descubrir qué formas de perfil diario existen (tipos de día), cuantificar en qué se diferencian las 12 regiones y localizar episodios atípicos o anómalos. El modelo predictivo actúa como una referencia basal de lo esperable para calcular residuos.
- **Entregable Principal:** Visualizaciones analíticas justificadas por tareas y canales perceptuales integradas en un panel interactivo de seis páginas en Streamlit (`app/streamlit_app.py`), que lee las tablas generadas en `data/processed/panel/`, y el informe en formato IEEE (`docs/IEEE/`).
- **Pila Tecnológica:** Python (pandas, NumPy, scikit-learn, XGBoost, statsmodels, holidays, pyarrow), JupyterLab / Jupyter Notebooks, Matplotlib y Seaborn (notebooks), Streamlit y Plotly (panel) y Docker Compose (ejecución opcional del panel).
- **Ruta de Documentación Modular:** Toda la documentación temática se gestiona en `docs/` (notas `01_proyecto.md` a `07_referencias.md`), optimizada para Obsidian y enlaces Markdown. El [README.md](README.md) actúa como índice de esas notas.

---

## 2. Estructura de Directorios

- `data/`:
  - `data/raw/`: Datos originales descargados de Kaggle (`*.csv`). **Nunca modificar directamente los datos en crudo**. Excluidos de control de versiones.
  - `data/processed/`: Datos procesados limpios por región (`<REGION>_clean.parquet`), consolidado horario (`consumo_horario.parquet`), agrupamientos (`tipos_de_dia*.parquet`), residuos y anomalías (`residuos_PJME.parquet`, `anomalias_PJME_*.parquet`).
  - `data/processed/panel/`: 17 tablas CSV exportadas por `src/export.py` junto con el `diccionario_datos.csv`, que alimentan el panel de Streamlit. La ruta se define en `PANEL_DIR` (`src/config.py`) y se monta en Docker desde `compose.yaml`; la exportación valida que todas las claves existan en su dimensión.
- `notebooks/`: Cuadernos Jupyter numerados para ejecución secuencial estricta:
  - `01_datos.ipynb`: Exploración inicial (EDA), calidad de datos, convención horaria, limpieza, interpolación de saltos por DST y validación formal de series.
  - `02_patrones.ipynb`: Patrones horarios, estacionalidad, correlaciones y comparativas regionales sobre el día operativo; perfiles diarios normalizados, k-medias/Ward, silueta y mezcla de tipos de día.
  - `03_pronostico_anomalias.ipynb`: Pronóstico de referencia a 24 horas (`PJME`), XGBoost frente a modelos base, MASE y validación en ventana móvil; detección de días atípicos con z modificado y contraste con episodios documentados.
- `src/`: Paquete de código Python modular y reutilizable:
  - `config.py`: Definición centralizada de rutas, constantes, semillas y parámetros del pipeline.
  - `data_loader.py`: Funciones de lectura y carga segura de datos crudos y procesados.
  - `cleaning.py`: Tratamiento de series temporales, duplicados, interpolación y validación formal.
  - `features.py`: Construcción de variables de calendario sobre el día operativo, rezagos temporales y medias móviles.
  - `modeling.py`: Particiones temporales, ajuste de modelos de pronóstico, métricas (MAE, RMSE, MAPE, MASE) y evaluación en ventana móvil.
  - `profiles.py`: Extracción de perfiles diarios de 24 horas, normalización, cálculo de coeficientes de silueta y agrupamiento.
  - `anomalies.py`: Cálculo de residuos diarios, z modificado y contraste con eventos históricos.
  - `export.py`: Exportación del modelo en estrella (17 tablas CSV y diccionario de datos) para el panel. Se ejecuta con `python src/export.py` después de los notebooks.
- `app/`: Panel interactivo en Streamlit:
  - `streamlit_app.py`: Punto de entrada y navegación entre las seis páginas.
  - `config.py`, `data_loader.py`, `filtros.py`, `graficos.py`, `estilos.py`: Configuración, carga con caché, filtros por región, estación y fecha, utilidades de gráficos y estilos.
  - `paginas/`: Un módulo por página (resumen, patrones, tipos de día, regiones, anomalías y pronóstico).
- `docs/`: Documentación técnica modular compatible con Obsidian (`01_proyecto.md` a `07_referencias.md`).
  - `docs/IEEE/`: Informe en formato de artículo IEEE (`Informe_IEEE_PJM_v4.md`) y sus figuras (`fig_*.png`).
  - `docs/img/`: Figuras del README (`resumen.png`, `mapa_calor.png`), generadas con `generar_figuras.py` desde las tablas del panel.
- `Dockerfile`, `compose.yaml`, `requirements-app.txt`: Imagen y servicio de Docker Compose del panel.

---

## 3. Decisiones de Diseño Fundamentales

Cualquier cambio o extensión en el código debe respetar las decisiones registradas en [docs/05_decisiones.md](docs/05_decisiones.md), que es la fuente única (D1 a D44). Las principales son:

1. **D1 · Convención Horaria y Día Operativo:** La columna `Datetime` marca el **final de la hora** de medición. Las variables de calendario (fecha, hora, día de la semana, mes, festivos) se calculan siempre desde `Datetime − 1 h` (día operativo). De lo contrario, la hora 24:00 se desplaza al día siguiente y desalinea los perfiles diarios de 24 horas. Esto incluye las tablas que exporta `src/export.py`.
2. **D2 · Tratamiento de Atípicos Aislados en Limpieza:** Los valores menores o iguales a 0 MW y los atípicos aislados de una hora se marcan como vacío y se interpolan. Un valor es aislado si se aleja más del 50 % del promedio de sus horas vecinas, estas difieren entre sí como máximo un 25 % y su z modificado respecto del patrón esperado supera 3.5 (`marcar_atipicos_aislados`). Los picos altos continuos y las rachas bajas se conservan. Además, se descartan a mano los errores revisados de `DEOK` (D14: `LECTURAS_DESCARTADAS` y `DIAS_EXCLUIDOS` en `src/config.py`).
3. **D3 · Series `NI` y `COMED`:** Se procesan y guardan por separado, documentando su relación histórica y su continuidad temporal.
4. **D4 · Plataforma de Entrega Analítica:** El panel se construye solo en Streamlit, por ser más dinámico, usar el mismo Python del análisis y no requerir licencias. Power BI se descartó.
5. **D5 · Evaluación Temporal en Ventana Móvil:** La evaluación de residuos y modelos se realiza con validación temporal en ventana móvil (6 pliegues de 12 meses, mínimo 3) para cubrir eventos clave (como el huracán Sandy en 2012 o el vórtice polar de 2014) sin fuga de información (*data leakage*).
6. **D6 · Agrupamiento Global Normalizado:** Se realiza un agrupamiento unificado sobre perfiles diarios normalizados para todas las regiones, lo que permite comparar directamente la distribución de tipos de día de cada región.
7. **D7 · Tratamiento de la Zona Horaria en `COMED` y `NI`:** Se conserva la hora de la fuente. `ALINEAR_HORA_CENTRAL` (`notebooks/02_patrones.ipynb`) queda en `False` y solo sirve para el análisis de sensibilidad; `src/export.py` usa la misma hora (D41).
8. **D8 · Detección de Días Atípicos con Z Modificado:** La detección de anomalías se realiza calculando el puntaje z modificado sobre los residuos del pronóstico usando la mediana y la desviación absoluta de la mediana (MAD), con el umbral robusto de 3.5 (Iglewicz y Hoaglin, 1993).

---

## 4. Directrices de Código y Tratamiento de Datos

1. **Tratamiento de Series Temporales:**
   - Manejar explícitamente duplicados y saltos temporales provocados por cambios de horario (Daylight Saving Time, DST) usando el pipeline de interpolación lineal validada en `src/cleaning.py`.
   - Todas las comparaciones interregionales deben utilizar periodos comunes verificados (por ejemplo, las 10 regiones vigentes entre 2013-06-01 y 2018-08-03).
   - Prohibido realizar divisiones aleatorias de entrenamiento y prueba (*random split*), las particiones deben ser siempre temporales (*time-based split*) o mediante ventana móvil expansiva.
2. **Buenas Prácticas en Python:**
   - Respetar PEP 8 para estilo de formato y convenciones de nombres.
   - Usar tipado estático (`typing`) explícito en argumentos y retornos de funciones en `src/`.
   - Incorporar docstrings descriptivos detallando parámetros, tipos y retornos en cada módulo de `src/`.
   - Evitar mutaciones directas in-place de DataFrames sin validación o copia previa.
3. **Reproducibilidad:**
   - Fijar y centralizar semillas aleatorias (`random_state = 42`) a través de `src/config.py`.
   - Registrar cualquier paquete nuevo o actualización en `requirements.txt` y `pyproject.toml`, y en `requirements-app.txt` si lo usa el panel.

---

## 5. Estándares de Documentación

- Mantener estricta sincronización entre el [README.md](README.md), el árbol de directorios y los documentos temáticos en `docs/`.
- Cualquier documento nuevo creado dentro de `docs/` debe incorporarse inmediatamente en la sección *Documentación* del [README.md](README.md) y enlazarse desde las notas relacionadas.
- Respetar la compatibilidad con Markdown estándar, tablas GFM y sintaxis KaTeX para fórmulas matemáticas.
