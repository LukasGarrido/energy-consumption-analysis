# Directrices para Agentes y Desarrolladores de IA (AGENTS.md)

Este documento establece las directrices, reglas de contexto, convenciones de código y estándares de documentación para cualquier agente de IA o colaborador que opere en este repositorio.

---

## 1. Contexto del Repositorio

- **Propósito:** Análisis de series temporales de consumo eléctrico horario de la red de transmisión eléctrica PJM Interconnection (EE. UU., 2002–2018).
- **Lenguaje Principal:** Python 3.
- **Herramientas de Documentación:** Obsidian (Markdown) y Jupyter Notebooks.
- **Ruta de Documentación:** Toda la documentación temática modular se encuentra en [docs/00_indice.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md) y sus archivos asociados en `docs/`.

---

## 2. Estructura de Directorios

- `data/`: Contiene subdirectorios para datos brutos (`data/raw/`) y datos limpios/procesados (`data/processed/`). **Nunca modificar directamente los datos en crudo**.
- `notebooks/`: Cuadernos Jupyter ordenados secuencialmente para exploración paso a paso (EDA, ingeniería de características, análisis de estacionalidad, modelado).
- `src/`: Código fuente modular reutilizable (funciones de carga, limpieza, métricas y utilidades de graficado).
- `docs/`: Documentación del proyecto compatible con Obsidian y wikilinks.
- `reports/`: Gráficos exportados, figuras e informes finales generados.
- `app/`: Aplicación interactiva o dashboard de visualización si aplica.

---

## 3. Directrices de Código y Análisis

1. **Tratamiento de Series Temporales:**
   - Prestar especial atención a la columna de fecha y hora (`Datetime`).
   - Manejar explícitamente duplicados y saltos temporales provocados por cambios de horario (Daylight Saving Time).
   - Realizar comparaciones entre regiones utilizando intervalos de fechas comunes verificados.
2. **Buenas Prácticas en Python:**
   - Seguir PEP 8 para estilo de código.
   - Usar tipado estático (`typing`) y docstrings descriptivos en funciones dentro de `src/`.
   - Evitar operaciones que muten datos in-place sin validación.
3. **Reproducibilidad:**
   - Mantener semillas fijas (`random_state`) en cualquier partición o modelo probabilístico/predictivo.
   - Declarar dependencias en `requirements.txt`.

---

## 4. Estándares de Documentación

- Mantener la sincronización entre el [README.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/README.md) y las notas en `docs/`.
- Cualquier nueva sección o documento agregado en `docs/` debe quedar registrado en [docs/00_indice.md](file:///c:/Users/lukas/Desktop/Projects/energy-consumption-analysis/docs/00_indice.md).
- Respetar la compatibilidad con Markdown estándar y enlaces tipo Obsidian (`[[nota]]` o enlaces relativos Markdown).
