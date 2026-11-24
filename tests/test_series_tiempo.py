"""Pruebas de humo del módulo de series temporales. Ejecutar desde la raíz:  python -m pytest tests/test_series_tiempo.py
Las pruebas con artefactos reales se omiten si faltan models/serie_meta.json o statsmodels."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
from app.modules import series_tiempo as st_  # noqa: E402

RUTA_META = config.MODELS_DIR / st_.ARCHIVO_META


def _art(tipo, **extra):
    return {"id": "SX", "tipo": tipo, "ultima_fecha": "2026-10", "horizonte_max": 12, "ultimos_12_ton_dia": [float(v) for v in range(1, 13)], **extra}


def test_baselines_y_fechas():
    ing, med, est = (st_.pronosticar(_art(t)) for t in ("ingenuo", "media_movil", "ingenuo_estacional"))
    assert list(ing.index[:2].strftime("%Y-%m")) == ["2026-11", "2026-12"] and len(ing) == 12
    dias = np.asarray(ing.index.days_in_month)
    assert np.allclose(ing["pronostico"], 12.0 * dias) and np.allclose(med["pronostico"], 6.5 * dias)
    assert np.allclose(est["pronostico"], np.arange(1, 13) * dias) and ing["inferior"].isna().all()
    assert len(st_.pronosticar(_art("ingenuo"), 6)) == 6


def test_textos_cubren_los_modelos_simples():
    assert set(st_.DESCRIPCION_SIMPLE) == set(st_.SIMPLES) and set(st_.SIMPLES) <= set(st_.CORTOS) and set(st_.NOMBRES) >= set(st_.CORTOS)
    assert all(len(v) <= 16 for v in st_.CORTOS.values())


def test_tipo_desconocido():
    with pytest.raises(ValueError):
        st_.pronosticar(_art("magia"))


def test_texto_comparacion_avisa_si_la_prueba_no_mejora():
    base = {"RMSE_val": 100.0, "MAE_val": 80.0, "MAPE_val": 4.0, "test_RMSE": 100.0, "test_MAE": 80.0, "test_MAPE": 4.0}
    mejor = {**base, "RMSE_val": 80.0, "MAE_val": 60.0, "MAPE_val": 3.0, "test_RMSE": 90.0, "test_MAE": 85.0, "test_MAPE": 4.5}
    frases = st_.texto_comparacion({"ingenuo_estacional": base, "ets": mejor}, "ets")
    assert len(frases) == 3 and "MAE" in frases[2] and "MAPE" in frases[2] and "RMSE" not in frases[2].split(":")[1]
    assert len(st_.texto_comparacion({"ingenuo_estacional": base}, "ingenuo_estacional")) == 1


def test_fmt():
    assert st_.fmt(247923.56) == "247 924" and st_.fmt(1234.5, 1) == "1 234.5"


@pytest.mark.skipif(not RUTA_META.exists(), reason="faltan los artefactos de series en models/")
def test_artefactos_reales_coinciden_con_su_csv():
    pytest.importorskip("statsmodels")
    meta = json.loads(RUTA_META.read_text(encoding="utf-8"))
    import joblib
    for sid, ms in meta["series"].items():
        art = joblib.load(config.MODELS_DIR / ms["archivo_modelo"])
        vivo = st_.pronosticar(art)
        csv = st_.leer_pronostico_csv(ms)
        assert len(vivo) == len(csv) == meta["horizonte_max"], sid
        for col in ("pronostico", "inferior", "superior"):
            a, b = vivo[col].values, csv[col].values
            assert np.array_equal(np.isnan(a), np.isnan(b)), (sid, col)
            assert np.nanmax(np.abs(a - b), initial=0) < 1.0, (sid, col)   # tolerancia de 1 tonelada por mes
        assert ms["ganador"] == art["tipo"]
        assert set(tabla for tabla in ms["tabla_modelos"]) >= {"ingenuo_estacional", ms["ganador"]}
