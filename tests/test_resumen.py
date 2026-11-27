"""Pruebas del módulo de resumen (datos de juguete escritos a mano; no son resultados).
Ejecutar desde la raíz:  python -m pytest tests/test_resumen.py"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.modules import resumen as rs  # noqa: E402
from app.utils import texto as tx  # noqa: E402


def test_leer_texto_subido():
    assert rs.leer_texto_subido("canción".encode("utf-8")) == "canción"
    assert rs.leer_texto_subido("canción".encode("utf-8-sig")) == "canción"
    assert rs.leer_texto_subido("canción".encode("cp1252")) == "canción"


def test_texto_valido():
    assert rs.texto_valido("   ")[0] is False
    assert rs.texto_valido("poco texto")[0] is False
    assert rs.texto_valido(rs.TEXTO_EJEMPLO) == (True, "")
    assert rs.texto_valido("palabra " * (rs.MAX_CARACTERES // 8 + 10))[0] is False


def test_extractivo_corto_y_ejemplo():
    resumen, reducido = rs.resumen_extractivo(rs.TEXTO_EJEMPLO, 3)
    assert reducido is False
    assert len(tx.dividir_oraciones(resumen)) == 3
    assert all(o in tx.dividir_oraciones(rs.TEXTO_EJEMPLO) for o in tx.dividir_oraciones(resumen))


def test_extractivo_largo_se_reduce_por_bloques():
    largo = " ".join(f"En la zona {i} el servicio de limpieza recoge residuos con la ruta {i % 7} cada semana." for i in range(700))
    resumen, reducido = rs.resumen_extractivo(largo, 2)
    assert reducido is True
    assert len(tx.dividir_oraciones(resumen)) == 2


def test_bloques_abstractivo_recorta():
    largo = " ".join(f"Esta es la oración {i} con varias palabras de relleno para llenar el bloque." for i in range(1500))
    bloques, recortado = rs.bloques_para_abstractivo(largo)
    assert recortado is True and len(bloques) == rs.MAX_BLOQUES_ABSTRACTIVO
    assert rs.bloques_para_abstractivo(rs.TEXTO_EJEMPLO)[1] is False


class _Lote(dict):
    def to(self, dispositivo):
        return self


class _TokFalso:
    def __call__(self, textos, **k):
        t = textos if isinstance(textos, list) else [textos]
        return _Lote(input_ids=[x.split() for x in t], textos=t)

    def batch_decode(self, ids, **k):
        return ids


class _ModeloFalso:
    def generate(self, textos, **k):
        return [" ".join(t.split()[:8]) + "." for t in textos]


def test_flujo_abstractivo_con_modelo_falso():
    resumen, info = rs.resumen_abstractivo(_TokFalso(), _ModeloFalso(), "cpu", rs.TEXTO_EJEMPLO)
    assert resumen.endswith(".") and info["bloques"] >= 1 and info["recortado"] is False
    assert info["bloques_truncados"] == 0


META_JUGUETE = {  # meta inventado solo para probar el formato (no son resultados)
    "metodos_principales": ["Lead-2", "TextRank-2", "Abstractivo"],
    "evaluacion": [{"fuente": "a", "metodo": "Lead-2", "n": 5, "rouge1": .2, "rouge2": .1, "rougeL": .15, "rougeL_desv": .05, "palabras_hip": 40, "ratio": .08, "seg_por_doc": .001},
                   {"fuente": "a", "metodo": "Lead-1", "n": 5, "rouge1": .2, "rouge2": .1, "rougeL": .16, "rougeL_desv": .05, "palabras_hip": 20, "ratio": .04, "seg_por_doc": .001}],
    "bootstrap_vs_lead": {"a|Abstractivo": {"dif_media": 0.05, "ic95": [0.01, 0.09], "excluye_cero": True, "n": 5},
                          "b|Abstractivo": {"dif_media": 0.005, "ic95": [-0.01, 0.02], "excluye_cero": False, "n": 5}},
}


def test_tabla_y_frases_desde_meta():
    t = rs.tabla_evaluacion(META_JUGUETE)
    assert list(t["metodo"]) == ["Lead-2", "Lead-1"] and list(t["principal"]) == [True, False]
    f = rs.frases_bootstrap(META_JUGUETE)
    assert "se distingue de cero" in f[0] and "NO se distingue" in f[1]
    assert rs.tabla_evaluacion({}).empty and rs.frases_bootstrap({}) == []


def test_librerias_faltantes_es_lista():
    assert isinstance(rs.librerias_faltantes(), list) and callable(rs.render)


def test_figura_con_barras_agrupadas():
    pytest.importorskip("plotly")
    fig = rs.figura_comparacion(rs.tabla_evaluacion(META_JUGUETE))
    assert fig.layout.barmode == "group"


def test_estimacion_cpu():
    assert rs.estimar_segundos_cpu(1) == rs.SEG_POR_LLAMADA_CPU
    assert rs.estimar_segundos_cpu(5) == 6 * rs.SEG_POR_LLAMADA_CPU
