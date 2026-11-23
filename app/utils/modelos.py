"""Carga de artefactos entrenados y lectura de *_meta.json (la app nunca entrena)."""
import json

import config

try:
    import streamlit as st
    _cache_resource = st.cache_resource
except ImportError:  # permite usar el módulo fuera de Streamlit (tests, notebooks)
    def _cache_resource(f):
        return f


def ruta_modelo(nombre):
    """Ruta absoluta de un archivo dentro de models/."""
    return config.MODELS_DIR / nombre


def meta_existe(nombre_meta):
    return ruta_modelo(nombre_meta).exists()


def leer_meta(nombre_meta):
    """Lee models/<nombre_meta> y devuelve un dict. Única fuente de métricas."""
    ruta = ruta_modelo(nombre_meta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe models/{nombre_meta}. Se genera al ejecutar el notebook de entrenamiento del módulo."
        )
    return json.loads(ruta.read_text(encoding="utf-8"))


@_cache_resource
def cargar_joblib(nombre):
    """Carga un modelo de scikit-learn/XGBoost guardado con joblib."""
    import joblib
    ruta = ruta_modelo(nombre)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe models/{nombre}. Entrena y guarda el modelo primero.")
    return joblib.load(ruta)


@_cache_resource
def cargar_keras(nombre):
    """Carga un modelo .keras (requiere tensorflow)."""
    from tensorflow import keras
    ruta = ruta_modelo(nombre)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe models/{nombre}. Entrena y guarda el modelo primero.")
    return keras.models.load_model(ruta)

