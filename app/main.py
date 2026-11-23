"""EcoResiduos IA: interfaz Streamlit con una pestaña por módulo.
Ejecutar desde la raíz del proyecto:  streamlit run app/main.py"""
import importlib
import importlib.util
import sys
from pathlib import Path

# Permite `import config` y `import app...` sin importar desde dónde se lance
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

import config  # noqa: E402
from app import estilos  # noqa: E402

st.set_page_config(page_title=config.NOMBRE_PROYECTO, layout="wide", initial_sidebar_state="collapsed")
estilos.aplicar()


def modulo_disponible(nombre):
    """True si existe app/modules/<nombre>.py."""
    return importlib.util.find_spec(f"app.modules.{nombre}") is not None


def mostrar_modulo(nombre):
    """Carga app/modules/<nombre>.py y ejecuta render(); un fallo no afecta a los demás módulos."""
    try:
        modulo = importlib.import_module(f"app.modules.{nombre}")
    except ModuleNotFoundError as e:
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


estilos.cabecera()

disponibles = [m for m in config.MODULOS if modulo_disponible(m["modulo"])]
if not disponibles:
    st.warning("No hay módulos disponibles en app/modules/.")
else:
    pestanas = st.tabs([m["titulo"] for m in disponibles])
    for pestana, m in zip(pestanas, disponibles):
        with pestana:
            mostrar_modulo(m["modulo"])

estilos.pie()
