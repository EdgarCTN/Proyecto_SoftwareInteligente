"""EcoCiudad IA - interfaz Streamlit con una pestaña por módulo de IA.
Ejecutar desde la raíz del proyecto:  streamlit run app/main.py"""
import importlib
import sys
from pathlib import Path

# Permite `import config` y `import app...` sin importar desde dónde se lance
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

import config  # noqa: E402
from app.utils.modelos import estado_modulo  # noqa: E402

st.set_page_config(page_title=config.NOMBRE_PROYECTO, page_icon="♻️", layout="wide")


def mostrar_modulo(nombre):
    """Carga app/modules/<nombre>.py y ejecuta render(); un fallo no tumba el resto de la app."""
    ruta_modulo = f"app.modules.{nombre}"
    try:
        modulo = importlib.import_module(ruta_modulo)
    except ModuleNotFoundError as e:
        if e.name == ruta_modulo:
            st.info("🚧 Módulo en construcción.")
        else:
            st.error(f"Falta la librería «{e.name}». Ejecuta: pip install -r requirements.txt")
        return
    except Exception as e:  # error de sintaxis o de importación dentro del módulo
        st.error(f"No se pudo cargar el módulo: {e}")
        return
    try:
        modulo.render()
    except Exception as e:
        st.error(f"El módulo falló: {e}")
        st.caption("El resto de la aplicación sigue funcionando.")


st.title(f"♻️ {config.NOMBRE_PROYECTO}")
st.caption("Gestión inteligente de residuos urbanos · Software Inteligente (UNMSM, 2026-2)")

with st.sidebar:
    st.subheader("Estado de los módulos")
    for m in config.MODULOS:
        st.write(("✅ " if estado_modulo(m) else "⏳ ") + m["titulo"])
    st.caption("✅ = modelo entrenado disponible · ⏳ = pendiente")
    with st.expander("Aviso de uso responsable"):
        st.write(config.AVISO_USO)

pestanas = st.tabs([m["titulo"] for m in config.MODULOS])
for pestana, m in zip(pestanas, config.MODULOS):
    with pestana:
        mostrar_modulo(m["modulo"])
