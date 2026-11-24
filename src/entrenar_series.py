"""Pronostica series mensuales de residuos de Nueva York (mismo código que notebooks/02_series_tiempo.ipynb, sin Jupyter).
Uso, desde la raíz:  python src/entrenar_series.py"""
import matplotlib
matplotlib.use("Agg")  # sin ventanas: las figuras se guardan en docs/figuras/

import json, sys, warnings, datetime, itertools, time
from pathlib import Path
import numpy as np, pandas as pd, joblib
import matplotlib.pyplot as plt
import statsmodels
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras

RAIZ = next(p for p in [Path.cwd(), Path.cwd().parent] if (p / "config.py").exists())
sys.path.insert(0, str(RAIZ))
import config
warnings.simplefilter("ignore")      # los ajustes de statsmodels emiten muchos avisos de convergencia; se registra el indicador `converged` del modelo final

# Parámetros (todo lo editable está aquí)
SEMILLA = config.RANDOM_STATE
H = 12                 # horizonte de prueba, de validación y de pronóstico (meses)
N_FOLDS = 4            # ventanas móviles de validación (cada una de H meses)
M = 12                 # estacionalidad mensual
SERIES = {"S1": {"col": "refuse", "nombre": "Basura (refuse)", "inicio": "1992-01-01"},
          "S2": {"col": "paper", "nombre": "Papel", "inicio": "2004-04-01"},
          "S3": {"col": "mgp", "nombre": "Metal, vidrio y plástico (MGP)", "inicio": "2004-04-01"}}
ORDENES = [(1, 1, 1), (0, 1, 1), (2, 1, 1)]                  # (p, d, q) de SARIMAX
ESTACIONALES = [(0, 1, 1, 12), (1, 1, 1, 12)]                # (P, D, Q, m)
CONJUNTOS_EXOG = [[], ["covid"], ["covid", "organicos_programa"]]
LOOK_BACK, EPOCAS_LSTM, UNIDADES_LSTM, N_SEMILLAS_LSTM = 12, 150, 32, 3
TOLERANCIA_EMPATE = 0.02
COMPLEJIDAD = ["ingenuo_estacional", "media_movil", "ingenuo", "ets", "sarimax", "lstm"]
NOMBRES = {"ingenuo": "Ingenuo (último valor)", "media_movil": "Media móvil 12 m", "ingenuo_estacional": "Ingenuo estacional",
           "ets": "ETS", "sarimax": "SARIMAX", "sarimax_sin_covid": "SARIMAX sin COVID en el entrenamiento", "lstm": "LSTM"}
RUTA_SERIE = config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["serie_ciudad"]
FIG = config.DOCS_DIR / "figuras"
for d in (FIG, config.MODELS_DIR, config.DATA_PROCESSED):
    d.mkdir(parents=True, exist_ok=True)
keras.utils.set_random_seed(SEMILLA)
print("statsmodels", statsmodels.__version__, "| TensorFlow", tf.__version__)

# 1. Datos: se modela toneladas por día y se reporta en toneladas por mes
def cargar(sid):
    cfg = SERIES[sid]
    d = pd.read_csv(RUTA_SERIE, parse_dates=["fecha"], index_col="fecha").asfreq("MS").loc[cfg["inicio"]:]
    assert d[cfg["col"]].notna().all(), f"{sid}: hay meses sin dato en la ventana"
    assert (d["cobertura_completa"] == 1).all(), f"{sid}: hay meses sin cobertura completa de distritos"
    y = (d[cfg["col"]] / d["dias_mes"]).rename("ton_dia")
    X = d[["covid", "organicos_programa"]].astype(float)
    return d, y, X

