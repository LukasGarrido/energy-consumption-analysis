"""Genera las figuras del README a partir de las tablas del panel.

Uso (desde la raíz del proyecto, después de ``python src/export.py``)::

    python docs/img/generar_figuras.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PANEL = RAIZ / "data" / "processed" / "panel"
SALIDA = Path(__file__).resolve().parent

AZUL, NARANJA, GRIS, ROJO = "#0072B2", "#E69F00", "#8C8C8C", "#D55E00"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

plt.rcParams.update({
    "font.size": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "legend.frameon": False,
})


def leer(nombre: str) -> pd.DataFrame:
    """Lee una tabla del panel por su nombre, sin la extensión."""
    return pd.read_csv(PANEL / f"{nombre}.csv", encoding="utf-8-sig")


def tipos_de_dia(ax: plt.Axes) -> None:
    """P1: curva media y banda de dispersión de cada tipo de día."""
    curvas = leer("curvas_tipo_dia")
    tipos = leer("dim_tipo_dia").set_index("grupo")
    for grupo, color in ((1, AZUL), (2, NARANJA)):
        d = curvas[curvas["grupo"] == grupo]
        etiqueta = f"{tipos.loc[grupo, 'nombre_grupo']} ({tipos.loc[grupo, 'pct_dias']:.1f} %)"
        ax.plot(d["hora"], d["media"], color=color, lw=3, label=etiqueta)
        ax.fill_between(d["hora"], d["inferior"], d["superior"], color=color, alpha=0.18, lw=0)
    ax.axhline(1, color=GRIS, lw=1, ls=":")
    ax.set(xlabel="Hora del día", ylabel="Demanda / promedio del día", xticks=range(0, 24, 3))
    ax.set_title("P1 · Dos tipos de día")
    ax.legend(loc="upper left")


def regiones(ax: plt.Axes) -> None:
    """P2: mezcla de tipos de día por región en el periodo común."""
    mezcla = leer("mezcla_region_tipo").dropna(subset=["pct_dias_comun"])
    vigentes = leer("indicadores_region").dropna(subset=["razon_inv_ver_comun"])["region"]
    t = (mezcla[mezcla["region"].isin(vigentes)]
         .pivot(index="region", columns="grupo", values="pct_dias_comun")
         .dropna()
         .sort_values(2, ascending=False))
    ax.barh(t.index, t[1], color=AZUL, label="Temporada fría")
    ax.barh(t.index, t[2], left=t[1], color=NARANJA, label="Verano")
    for y, valor in enumerate(t[2]):
        ax.text(98.5, y, f"{valor:.0f} %", ha="right", va="center", fontsize=10)
    ax.set(xlim=(0, 100), xlabel="% de los días (2013-06 a 2018-08)")
    ax.set_title("P2 · Mezcla por región")


def anomalias(ax: plt.Axes) -> None:
    """P3: residuo diario de PJME con los días atípicos destacados."""
    d = leer("anomalias_dias")
    d["fecha"] = pd.to_datetime(d["fecha"])
    atipicos = d[d["es_atipico"]]
    altos = atipicos[atipicos["residuo_pct"] > 0]
    bajos = atipicos[atipicos["residuo_pct"] < 0]
    ax.scatter(d["fecha"], d["residuo_pct"], s=4, color="#C4C4C4")
    ax.scatter(altos["fecha"], altos["residuo_pct"], s=45, color=ROJO,
               label=f"Más demanda ({len(altos)})")
    ax.scatter(bajos["fecha"], bajos["residuo_pct"], s=45, color=AZUL, marker="s",
               label=f"Menos demanda ({len(bajos)})")
    for dia, texto in (("2012-10-30", "Huracán Sandy"), ("2014-01-07", "Vórtice polar")):
        fila = d[d["fecha"] == dia].iloc[0]
        ax.annotate(texto, (fila["fecha"], fila["residuo_pct"]), xytext=(8, -3),
                    textcoords="offset points", fontsize=11, weight="bold")
    ax.axhline(0, color=GRIS, lw=1)
    ax.set(ylabel="Residuo (% de lo esperado)", ylim=(-32, 38))
    ax.set_title(f"P3 · {len(atipicos)} días atípicos en PJME")
    ax.legend(loc="upper right", ncol=2, fontsize=10)


def pronostico(ax: plt.Axes) -> None:
    """P4: MAE de XGBoost y del modelo base en cada pliegue."""
    m = leer("pronostico_metricas")
    m = m[m["pliegue"] > 0]
    for desfase, modelo, color, etiqueta in ((-0.2, "Base", GRIS, "Base 24 h"),
                                             (0.2, "XGBoost", AZUL, "XGBoost")):
        d = m[m["modelo"] == modelo]
        ax.bar(d["pliegue"] + desfase, d["MAE"], 0.4, color=color, label=etiqueta)
    ax.set(xlabel="Pliegue de la ventana móvil", ylabel="MAE (MW)", ylim=(0, 2900),
           xticks=range(1, 7))
    ax.set_title("P4 · Pronóstico a 24 h frente al base")
    ax.legend(loc="upper center", ncol=2)


def figura_resumen() -> None:
    """Guarda ``resumen.png``: un panel por pregunta de investigación."""
    fig, ejes = plt.subplots(2, 2, figsize=(14, 9), layout="constrained")
    for dibujar, ax in zip((tipos_de_dia, regiones, anomalias, pronostico), ejes.flat):
        dibujar(ax)
    fig.get_layout_engine().set(w_pad=0.2, h_pad=0.2)
    fig.savefig(SALIDA / "resumen.png", dpi=150, facecolor="white")
    plt.close(fig)


def figura_mapa_calor(region: str = "PJME") -> None:
    """Guarda ``mapa_calor.png``: demanda relativa por hora y día de la semana."""
    patron = leer("patron_hora_dia")
    matriz = (patron[patron["region"] == region]
              .groupby(["dia_semana", "hora"])["MW_rel_medio"].mean()
              .unstack())
    fig, ax = plt.subplots(figsize=(14, 4.2), layout="constrained")
    imagen = ax.imshow(matriz.to_numpy(), aspect="auto", cmap="Blues")
    ax.set_yticks(range(7), DIAS)
    ax.set_xticks(range(24))
    ax.set(xlabel="Hora del día")
    ax.set_title(f"{region} · Demanda relativa media por hora y día de la semana")
    fig.colorbar(imagen, ax=ax, label="Demanda / promedio")
    fig.savefig(SALIDA / "mapa_calor.png", dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    figura_resumen()
    figura_mapa_calor()
    print(f"Figuras guardadas en {SALIDA}")
