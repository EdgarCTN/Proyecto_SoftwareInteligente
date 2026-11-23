"""Configuración central de EcoCiudad IA: rutas, semilla y registro de módulos."""
from pathlib import Path

NOMBRE_PROYECTO = "EcoCiudad IA"
RANDOM_STATE = 42

# Rutas relativas a la raíz del proyecto (nunca absolutas)
BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
IMG_DIR = BASE_DIR / "data" / "imagenes"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Datos procesados (nombres provisionales de C3 sec. 4; la Fase 2 los confirma)
ARCHIVOS_PROCESADOS = {
    "paises": "paises_residuos.csv",
    "dsny_distritos": "dsny_distritos_mensual.csv",
    "serie_ciudad": "serie_ciudad_mensual.csv",
    "distritos_nyc": "distritos_nyc_perfil.csv",
    "textos": "textos_residuos.csv",
}

# Módulos de la app: `modulo` = archivo en app/modules/, `meta` = metadatos en models/
MODULOS = [
    {"id": "prediccion", "titulo": "📈 Predicción", "modulo": "prediccion", "meta": "prediccion_meta.json"},
    {"id": "series", "titulo": "🕒 Series temporales", "modulo": "series_tiempo", "meta": "serie_meta.json"},
    {"id": "imagenes", "titulo": "🖼️ Imágenes", "modulo": "imagenes", "meta": "imagenes_meta.json"},
    {"id": "clustering", "titulo": "🧩 Clustering", "modulo": "clustering", "meta": "clustering_meta.json"},
    {"id": "resumen", "titulo": "📝 Resumen", "modulo": "resumen", "meta": "resumen_meta.json"},
]

# Esquemas de contenedores por tipo de residuo: se completa en la Fase 5,
# cuando se verifiquen las clases reales del dataset de imágenes y la norma elegida.
CONTENEDORES = {}

AVISO_USO = (
    "Herramienta académica de apoyo a la decisión. Las estimaciones y clasificaciones "
    "pueden contener errores y sesgos de los datos; no sustituyen la evaluación de un "
    "especialista. No subas imágenes con personas ni textos con datos personales."
)
