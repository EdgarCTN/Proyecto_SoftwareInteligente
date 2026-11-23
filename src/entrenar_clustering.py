"""Agrupa países por perfil de residuos (mismo código que notebooks/04_clustering.ipynb, sin Jupyter).
Uso, desde la raíz:  python src/entrenar_clustering.py"""
import matplotlib
matplotlib.use("Agg")  # sin ventanas: las figuras se guardan en docs/figuras/

import json, sys, warnings, datetime
from pathlib import Path
import numpy as np, pandas as pd, joblib, sklearn
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.base import clone
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.metrics import (silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score,
                             normalized_mutual_info_score, homogeneity_completeness_v_measure)

RAIZ = next(p for p in [Path.cwd(), Path.cwd().parent] if (p / "config.py").exists())
sys.path.insert(0, str(RAIZ))
import config
SEMILLA = config.RANDOM_STATE
FIG = config.DOCS_DIR / "figuras"; FIG.mkdir(parents=True, exist_ok=True)
config.MODELS_DIR.mkdir(exist_ok=True); config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
print("scikit-learn", sklearn.__version__)

VARS = ["gpc_kg_hab_dia", "comp_food_organic_waste_pct", "comp_paper_cardboard_pct", "comp_plastic_pct",
        "comp_glass_pct", "comp_metal_pct", "comp_other_pct"]
COMP = VARS[1:]
EXTRA = ["cobertura_total_percent_of_population", "trat_recycling_pct"]
df0 = pd.read_csv(config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["paises"])
faltan = [c for c in VARS + EXTRA + ["iso3c", "pais", "income_id", "region_id"] if c not in df0.columns]
assert not faltan, f"Faltan columnas en el CSV: {faltan}"
vacios = (df0[VARS + EXTRA].isna().mean() * 100).round(1)
df = df0.dropna(subset=VARS).reset_index(drop=True)
descartados = df0[df0[VARS].isna().any(axis=1)]
assert (df[VARS] >= 0).all().all()
print(f"Países en el CSV: {len(df0)} | con las 7 variables completas (usados): {len(df)} | descartados: {len(descartados)}")
print("Vacíos % por variable:", vacios.to_dict())
suma = df[COMP].sum(axis=1)
print("Suma de los 6 porcentajes de composición (resto: caucho, madera, jardín):", suma.describe().round(1).to_dict())
print("Países por grupo de ingreso (usados):", df["income_id"].value_counts().to_dict())

prep = Pipeline([("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")), ("esc", StandardScaler())])
X = prep.fit_transform(df[VARS])
print("Matriz de agrupamiento:", X.shape)

def evaluar(X, etiquetas):
    """Métricas internas sobre los puntos que no son ruido (-1). None si no hay al menos 2 clústeres."""
    mask = etiquetas != -1
    ids = np.unique(etiquetas[mask])
    if len(ids) < 2 or mask.sum() <= len(ids):
        return None
    tam = pd.Series(etiquetas[mask]).value_counts()
    return {"n_clusters": int(len(ids)), "ruido_pct": float(100 * (~mask).mean()), "tam_min": int(tam.min()),
            "silhouette": float(silhouette_score(X[mask], etiquetas[mask])),
            "davies_bouldin": float(davies_bouldin_score(X[mask], etiquetas[mask])),
            "calinski_harabasz": float(calinski_harabasz_score(X[mask], etiquetas[mask]))}

def configuraciones():
    for k in range(2, 11):
        yield "K-Means", {"k": k}, KMeans(n_clusters=k, n_init=20, random_state=SEMILLA)
        yield "Agglomerative (Ward)", {"k": k}, AgglomerativeClustering(n_clusters=k, linkage="ward")
        yield "GMM (diag)", {"k": k}, GaussianMixture(n_components=k, covariance_type="diag", n_init=5, random_state=SEMILLA)
    for eps in np.round(np.arange(0.6, 2.61, 0.2), 1):
        for ms in (3, 5, 8):
            yield "DBSCAN", {"eps": float(eps), "min_samples": ms}, DBSCAN(eps=float(eps), min_samples=ms)

