"""Configuración central de EcoResiduos IA: rutas, semilla y registro de módulos."""
from pathlib import Path

NOMBRE_PROYECTO = "EcoResiduos IA"
DESCRIPCION_PROYECTO = (
    "Análisis y apoyo a la decisión en la gestión de residuos sólidos municipales, "
    "con modelos de aprendizaje automático sobre datos abiertos."
)
RANDOM_STATE = 42

# Rutas relativas a la raíz del proyecto (nunca absolutas)
BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
IMG_DIR = BASE_DIR / "data" / "imagenes"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Archivos de datos procesados (generados por src/preparar_datos.py)
ARCHIVOS_PROCESADOS = {
    "paises": "paises_residuos.csv",
    "dsny_distritos": "dsny_distritos_mensual.csv",
    "serie_ciudad": "serie_ciudad_mensual.csv",
}

# Módulos de la app: `modulo` = archivo en app/modules/, `meta` = metadatos en models/
MODULOS = [
    {"id": "prediccion", "titulo": "Predicción", "modulo": "prediccion", "meta": "prediccion_meta.json"},
    {"id": "series", "titulo": "Series temporales", "modulo": "series_tiempo", "meta": "serie_meta.json"},
    {"id": "imagenes", "titulo": "Imágenes", "modulo": "imagenes", "meta": "imagenes_meta.json"},
    {"id": "clustering", "titulo": "Clustering", "modulo": "clustering", "meta": "clustering_meta.json"},
    {"id": "resumen", "titulo": "Resumen de texto", "modulo": "resumen", "meta": "resumen_meta.json"},
]

# --- Módulo 3 (imágenes): nombres, contenedores y umbrales (clases reales de models/clases_imagenes.json) ---
NOMBRES_CLASES = {
    "battery": "Batería o pila", "biological": "Residuo orgánico", "cardboard": "Cartón", "clothes": "Ropa",
    "glass": "Vidrio", "metal": "Metal", "paper": "Papel", "plastic": "Plástico", "shoes": "Zapatos",
    "trash": "Basura general",
}
RESIDUOS_PELIGROSOS = ["battery"]
# Umbrales heurísticos (no derivados de los datos; el modelo no está calibrado):
UMBRAL_CONFIANZA = 0.60            # por debajo se pide otra foto y no se sugiere contenedor
UMBRAL_PELIGROSO_POSIBLE = 0.20    # si una clase peligrosa (2.ª o 3.ª) llega a esta probabilidad, se avisa igual
ESQUEMA_PREDETERMINADO = "proyecto"

_HEX = {"verde": "#2e7d32", "negro": "#212121", "marron": "#6d4c41", "rojo": "#c62828", "azul": "#1565c0",
        "blanco": "#ffffff", "amarillo": "#f9a825", "plomo": "#9e9e9e"}


def _c(color, contenedor, origen, nota=""):
    """Entrada de contenedor. origen: 'norma' (la fuente del esquema lo asigna) o 'proyecto' (criterio del equipo)."""
    return {"color": color, "hex": _HEX[color], "contenedor": contenedor, "origen": origen, "nota": nota}


_NOTA_PELIGRO = "No va a un contenedor común: llévala a un punto de acopio autorizado o consulta a tu municipalidad."
_NOTA_ROPA = "Si está en buen estado, mejor reúso o donación."
_NOTA_NORMA_PE = "Resumen de Inacal publicado por la agencia Andina (2019) sobre la NTP 900.058:2019, 2.ª ed.; de aplicación voluntaria. Conviene contrastar los colores con el texto oficial de INACAL antes de citarla como norma."

CONTENEDORES = {
    "proyecto": {
        "nombre": "Esquema del proyecto (pedagógico, no es un estándar)",
        "fuente": "Convención propia de la aplicación para ilustrar la separación en la fuente; no es una norma oficial.",
        "clases": {
            "paper": _c("azul", "Papel y cartón", "proyecto"), "cardboard": _c("azul", "Papel y cartón", "proyecto"),
            "glass": _c("verde", "Vidrio", "proyecto"), "plastic": _c("amarillo", "Plástico y metal", "proyecto"),
            "metal": _c("amarillo", "Plástico y metal", "proyecto"), "biological": _c("marron", "Orgánico", "proyecto"),
            "trash": _c("negro", "No aprovechable", "proyecto"),
            "battery": _c("rojo", "Punto de acopio especial (pilas y baterías)", "proyecto", _NOTA_PELIGRO),
            "clothes": _c("negro", "Reúso o donación; si no sirve, no aprovechable", "proyecto", _NOTA_ROPA),
            "shoes": _c("negro", "Reúso o donación; si no sirven, no aprovechable", "proyecto", _NOTA_ROPA),
        },
    },
    "peru_municipal": {
        "nombre": "Perú · NTP 900.058:2019 · ámbito municipal",
        "fuente": _NOTA_NORMA_PE,
        "clases": {
            "paper": _c("verde", "Aprovechables", "norma"), "cardboard": _c("verde", "Aprovechables", "norma"),
            "glass": _c("verde", "Aprovechables", "norma"), "plastic": _c("verde", "Aprovechables", "norma"),
            "metal": _c("verde", "Aprovechables", "norma"),
            "clothes": _c("verde", "Aprovechables (textiles)", "norma", _NOTA_ROPA),
            "biological": _c("marron", "Orgánicos", "norma"),
            "battery": _c("rojo", "Peligrosos", "norma", _NOTA_PELIGRO),
            "trash": _c("negro", "No aprovechables", "proyecto", "La norma define los no aprovechables con ejemplos; que una foto de «basura general» caiga aquí es criterio del proyecto."),
            "shoes": _c("negro", "No aprovechables", "proyecto", "El resumen consultado no menciona calzado (sí cuero y textiles); criterio del proyecto. Si están en buen estado, dónalos."),
        },
    },
    "peru_no_municipal": {
        "nombre": "Perú · NTP 900.058:2019 · ámbito no municipal",
        "fuente": _NOTA_NORMA_PE,
        "clases": {
            "paper": _c("azul", "Papel y cartón", "norma"), "cardboard": _c("azul", "Papel y cartón", "norma"),
            "plastic": _c("blanco", "Plástico", "norma"), "metal": _c("amarillo", "Metales", "norma"),
            "biological": _c("marron", "Orgánicos", "norma"), "glass": _c("plomo", "Vidrio", "norma"),
            "battery": _c("rojo", "Peligrosos", "norma", _NOTA_PELIGRO),
            "trash": _c("negro", "No aprovechables", "proyecto", "Que una foto de «basura general» caiga aquí es criterio del proyecto."),
            "clothes": _c("negro", "No aprovechables", "proyecto", "El resumen consultado no asigna color a textiles; criterio del proyecto. " + _NOTA_ROPA),
            "shoes": _c("negro", "No aprovechables", "proyecto", "El resumen consultado no asigna color a calzado; criterio del proyecto. " + _NOTA_ROPA),
        },
    },
}

AVISO_USO = (
    "Herramienta académica de apoyo a la decisión. Las estimaciones y clasificaciones "
    "pueden contener errores y sesgos de los datos; no sustituyen la evaluación de un "
    "especialista. No subas imágenes con personas ni textos con datos personales."
)
