"""Módulo 4 · Clustering: agrupa países por su perfil de residuos (generación y composición).
La app NO entrena: usa models/clustering_mejor.pkl, models/clustering_meta.json y data/processed/clustering_paises.csv."""
import json
import traceback

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config
from app.utils.graficos import mostrar_metricas
from app.utils.modelos import cargar_joblib, leer_meta

ARCHIVO_MODELO = "clustering_mejor.pkl"
ARCHIVO_META = "clustering_meta.json"
ARCHIVO_NOMBRES = "clustering_nombres.json"
ARCHIVO_PAISES = "clustering_paises.csv"
ETIQUETAS = {"gpc_kg_hab_dia": "Generación (kg/hab/día)", "comp_food_organic_waste_pct": "Orgánico (%)",
             "comp_paper_cardboard_pct": "Papel y cartón (%)", "comp_plastic_pct": "Plástico (%)",
             "comp_glass_pct": "Vidrio (%)", "comp_metal_pct": "Metal (%)", "comp_other_pct": "Otros (%)"}


# ---------- Funciones puras (sin Streamlit; las usan las pruebas de la Fase 8) ----------
def etiqueta(variable):
    return ETIQUETAS.get(variable, variable)


def cargar_nombres(meta):
    """(nombres, avisos): nombre, descripción y política por clúster. Si el archivo no existe o es de otra ejecución, numera."""
    base = {int(c): {"nombre": f"Clúster {c}", "descripcion": "", "politica": ""} for c in meta["clases"]}
    ruta = config.MODELS_DIR / ARCHIVO_NOMBRES
    if not ruta.exists():
        return base, [("info", "No hay archivo de nombres: los clústeres se muestran numerados.")]
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    esperado = {int(k): v for k, v in datos.get("tamanos_de_la_ejecucion", {}).items()}
    real = {int(c): p["n_paises"] for c, p in meta.get("perfiles", {}).items()}
    if esperado != real:
        return base, [("warning", f"Los nombres de `clustering_nombres.json` son de otra ejecución (tamaños {esperado} frente a {real}); "
                                  "se muestran los clústeres numerados. Hay que revisar los nombres.")]
    for k, v in datos.get("clusters", {}).items():
        base[int(k)].update(v)
    return base, []


def asignar_perfil(art, valores):
    """Asigna un perfil nuevo al centroide más cercano (espacio estandarizado). Devuelve (cluster, distancias, vector)."""
    fila = pd.DataFrame([{v: valores[v] for v in art["variables"]}])
    x = art["prep"].transform(fila)[0]
    dist = np.linalg.norm(art["centroides"] - x, axis=1)
    return int(art["ids_cluster"][int(np.argmin(dist))]), dict(zip(art["ids_cluster"], dist.tolist())), x


def vecinos_de_vector(art, paises, x, n=5, excluir=None):
    """Los n países más cercanos a un vector estandarizado x. Devuelve un DataFrame con la distancia."""
    X = art["prep"].transform(paises[art["variables"]])
    d = np.linalg.norm(X - x, axis=1)
    tabla = paises.assign(distancia=d)
    if excluir is not None:
        tabla = tabla[tabla["iso3c"] != excluir]
    return tabla.sort_values("distancia").head(n)


def margen_frontera(distancias):
    """(d2 - d1) / d2: cerca de 0 si el perfil está casi a la misma distancia de dos grupos."""
    d = sorted(distancias.values())
    return float((d[1] - d[0]) / d[1]) if len(d) > 1 and d[1] > 0 else 1.0


def z_perfiles(paises, variables):
    """Mediana de cada clúster menos la mediana global, en desviaciones estándar globales."""
    med, sd = paises[variables].median(), paises[variables].std()
    return (paises.groupby("cluster")[variables].median() - med) / sd


def avisos_estructura(meta):
    """Advertencias sobre qué tan definida y estable es la agrupación, calculadas con las métricas del meta."""
    avisos = []
    sil = meta["metricas"].get("silhouette")
    if sil is not None and sil <= 0.25:
        avisos.append(("warning", f"El Silhouette es {sil:.3f}: según una convención habitual (≤ 0.25) los grupos no están bien separados. "
                                  "Los países forman un continuo y los grupos son una tipología orientativa."))
    est = meta.get("estabilidad")
    if est and est["ARI_media"] < 0.8:
        avisos.append(("warning", f"Estabilidad moderada: al repetir el agrupamiento con el 80 % de los países, el ARI medio es {est['ARI_media']:.2f} "
                                  f"± {est['ARI_desv']:.2f} (mínimo {est['ARI_min']:.2f})."))
    clr = meta.get("sensibilidad", {}).get("CLR")
    if clr and clr["ARI_vs_principal"] < 0.5:
        avisos.append(("info", f"Con otro preprocesamiento (log-ratio de la composición) la concordancia es baja (ARI {clr['ARI_vs_principal']:.2f}): "
                               "el resultado depende de cómo se transforman los porcentajes."))
    return avisos