filas, modelos, etiquetas_cfg = [], [], []
for algoritmo, params, modelo in configuraciones():
    et = modelo.fit_predict(X)
    m = evaluar(X, et)
    if m is None:
        continue
    extra = {}
    if algoritmo == "K-Means": extra["inercia"] = float(modelo.inertia_)
    if algoritmo == "GMM (diag)": extra["bic"] = float(modelo.bic(X))
    filas.append({"algoritmo": algoritmo, "parametros": json.dumps(params), **m, **extra})
    modelos.append(modelo); etiquetas_cfg.append(et)
res = pd.DataFrame(filas)
res.to_csv(config.DATA_PROCESSED / "m4_resultados.csv", index=False)
print(f"Configuraciones evaluadas con al menos 2 clústeres: {len(res)} de {sum(1 for _ in configuraciones())}")

elegibles = res[res["n_clusters"].between(3, 8) & (res["ruido_pct"] <= 10) & (res["tam_min"] >= 5)]
assert len(elegibles) > 0, "Ninguna configuración cumple la regla (3 a 8 clústeres, ruido <= 10 %, tamaño mínimo 5); revisar la regla"
orden = elegibles.sort_values(["silhouette", "davies_bouldin"], ascending=[False, True])
pos = orden.index[0]
ganador = {"cfg": res.loc[pos], "modelo": modelos[pos], "etiquetas": etiquetas_cfg[pos]}
cols = ["algoritmo", "parametros", "n_clusters", "ruido_pct", "tam_min", "silhouette", "davies_bouldin", "calinski_harabasz"]
mejor_por_alg = orden.drop_duplicates("algoritmo")[cols]
print("Mejor configuración elegible por algoritmo (ordenadas por la regla):")
print(mejor_por_alg.round(3).to_string(index=False))
sin_restr = res.sort_values("silhouette", ascending=False).iloc[0]
print(f"\nGanador: {ganador['cfg']['algoritmo']} {ganador['cfg']['parametros']} · {int(ganador['cfg']['n_clusters'])} clústeres · "
      f"Silhouette {ganador['cfg']['silhouette']:.3f}, Davies-Bouldin {ganador['cfg']['davies_bouldin']:.3f}, "
      f"Calinski-Harabasz {ganador['cfg']['calinski_harabasz']:.1f}")
print(f"Mejor Silhouette sin restricciones: {sin_restr['algoritmo']} {sin_restr['parametros']} -> {int(sin_restr['n_clusters'])} clústeres, "
      f"{sin_restr['silhouette']:.3f} (ruido {sin_restr['ruido_pct']:.1f} %)")
codo = res[res["algoritmo"] == "K-Means"].assign(k=lambda d: d["parametros"].map(lambda s: json.loads(s)["k"]))[["k", "inercia", "silhouette"]]
print("\nK-Means: inercia y Silhouette por K (método del codo):")
print(codo.round(3).to_string(index=False))
ref = ganador["etiquetas"]

def estabilidad(modelo, X, ref, n_rep=30, frac=0.8):
    rng = np.random.default_rng(SEMILLA)
    aris = []
    for _ in range(n_rep):
        idx = rng.choice(len(X), int(frac * len(X)), replace=False)
        aris.append(adjusted_rand_score(ref[idx], clone(modelo).fit_predict(X[idx])))
    return np.array(aris)

aris = estabilidad(ganador["modelo"], X, ref)
estab = {"ARI_media": float(aris.mean()), "ARI_desv": float(aris.std()), "ARI_min": float(aris.min()), "repeticiones": 30, "fraccion": 0.8}
print(f"Estabilidad (30 submuestras del 80 %): ARI = {aris.mean():.3f} ± {aris.std():.3f} (mín {aris.min():.3f})")

contraste = {}
for col in ["income_id", "region_id"]:
    h, c, v = homogeneity_completeness_v_measure(df[col], ref)
    contraste[col] = {"ARI": float(adjusted_rand_score(df[col], ref)), "NMI": float(normalized_mutual_info_score(df[col], ref)),
                      "homogeneidad": float(h), "completitud": float(c), "V_measure": float(v)}
print("Contraste con etiquetas de referencia (no son verdad absoluta):")
print(pd.DataFrame(contraste).T.round(3).to_string())