def exog_futuro(X, h):
    idx = pd.date_range(X.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
    return pd.DataFrame({"covid": 0.0, "organicos_programa": float(X["organicos_programa"].iloc[-1])}, index=idx)

def a_mes(valores_dia, idx):
    return np.asarray(valores_dia, dtype=float) * np.asarray(idx.days_in_month)

def metricas(real, pred):
    e = np.asarray(real, dtype=float) - np.asarray(pred, dtype=float)
    return {"RMSE": float(np.sqrt(np.mean(e ** 2))), "MAE": float(np.mean(np.abs(e))), "MAPE": float(np.mean(np.abs(e / np.asarray(real))) * 100)}

for sid in SERIES:
    d, y, X = cargar(sid)
    print(f"{sid} {SERIES[sid]['nombre']}: {y.index[0]:%Y-%m} a {y.index[-1]:%Y-%m}, {len(y)} meses")

# 2. Exploración: tendencia, estacionalidad, estacionariedad y autocorrelación (figuras para el informe)
ADF = {}
for sid, cfg in SERIES.items():
    d, y, X = cargar(sid)
    p = lambda s: float(adfuller(s.dropna())[1])
    ADF[sid] = {"serie": p(y), "dif_1": p(y.diff()), "dif_1_y_12": p(y.diff().diff(M))}
    dec = seasonal_decompose(y, model="multiplicative", period=M)
    fig, ax = plt.subplots(2, 2, figsize=(12, 7))
    (d[cfg["col"]]).plot(ax=ax[0, 0], title=f"{sid} {cfg['nombre']}: toneladas por mes")
    ax[0, 0].fill_between(d.index, 0, d[cfg["col"]].max(), where=d["covid"] == 1, alpha=0.15, color="red", label="covid = 1"); ax[0, 0].legend()
    dec.trend.plot(ax=ax[0, 1], title="Tendencia (toneladas por día, descomposición multiplicativa)")
    dec.seasonal.iloc[:M].set_axis(dec.seasonal.iloc[:M].index.month).plot(ax=ax[1, 0], kind="bar", title="Estacionalidad: factor por mes")
    plot_acf(y.diff().diff(M).dropna(), lags=36, ax=ax[1, 1], title="ACF de la serie con diferencias (1 y 12)")
    plt.tight_layout(); plt.savefig(FIG / f"m2_eda_{sid}.png", dpi=130); plt.show()
    print(f"{sid} ADF (p-valor): serie {ADF[sid]['serie']:.4f} | dif 1: {ADF[sid]['dif_1']:.4g} | dif 1 y 12: {ADF[sid]['dif_1_y_12']:.4g}")

# 3. Modelos. Todos reciben la serie en toneladas por día y devuelven (pronóstico, inferior, superior); inferior/superior = None si no hay intervalo
def pron_ingenuo(y, h): return np.repeat(y.iloc[-1], h)
def pron_media_movil(y, h): return np.repeat(y.iloc[-M:].mean(), h)
def pron_ingenuo_est(y, h): return np.resize(y.iloc[-M:].values, h)

def ajustar_sarimax(y, X, cfg, maxiter=200):
    esc = float(y.mean())                                   # se escala para ayudar a la convergencia
    cols = cfg["exog"]
    mod = SARIMAX(y / esc, exog=X.loc[y.index, cols] if cols else None, order=cfg["orden"], seasonal_order=cfg["estacional"],
                  enforce_stationarity=False, enforce_invertibility=False)
    return mod.fit(disp=False, maxiter=maxiter), esc

def pron_desde_sarimax(res, esc, Xf, h, cfg):
    fc = res.get_forecast(h, exog=Xf[cfg["exog"]] if cfg["exog"] else None)
    ic = fc.conf_int(alpha=0.05)
    return fc.predicted_mean.values * esc, ic.iloc[:, 0].values * esc, ic.iloc[:, 1].values * esc

def pron_sarimax(y, X, Xf, h, cfg):
    res, esc = ajustar_sarimax(y, X, cfg)
    return pron_desde_sarimax(res, esc, Xf, h, cfg)

def elegir_sarimax(y, X):
    mejor = None
    for orden, est, cols in itertools.product(ORDENES, ESTACIONALES, CONJUNTOS_EXOG):
        cfg = {"orden": orden, "estacional": est, "exog": cols}
        try:
            aic = float(ajustar_sarimax(y, X, cfg)[0].aic)
        except Exception:
            continue
        if np.isfinite(aic) and (mejor is None or aic < mejor[0]):
            mejor = (aic, cfg)
    return mejor[1], mejor[0]

CONFIG_ETS = [{"error": e, "trend": t, "damped": t is not None, "seasonal": s} for e in ("add", "mul") for t in (None, "add") for s in ("add", "mul")]

def ajustar_ets(y, cfg):
    esc = float(y.mean())
    mod = ETSModel(y / esc, error=cfg["error"], trend=cfg["trend"], damped_trend=cfg["damped"], seasonal=cfg["seasonal"], seasonal_periods=M)
    return mod.fit(disp=False, maxiter=1000), esc

def pron_desde_ets(res, esc, n, h):
    # los intervalos de ETS con componentes multiplicativos se simulan: se fija la semilla para que sean reproducibles
    sf = res.get_prediction(start=n, end=n + h - 1, rng=np.random.default_rng(SEMILLA)).summary_frame(alpha=0.05)
    return sf["mean"].values * esc, sf["pi_lower"].values * esc, sf["pi_upper"].values * esc

def pron_ets(y, h, cfg):
    res, esc = ajustar_ets(y, cfg)
    return pron_desde_ets(res, esc, len(y), h)

def elegir_ets(y):
    mejor = None
    for cfg in CONFIG_ETS:
        try:
            aicc = float(ajustar_ets(y, cfg)[0].aicc)
        except Exception:
            continue
        if np.isfinite(aicc) and (mejor is None or aicc < mejor[0]):
            mejor = (aicc, cfg)
    return mejor[1], mejor[0]

def entrenar_lstm(y, semilla):
    keras.utils.set_random_seed(semilla)
    sc = MinMaxScaler().fit(y.values.reshape(-1, 1))        # el escalador se ajusta solo con el entrenamiento
    a = sc.transform(y.values.reshape(-1, 1))[:, 0]
    Xw = np.array([a[i - LOOK_BACK:i] for i in range(LOOK_BACK, len(a))])[..., None]
    tw = np.array([a[i] for i in range(LOOK_BACK, len(a))])
    m = keras.Sequential([keras.layers.Input((LOOK_BACK, 1)), keras.layers.LSTM(UNIDADES_LSTM), keras.layers.Dense(1)])
    m.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse")
    m.fit(Xw, tw, epochs=EPOCAS_LSTM, batch_size=16, validation_split=0.1, verbose=0,
          callbacks=[keras.callbacks.EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True)])
    return m, sc, a[-LOOK_BACK:]

