"""
/src/export.py: Script de exportación de tablas para Power BI y Streamlit.

Reúne los resultados de limpieza, patrones, agrupamiento y anomalías en un
modelo en estrella de 17 tablas CSV en data/processed/powerbi/.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.config import PROCESSED_DIR
from src.features import agregar_variables_temporales, ESTACIONES as MAPA_ESTACIONES

# Constantes de nombres
TABLAS_REQUERIDAS = [
    "dim_region", "dim_fecha", "dim_estacion", "dim_tipo_dia",
    "hechos_diario", "patron_hora_dia", "patron_tipo_calendario",
    "tendencia_anual", "estacionalidad_mensual", "indicadores_region",
    "curvas_tipo_dia", "mezcla_region_tipo", "silueta_k",
    "pronostico_horario", "pronostico_metricas", "anomalias_dias",
    "anomalias_episodios",
]

MAPA_NOMBRES_GRUPOS = {
    "Temporada fría (oct–may)": "Temporada fría",
    "Verano (jun–sep)": "Verano"
}

NOMBRES_DIAS = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

NOMBRES_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

class EnergyDataExporter:
    def __init__(self, processed_dir: Path = PROCESSED_DIR):
        self.processed_dir = processed_dir
        self.output_dir = processed_dir / "powerbi"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}  # Caché de parquets

    def load_parquet(self, name: str) -> pd.DataFrame:
        if name not in self.data:
            path = self.processed_dir / f"{name}.parquet"
            if not path.exists():
                raise FileNotFoundError(f"Falta el archivo: {path}. Ejecuta los notebooks previos.")
            self.data[name] = pd.read_parquet(path)
        return self.data[name]

    def save_csv(self, df: pd.DataFrame, name: str):
        path = self.output_dir / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Exportado: {name}.csv ({len(df):,} filas)")

    def run(self):
        print(f"Iniciando exportación a {self.output_dir}...")
        
        # 1. Cargar datos base
        consumo = self.load_parquet("consumo_horario")
        consumo = agregar_variables_temporales(consumo)
        
        # 2. Exportar dimensiones básicas
        self._export_dim_region(consumo)
        self._export_dim_fecha(consumo)
        self._export_dim_estacion()
        
        # 3. Agrupamiento (Notebook 05)
        tipos = self.load_parquet("tipos_de_dia")
        resumen = self.load_parquet("tipos_de_dia_resumen")
        
        # Normalizar nombres de grupos en tipos y resumen
        tipos["nombre_grupo"] = tipos["nombre_grupo"].replace(MAPA_NOMBRES_GRUPOS)
        resumen["nombre_grupo"] = resumen["nombre_grupo"].replace(MAPA_NOMBRES_GRUPOS)
        
        self._export_dim_tipo_dia(resumen)
        self._export_hechos_diario(tipos)
        self._export_curvas_tipo_dia()
        self._export_mezcla_region_tipo()
        self._export_silueta_k()
        
        # 4. Patrones y Análisis (Notebook 03)
        self._export_patrones(consumo)
        self._export_indicadores(consumo)
        
        # 5. Pronóstico (Notebook 04)
        self._export_pronostico()
        
        # 6. Anomalías (Notebook 06)
        self._export_anomalias()
        
        # 7. Diccionario de datos
        self._export_diccionario()
        
        print("\nExportación completada con éxito.")

    def _export_dim_region(self, df: pd.DataFrame):
        dim = pd.DataFrame({"region": sorted(df["region"].unique())})
        self.save_csv(dim, "dim_region")

    def _export_dim_fecha(self, df: pd.DataFrame):
        dim = df[["fecha", "anio", "mes", "dia_semana", "es_fin_de_semana", "estacion", "es_festivo"]].drop_duplicates("fecha")
        dim = dim.sort_values("fecha")
        self.save_csv(dim, "dim_fecha")

    def _export_dim_estacion(self):
        dim = pd.DataFrame({"estacion": ["Invierno", "Primavera", "Verano", "Otoño"]})
        self.save_csv(dim, "dim_estacion")

    def _export_dim_tipo_dia(self, resumen: pd.DataFrame):
        # Seleccionar columnas para dim_tipo_dia
        cols = ["grupo", "nombre_grupo", "n_dias", "pct_dias", "hora_pico", "amplitud", "pct_fin_de_semana"]
        self.save_csv(resumen[cols], "dim_tipo_dia")

    def _export_hechos_diario(self, tipos: pd.DataFrame):
        cols = ["region", "fecha", "grupo", "MW_medio_dia"]
        self.save_csv(tipos[cols], "hechos_diario")

    def _export_patrones(self, df: pd.DataFrame):
        # MW_rel ya viene en consumo_horario si se aplicó features.normalizar_por_region
        # Si no, lo calculamos aquí
        if "MW_rel" not in df.columns:
            df["MW_rel"] = df["MW"] / df.groupby("region")["MW"].transform("mean")
            
        # 1. patron_hora_dia (para heatmap)
        phd = df.groupby(["region", "estacion", "dia_semana", "hora"])["MW_rel"].mean().reset_index()
        phd.rename(columns={"MW_rel": "MW_rel_medio", "MW": "MW_medio"}, inplace=False) # Wait, MW is not in agg
        # Re-agg to include MW_medio too
        phd = df.groupby(["region", "estacion", "dia_semana", "hora"]).agg(
            MW_medio=("MW", "mean"),
            MW_rel_medio=("MW_rel", "mean")
        ).reset_index()
        phd["nombre_dia"] = phd["dia_semana"].map(NOMBRES_DIAS)
        self.save_csv(phd, "patron_hora_dia")
        
        # 2. patron_tipo_calendario
        df["tipo_calendario"] = "Laborable"
        df.loc[df["es_fin_de_semana"], "tipo_calendario"] = "Fin de semana"
        df.loc[df["es_festivo"], "tipo_calendario"] = "Festivo"
        
        ptc = df.groupby(["region", "estacion", "tipo_calendario", "hora"])["MW_rel"].mean().reset_index()
        ptc.rename(columns={"MW_rel": "MW_rel_medio"}, inplace=True)
        self.save_csv(ptc, "patron_tipo_calendario")
        
        # 3. tendencia_anual
        tend = df.groupby(["region", "anio"])["MW"].mean().reset_index()
        tend.rename(columns={"MW": "MW_medio"}, inplace=True)
        self.save_csv(tend, "tendencia_anual")
        
        # 4. estacionalidad_mensual
        est = df.groupby(["region", "mes"])["MW_rel"].mean().reset_index()
        est.rename(columns={"MW_rel": "MW_rel_medio"}, inplace=True)
        est["nombre_mes"] = est["mes"].map(NOMBRES_MESES)
        self.save_csv(est, "estacionalidad_mensual")

    def _export_indicadores(self, df: pd.DataFrame):
        # Periodo común
        counts = df.groupby("fecha")["region"].nunique()
        n_regiones = df["region"].nunique()
        fechas_comunes = counts[counts == n_regiones].index
        
        def calc_metrics(data):
            # razon_inv_ver = Invierno / Verano
            inv = data[data["estacion"] == "Invierno"]["MW"].mean()
            ver = data[data["estacion"] == "Verano"]["MW"].mean()
            razon = inv / ver if ver > 0 else np.nan
            
            # amplitud_diaria = mean(max - min del día)
            amp = data.groupby("fecha")["MW"].agg(lambda x: x.max() - x.min()).mean()
            return pd.Series({"razon": razon, "amplitud": amp})

        # Totales
        ind_total = df.groupby("region").apply(calc_metrics)
        # Comunes
        ind_comun = df[df["fecha"].isin(fechas_comunes)].groupby("region").apply(calc_metrics)
        
        ind = pd.concat([
            ind_total.rename(columns={"razon": "razon_inv_ver", "amplitud": "amplitud_diaria"}),
            ind_comun.rename(columns={"razon": "razon_inv_ver_comun", "amplitud": "amplitud_diaria_comun"})
        ], axis=1).reset_index()
        
        self.save_csv(ind, "indicadores_region")

    def _export_curvas_tipo_dia(self):
        curvas = self.load_parquet("tipos_de_dia_curvas")
        # No hay mapeo de nombres de grupo aquí porque usa 'grupo' (int)
        self.save_csv(curvas, "curvas_tipo_dia")

    def _export_mezcla_region_tipo(self):
        mezcla = self.load_parquet("tipos_de_dia_mezcla_region")
        self.save_csv(mezcla, "mezcla_region_tipo")

    def _export_silueta_k(self):
        sil = self.load_parquet("tipos_de_dia_silueta_k")
        self.save_csv(sil, "silueta_k")

    def _export_pronostico(self):
        # Nota: Por simplicidad exportamos los resultados de PJME
        # En un sistema completo esto iteraría por regiones
        res = self.load_parquet("residuos_PJME")
        res["error_abs"] = res["residuo"].abs()
        res["error_pct"] = res["error_abs"] / res["real"] * 100
        res["hora"] = res["Datetime"].dt.hour
        res["mes"] = res["Datetime"].dt.month
        res["fecha"] = res["Datetime"].dt.normalize()
        self.save_csv(res, "pronostico_horario")
        
        met = self.load_parquet("metricas_ventana_movil_PJME")
        # app espera: MAE, RMSE, MAPE_pct, MASE, mejora_MAE_pct
        met = met.reset_index()
        met.rename(columns={"MAPE_%": "MAPE_pct", "mejora_MAE_%": "mejora_MAE_pct"}, inplace=True)
        self.save_csv(met, "pronostico_metricas")

    def _export_anomalias(self):
        # Nota: PJME
        diario = self.load_parquet("anomalias_PJME_diario")
        self.save_csv(diario, "anomalias_dias")
        
        episodios = self.load_parquet("anomalias_PJME_episodios")
        self.save_csv(episodios, "anomalias_episodios")

    def _export_diccionario(self):
        # Generación simplificada del diccionario basado en las columnas exportadas
        filas = []
        for csv_file in self.output_dir.glob("*.csv"):
            if csv_file.name == "diccionario_datos.csv": continue
            df = pd.read_csv(csv_file, nrows=0)
            for col in df.columns:
                filas.append({
                    "tabla": csv_file.stem,
                    "columna": col,
                    "descripcion": f"Variable {col} de la tabla {csv_file.stem}"
                })
        dic = pd.DataFrame(filas)
        self.save_csv(dic, "diccionario_datos")

def run_export():
    exporter = EnergyDataExporter()
    exporter.run()

if __name__ == "__main__":
    run_export()
