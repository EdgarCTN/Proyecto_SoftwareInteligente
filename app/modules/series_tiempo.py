"""Módulo 2 · Series temporales: pronóstico mensual de toneladas de residuos de Nueva York (DSNY, DS2).
La app NO entrena: usa models/serie_<id>.joblib (si no se puede cargar, data/processed/m2_pronostico_<id>.csv) y models/serie_meta.json."""
import json
import traceback

import numpy as np
import pandas as pd
import streamlit as st

import config
from app.utils.datos import cargar_procesado
from app.utils.graficos import grafico_pronostico
from app.utils.modelos import cargar_joblib, cargar_keras, leer_meta

ARCHIVO_META = "serie_meta.json"
NOMBRES = {"ingenuo": "Ingenuo (último valor)", "media_movil": "Media móvil 12 m", "ingenuo_estacional": "Ingenuo estacional",
           "ets": "ETS", "sarimax": "SARIMAX", "sarimax_sin_covid": "SARIMAX sin COVID en el entrenamiento", "lstm": "LSTM"}
SIMPLES = ("ingenuo", "media_movil", "ingenuo_estacional")
CORTOS = {"ingenuo": "Ingenuo", "media_movil": "Media móvil", "ingenuo_estacional": "Ing. estacional", "ets": "ETS", "sarimax": "SARIMAX", "lstm": "LSTM"}
DESCRIPCION_SIMPLE = {"ingenuo": "repite el último valor diario conocido (solo cambia con los días de cada mes)",
                      "media_movil": "repite el promedio diario de los últimos 12 meses (solo cambia con los días de cada mes)",
                      "ingenuo_estacional": "repite lo ocurrido en los mismos meses del año anterior"}


# ---------- Funciones puras (sin interfaz; las usan las pruebas) ----------
def nombre_modelo(m):
    return NOMBRES.get(m, m)


def fmt(x, dec=0):
    """Número con espacio como separador de miles (123 456)."""
    return f"{x:,.{dec}f}".replace(",", " ")


def fechas_futuras(ultima_fecha, h):
    """Fechas (inicio de mes) de los h meses siguientes a `ultima_fecha` ('YYYY-MM')."""
    return pd.date_range(pd.Timestamp(ultima_fecha + "-01") + pd.offsets.MonthBegin(1), periods=h, freq="MS")


def pronosticar(art, h=None):
    """Pronóstico de h meses (por defecto el máximo del artefacto) en TONELADAS POR MES, desde el diccionario de `serie_<id>.joblib`.
    Devuelve un DataFrame con índice de fechas y columnas pronostico, inferior, superior (NaN si el modelo no da intervalo)."""
    h = int(h or art["horizonte_max"])
    idx = fechas_futuras(art["ultima_fecha"], h)
    tipo, lo, hi = art["tipo"], None, None
    if tipo in SIMPLES:
        ult = np.asarray(art["ultimos_12_ton_dia"], dtype=float)
        p = {"ingenuo": np.repeat(ult[-1], h), "media_movil": np.repeat(ult.mean(), h), "ingenuo_estacional": np.resize(ult, h)}[tipo]
    elif tipo == "sarimax":
        cols = art["config"]["exog"]
        exog = pd.DataFrame({c: [art["exog_futuro"][c]] * h for c in cols}, index=idx) if cols else None
        fc = art["modelo"].get_forecast(h, exog=exog)
        ic = fc.conf_int(alpha=0.05)
        esc = art["escala"]
        p, lo, hi = fc.predicted_mean.values * esc, ic.iloc[:, 0].values * esc, ic.iloc[:, 1].values * esc
    elif tipo == "ets":
        m = art["modelo"]
        n = int(m.nobs)
        # los intervalos se simulan; con la misma semilla del entrenamiento coinciden con data/processed/m2_pronostico_<id>.csv (h = 12)
        sf = m.get_prediction(start=n, end=n + h - 1, rng=np.random.default_rng(config.RANDOM_STATE)).summary_frame(alpha=0.05)
        esc = art["escala"]
        p, lo, hi = sf["mean"].values * esc, sf["pi_lower"].values * esc, sf["pi_upper"].values * esc
    elif tipo == "lstm":
        salidas = []
        for nombre in art["keras"]:
            modelo, ventana, s = cargar_keras(nombre), list(art["ultimos_escalados"]), []
            for _ in range(h):                        # pronóstico recursivo, igual que en el entrenamiento
                x = np.array(ventana[-art["look_back"]:], dtype="float32").reshape(1, art["look_back"], 1)
                v = float(modelo(x, training=False)[0, 0])
                s.append(v)
                ventana.append(v)
            salidas.append(s)
        p = np.mean(salidas, axis=0) * (art["escalador_max"] - art["escalador_min"]) + art["escalador_min"]
    else:
        raise ValueError(f"Tipo de modelo desconocido: {tipo}")
    dias = np.asarray(idx.days_in_month)
    nan = np.full(h, np.nan)
    return pd.DataFrame({"pronostico": p * dias, "inferior": nan if lo is None else lo * dias, "superior": nan if hi is None else hi * dias}, index=idx)


