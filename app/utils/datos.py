"""Lectura de los CSV procesados (generados por src/preparar_datos.py en la Fase 2)."""
import config

try:
    import streamlit as st
    _cache_data = st.cache_data
except ImportError:
    def _cache_data(f):
        return f


def ruta_procesado(clave):
    """Ruta de un CSV procesado según la clave de config.ARCHIVOS_PROCESADOS."""
    return config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS[clave]


def procesado_existe(clave):
    return ruta_procesado(clave).exists()


@_cache_data
def cargar_procesado(clave):
    """Devuelve el CSV procesado como DataFrame; error claro si aún no existe."""
    import pandas as pd
    ruta = ruta_procesado(clave)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe data/processed/{ruta.name}. Ejecuta python src/preparar_datos.py (Fase 2)."
        )
    return pd.read_csv(ruta)