df["cluster"] = ref
ids = sorted(set(ref) - {-1})
perfil_med = df.groupby("cluster")[VARS].median()
tamanos = df["cluster"].value_counts().sort_index()
global_med, global_std = df[VARS].median(), df[VARS].std()
z_perfil = (perfil_med - global_med) / global_std
cent = np.vstack([X[ref == c].mean(axis=0) for c in ids])
print("\nPerfil de cada clúster (mediana de las variables originales) y número de países:")
print(perfil_med.assign(n_paises=tamanos).round(2).to_string())
print("\nPaíses por clúster y grupo de ingreso:"); print(pd.crosstab(df["cluster"], df["income_id"]).to_string())
print("\nPaíses por clúster y región:"); print(pd.crosstab(df["cluster"], df["region_id"]).to_string())
representativos = {}
for i, c in enumerate(ids):
    sub = df[df["cluster"] == c]
    d = np.linalg.norm(X[sub.index] - cent[i], axis=1)
    representativos[int(c)] = sub.iloc[np.argsort(d)[:8]]["pais"].tolist()
print("\nPaíses más cercanos al centro de cada clúster:")
for c, v in representativos.items(): print(f"  Clúster {c}: {', '.join(v)}")

sens = {}
# (a) CLR de la composición (pseudo-conteo de 0.5 puntos porcentuales para los ceros) + log de gpc
lc = np.log(df[COMP].to_numpy(float) + 0.5)
Xc = StandardScaler().fit_transform(np.column_stack([np.log1p(df[["gpc_kg_hab_dia"]].to_numpy(float)), lc - lc.mean(axis=1, keepdims=True)]))
lab_c = clone(ganador["modelo"]).fit_predict(Xc)
sens["CLR"] = {"ARI_vs_principal": float(adjusted_rand_score(ref, lab_c)), "n_clusters": int(len(set(lab_c) - {-1}))}
# (b) semillas distintas (solo algoritmos con random_state)
if "random_state" in ganador["modelo"].get_params():
    a_s = [adjusted_rand_score(ref, clone(ganador["modelo"]).set_params(random_state=s).fit_predict(X)) for s in range(10)]
    sens["semillas_0_a_9"] = {"ARI_media": float(np.mean(a_s)), "ARI_min": float(np.min(a_s))}
# (c) conjunto ampliado con cobertura y reciclaje, solo países que tienen ambas (sin imputar)
dE = df.dropna(subset=EXTRA)
if len(dE) >= 40:
    XE = Pipeline([("log", FunctionTransformer(np.log1p)), ("esc", StandardScaler())]).fit_transform(dE[VARS + EXTRA])
    labE = clone(ganador["modelo"]).fit_predict(XE)
    sens["ampliado_9_variables"] = {"n_paises": int(len(dE)), "n_clusters": int(len(set(labE) - {-1})),
                                    "ARI_vs_principal_mismos_paises": float(adjusted_rand_score(ref[dE.index], labE)),
                                    "silhouette": (evaluar(XE, labE) or {}).get("silhouette")}
else:
    sens["ampliado_9_variables"] = {"n_paises": int(len(dE)), "nota": "muy pocos países con cobertura y reciclaje; no se evalúa"}
print(json.dumps(sens, indent=1, ensure_ascii=False))

ks = list(range(2, 11))
fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
ejes[0].plot(codo["k"], codo["inercia"], "o-"); ejes[0].set_xlabel("K"); ejes[0].set_ylabel("Inercia (WCSS)"); ejes[0].set_title("K-Means: método del codo")
for alg in ["K-Means", "Agglomerative (Ward)", "GMM (diag)"]:
    s = res[res["algoritmo"] == alg].assign(k=lambda d: d["parametros"].map(lambda t: json.loads(t)["k"])).sort_values("k")
    ejes[1].plot(s["k"], s["silhouette"], "o-", label=alg)
ejes[1].axvspan(3, 8, alpha=0.08); ejes[1].set_xlabel("K (zona sombreada = rango elegible)"); ejes[1].set_ylabel("Silhouette")
ejes[1].set_title("Silhouette por algoritmo"); ejes[1].legend()
plt.tight_layout(); plt.savefig(FIG / "m4_codo_silhouette.png", dpi=130); plt.show()