def pron_lstm_modelo(m, sc, ultimos, h):
    ventana, salida = list(ultimos), []
    for _ in range(h):                                        # pronóstico recursivo: cada predicción entra a la ventana
        p = float(m(np.array(ventana[-LOOK_BACK:], dtype="float32").reshape(1, LOOK_BACK, 1), training=False)[0, 0])
        salida.append(p); ventana.append(p)
    return sc.inverse_transform(np.array(salida).reshape(-1, 1))[:, 0]

def pron_lstm(y, h):
    preds = []
    for k in range(N_SEMILLAS_LSTM):
        m, sc, ult = entrenar_lstm(y, SEMILLA + k)
        preds.append(pron_lstm_modelo(m, sc, ult, h))
    return np.mean(preds, axis=0)

def predecir(modelo, y, X, Xf, h, cfgs):
    if modelo == "ingenuo": return pron_ingenuo(y, h), None, None
    if modelo == "media_movil": return pron_media_movil(y, h), None, None
    if modelo == "ingenuo_estacional": return pron_ingenuo_est(y, h), None, None
    if modelo == "ets": return pron_ets(y, h, cfgs["ets"])
    if modelo == "sarimax": return pron_sarimax(y, X, Xf, h, cfgs["sarimax"])
    if modelo == "sarimax_sin_covid":                         # el periodo COVID se pone como dato faltante (SARIMAX lo admite)
        cfg = {**cfgs["sarimax"], "exog": [c for c in cfgs["sarimax"]["exog"] if c != "covid"]}
        return pron_sarimax(y.where(X.loc[y.index, "covid"] == 0), X, Xf, h, cfg)
    if modelo == "lstm": return pron_lstm(y, h), None, None
    raise ValueError(modelo)
MODELOS = ["ingenuo", "media_movil", "ingenuo_estacional", "ets", "sarimax", "sarimax_sin_covid", "lstm"]