def ruido_configuracion(algoritmo, parametros):
    """% de ruido de una configuración, leído de data/processed/m4_resultados.csv; None si no se puede."""
    ruta = config.DATA_PROCESSED / "m4_resultados.csv"
    try:
        d = pd.read_csv(ruta)
        fila = d[(d["algoritmo"] == algoritmo) & (d["parametros"].map(lambda s: json.loads(s)) == json.loads(parametros))]
        return float(fila["ruido_pct"].iloc[0]) if len(fila) else None
    except Exception:  # noqa: BLE001
        return None


def validar_perfil(valores, comp_vars):
    """Avisos sobre un perfil introducido a mano (la composición no puede sumar más de 100 %)."""
    suma = sum(valores[v] for v in comp_vars)
    return suma, ([("error", f"Los porcentajes de composición suman {suma:.1f} %: no pueden pasar de 100 %.")] if suma > 100.5 else [])


# ---------- Interfaz ----------
@st.cache_data
def _leer_paises():
    df = pd.read_csv(config.DATA_PROCESSED / ARCHIVO_PAISES)
    df["pais"] = df["pais"].fillna(df["iso3c"]).astype(str)  # un nombre vacío no debe romper la lista ni el ordenamiento
    return df


def _nombre(nombres, c):
    return f"{nombres[int(c)]['nombre']} (clúster {int(c)})"


def _pais(meta, art, paises, nombres):
    modo = st.radio("¿Qué quieres explorar?", ["País del dataset", "Perfil nuevo"], horizontal=True, key="clu_modo")
    variables = art["variables"]
    seleccion = None
    if modo == "País del dataset":
        pais = st.selectbox("País o territorio", sorted(paises["pais"].unique()), key="clu_pais")
        seleccion = paises[paises["pais"] == pais].iloc[0]
        c = int(seleccion["cluster"])
        x = art["prep"].transform(paises.loc[[seleccion.name], variables])[0]
        vec = vecinos_de_vector(art, paises, x, 5, excluir=seleccion["iso3c"])
        valores = {v: float(seleccion[v]) for v in variables}
        c1, c2, c3 = st.columns(3)
        c1.metric("Grupo", f"Clúster {c}")
        c2.metric("Países en el grupo", int(meta["perfiles"][str(c)]["n_paises"]))
        c3.metric("Ingreso · región", f"{seleccion['income_id']} · {seleccion['region_id']}")
        st.subheader(nombres[c]["nombre"])  # el nombre completo no cabe en un st.metric
    else:
        st.caption("Introduce un perfil de residuos; se asigna al grupo cuyo centro está más cerca.")
        med = paises[variables].median()
        valores = {}
        cols = st.columns(len(variables))
        for col, v in zip(cols, variables):
            maximo = 10.0 if v == "gpc_kg_hab_dia" else 100.0
            valores[v] = col.number_input(etiqueta(v), min_value=0.0, max_value=maximo, value=float(round(med[v], 1)),
                                          step=0.1 if v == "gpc_kg_hab_dia" else 0.5, key=f"clu_in_{v}")
        comp_vars = [v for v in variables if v != "gpc_kg_hab_dia"]
        suma, avisos = validar_perfil(valores, comp_vars)
        st.caption(f"Suma de la composición: {suma:.1f} % (el resto sería caucho, madera y residuos de jardín).")
        for nivel, texto in avisos:
            st.error(texto)
        if avisos:
            return None
        c, dist, x = asignar_perfil(art, valores)
        vec = vecinos_de_vector(art, paises, x, 5)
        st.metric("Grupo asignado", _nombre(nombres, c))
        if margen_frontera(dist) < 0.15:
            st.warning("El perfil está casi a la misma distancia de dos grupos (límite entre ellos): la asignación es poco firme.")
        figd = px.bar(pd.DataFrame({"grupo": [_nombre(nombres, k) for k in dist], "distancia": list(dist.values())}),
                      x="grupo", y="distancia", title="Distancia a cada centro (menor = más parecido)")
        figd.update_layout(margin=dict(t=50, b=20))
        st.plotly_chart(figd)

    info = nombres[c]
    if info["descripcion"]:
        st.info(info["descripcion"])
    med_global, sd_global = paises[variables].median(), paises[variables].std()
    med_cluster = pd.Series(meta["perfiles"][str(c)]["mediana"])
    tabla = pd.DataFrame({"Variable": [etiqueta(v) for v in variables], "Valor": [valores[v] for v in variables],
                          "Mediana del grupo": [med_cluster[v] for v in variables], "Mediana global": [med_global[v] for v in variables]})
    st.dataframe(tabla.round(2))
    z = pd.DataFrame({"Variable": [etiqueta(v) for v in variables] * 2,
                      "Serie": ["Este perfil"] * len(variables) + ["Mediana del grupo"] * len(variables),
                      "Desviaciones vs. mediana global": [(valores[v] - med_global[v]) / sd_global[v] for v in variables]
                                                         + [(med_cluster[v] - med_global[v]) / sd_global[v] for v in variables]})
    figz = px.bar(z, x="Variable", y="Desviaciones vs. mediana global", color="Serie", barmode="group",
                  title="Perfil frente al promedio de los países (en desviaciones estándar)")
    figz.update_layout(margin=dict(t=50, b=20))
    st.plotly_chart(figz)

    st.subheader("Países más parecidos")
    mostrar = vec[["pais", "cluster", "income_id", "region_id", "distancia"]].copy()
    mostrar["cluster"] = mostrar["cluster"].map(lambda k: nombres[int(k)]["nombre"])
    mostrar.columns = ["País", "Grupo", "Ingreso", "Región", "Distancia"]
    st.dataframe(mostrar.round(2))
    fuera = int((vec["cluster"] != c).sum())
    if fuera:
        st.caption(f"{fuera} de los 5 países más parecidos pertenecen a otro grupo: los límites entre grupos son difusos.")
    return seleccion


