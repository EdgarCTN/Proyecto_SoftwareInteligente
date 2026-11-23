"""Pruebas de humo del módulo de imágenes. Ejecutar desde la raíz:  python -m pytest tests/test_imagenes.py
Las pruebas con el modelo se omiten si faltan TensorFlow o los archivos de models/."""
import io
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
from app.modules import imagenes as im  # noqa: E402

RUTA_CLASES = config.MODELS_DIR / im.ARCHIVO_CLASES
hay_archivos = RUTA_CLASES.exists() and (config.MODELS_DIR / im.ARCHIVO_MODELO).exists() and (config.MODELS_DIR / im.ARCHIVO_META).exists()
requiere_modelo = pytest.mark.skipif(not hay_archivos, reason="faltan los archivos del modelo en models/")


@requiere_modelo
def test_config_cubre_todas_las_clases():
    clases = json.loads(RUTA_CLASES.read_text(encoding="utf-8"))
    assert set(config.NOMBRES_CLASES) == set(clases)
    assert set(config.RESIDUOS_PELIGROSOS) <= set(clases)
    assert config.ESQUEMA_PREDETERMINADO in config.CONTENEDORES
    for esquema_id, esquema in config.CONTENEDORES.items():
        assert set(esquema["clases"]) == set(clases), esquema_id
        assert all(e["origen"] in ("norma", "proyecto") for e in esquema["clases"].values())


def test_top_k_y_aviso_peligroso():
    clases = ["battery", "paper", "glass"]
    assert im.top_k(np.array([0.1, 0.7, 0.2]), clases, 2) == [("paper", pytest.approx(0.7)), ("glass", pytest.approx(0.2))]
    assert im.clase_peligrosa(im.top_k(np.array([0.25, 0.6, 0.15]), clases)) == ("battery", False)   # 2.ª con 0.25 >= umbral
    assert im.clase_peligrosa(im.top_k(np.array([0.05, 0.6, 0.35]), clases)) is None
    assert im.clase_peligrosa(im.top_k(np.array([0.9, 0.05, 0.05]), clases)) == ("battery", True)


def test_abrir_imagen_transparencia_y_formato():
    buf = io.BytesIO()
    Image.new("RGBA", (40, 30), (255, 0, 0, 0)).save(buf, "PNG")        # totalmente transparente
    img = im.abrir_imagen(buf.getvalue())
    assert img.mode == "RGB" and img.size == (40, 30) and img.getpixel((0, 0)) == (255, 255, 255)
    with pytest.raises(Exception):
        im.abrir_imagen(b"esto no es una imagen")


def test_caja_escapa_html():
    assert "&lt;" in im._caja("#2e7d32", "<b>x</b>")


@requiere_modelo
def test_modelo_carga_y_predice():
    pytest.importorskip("tensorflow")
    import keras
    from app.utils.modelos import leer_meta, ruta_modelo
    meta = leer_meta(im.ARCHIVO_META)
    clases = im.leer_clases(meta)
    modelo = keras.models.load_model(ruta_modelo(im.ARCHIVO_MODELO))
    probs = im.predecir(modelo, Image.new("RGB", (320, 240), (90, 120, 60)), im.tam_entrada(meta))
    assert probs.shape == (len(clases),) and abs(float(probs.sum()) - 1) < 1e-3
    for conf in (im.confundidas_con(meta, "plastic"),):
        assert all(n > 0 for n, _ in conf)
