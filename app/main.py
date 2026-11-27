"""EcoCiudad IA - interfaz Streamlit: inicio + una pestaña por módulo de IA.
Ejecutar desde la raíz del proyecto:  streamlit run app/main.py"""
import importlib
import sys
import time
import traceback
from pathlib import Path

# Permite `import config` y `import app...` sin importar desde dónde se lance
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

import config  # noqa: E402
from app.utils.diagnostico import revisar_todos  # noqa: E402

st.set_page_config(page_title=config.NOMBRE_PROYECTO, page_icon="♻️", layout="wide")


def mostrar_modulo(nombre):
    """Carga app/modules/<nombre>.py y ejecuta render(); un fallo no tumba el resto de la app.
    Devuelve {'estado': 'ok'|'construccion'|'error', 'segundos': float, 'detalle': str}."""
    t0 = time.perf_counter()
    ruta_modulo = f"app.modules.{nombre}"
    estado, detalle = "ok", ""
    try:
        modulo = importlib.import_module(ruta_modulo)
    except ModuleNotFoundError as e:
        if e.name == ruta_modulo:
            estado = "construccion"
            st.info("🚧 Módulo en construcción.")
        else:
            estado, detalle = "error", f"Falta la librería «{e.name}»."
            st.error(f"Falta la librería «{e.name}». Ejecuta: pip install -r requirements.txt")
    except Exception as e:  # noqa: BLE001  (error de sintaxis o de importación dentro del módulo)
        estado, detalle = "error", f"No se pudo cargar el módulo: {e}"
        st.error(detalle)
        with st.expander("Detalle técnico del error"):
            st.code(traceback.format_exc())
    else:
        try:
            modulo.render()
        except Exception as e:  # noqa: BLE001
            estado, detalle = "error", f"El módulo falló: {e}"
            st.error(detalle)
            st.caption("El resto de la aplicación sigue funcionando.")
            with st.expander("Detalle técnico del error"):
                st.code(traceback.format_exc())
    return {"estado": estado, "segundos": time.perf_counter() - t0, "detalle": detalle}


st.title(f"♻️ {config.NOMBRE_PROYECTO}")
st.caption("Gestión inteligente de residuos urbanos · Software Inteligente (UNMSM, 2026-2)")

with st.sidebar:
    st.subheader("Estado de los módulos")
    try:
        for r in revisar_todos():
            st.write(("✅ " if r["listo"] else "⏳ ") + r["titulo"])
            if r["faltan"]:
                st.caption("Faltan: " + ", ".join(r["faltan"]))
    except Exception as e:  # noqa: BLE001
        st.caption(f"No se pudo revisar el estado de los módulos: {e}")
    st.caption("✅ = archivos del módulo presentes (no prueba que funcione) · ⏳ = faltan archivos")
    with st.expander("Aviso de uso responsable"):
        st.write(config.AVISO_USO)

titulos = ["🏠 Inicio"] + [m["titulo"] for m in config.MODULOS]
nombres = ["inicio"] + [m["modulo"] for m in config.MODULOS]
resultados = {}
for pestana, titulo, nombre in zip(st.tabs(titulos), titulos, nombres):
    with pestana:
        resultados[titulo] = mostrar_modulo(nombre)

with st.sidebar:
    with st.expander("Diagnóstico técnico"):
        st.caption("Tiempo de esta ejecución de la página (todas las pestañas se ejecutan en cada interacción; "
                   "los modelos y datos se cargan una sola vez gracias a la caché).")
        for titulo, r in resultados.items():
            marca = {"ok": "✅", "construccion": "🚧", "error": "❌"}[r["estado"]]
            st.write(f"{marca} {titulo}: {r['segundos']:.2f} s")
            if r["detalle"]:
                st.caption(r["detalle"])