def leer_pronostico_csv(meta_serie):
    """Respaldo: la tabla de pronóstico que dejó el entrenamiento (data/processed/m2_pronostico_<id>.csv)."""
    ruta = config.DATA_PROCESSED / meta_serie["archivo_pronostico"]
    if not ruta.exists():
        raise FileNotFoundError(f"No existe data/processed/{ruta.name}.")
    d = pd.read_csv(ruta, parse_dates=["fecha"], index_col="fecha")
    return d.rename(columns={"pronostico_ton_mes": "pronostico", "inferior_ton_mes": "inferior", "superior_ton_mes": "superior"})


def texto_comparacion(tabla, ganador):
    """Frases calculadas desde `tabla_modelos` de serie_meta.json: el modelo elegido frente al ingenuo estacional."""
    if ganador == "ingenuo_estacional" or "ingenuo_estacional" not in tabla:
        return ["El modelo elegido es el propio ingenuo estacional: ningún modelo más complejo lo superó en la validación."]
    g, b = tabla[ganador], tabla["ingenuo_estacional"]
    cambio = lambda x, y: (x / y - 1) * 100
    frases = [f"En validación (media de 4 ventanas de 12 meses) el RMSE del modelo elegido es {fmt(g['RMSE_val'])} t/mes frente a {fmt(b['RMSE_val'])} del ingenuo estacional "
              f"({cambio(g['RMSE_val'], b['RMSE_val']):+.0f} %); MAE {fmt(g['MAE_val'])} frente a {fmt(b['MAE_val'])}; MAPE {g['MAPE_val']:.1f} % frente a {b['MAPE_val']:.1f} %.",
              f"En la ventana de prueba (últimos 12 meses): RMSE {fmt(g['test_RMSE'])} frente a {fmt(b['test_RMSE'])} ({cambio(g['test_RMSE'], b['test_RMSE']):+.0f} %); "
              f"MAE {fmt(g['test_MAE'])} frente a {fmt(b['test_MAE'])}; MAPE {g['test_MAPE']:.1f} % frente a {b['test_MAPE']:.1f} %."]
    peor = [k for k in ("RMSE", "MAE", "MAPE") if g[f"test_{k}"] > b[f"test_{k}"]]
    if peor:
        frases.append("En la prueba el modelo elegido **no mejora** al ingenuo estacional en: " + ", ".join(peor) +
                      ". La prueba es una sola ventana de 12 meses y es menos estable que la validación.")
    return frases


def tabla_modelos_df(meta_serie):
    t = pd.DataFrame(meta_serie["tabla_modelos"]).T
    t.insert(0, "Modelo", [nombre_modelo(m) + (" ★" if m == meta_serie["ganador"] else "") for m in t.index])
    t = t.rename(columns={"RMSE_val": "RMSE validación", "RMSE_val_sd": "± RMSE validación", "MAE_val": "MAE validación", "MAPE_val": "MAPE validación (%)",
                          "test_RMSE": "RMSE prueba", "test_MAE": "MAE prueba", "test_MAPE": "MAPE prueba (%)"})
    return t.reset_index(drop=True).round(2)


def serie_historica(clave_serie, columna, inicio):
    d = cargar_procesado(clave_serie)
    s = pd.Series(d[columna].values, index=pd.to_datetime(d["fecha"]), name=columna)
    return s.loc[inicio + "-01":]