# 4. Validación en ventana móvil + prueba final, por serie
def evaluar_serie(sid):
    t0 = time.time()
    d, y, X = cargar(sid)
    n = len(y); T0 = n - H
    origenes = [T0 - H * k for k in range(N_FOLDS, 0, -1)]
    cfg_sar, aic = elegir_sarimax(y.iloc[:origenes[0]], X.iloc[:origenes[0]])
    cfg_ets, aicc = elegir_ets(y.iloc[:origenes[0]])
    cfgs = {"sarimax": cfg_sar, "ets": cfg_ets}
    filas, preds_test = [], {}
    for etiqueta, o in [(f"val{k + 1}", o) for k, o in enumerate(origenes)] + [("test", T0)]:
        real = y.iloc[o:o + H]
        for modelo in MODELOS:
            p, lo, hi = predecir(modelo, y.iloc[:o], X.iloc[:o], X.iloc[o:o + H], H, cfgs)   # en validación/prueba los indicadores se conocen
            fila = {"serie": sid, "modelo": modelo, "particion": etiqueta, "inicio": real.index[0].strftime("%Y-%m"), **metricas(a_mes(real.values, real.index), a_mes(p, real.index))}
            filas.append(fila)
            if etiqueta == "test":
                preds_test[modelo] = (a_mes(p, real.index), None if lo is None else a_mes(lo, real.index), None if hi is None else a_mes(hi, real.index))
        print(f"  {sid} {etiqueta} listo ({time.time() - t0:.0f} s)")
    res = pd.DataFrame(filas)
    cv = res[res.particion != "test"].groupby("modelo").agg(RMSE_val=("RMSE", "mean"), RMSE_val_sd=("RMSE", "std"), MAE_val=("MAE", "mean"), MAPE_val=("MAPE", "mean"))
    te = res[res.particion == "test"].set_index("modelo")[["RMSE", "MAE", "MAPE"]].add_prefix("test_")
    tabla = cv.join(te).loc[MODELOS]
    cand = tabla.drop(index="sarimax_sin_covid")
    mejor = cand.RMSE_val.min()
    empatados = [m for m in cand.index if cand.loc[m, "RMSE_val"] <= mejor * (1 + TOLERANCIA_EMPATE)]
    ganador = min(empatados, key=COMPLEJIDAD.index)
    return {"y": y, "X": X, "d": d, "origenes": origenes, "T0": T0, "cfgs": cfgs, "aic": aic, "aicc": aicc, "res": res, "tabla": tabla,
            "ganador": ganador, "empatados": empatados, "preds_test": preds_test, "segundos": time.time() - t0}

R = {}
for sid in SERIES:
    print(f"== {sid} {SERIES[sid]['nombre']}")
    R[sid] = evaluar_serie(sid)
    print(R[sid]["tabla"].round(3).to_string()); print("Ganador:", NOMBRES[R[sid]["ganador"]], "| empatados:", R[sid]["empatados"])

# 5. Comparación y análisis del quiebre COVID
print("Configuraciones elegidas por AIC/AICc con datos anteriores a la primera validación:")
for sid, r in R.items():
    print(f"  {sid}: SARIMAX {r['cfgs']['sarimax']} (AIC {r['aic']:.1f}) | ETS {r['cfgs']['ets']} (AICc {r['aicc']:.1f})")
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for a, (sid, r) in zip(ax, R.items()):
    t = r["tabla"]; x = np.arange(len(t))
    a.bar(x - 0.2, t.RMSE_val, 0.4, yerr=t.RMSE_val_sd.fillna(0), label="validación (media de 4 ventanas)")
    a.bar(x + 0.2, t.test_RMSE, 0.4, label="prueba (últimos 12 meses)")
    a.set_xticks(x); a.set_xticklabels([NOMBRES[m] for m in t.index], rotation=70, ha="right", fontsize=7)
    a.set_title(f"{sid} {SERIES[sid]['nombre']}: RMSE (ton/mes)"); a.legend(fontsize=7)
plt.tight_layout(); plt.savefig(FIG / "m2_comparacion.png", dpi=130); plt.show()
print("\nEfecto de quitar COVID del entrenamiento (SARIMAX; RMSE en ton/mes):")
for sid, r in R.items():
    t = r["tabla"]
    print(f"  {sid}: validación {t.loc['sarimax', 'RMSE_val']:.0f} (con COVID) vs {t.loc['sarimax_sin_covid', 'RMSE_val']:.0f} (sin) | prueba {t.loc['sarimax', 'test_RMSE']:.0f} vs {t.loc['sarimax_sin_covid', 'test_RMSE']:.0f}")
pd.concat([r["res"] for r in R.values()]).to_csv(config.DATA_PROCESSED / "m2_resultados.csv", index=False)