def _mapa(meta, art, paises, nombres, seleccion):
    var_exp = art["pca"].explained_variance_ratio_
    df = paises.assign(grupo=paises["cluster"].map(lambda k: nombres[int(k)]["nombre"]))
    orden = [nombres[int(k)]["nombre"] for k in art["ids_cluster"]]
    fig = px.scatter(df, x="pc1", y="pc2", color="grupo", hover_name="pais", hover_data=["income_id", "region_id"],
                     category_orders={"grupo": orden}, title="Países en 2 dimensiones (PCA) por grupo")
    if seleccion is not None:
        fig.add_trace(go.Scatter(x=[seleccion["pc1"]], y=[seleccion["pc2"]], mode="markers+text", text=[seleccion["pais"]],
                                 textposition="top center", marker=dict(size=14, symbol="star", color="black"), name="Seleccionado"))
    fig.update_xaxes(title=f"PC1 ({var_exp[0] * 100:.0f} % de la varianza)")
    fig.update_yaxes(title=f"PC2 ({var_exp[1] * 100:.0f} %)")
    fig.update_layout(margin=dict(t=50, b=20))
    st.plotly_chart(fig)
    st.caption("El mapa resume 7 dimensiones en 2: dos países cercanos aquí pueden diferir en dimensiones que no se ven. "
               "Los grupos se solapan, lo que refleja una estructura débil.")

    z = z_perfiles(paises, art["variables"])
    z.index = [nombres[int(k)]["nombre"] for k in z.index]
    z.columns = [etiqueta(v) for v in z.columns]
    figh = px.imshow(z, text_auto=".1f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-2, zmax=2,
                     title="Perfil de cada grupo (mediana frente a la global, en desv. estándar)")
    figh.update_layout(margin=dict(t=50, b=20))
    st.plotly_chart(figh)

    st.subheader("Los grupos")
    for k in art["ids_cluster"]:
        info, perfil = nombres[int(k)], meta["perfiles"][str(k)]
        with st.expander(f"{_nombre(nombres, k)} · {perfil['n_paises']} países"):
            if info["descripcion"]:
                st.write(info["descripcion"])
            st.write(f"**Ingreso de sus países:** {perfil['ingreso']}")
            st.write(f"**Países más cercanos al centro:** {', '.join(perfil['representativos'])}")
            if info["politica"]:
                st.write(f"**Política sugerida (orientativa, no se deriva de los datos):** {info['politica']}")