# ---------- Interfaz ----------
@st.cache_data(show_spinner=False)
def _pronostico(sid, archivo_modelo, meta_serie_json, firma):
    """Calcula el pronóstico máximo con el modelo guardado; si no se puede, usa el CSV del entrenamiento. `firma` invalida la caché si cambia el archivo."""
    try:
        return pronosticar(cargar_joblib(archivo_modelo)), "modelo", ""
    except Exception as e:  # noqa: BLE001
        return leer_pronostico_csv(json.loads(meta_serie_json)), "csv", f"{type(e).__name__}: {e}"


def _pronosticar_ui(meta):
    series = meta["series"]
    c1, c2, c3 = st.columns([2, 1, 1])
    sid = c1.selectbox("Serie", list(series), format_func=lambda i: f"{i} · {series[i]['nombre']}")
    hmax = int(meta.get("horizonte_max", 12))
    h = c2.slider("Meses a pronosticar", 1, hmax, hmax)
    ventana = c3.selectbox("Histórico a mostrar", [36, 60, 120, 0], index=1, format_func=lambda v: "Todo" if v == 0 else f"Últimos {v // 12} años")
    ms = series[sid]
    ruta = config.MODELS_DIR / ms["archivo_modelo"]
    firma = ruta.stat().st_mtime_ns if ruta.exists() else 0
    df, origen, aviso = _pronostico(sid, ms["archivo_modelo"], json.dumps(ms), firma)
    p = df.iloc[:h]
    hist = serie_historica("serie_ciudad", ms["columna"], ms["inicio"])
    if ventana:
        hist = hist.iloc[-ventana:]
    con_intervalo = p["inferior"].notna().all()
    fig = grafico_pronostico(hist, p["pronostico"], p["inferior"] if con_intervalo else None, p["superior"] if con_intervalo else None,
                             titulo=f"{ms['nombre']}: histórico y pronóstico a {h} meses", unidad="toneladas por mes")
    st.plotly_chart(fig)
    g, mt = ms["ganador"], ms["metricas_test"]
    k = st.columns(4)
    k[0].metric("Modelo elegido", CORTOS.get(g, g), help=nombre_modelo(g))
    k[1].metric("RMSE en prueba", f"{fmt(mt['RMSE'])} t/mes")
    k[2].metric("MAE en prueba", f"{fmt(mt['MAE'])} t/mes")
    k[3].metric("MAPE en prueba", f"{mt['MAPE']:.1f} %")
    if origen == "csv":
        st.warning(f"No pude usar el modelo guardado y muestro la tabla de pronóstico del entrenamiento ({aviso}). "
                   "Revisa que la versión de statsmodels sea la de `serie_meta.json` → `librerias`.")
    if not ms.get("intervalo", False):
        st.info(f"El modelo elegido es «{nombre_modelo(g)}», un modelo simple: {DESCRIPCION_SIMPLE.get(g, 'no calcula intervalo')}. "
                "No calcula intervalo, y ningún modelo más complejo lo superó en la validación de esta serie.")
    if ms.get("convergio") is False:
        st.warning("El ajuste final de este modelo no terminó de converger; trata el pronóstico y su intervalo con más cautela.")
    st.caption("Supuestos: no hay otra pandemia (indicador `covid` = 0) y el programa de orgánicos sigue como en el último dato. "
               "El intervalo (95 %) solo existe para ETS y SARIMAX. Una sola ciudad: no generalizar a otras.")
    tabla = p.rename_axis("fecha").reset_index()
    tabla["fecha"] = tabla["fecha"].dt.strftime("%Y-%m")
    mostrar = tabla.rename(columns={"pronostico": "Pronóstico (t/mes)", "inferior": "Límite inferior 95 %", "superior": "Límite superior 95 %"}).round(0)
    with st.expander("Ver tabla del pronóstico y descargarla"):
        st.dataframe(mostrar, hide_index=True)
        st.download_button("Descargar CSV", data=mostrar.to_csv(index=False).encode("utf-8"), file_name=f"pronostico_{sid}_{h}m.csv", mime="text/csv")
    with st.expander("¿Qué tan fiable es este pronóstico?", expanded=True):
        for frase in texto_comparacion(ms["tabla_modelos"], g):
            st.write(frase)
        st.write(f"Orden de magnitud: la serie se mueve entre {fmt(hist.min())} y {fmt(hist.max())} t/mes en el periodo mostrado; el error típico de validación es del "
                 f"{ms['metricas_validacion']['MAPE']:.1f} % (MAPE).")


