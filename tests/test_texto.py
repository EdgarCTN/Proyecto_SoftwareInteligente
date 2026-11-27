"""Pruebas de las utilidades de texto (datos de juguete escritos a mano; no son resultados).
Ejecutar desde la raíz:  python -m pytest tests/test_texto.py"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from app.utils import texto as t  # noqa: E402

TEXTO = ("El Dr. Pérez habló ayer en Lima. La ciudad recoge mucha basura cada día. "
         "El reciclaje de plástico y papel avanza poco. EE. UU. anunció un plan nuevo. ¿Funcionará el plan? Nadie lo sabe.")


def test_oraciones_abreviaturas():
    o = t.dividir_oraciones(TEXTO)
    assert o[0] == "El Dr. Pérez habló ayer en Lima."
    assert o[3].startswith("EE. UU. anunció")
    assert len(o) == 6


def test_lead_y_textrank():
    assert t.lead_n(TEXTO, 2) == "El Dr. Pérez habló ayer en Lima. La ciudad recoge mucha basura cada día."
    r = t.textrank(TEXTO, 2)
    assert len(t.dividir_oraciones(r)) == 2
    assert t.textrank("Una sola oración.", 3) == "Una sola oración."
    assert t.textrank("", 2) == ""


def test_textrank_conserva_orden():
    texto = " ".join(f"La planta {i} procesa residuos orgánicos y papel de la ciudad." for i in range(8))
    r = t.dividir_oraciones(t.textrank(texto, 3))
    idx = [int(o.split()[2]) for o in r]
    assert idx == sorted(idx)


def test_rouge_valores_a_mano():
    r = t.rouge_f1("el gato come pescado", "el gato duerme")
    assert r["rouge1"] == pytest.approx(4 / 7)
    assert r["rouge2"] == pytest.approx(0.4)
    assert r["rougeL"] == pytest.approx(4 / 7)
    assert t.rouge_f1("a b c", "a b c")["rougeL"] == 1.0
    assert t.rouge_f1("", "a")["rouge1"] == 0.0


def test_tokenizador_conserva_tildes_y_enie():
    assert t.tokenizar("Canción PEQUEÑA, 2026!") == ["canción", "pequeña", "2026"]
    assert t.rouge_f1("pequeña", "pequeño")["rouge1"] == 0.0


def test_bloques_y_jerarquico():
    texto = " ".join(f"Esta es la oración número {i} con varias palabras de relleno." for i in range(60))
    bloques = t.dividir_en_bloques(texto, palabras=100)
    assert len(bloques) > 1 and all(t.contar_palabras(b) <= 100 for b in bloques)
    final, niveles = t.resumen_jerarquico(texto, lambda x: t.lead_n(x, 1), palabras=100)
    assert isinstance(final, str) and final and len(niveles) >= 1


def test_ratio_y_palabras_residuos():
    assert t.ratio_compresion("a b", "a b c d") == 0.5
    assert t.contar_palabras_residuos("La BASURA y el reciclaje; no hay relleno sanitario") == 3


def test_datos_no_respaldados():
    marcadas = t.datos_no_respaldados("Save the Children dijo 12 metros en Nicaragua.", "War Child dijo que 5 metros en Nicaragua.")
    assert marcadas == ["Save", "Children", "12"]
    assert t.datos_no_respaldados("La Ciudad de Lima.", "la ciudad de lima crece") == []