def _modelo(meta):
    st.subheader(meta.get("modelo", "Modelo"))
    mostrar_metricas(meta)
    st.caption(f"{meta['paises_usados']} países usados; {len(meta['paises_descartados'])} descartados por falta de datos de composición. "
               f"Variables: {', '.join(etiqueta(v) for v in meta['features'])}. Preprocesamiento: {meta.get('preprocesamiento', '')}.")
    for nivel, texto in avisos_estructura(meta):
        (st.warning if nivel == "warning" else st.info)(texto)
    comp = pd.DataFrame(meta.get("comparacion_algoritmos", []))
    if len(comp):
        st.markdown("**Comparación de algoritmos** (mejor configuración que cumple la regla: 3 a 8 grupos, ≤ 10 % de ruido, mínimo 5 países por grupo)")
        st.dataframe(comp.round(3))
        faltan = [a for a in ["K-Means", "Agglomerative (Ward)", "GMM (diag)", "DBSCAN"] if a not in set(comp["algoritmo"])]
        if faltan:
            st.caption(f"Sin configuración que cumpla la regla: {', '.join(faltan)}.")
    sr = meta.get("mejor_sin_restricciones")
    if sr:
        ruido = ruido_configuracion(sr["algoritmo"], sr["parametros"])
        extra = (f" Tenía {ruido:.1f} % de ruido, así que su Silhouette cubre solo el {100 - ruido:.1f} % de los países." if ruido is not None else "")
        st.caption(f"Mejor Silhouette sin restricciones: {sr['algoritmo']} {sr['parametros']} → {sr['n_clusters']} grupos, "
                   f"{sr['silhouette']:.3f}; el Silhouette solo se calcula sobre puntos que no son ruido.{extra}")
    est = meta.get("estabilidad")
    if est:
        st.markdown(f"**Estabilidad:** ARI {est['ARI_media']:.3f} ± {est['ARI_desv']:.3f} (mínimo {est['ARI_min']:.3f}) con {est['repeticiones']} submuestras del {est['fraccion'] * 100:.0f} %.")
    if meta.get("contraste_externo"):
        st.markdown("**Contraste con ingreso y región** (referencia, no verdad absoluta)")
        st.dataframe(pd.DataFrame(meta["contraste_externo"]).T.round(3))
    if meta.get("sensibilidad"):
        st.markdown("**Sensibilidad**")
        st.json(meta["sensibilidad"])
    for nombre, pie in (("m4_codo_silhouette.png", "Codo y Silhouette"), ("m4_dendrograma.png", "Dendrograma"),
                        ("m4_perfiles.png", "Perfiles de los grupos")):
        ruta = config.DOCS_DIR / "figuras" / nombre
        if ruta.exists():
            st.image(str(ruta), caption=pie)
    with st.expander("Países sin datos suficientes (no agrupados)"):
        st.write(", ".join("(sin nombre)" if p is None else str(p) for p in meta["paises_descartados"]))
    if meta.get("notas"):
        st.caption(f"Limitaciones: {meta['notas']}")


def render():
    st.header("🧩 Clustering de países por perfil de residuos")
    st.write("Agrupa países según cuánto residuo generan por habitante y de qué se compone. Es un análisis exploratorio: "
             "describe parecidos, no causas.")
    try:
        meta = leer_meta(ARCHIVO_META)
        art = cargar_joblib(ARCHIVO_MODELO)
        paises = _leer_paises()
    except FileNotFoundError as e:
        st.info(f"Este módulo aún no tiene modelo entrenado. {e}")
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudo cargar el modelo: {e}")
        return
    try:
        nombres, avisos_n = cargar_nombres(meta)
        for nivel, texto in avisos_n:
            (st.warning if nivel == "warning" else st.info)(texto)
        for nivel, texto in avisos_estructura(meta)[:1]:
            st.warning(texto)
        pestanas = st.tabs(["Explorar", "Mapa y grupos", "Modelo y métricas"])
        with pestanas[0]:
            seleccion = _pais(meta, art, paises, nombres)
        with pestanas[1]:
            _mapa(meta, art, paises, nombres, seleccion)
        with pestanas[2]:
            _modelo(meta)
        with st.expander("Aviso de uso responsable y fuentes"):
            st.write(config.AVISO_USO)
            st.write("Datos: Banco Mundial, *What a Waste* (nivel país; licencia indicada en la ficha: CC-BY-4.0). Los años de referencia "
                     "difieren entre países, y los nombres y políticas de los grupos son propuestas del equipo, no resultados del algoritmo.")
    except Exception as e:  # noqa: BLE001
        st.error(f"El módulo de clustering falló: {e}")
        with st.expander("Detalle técnico del error"):
            st.code(traceback.format_exc())
