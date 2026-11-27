"""Revisa si cada módulo tiene los archivos que necesita (solo mira que existan; no los abre)."""
import config


def revisar_modulo(modulo, models_dir=None, data_dir=None, artefactos=None):
    """modulo: dict de config.MODULOS. Devuelve {id, titulo, listo, faltan} (faltan = rutas relativas)."""
    models_dir = models_dir or config.MODELS_DIR
    data_dir = data_dir or config.DATA_PROCESSED
    art = (artefactos if artefactos is not None else config.ARTEFACTOS_MODULO).get(modulo["id"], {})
    faltan = [f"models/{n}" for n in art.get("models", []) if not (models_dir / n).exists()]
    faltan += [f"data/processed/{n}" for n in art.get("data", []) if not (data_dir / n).exists()]
    return {"id": modulo["id"], "titulo": modulo["titulo"], "listo": not faltan, "faltan": faltan}


def revisar_todos(**kw):
    return [revisar_modulo(m, **kw) for m in config.MODULOS]
