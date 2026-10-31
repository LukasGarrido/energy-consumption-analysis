# Directrices para Agentes y Desarrolladores de IA (AGENTS.md)

Este documento establece las directrices, reglas de contexto, convenciones de código y estándares de documentación para cualquier agente de IA o colaborador que opere en este repositorio.

---

## 1. Contexto del Repositorio y Enfoque del Proyecto

- **Propósito del Proyecto:** Caracterización visual y cuantitativa de la demanda eléctrica horaria de 12 regiones de la red de transmisión PJM Interconnection (EE. UU., 1998–2018).
- **Aporte Diferencial (De Pronosticar a Caracterizar):** El objetivo central no es competir por décimas de precisión en pronóstico, sino caracterizar cómo es la demanda: descubrir qué formas de perfil diario existen (tipos de día), cuantificar en qué se diferencian las 12 regiones y localizar episodios atípicos o anómalos. El modelo predictivo actúa como una referencia basal de lo esperable para calcular residuos.
- **Entregable Principal:** Visualizaciones analíticas justificadas por tareas y canales perceptuales integradas en un panel interactivo de Power BI (con tablas generadas en `data/processed/powerbi/`), complementado por un prototipo opcional en Streamlit.
- **Pila Tecnológica:** Python (pandas, NumPy, scikit-learn, XGBoost, statsmodels, holidays, pyarrow), JupyterLab / Jupyter Notebooks, Power BI, Matplotlib y Seaborn.
- **Ruta de Documentación Modular:** Toda la documentación temática se gestiona en `docs/`, indexada en [docs/00_indice.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md) (notas `01` a `11`), optimizada para Obsidian y enlaces Markdown/wikilinks.

---

## 2. Estructura de Directorios

- `data/`:
  - `data/raw/`: Datos originales descargados de Kaggle (`*.csv`). **Nunca modificar directamente los datos en crudo**. Excluidos de control de versiones.
  - `data/processed/`: Datos procesados limpios por región (`<REGION>_clean.parquet`), consolidado horario (`consumo_horario.parquet`), agrupamientos (`tipos_de_dia*.parquet`), residuos y anomalías (`anomalias_*.parquet`).
  - `data/processed/powerbi/`: 17 tablas CSV exportadas por el notebook 07 junto con el `diccionario_datos.csv` para alimentar el panel interactivo.
- `notebooks/`: Cuadernos Jupyter numerados para ejecución secuencial estricta:
  - `01_exploracion.ipynb`: Exploración inicial (EDA), calidad de datos y convención horaria.
  - `02_limpieza.ipynb`: Limpieza, interpolación de saltos por DST y validación formal de series.
  - `03_analisis.ipynb`: Patrones horarios, día operativo, estacionalidad, correlaciones y comparativas regionales.
  - `04_modelado.ipynb`: Pronóstico de referencia a 24 horas (`PJME`), XGBoost vs basales, MASE y validación temporal en ventana móvil.
  - `05_agrupamiento.ipynb`: Perfiles diarios normalizados, k-medias/jerárquico, cálculo de silueta y mezcla de tipos de día.
  - `06_anomalias.ipynb`: Detección de anomalías basada en residuos del modelo, puntaje z modificado y contraste con episodios históricos documentados.
  - `07_exportacion.ipynb`: Generación y exportación de tablas normalizadas y dimensiones para Power BI.
- `src/`: Paquete de código Python modular y reutilizable:
  - `config.py`: Definición centralizada de rutas, constantes, semillas y parámetros del pipeline.
  - `data_loader.py`: Funciones de lectura y carga segura de datos crudos y procesados.
  - `cleaning.py`: Tratamiento de series temporales, duplicados, interpolación y validación formal.
  - `features.py`: Construcción de variables de calendario sobre el día operativo, rezagos temporales y medias móviles.
  - `modeling.py`: Particiones temporales, ajuste de modelos de pronóstico, métricas (MAE, RMSE, MAPE, MASE) y evaluación en ventana móvil.
  - `profiles.py`: Extracción de perfiles diarios de 24 horas, normalización, cálculo de coeficientes de silueta y agrupamiento.
  - `anomalies.py`: Cálculo de residuos diarios, z modificado y contraste con eventos históricos.
  - `plots.py`: Funciones auxiliares de visualización y estilo consistente de gráficos.
