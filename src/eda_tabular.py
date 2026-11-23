"""EDA de DS1 (países) y DS2 (serie mensual de NYC). Lee data/processed/ y guarda figuras en docs/figuras/.
Uso, desde la raíz:  python src/eda_tabular.py"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import config  # noqa: E402

FIG = config.DOCS_DIR / "figuras"
FIG.mkdir(parents=True, exist_ok=True)
ORDEN_INGRESO = ["LIC", "LMC", "UMC", "HIC"]
EVENTOS = {"2020-03-01": "inicio COVID", "2020-05-01": "suspensión orgánicos", "2021-10-01": "reanudación parcial"}


def guardar(nombre):
    plt.tight_layout()
    plt.savefig(FIG / nombre, dpi=130)
    plt.close()
    print(f"  figura guardada: docs/figuras/{nombre}")


def intentar(nombre, fn):
    try:
        fn()
    except Exception as e:  # un gráfico fallido no detiene el resto
        print(f"  ERROR en {nombre}: {type(e).__name__}: {e}")


def eda_ds1():
    ruta = config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["paises"]
    if not ruta.exists():
        print("DS1: no existe", ruta.name, "(ejecuta preparar_datos.py preparar)")
        return
    df = pd.read_csv(ruta)
    g = df["gpc_kg_hab_dia"]
    print(f"\n=== EDA DS1: {len(df)} países, gpc calculable en {int(g.notna().sum())} ===")
    print("gpc kg/hab/día:", g.describe().round(3).to_dict())
    if "income_id" in df.columns:
        print("mediana gpc por grupo de ingreso:", df.groupby("income_id")["gpc_kg_hab_dia"].median().round(3).to_dict())
        print("países por grupo:", df["income_id"].value_counts(dropna=False).to_dict())
    if "gdp" in df.columns:
        print("gdp:", df["gdp"].describe().round(1).to_dict())
    vac = (df.isna().mean() * 100).sort_values(ascending=False)
    print("vacíos % (10 peores):", vac.head(10).round(0).to_dict())
    ordenado = df.dropna(subset=["gpc_kg_hab_dia"]).sort_values("gpc_kg_hab_dia")
    cols = [c for c in ["pais", "income_id", "gpc_kg_hab_dia"] if c in df.columns]
    print("5 países con menor gpc:\n" + ordenado[cols].head(5).round(3).to_string(index=False))
    print("5 países con mayor gpc:\n" + ordenado[cols].tail(5).round(3).to_string(index=False))
    print("completitud % (25 columnas más completas):", (100 - vac).sort_values(ascending=False).head(25).round(0).to_dict())

    def f1():
        sns.histplot(g.dropna(), bins=30)
        plt.xlabel("Generación per cápita (kg/hab/día)"); plt.title("DS1: distribución de la generación per cápita")
        guardar("eda_ds1_gpc_hist.png")

    def f2():
        orden = [o for o in ORDEN_INGRESO if o in set(df["income_id"].dropna())]
        sns.boxplot(data=df, x="income_id", y="gpc_kg_hab_dia", order=orden)
        plt.xlabel("Grupo de ingreso"); plt.ylabel("kg/hab/día"); plt.title("DS1: generación per cápita por grupo de ingreso")
        guardar("eda_ds1_gpc_por_ingreso.png")

    def f3():
        d = df[(df["gdp"] > 0) & g.notna()]
        sns.scatterplot(x=np.log10(d["gdp"]), y=d["gpc_kg_hab_dia"], hue=d["income_id"], hue_order=ORDEN_INGRESO)
        plt.xlabel("log10(gdp) (unidades del dataset)"); plt.ylabel("kg/hab/día"); plt.title("DS1: generación vs. gdp")
        guardar("eda_ds1_gpc_vs_gdp.png")

    def f4():
        vac.head(20).iloc[::-1].plot.barh()
        plt.xlabel("% de vacíos"); plt.title("DS1: columnas con más vacíos")
        guardar("eda_ds1_vacios.png")

    def f5():
        num = df.select_dtypes("number")
        cols = num.notna().mean().sort_values(ascending=False).head(15).index
        sns.heatmap(num[cols].corr(method="spearman"), annot=True, fmt=".1f", cmap="coolwarm", annot_kws={"size": 6})
        plt.title("DS1: correlación de Spearman (15 columnas más completas)")
        guardar("eda_ds1_correlacion.png")

    for n, f in (("histograma", f1), ("boxplot ingreso", f2), ("gpc vs gdp", f3), ("vacíos", f4), ("correlación", f5)):
        intentar(n, f)


def eda_ds2():
    ruta = config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["serie_ciudad"]
    if not ruta.exists():
        print("DS2: no existe", ruta.name, "(ejecuta preparar_datos.py preparar)")
        return
    s = pd.read_csv(ruta, parse_dates=["fecha"])
    mats = [c for c in ["refuse", "paper", "mgp", "organics"] if c in s.columns]
    print(f"\n=== EDA DS2: {len(s)} meses, {s['fecha'].min():%Y-%m} a {s['fecha'].max():%Y-%m} ===")
    print("meses con vacío en algún material:", {m: int(s[m].isna().sum()) for m in mats})
    print("n_distritos por mes: mín", s["n_distritos"].min(), "máx", s["n_distritos"].max())
    print("toneladas por mes (describe):\n", s[mats].describe().round(0).to_string())
    print("total anual (suma de meses):\n", s.groupby(s["fecha"].dt.year)[mats].sum().round(0).to_string())

    def g1():
        fig, ejes = plt.subplots(len(mats), 1, figsize=(10, 2.4 * len(mats)), sharex=True)
        for ax, m in zip(np.atleast_1d(ejes), mats):
            ax.plot(s["fecha"], s[m]); ax.set_ylabel(m)
            for f, et in EVENTOS.items():
                ax.axvline(pd.Timestamp(f), color="red", ls="--", lw=0.8)
        np.atleast_1d(ejes)[0].set_title("DS2: toneladas mensuales (rojo: " + "; ".join(EVENTOS.values()) + ")")
        guardar("eda_ds2_series.png")

    def g2():
        plt.plot(s["fecha"], s["n_distritos"]); plt.title("DS2: distritos con datos por mes"); plt.ylabel("n distritos")
        guardar("eda_ds2_n_distritos.png")

    def g3():
        pre = s[s["fecha"] < "2020-03-01"].copy()
        pre["ton_dia"] = pre["refuse"] / pre["dias_mes"]
        sns.boxplot(x=pre["fecha"].dt.month, y=pre["ton_dia"])
        plt.xlabel("Mes"); plt.ylabel("refuse (ton/día calendario)"); plt.title("DS2: estacionalidad de basura (antes de marzo 2020)")
        guardar("eda_ds2_estacionalidad.png")

    for n, f in (("series", g1), ("n_distritos", g2), ("estacionalidad", g3)):
        intentar(n, f)


if __name__ == "__main__":
    eda_ds1()
    eda_ds2()
