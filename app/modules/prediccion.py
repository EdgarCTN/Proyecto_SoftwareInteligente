"""Módulo 1 · Predicción de la generación de residuos per cápita (kg/hab/día) a partir de variables socioeconómicas.
La app NO entrena: carga models/prediccion_mejor.pkl y lee las métricas de models/prediccion_meta.json."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

import config
from app.utils.datos import cargar_procesado
from app.utils.graficos import mostrar_metricas
from app.utils.modelos import cargar_joblib, leer_meta

ARCHIVO_MODELO = "prediccion_mejor.pkl"
ARCHIVO_META = "prediccion_meta.json"
ORDEN_INGRESO = ["HIC", "UMC", "LMC", "LIC"]
NOMBRE_INGRESO = {"HIC": "ingreso alto", "UMC": "ingreso medio-alto", "LMC": "ingreso medio-bajo", "LIC": "ingreso bajo"}


# ---------- Funciones puras (sin Streamlit; las usan las pruebas de la Fase 8) ----------
def fmt(x, decimales=0):
    """Número con espacio como separador de miles."""
    return f"{x:,.{decimales}f}".replace(",", " ")


def construir_tabla(valores, features, n=1):
    """DataFrame con las columnas que espera el modelo, en su orden. Un valor puede ser escalar o una lista de n valores."""
    faltan = [f for f in features if f not in valores]
    if faltan:
        raise KeyError(faltan)
    return pd.DataFrame({f: (list(valores[f]) if isinstance(valores[f], (list, tuple, np.ndarray)) else [valores[f]] * n)
                         for f in features})


def estimar(modelo, tabla):
    """Predicciones en kg/hab/día. Devuelve (array sin valores negativos, hubo_negativos)."""
    pred = np.asarray(modelo.predict(tabla), dtype=float)
    return np.clip(pred, 0.0, None), bool((pred < 0).any())


def avisos_rango(gdp, poblacion, meta):
    """Lista de (nivel, texto) cuando los valores salen del rango de entrenamiento o parecen un territorio extremo."""
    rg = meta.get("rangos_variables", {})
    avisos = []
    for nombre, valor, etiqueta in (("gdp", gdp, "El PIB"), ("poblacion", poblacion, "La población")):
        r = rg.get(nombre)
        if not r:
            continue
        if valor < r["min"] or valor > r["max"]:
            avisos.append(("warning", f"{etiqueta} está fuera del rango de los países usados para entrenar "
                                      f"({fmt(r['min'])} a {fmt(r['max'])}): es una extrapolación y la estimación es poco fiable."))
        elif valor < r["p05"] or valor > r["p95"]:
            avisos.append(("info", f"{etiqueta} está en los extremos del rango de entrenamiento (fuera del percentil 5 a 95)."))
    g, p = rg.get("gdp"), rg.get("poblacion")
    if g and p and poblacion < p["p05"] and gdp > g["mediana"]:
        extremos = ", ".join(meta.get("extremos", []))
        avisos.append(("warning", "Perfil de territorio pequeño de ingreso alto. Los 5 países con mayor generación per cápita del "
                                  f"dataset ({extremos}) son de este tipo y hay pocos casos parecidos: trata la estimación con más cautela."))
    return avisos


def referencia(meta, tipo, clave):
    """Promedio de generación (y n) de una región o grupo de ingreso, desde el meta; None si no existe."""
    return meta.get("referencias_app", {}).get(tipo, {}).get(clave)


def comparacion_con_baseline(meta):
    """Mejora porcentual del modelo frente al baseline en la prueba, o None si el meta no trae el baseline."""
    m, b = meta.get("metricas", {}), meta.get("baseline", {}).get("metricas_prueba")
    if not b or m.get("RMSE") is None or m.get("MAE") is None:
        return None
    return {"rmse_modelo": m["RMSE"], "rmse_base": b["RMSE"], "mae_modelo": m["MAE"], "mae_base": b["MAE"],
            "mejora_rmse_pct": (b["RMSE"] - m["RMSE"]) / b["RMSE"] * 100, "mejora_mae_pct": (b["MAE"] - m["MAE"]) / b["MAE"] * 100}


def curva_pib(modelo, meta, poblacion, region, puntos=60):
    """Estimación para PIB entre el mínimo y el máximo de entrenamiento (población y región fijas)."""
    rg = meta["rangos_variables"]["gdp"]
    grilla = np.geomspace(max(rg["min"], 1.0), rg["max"], puntos)
    tabla = construir_tabla({"gdp": grilla, "poblacion": poblacion, "region_id": region}, meta["features"], puntos)
    pred, _ = estimar(modelo, tabla)
    return pd.DataFrame({"gdp": grilla, "estimacion": pred})


# ---------- Interfaz ----------
def _simulador(meta, modelo):
    rg, cat = meta["rangos_variables"], meta["categorias"]
    rmse, n_prueba = meta["metricas"]["RMSE"], meta["n_prueba"]
    entrada, resultado = st.columns([1, 2])
    with entrada:
        st.subheader("Datos del país")
        gdp = st.number_input("PIB (en las unidades del dataset)", min_value=0.0, value=float(round(rg["gdp"]["mediana"])),
                              step=500.0, format="%.0f", key="pred_gdp",
                              help="Por su magnitud parece un PIB per cápita; confirmar con el codebook de la fuente.")
        poblacion = st.number_input("Población (habitantes)", min_value=1000, value=int(rg["poblacion"]["mediana"]),
                                    step=100000, format="%d", key="pred_pob")
        region = st.selectbox("Región (código del Banco Mundial)", cat["region_id"], key="pred_region")
        grupos = [g for g in ORDEN_INGRESO if g in cat.get("income_id", [])]
        grupo = st.selectbox("Grupo de ingreso para comparar (opcional)", ["(no comparar)"] + grupos, key="pred_grupo",
                             format_func=lambda g: g if g == "(no comparar)" else f"{g} · {NOMBRE_INGRESO.get(g, '')}")
    valores = {"gdp": gdp, "poblacion": poblacion, "region_id": region}
    try:
        tabla = construir_tabla(valores, meta["features"])
    except KeyError as e:
        st.warning(f"El modelo guardado usa variables que este simulador no sabe pedir: {e.args[0]}. "
                   "Vuelve a entrenar con el conjunto A0 o actualiza el módulo.")
        return
    pred, hubo_neg = estimar(modelo, tabla)
    est = float(pred[0])
    with resultado:
        st.subheader("Estimación")
        for nivel, texto in avisos_rango(gdp, poblacion, meta):
            (st.warning if nivel == "warning" else st.info)(texto)
        c1, c2, c3 = st.columns(3)
        c1.metric("Generación per cápita", f"{est:.2f} kg/hab/día")
        c2.metric("Banda orientativa (± error típico)", f"{max(est - rmse, 0):.2f} a {est + rmse:.2f}")
        c3.metric("Equivale a (nacional)", f"{fmt(est * poblacion * 365 / 1000)} t/año")
        st.caption(f"Error típico = RMSE en {n_prueba} países de prueba ({rmse:.2f} kg/hab/día); no es un intervalo de confianza formal. "
                   "Es un promedio nacional estimado, no una ciudad.")
        if hubo_neg:
            st.caption("El modelo calculó un valor negativo; se muestra 0.")

    nombres, valores_y, errores = ["Estimación del modelo"], [est], [rmse]
    ref_r = referencia(meta, "por_region", region)
    if ref_r:
        nombres.append(f"Promedio región {region} (n = {ref_r['n']})"); valores_y.append(ref_r["media"]); errores.append(0)
        if ref_r["n"] < 5:
            st.caption(f"La región {region} tiene solo {ref_r['n']} países en el dataset: su promedio es poco representativo.")
    if grupo != "(no comparar)":
        ref_g = referencia(meta, "por_ingreso", grupo)
        if ref_g:
            nombres.append(f"Promedio grupo {grupo} (n = {ref_g['n']})"); valores_y.append(ref_g["media"]); errores.append(0)
    fig = go.Figure(go.Bar(x=nombres, y=valores_y, error_y=dict(type="data", array=errores, visible=True)))
    fig.update_layout(title="Comparación (kg/hab/día)", yaxis_title="kg/hab/día", margin=dict(t=50, b=20))
    st.plotly_chart(fig)

    st.subheader("¿Qué pasa si cambia el PIB?")
    curva = curva_pib(modelo, meta, poblacion, region)
    figc = go.Figure()
    figc.add_trace(go.Scatter(x=list(curva["gdp"]) + list(curva["gdp"][::-1]),
                              y=list(curva["estimacion"] + rmse) + list((curva["estimacion"] - rmse).clip(lower=0)[::-1]),
                              fill="toself", line=dict(width=0), opacity=0.2, name="± error típico"))
    figc.add_trace(go.Scatter(x=curva["gdp"], y=curva["estimacion"], mode="lines", name="Estimación"))
    figc.add_trace(go.Scatter(x=[gdp], y=[est], mode="markers", name="Tu valor", marker=dict(size=11)))
    figc.update_layout(title="Estimación según el PIB (población y región fijas)", xaxis_title="PIB (escala logarítmica)",
                       yaxis_title="kg/hab/día", xaxis_type="log", margin=dict(t=50, b=20))
    st.plotly_chart(figc)
    st.caption("Es una asociación entre países, no una causa: subir el PIB de un país no garantiza que aumente su generación.")


def _paises(meta, modelo):
    df = cargar_procesado("paises").copy()
    df["pais"] = df["pais"].fillna(df["iso3c"]).astype(str)  # p. ej. TWN no trae nombre en DS1: se muestra su código
    pais = st.selectbox("País o territorio", sorted(df["pais"].unique()), key="pred_pais")
    fila = df[df["pais"] == pais].iloc[0]
    st.info("Ajuste **dentro de la muestra**: el modelo final se reentrenó con todos los países, así que esta comparación "
            "NO es una validación. Las métricas de validación están en la pestaña «Modelo y métricas».")
    if fila["iso3c"] in meta.get("extremos", []):
        st.warning("Este país está entre los 5 con mayor generación per cápita del dataset (territorios pequeños de ingreso alto).")
    faltan = [f for f in meta["features"] if f not in fila.index]
    if faltan:
        st.warning(f"El CSV no tiene las variables del modelo: {faltan}")
        return
    pred, _ = estimar(modelo, construir_tabla({f: fila[f] for f in meta["features"]}, meta["features"]))
    real = fila["gpc_kg_hab_dia"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor real (derivado)", "sin dato" if pd.isna(real) else f"{real:.2f} kg/hab/día")
    c2.metric("Ajuste del modelo", f"{pred[0]:.2f} kg/hab/día")
    c3.metric("Diferencia", "—" if pd.isna(real) else f"{pred[0] - real:+.2f}")
    ref_r, ref_g = referencia(meta, "por_region", fila["region_id"]), referencia(meta, "por_ingreso", fila["income_id"])
    st.caption(f"Región {fila['region_id']}: promedio {ref_r['media']:.2f} (n = {ref_r['n']}) · "
               f"Grupo {fila['income_id']}: promedio {ref_g['media']:.2f} (n = {ref_g['n']})." if ref_r and ref_g
               else f"Región {fila['region_id']} · grupo {fila['income_id']}.")


def _modelo(meta):
    st.subheader(meta.get("modelo", "Modelo"))
    mostrar_metricas(meta)
    comp = comparacion_con_baseline(meta)
    if comp:
        mejor = comp["mejora_rmse_pct"] > 0
        st.markdown(
            f"**Frente al baseline** (promedio del grupo de ingreso), en {meta['n_prueba']} países de prueba el modelo "
            f"{'reduce' if mejor else 'NO reduce'} el RMSE de {comp['rmse_base']:.3f} a {comp['rmse_modelo']:.3f} "
            f"({comp['mejora_rmse_pct']:+.1f} %) y el MAE de {comp['mae_base']:.3f} a {comp['mae_modelo']:.3f} ({comp['mejora_mae_pct']:+.1f} %).")
        tabla = pd.DataFrame({"Modelo": meta["metricas"], "Baseline": meta["baseline"]["metricas_prueba"]}).dropna()
        st.dataframe(tabla.round(3))
    cv = meta.get("metricas_cv")
    if cv:
        st.caption(f"Validación cruzada 5×3 sobre entrenamiento: RMSE {cv['RMSE_cv']:.3f} ± {cv['RMSE_cv_std']:.3f}. "
                   "Un valor de la prueba (n pequeño) tiene incertidumbre: no sobreinterpretar diferencias pequeñas.")
    if meta.get("metricas_sin_extremos"):
        st.markdown("**Prueba sin los 5 países extremos**")
        st.dataframe(pd.DataFrame(meta["metricas_sin_extremos"]).T.round(3))
    imp = meta.get("importancia_permutacion")
    if imp:
        fig = px.bar(pd.DataFrame({"variable": list(imp), "aumento_RMSE": list(imp.values())}).sort_values("aumento_RMSE"),
                     x="aumento_RMSE", y="variable", orientation="h", title="Importancia por permutación (aumento del RMSE)")
        fig.update_layout(margin=dict(t=50, b=20))
        st.plotly_chart(fig)
    st.markdown(f"**Variables:** {', '.join(meta['features'])} · **Parámetros:** {meta.get('parametros', {})} · "
                f"**Entrenamiento:** {meta['n_entrenamiento']} países · **Fecha:** {meta.get('fecha', 's/f')}")
    for nombre, pie in (("m1_comparacion_cv.png", "Comparación de modelos (validación cruzada)"),
                        ("m1_real_vs_predicho.png", "Real vs. predicho en prueba")):
        ruta = config.DOCS_DIR / "figuras" / nombre
        if ruta.exists():
            st.image(str(ruta), caption=pie)
    if meta.get("notas"):
        st.caption(f"Limitaciones: {meta['notas']}")


def render():
    st.header("📈 Predicción de generación de residuos per cápita")
    st.write("Estima cuántos kg de residuos genera por día un habitante de un país a partir de su PIB, su población y su región.")
    try:
        meta = leer_meta(ARCHIVO_META)
        modelo = cargar_joblib(ARCHIVO_MODELO)
    except FileNotFoundError as e:
        st.info(f"Este módulo aún no tiene modelo entrenado. {e}")
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudo cargar el modelo: {e}")
        return
    st.warning(f"Herramienta orientativa: el error típico es de ≈ {meta['metricas']['RMSE']:.2f} kg/hab/día "
               f"(MAPE ≈ {meta['metricas']['MAPE']:.0f} %) y estima un promedio nacional, no una ciudad.")
    pestanas = st.tabs(["Simulador", "Países del dataset", "Modelo y métricas"])
    try:
        for pestana, funcion, args in ((pestanas[0], _simulador, (meta, modelo)), (pestanas[1], _paises, (meta, modelo)),
                                       (pestanas[2], _modelo, (meta,))):
            with pestana:
                funcion(*args)
        with st.expander("Aviso de uso responsable y fuentes"):
            st.write(config.AVISO_USO)
            st.write("Datos: Banco Mundial, *What a Waste* (nivel país; licencia indicada en la ficha: CC-BY-4.0). Los años de referencia "
                     "difieren entre países y la relación con el PIB es una asociación, no una causa.")
    except Exception as e:  # noqa: BLE001
        st.error(f"El módulo de predicción falló: {e}")