plt.figure(figsize=(9, 4.5))
dendrogram(linkage(X, "ward"), truncate_mode="lastp", p=30, show_leaf_counts=True, leaf_rotation=90)
plt.title("Dendrograma (Ward, últimos 30 grupos fusionados)"); plt.ylabel("Distancia de fusión")
plt.tight_layout(); plt.savefig(FIG / "m4_dendrograma.png", dpi=130); plt.show()

pca = PCA(n_components=2, random_state=SEMILLA).fit(X)
P = pca.transform(X)
plt.figure(figsize=(6.5, 5))
for c in sorted(set(ref)):
    plt.scatter(P[ref == c, 0], P[ref == c, 1], s=22, label=("ruido" if c == -1 else f"Clúster {c}"))
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.0f} % de la varianza)"); plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.0f} %)")
plt.title("Países en 2D (PCA) por clúster"); plt.legend(); plt.tight_layout(); plt.savefig(FIG / "m4_pca_clusters.png", dpi=130); plt.show()

fig, ax = plt.subplots(figsize=(8, 0.6 * len(ids) + 2))
im = ax.imshow(z_perfil.to_numpy(), cmap="coolwarm", vmin=-2, vmax=2, aspect="auto")
ax.set_xticks(range(len(VARS))); ax.set_xticklabels([v.replace("comp_", "").replace("_pct", "") for v in VARS], rotation=35, ha="right")
ax.set_yticks(range(len(z_perfil))); ax.set_yticklabels([f"Clúster {c} (n={tamanos[c]})" for c in z_perfil.index])
for i in range(z_perfil.shape[0]):
    for j in range(z_perfil.shape[1]):
        ax.text(j, i, f"{z_perfil.iloc[i, j]:.1f}", ha="center", va="center", fontsize=8)
plt.colorbar(im, label="Mediana del clúster vs. mediana global (en desv. est.)"); plt.title("Perfil de cada clúster")
plt.tight_layout(); plt.savefig(FIG / "m4_perfiles.png", dpi=130); plt.show()