- `docs/`: Documentación técnica modular compatible con Obsidian (`00_indice.md` hasta `11_conceptos.md`).
- `public/`: Recursos estáticos, imágenes ilustrativas y plantillas de reportes (`public/templates/`).
- `reports/`: Artefactos exportados:
  - `reports/figures/`: Gráficos y figuras generadas listas para publicación.
- `app/`: Aplicación de visualización interactiva:
  - `streamlit_app.py`: Prototipo interactivo en Streamlit (opcional).
  - Archivos o especificaciones asociadas al panel de Power BI (`panel_pjm.pbix`).

---

## 3. Decisiones de Diseño Fundamentales (D1–D8)

Cualquier cambio o extensión en el código debe respetar estrictamente las decisiones registradas en `docs/04_metodologia_desarrollo.md`:

1. **D1 · Convención Horaria y Día Operativo:** La columna `Datetime` marca el **final de la hora** de medición. Las variables de calendario (fecha, día de la semana, mes, festivos) se calculan siempre desde `Datetime − 1 h` (día operativo). De lo contrario, la hora 24:00 se desplaza al día siguiente y desalinea los perfiles diarios de 24 horas.
2. **D2 · Tratamiento de Atípicos Aislados en Limpieza:** Solo se corrigen valores idénticos a 0 MW mediante interpolación. Valores atípicos aislados pero no nulos (como `DOM` a 1,253 MW o `PJMW` a 487 MW) se conservan en la fase de limpieza y se analizan en modelado/anomalías para evitar borrar picos reales.
3. **D3 · Series `NI` y `COMED`:** Se procesan y guardan por separado, documentando su relación histórica y su continuidad temporal.
4. **D4 · Plataforma de Entrega Analítica:** El panel principal se construye en Power BI para cumplir la rúbrica y los requerimientos de interacción ejecutiva, Streamlit permanece como prototipo auxiliar.
5. **D5 · Evaluación Temporal en Ventana Móvil:** La evaluación de residuos y modelos se realiza con validación temporal en ventana móvil (mínimo 3 a 6 pliegues de 12 meses) para cubrir eventos clave (como el huracán Sandy en 2012 o el vórtice polar de 2014) sin fuga de información (*data leakage*).
6. **D6 · Agrupamiento Global Normalizado:** Se realiza un agrupamiento unificado sobre perfiles diarios normalizados para todas las regiones, lo que permite proyectar y comparar directamente la distribución de tipos de día de cada región.
7. **D7 · Tratamiento de la Zona Horaria en `COMED` y `NI`:** Se mantiene la hora reportada por defecto, permitiendo alinearla a hora central mediante el parámetro configurable `ALINEAR_HORA_CENTRAL` (sincronizado entre `notebooks/05_agrupamiento.ipynb` y `notebooks/07_exportacion.ipynb`).
8. **D8 · Detección de Días Atípicos con Z Modificado:** La detección de anomalías se realiza calculando el puntaje z modificado sobre los residuos del pronóstico usando la mediana y la desviación absoluta de la mediana (MAD), comparando con el umbral robusto de 3.5 (Iglewicz y Hoaglin, 1993).

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
   - Registrar cualquier paquete nuevo o actualización en `requirements.txt` y `pyproject.toml`.

---

## 5. Estándares de Documentación

- Mantener estricta sincronización entre el [README.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/README.md), el árbol de directorios y los documentos temáticos en `docs/`.
- Cualquier documento nuevo creado dentro de `docs/` debe incorporarse inmediatamente en [docs/00_indice.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md) y añadir su correspondiente wikilink de Obsidian (`[[nota]]`).
- Respetar la compatibilidad con Markdown estándar, tablas GFM y sintaxis KaTeX para fórmulas matemáticas.
