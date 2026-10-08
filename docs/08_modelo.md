# Documentación del modelo

> Este documento se completa a medida que avanza el proyecto. Los campos marcados como `[por definir]` se llenan al terminar el EDA y al elegir los modelos.

---

## 1. Datos de entrada

|Elemento|Detalle|
|---|---|
|Regiones utilizadas|`[por definir]`|
|Periodo|`[por definir]`|
|Variable objetivo|Consumo horario en MW|
|Archivo de entrada|`data/processed/` `[por definir]`|

---

## 2. Preparación de los datos

### 2.1 Tratamiento de calidad

|Problema|Tratamiento aplicado|
|---|---|
|Valores nulos|`[por definir]`|
|Duplicados|`[por definir]`|
|Horas faltantes por cambio de horario|`[por definir]`|
|Valores atípicos|`[por definir]`|

### 2.2 Variables creadas

|Variable|Descripción|
|---|---|
|Hora|Hora del día (0 a 23)|
|Día de la semana|Lunes a domingo|
|Mes|Mes del año|
|Estación|Estación del año|
|Día festivo|Indica si la fecha es festivo en EE. UU.|

---

## 3. Diseño del experimento

### 3.1 División de los datos

Por tratarse de una serie de tiempo, la división respeta el orden cronológico: no se mezclan fechas entre entrenamiento y prueba.

|Conjunto|Periodo|
|---|---|
|Entrenamiento|`[por definir]`|
|Validación (si aplica)|`[por definir]`|
|Prueba|`[por definir]`|

### 3.2 Modelo base

Se define un modelo sencillo contra el cual comparar los demás. `[por definir]`

### 3.3 Horizonte de pronóstico

`[por definir]` (por ejemplo, las siguientes 24 horas o los siguientes 7 días).

---

## 4. Algoritmos

|Modelo|Motivo de elección|Parámetros principales|
|---|---|---|
|`[por definir]`|`[por definir]`|`[por definir]`|
|`[por definir]`|`[por definir]`|`[por definir]`|

---

## 5. Métricas y resultados

Las métricas se describen en [06_plan_proyecto.md](https://claude.ai/chat/06_plan_proyecto.md): MAE, RMSE y MAPE.

|Modelo|MAE (MW)|RMSE (MW)|MAPE (%)|
|---|---|---|---|
|Modelo base|`[por definir]`|`[por definir]`|`[por definir]`|
|`[por definir]`|`[por definir]`|`[por definir]`|`[por definir]`|

### Interpretación

`[por definir]`

---

## 6. Limitaciones

- El modelo no incorpora factores externos como temperatura, precios de energía o eventos especiales.
- Las regiones cubren periodos distintos, lo que limita las comparaciones entre ellas.
- `[completar según los resultados]`

---

## 7. Reproducibilidad

El código del modelo está en `notebooks/04_modelado.ipynb` y en `src/`. Los pasos para ejecutarlo están en la [guía de usuario](https://claude.ai/chat/09_guia_usuario.md).