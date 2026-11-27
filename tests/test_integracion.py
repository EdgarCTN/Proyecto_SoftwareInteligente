"""Pruebas de integración de la app completa (Fase 8 B). Ejecutar desde la raíz:  python -m pytest tests/test_integracion.py
Usan los artefactos reales de models/ y data/processed/; las pruebas de entradas inválidas usan datos de juguete escritos a mano (no son resultados)."""
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
from app.modules import clustering, imagenes, prediccion, resumen, series_tiempo  # noqa: E402
from app.utils import modelos  # noqa: E402
from app.utils.diagnostico import revisar_modulo, revisar_todos  # noqa: E402

MAIN = str(RAIZ / "app" / "main.py")


def abrir_app():
    return AppTest.from_file(MAIN, default_timeout=180).run()


# ---------- Artefactos ----------
def test_artefactos_de_todos_los_modulos_presentes():
    faltan = {r["id"]: r["faltan"] for r in revisar_todos() if not r["listo"]}
    assert not faltan, f"Faltan archivos: {faltan}"


def test_diagnostico_detecta_archivo_faltante(tmp_path):
    m = {"id": "x", "titulo": "X"}
    r = revisar_modulo(m, models_dir=tmp_path, data_dir=tmp_path, artefactos={"x": {"models": ["a.pkl"], "data": ["b.csv"]}})
    assert not r["listo"] and r["faltan"] == ["models/a.pkl", "data/processed/b.csv"]
    (tmp_path / "a.pkl").write_bytes(b"0")
    (tmp_path / "b.csv").write_text("x\n1\n")
    assert revisar_modulo(m, models_dir=tmp_path, data_dir=tmp_path, artefactos={"x": {"models": ["a.pkl"], "data": ["b.csv"]}})["listo"]


def test_todos_los_modulos_exponen_render():
    for mod in (prediccion, series_tiempo, imagenes, clustering, resumen):
        assert callable(getattr(mod, "render", None)), mod.__name__
    assert {m["modulo"] for m in config.MODULOS} == {"prediccion", "series_tiempo", "imagenes", "clustering", "resumen"}


# ---------- La app completa ----------
def test_app_abre_sin_excepciones_ni_errores():
    at = abrir_app()
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]
    etiquetas = [t.label for t in at.tabs]
    for esperado in ["🏠 Inicio"] + [m["titulo"] for m in config.MODULOS]:
        assert esperado in etiquetas


def test_un_modulo_roto_no_tumba_la_app(monkeypatch):
    def falla():
        raise ValueError("fallo simulado")
    monkeypatch.setattr(clustering, "render", falla)
    at = abrir_app()
    assert not at.exception
    assert any("El módulo falló: fallo simulado" in e.value for e in at.error)
    assert len(at.error) == 1  # solo ese módulo; los demás siguen funcionando
    assert "📈 Predicción" in [t.label for t in at.tabs]


def test_modulo_ausente_muestra_en_construccion(monkeypatch):
    nuevo = {"id": "futuro", "titulo": "🔮 Futuro", "modulo": "modulo_que_no_existe", "meta": "futuro_meta.json"}
    monkeypatch.setattr(config, "MODULOS", config.MODULOS + [nuevo])
    at = abrir_app()
    assert not at.exception
    assert any("en construcción" in i.value for i in at.info)


def test_inicio_avisa_si_falta_un_archivo(monkeypatch):
    monkeypatch.setattr(config, "ARTEFACTOS_MODULO", {**config.ARTEFACTOS_MODULO, "resumen": {"models": ["no_existe.json"], "data": []}})
    at = abrir_app()
    assert not at.exception
    assert any("models/no_existe.json" in w.value for w in at.warning)


# ---------- Entradas inválidas (datos de juguete) ----------
@pytest.mark.parametrize("texto", ["", "   \n ", "una dos tres cuatro cinco"])
def test_resumen_rechaza_textos_vacios_o_cortos(texto):
    ok, motivo = resumen.texto_valido(texto)
    assert not ok and motivo


def test_resumen_rechaza_texto_demasiado_largo():
    ok, motivo = resumen.texto_valido("palabra " * (resumen.MAX_CARACTERES // 8 + 10))
    assert not ok and "demasiado largo" in motivo


def test_resumen_acepta_texto_normal():
    ok, _ = resumen.texto_valido("palabra " * (resumen.MIN_PALABRAS + 5))
    assert ok


def test_imagen_que_no_es_imagen_lanza_error_controlable():
    with pytest.raises(Exception):  # la interfaz lo captura (imagenes._clasificar) y muestra un mensaje
        imagenes.abrir_imagen(b"esto no es una imagen")


def test_clustering_perfil_con_composicion_imposible():
    suma, avisos = clustering.validar_perfil({"a": 70.0, "b": 50.0}, ["a", "b"])
    assert suma == 120.0 and avisos and avisos[0][0] == "error"


def test_prediccion_avisa_si_extrapola():
    meta = {"rangos_variables": {"gdp": {"min": 1.0, "max": 10.0, "p05": 2.0, "p95": 9.0, "mediana": 5.0},
                                 "poblacion": {"min": 1.0, "max": 10.0, "p05": 2.0, "p95": 9.0, "mediana": 5.0}}}
    avisos = prediccion.avisos_rango(100.0, 5.0, meta)
    assert any(nivel == "warning" for nivel, _ in avisos)


def test_series_fechas_futuras_empiezan_el_mes_siguiente():
    f = series_tiempo.fechas_futuras("2026-10", 3)
    assert [d.strftime("%Y-%m-%d") for d in f] == ["2026-11-01", "2026-12-01", "2027-01-01"]


def test_leer_meta_inexistente_da_error_claro():
    with pytest.raises(FileNotFoundError, match="No existe"):
        modelos.leer_meta("meta_que_no_existe.json")