def _modelos_ui(meta):
    series = meta["series"]
    sid = st.selectbox("Serie", list(series), format_func=lambda i: f"{i} · {series[i]['nombre']}", key="serie_modelos")
    ms = series[sid]
    st.write(f"**Periodo:** {ms['inicio']} a {ms['fin']} ({ms['n_meses']} meses). **Elegido:** {nombre_modelo(ms['ganador'])} "
             f"(mejor RMSE medio de validación; empate ≤ 2 % → el más simple). Métricas en toneladas por mes.")
    st.dataframe(tabla_modelos_df(ms), hide_index=True)
    t = ms["tabla_modelos"]
    if "sarimax_sin_covid" in t and "sarimax" in t:
        st.write(f"**Quiebre COVID:** quitar 2020-03 a 2021-12 del entrenamiento de SARIMAX cambia el RMSE de validación de {fmt(t['sarimax']['RMSE_val'])} a "
                 f"{fmt(t['sarimax_sin_covid']['RMSE_val'])} y el de prueba de {fmt(t['sarimax']['test_RMSE'])} a {fmt(t['sarimax_sin_covid']['test_RMSE'])}. "
                 "Es un análisis: esa variante no compite por la regla fijada de antemano.")
    adf = ms.get("adf_p_valor")
    if adf:
        st.caption(f"Prueba ADF (p-valor): serie {adf['serie']:.3f}; con 1 diferencia {adf['dif_1']:.2g}; con diferencias 1 y 12 {adf['dif_1_y_12']:.2g}. "
                   "Un p-valor alto en la serie original indica que no es estacionaria, y por eso los modelos usan diferencias.")
    figs = config.DOCS_DIR / "figuras"
    for nombre, pie in ((f"m2_eda_{sid}.png", "Tendencia, estacionalidad y autocorrelación"), ("m2_comparacion.png", "Comparación de errores por modelo (todas las series)")):
        if (figs / nombre).exists():
            st.image(str(figs / nombre), caption=pie)
    with st.expander("Datos, supuestos y limitaciones"):
        st.write(f"Datos: {meta.get('dataset', 'DS2 DSNY Monthly Tonnage')}. Unidades: {meta.get('unidades', 'toneladas por mes')}.")
        st.write(meta.get("notas", ""))
        st.write("La serie S4 (orgánicos) no se modela por tener solo 25 meses con cobertura completa. Los modelos y sus intervalos suponen que el futuro se parece al pasado reciente.")


def render():
    st.header("🕒 Series temporales: pronóstico de residuos de Nueva York")
    st.write("Elige una serie y cuántos meses quieres pronosticar. Es una ayuda orientativa basada en datos históricos de una sola ciudad (DSNY), no una predicción garantizada.")
    try:
        meta = leer_meta(ARCHIVO_META)
        if not meta.get("series"):
            raise ValueError("serie_meta.json no tiene el campo `series`.")
    except FileNotFoundError as e:
        st.info(f"Este módulo aún no tiene modelos entrenados. {e}")
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudo leer serie_meta.json: {e}")
        return
    try:
        pestanas = st.tabs(["Pronóstico", "Modelos y datos"])
        with pestanas[0]:
            _pronosticar_ui(meta)
        with pestanas[1]:
            _modelos_ui(meta)
        with st.expander("Aviso de uso responsable y fuentes"):
            st.write(config.AVISO_USO)
            st.write("Datos: DSNY Monthly Tonnage Data (NYC Open Data); consulta sus términos de uso en el portal. Modelos entrenados con statsmodels y TensorFlow.")
    except Exception as e:  # noqa: BLE001
        st.error(f"El módulo de series temporales falló: {e}")
        with st.expander("Detalle técnico del error"):
            st.code(traceback.format_exc())