# 6. Ajuste final del ganador con TODOS los datos y pronóstico de H meses (guarda modelo, tabla de pronóstico y figura)
def ajuste_final(sid, r):
    y, X, g = r["y"], r["X"], r["ganador"]
    Xf = exog_futuro(X, H); idx = Xf.index
    art = {"id": sid, "tipo": g, "ultima_fecha": y.index[-1].strftime("%Y-%m"), "horizonte_max": H, "exog_futuro": {k: float(v) for k, v in Xf.iloc[0].items()},
           "config": r["cfgs"].get(g), "unidad_modelo": "toneladas por día (multiplicar por los días del mes)"}
    lo = hi = None; convergio = None
    if g in ("ingenuo", "media_movil", "ingenuo_estacional"):
        p = {"ingenuo": pron_ingenuo, "media_movil": pron_media_movil, "ingenuo_estacional": pron_ingenuo_est}[g](y, H)
        art["ultimos_12_ton_dia"] = [float(v) for v in y.iloc[-M:]]
    elif g == "sarimax":
        res, esc = ajustar_sarimax(y, X, r["cfgs"]["sarimax"], maxiter=1000)   # el ajuste final admite más iteraciones; la selección no cambia
        convergio = bool(res.mle_retvals.get("converged", True))
        p, lo, hi = pron_desde_sarimax(res, esc, Xf, H, r["cfgs"]["sarimax"]); art.update(modelo=res, escala=esc)
    elif g == "ets":
        res, esc = ajustar_ets(y, r["cfgs"]["ets"]); p, lo, hi = pron_desde_ets(res, esc, len(y), H); art.update(modelo=res, escala=esc)
    else:                                                      # lstm: se guardan los modelos de cada semilla y lo necesario para pronosticar
        preds, rutas = [], []
        for k in range(N_SEMILLAS_LSTM):
            m, sc, ult = entrenar_lstm(y, SEMILLA + k); preds.append(pron_lstm_modelo(m, sc, ult, H))
            ruta = config.MODELS_DIR / f"serie_{sid}_lstm_{k}.keras"; m.save(ruta); rutas.append(ruta.name)
        p = np.mean(preds, axis=0)
        art.update(keras=rutas, escalador_min=float(sc.data_min_[0]), escalador_max=float(sc.data_max_[0]), look_back=LOOK_BACK, ultimos_escalados=[float(v) for v in ult])
    tabla = pd.DataFrame({"fecha": idx.strftime("%Y-%m-%d"), "pronostico_ton_mes": a_mes(p, idx),
                          "inferior_ton_mes": np.nan if lo is None else a_mes(lo, idx), "superior_ton_mes": np.nan if hi is None else a_mes(hi, idx)})
    tabla.to_csv(config.DATA_PROCESSED / f"m2_pronostico_{sid}.csv", index=False)
    joblib.dump(art, config.MODELS_DIR / f"serie_{sid}.joblib")
    # figura: prueba (todos los modelos) y pronóstico futuro del ganador
    fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
    real = r["d"][SERIES[sid]["col"]].iloc[-H:]
    ax[0].plot(real.index, real.values, "k-o", label="real")
    for m_, (pp, _, _) in r["preds_test"].items():
        if m_ != "sarimax_sin_covid": ax[0].plot(real.index, pp, "--", label=NOMBRES[m_])
    ax[0].set_title(f"{sid}: prueba (últimos {H} meses), ton/mes"); ax[0].legend(fontsize=7)
    hist = r["d"][SERIES[sid]["col"]].iloc[-60:]
    ax[1].plot(hist.index, hist.values, "k-", label="histórico"); ax[1].plot(idx, tabla.pronostico_ton_mes, "C0-o", label=f"pronóstico ({NOMBRES[g]})")
    if lo is not None: ax[1].fill_between(idx, tabla.inferior_ton_mes, tabla.superior_ton_mes, alpha=0.25, label="intervalo 95 %")
    ax[1].set_title(f"{sid} {SERIES[sid]['nombre']}: pronóstico de {H} meses (ton/mes)"); ax[1].legend(fontsize=7)
    plt.tight_layout(); plt.savefig(FIG / f"m2_pronostico_{sid}.png", dpi=130); plt.show()
    art["convergio"] = convergio
    return tabla, art, convergio

FINAL = {sid: ajuste_final(sid, r) for sid, r in R.items()}
for sid, (tabla, art, conv) in FINAL.items():
    print(f"\n{sid} pronóstico con {NOMBRES[art['tipo']]} (convergió: {conv}):"); print(tabla.round(0).to_string(index=False))

# 7. Metadatos (serie_meta.json) y resumen de texto para pegar en el chat
def mejora_vs_estacional(t, m): return float((1 - t.loc[m, "test_RMSE"] / t.loc["ingenuo_estacional", "test_RMSE"]) * 100)