def a_json(x):
    if isinstance(x, dict): return {str(k): a_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [a_json(v) for v in x]
    if isinstance(x, (np.floating, float)): return None if np.isnan(x) else float(x)
    if isinstance(x, np.integer): return int(x)
    return x

paises = df[["iso3c", "pais", "income_id", "region_id"] + VARS].copy()
paises["cluster"] = ref
paises[["pc1", "pc2"]] = P
paises.to_csv(config.DATA_PROCESSED / "clustering_paises.csv", index=False)
cfg = ganador["cfg"]
artefacto = {"prep": prep, "centroides": cent, "ids_cluster": [int(c) for c in ids], "variables": VARS, "pca": pca,
             "algoritmo": cfg["algoritmo"], "parametros": json.loads(cfg["parametros"])}
joblib.dump(artefacto, config.MODELS_DIR / "clustering_mejor.pkl")
# Comprobación: asignar cada país al centroide más cercano reproduce las etiquetas?
rec = joblib.load(config.MODELS_DIR / "clustering_mejor.pkl")
Xr = rec["prep"].transform(df[VARS])
asig = np.array(rec["ids_cluster"])[np.argmin(np.linalg.norm(Xr[:, None, :] - rec["centroides"][None, :, :], axis=2), axis=1)]
coincide = float((asig == ref).mean() * 100)
print(f"Asignación por centroide más cercano coincide con las etiquetas en el {coincide:.1f} % de los países")

meta = {
    "modulo": "clustering", "variante": "A (países, DS1)",
    "modelo": f"{cfg['algoritmo']} {cfg['parametros']}",
    "fecha": datetime.date.today().isoformat(),
    "dataset": "DS1 What a Waste (nivel país), data/processed/paises_residuos.csv",
    "n_entrenamiento": int(len(df)), "n_prueba": 0,
    "parametros": json.loads(cfg["parametros"]),
    "metricas": {"silhouette": float(cfg["silhouette"]), "davies_bouldin": float(cfg["davies_bouldin"]),
                 "calinski_harabasz": float(cfg["calinski_harabasz"]), "n_clusters": int(cfg["n_clusters"]),
                 "ruido_pct": float(cfg["ruido_pct"])},
    "features": VARS, "clases": [int(c) for c in ids],
    "librerias": {"scikit-learn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
    "preprocesamiento": "log1p y estandarización de las 7 variables; asignación de países nuevos al centroide más cercano",
    "regla_seleccion": "mayor Silhouette con 3 a 8 clústeres, ruido <= 10 %, tamaño mínimo 5; desempate por menor Davies-Bouldin",
    "mejor_sin_restricciones": {"algoritmo": sin_restr["algoritmo"], "parametros": sin_restr["parametros"],
                                "n_clusters": int(sin_restr["n_clusters"]), "silhouette": float(sin_restr["silhouette"])},
    "comparacion_algoritmos": mejor_por_alg.to_dict(orient="records"),
    "estabilidad": estab, "contraste_externo": contraste, "sensibilidad": sens,
    "paises_usados": int(len(df)), "paises_descartados": descartados["pais"].tolist(), "vacios_pct": vacios.to_dict(),
    "perfiles": {str(c): {"n_paises": int(tamanos[c]), "mediana": perfil_med.loc[c].to_dict(),
                          "ingreso": df[df["cluster"] == c]["income_id"].value_counts().to_dict(),
                          "representativos": representativos[int(c)]} for c in ids},
    "notas": ("Los clústeres describen perfiles de residuos, no causas; los datos de DS1 son de años distintos según el país; "
              "se excluyen los países con algún dato faltante en las 7 variables; el resultado depende de las variables y del "
              "preprocesamiento, y el Silhouette es una guía, no una prueba. Los nombres de los clústeres están en models/clustering_nombres.json."),
}
(config.MODELS_DIR / "clustering_meta.json").write_text(json.dumps(a_json(meta), ensure_ascii=False, indent=2), encoding="utf-8")
print("Guardados: models/clustering_mejor.pkl, models/clustering_meta.json y data/processed/clustering_paises.csv")

L = [f"Países en el CSV: {len(df0)}; usados (7 variables completas): {len(df)}; descartados: {len(descartados)}",
     f"Vacíos % por variable: {vacios.to_dict()}",
     f"scikit-learn {sklearn.__version__}",
     "", "Mejor configuración elegible por algoritmo:", mejor_por_alg.round(3).to_string(index=False),
     "", f"Ganador: {cfg['algoritmo']} {cfg['parametros']}; {int(cfg['n_clusters'])} clústeres; Silhouette {cfg['silhouette']:.3f}; "
         f"Davies-Bouldin {cfg['davies_bouldin']:.3f}; Calinski-Harabasz {cfg['calinski_harabasz']:.1f}; ruido {cfg['ruido_pct']:.1f} %; tamaño mínimo {int(cfg['tam_min'])}",
     f"Mejor Silhouette sin restricciones: {sin_restr['algoritmo']} {sin_restr['parametros']} -> {int(sin_restr['n_clusters'])} clústeres, {sin_restr['silhouette']:.3f}",
     "", "K-Means (codo):", codo.round(3).to_string(index=False),
     "", f"Estabilidad (30 submuestras del 80 %): ARI {estab['ARI_media']:.3f} ± {estab['ARI_desv']:.3f} (mín {estab['ARI_min']:.3f})",
     "", "Contraste externo:", pd.DataFrame(contraste).T.round(3).to_string(),
     "", "Sensibilidad:", json.dumps(sens, ensure_ascii=False),
     "", "Perfil (mediana) y tamaño por clúster:", perfil_med.assign(n_paises=tamanos).round(2).to_string(),
     "", "Clúster por grupo de ingreso:", pd.crosstab(df["cluster"], df["income_id"]).to_string(),
     "", "Clúster por región:", pd.crosstab(df["cluster"], df["region_id"]).to_string(),
     "", "Países más cercanos al centro de cada clúster:"] + [f"  Clúster {c}: {', '.join(v)}" for c, v in representativos.items()] + \
    ["", f"Asignación por centroide coincide con las etiquetas en el {coincide:.1f} % de los países"]
texto = "\n".join(L)
(config.DATA_PROCESSED / "m4_resumen.txt").write_text(texto + "\n", encoding="utf-8")
print(texto)