series_meta = {}
for sid, r in R.items():
    t, g = r["tabla"], r["ganador"]
    series_meta[sid] = {"nombre": SERIES[sid]["nombre"], "columna": SERIES[sid]["col"], "inicio": r["y"].index[0].strftime("%Y-%m"), "fin": r["y"].index[-1].strftime("%Y-%m"),
                        "n_meses": int(len(r["y"])), "ganador": g, "archivo_modelo": f"serie_{sid}.joblib", "archivo_pronostico": f"m2_pronostico_{sid}.csv",
                        "metricas_test": {k.replace("test_", ""): float(t.loc[g, k]) for k in ("test_RMSE", "test_MAE", "test_MAPE")},
                        "metricas_validacion": {"RMSE": float(t.loc[g, "RMSE_val"]), "MAE": float(t.loc[g, "MAE_val"]), "MAPE": float(t.loc[g, "MAPE_val"])},
                        "mejora_rmse_test_vs_ingenuo_estacional_pct": mejora_vs_estacional(t, g),
                        "tabla_modelos": {m: {k: float(v) for k, v in t.loc[m].items()} for m in t.index},
                        "empatados_con_el_mejor": r["empatados"], "config_sarimax": r["cfgs"]["sarimax"], "config_ets": r["cfgs"]["ets"],
                        "adf_p_valor": ADF[sid], "intervalo": g in ("ets", "sarimax"), "convergio": FINAL[sid][2]}
s1 = series_meta["S1"]
meta = {"modulo": "series_temporales", "modelo": "un modelo por serie (ver series)", "fecha": datetime.date.today().isoformat(),
        "dataset": "DS2 DSNY Monthly Tonnage (NYC Open Data), serie de ciudad: data/processed/serie_ciudad_mensual.csv",
        "n_entrenamiento": {sid: len(r["y"]) - H for sid, r in R.items()}, "n_prueba": H,
        "parametros": {"horizonte": H, "ventanas_validacion": N_FOLDS, "regla_ganador": f"menor RMSE medio de validación; empate <= {TOLERANCIA_EMPATE:.0%} -> más simple",
                       "orden_complejidad": COMPLEJIDAD, "lstm": {"look_back": LOOK_BACK, "unidades": UNIDADES_LSTM, "epocas_max": EPOCAS_LSTM, "semillas": N_SEMILLAS_LSTM},
                       "semilla": SEMILLA, "exog_futuro": "covid = 0; organicos_programa = último valor conocido"},
        "metricas": {"serie": "S1", **s1["metricas_test"]},
        "features": {"exogenas": ["covid", "organicos_programa"], "frecuencia": "MS"},
        "librerias": {"statsmodels": statsmodels.__version__, "tensorflow": tf.__version__, "numpy": np.__version__, "pandas": pd.__version__},
        "frecuencia": "MS", "horizonte_max": H, "unidades": "toneladas por mes (se modela por día y se multiplica por los días del mes)",
        "series": series_meta,
        "notas": "Una sola ciudad; solo residuos recogidos por DSNY en residencias e instituciones. Unidad ton/mes por contrastar con un PDF de DSNY. "
                 "El pronóstico supone covid = 0 y no cubre pandemias ni cambios de política. S4 (orgánicos) no se modela. Intervalos del 95 % solo para ETS y SARIMAX."}
(config.MODELS_DIR / "serie_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

L = [f"M2 SERIES — resumen (ejecución real, {meta['fecha']})", f"statsmodels {statsmodels.__version__}, TensorFlow {tf.__version__}"]
for sid, r in R.items():
    t = r["tabla"]
    L += [f"\n== {sid} {SERIES[sid]['nombre']}: {series_meta[sid]['inicio']} a {series_meta[sid]['fin']} ({series_meta[sid]['n_meses']} meses); tiempo {r['segundos']:.0f} s",
          f"ADF p-valor: {ADF[sid]}", f"SARIMAX elegido: {r['cfgs']['sarimax']} (AIC {r['aic']:.1f}) | ETS elegido: {r['cfgs']['ets']} (AICc {r['aicc']:.1f})",
          "Métricas en toneladas por mes (val = media de 4 ventanas de 12 meses; test = últimos 12 meses):", t.round(2).to_string(),
          f"GANADOR: {NOMBRES[r['ganador']]} (dentro del 2 % del mejor: {r['empatados']}); mejora del RMSE de prueba frente al ingenuo estacional: {series_meta[sid]['mejora_rmse_test_vs_ingenuo_estacional_pct']:.1f} %",
          f"Convergencia del modelo final: {FINAL[sid][2]}", "Pronóstico:", FINAL[sid][0].round(0).to_string(index=False)]
(config.DATA_PROCESSED / "m2_resumen.txt").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
