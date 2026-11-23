"""Prepara los textos de evaluación del módulo 5: DS5 (XL-Sum, español) y DS6 (MLSUM, español).
Solo usa la partición *test* (no se entrena ningún modelo). Genera data/processed/textos_residuos.csv
(NO va al repositorio: licencia no comercial), log_textos.txt y revision_filtro.csv (revisión manual).
Uso, desde la raíz:  python src/preparar_textos.py [--n 500] [--fuente xlsum|mlsum|ambas]
                     [--xlsum_archivo RUTA] [--mlsum_archivo RUTA]
Carga: (1) archivos parquet de la rama «refs/convert/parquet» del Hub (vía huggingface_hub, ya instalado con `datasets`);
(2) si falla, un archivo local de la partición test (.parquet, .csv, .jsonl) descargado a mano desde las fuentes de C3."""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import config  # noqa: E402

SEMILLA = config.RANDOM_STATE
# Prefijos de palabras (sin tildes) que marcan un artículo como "sobre residuos" (heurística editable)
PALABRAS_RESIDUOS = ["residuo", "basura", "basurero", "botadero", "reciclaj", "reciclar", "plastico",
                     "vertedero", "relleno sanitario", "desecho", "compostaje"]
RE_RESIDUOS = re.compile(r"\b(" + "|".join(PALABRAS_RESIDUOS) + ")")
# Los scripts de carga de estos datasets ya no funcionan con `datasets` actual (error real, 2026-11-21): se leen los parquet
REPOS = {"xlsum": ("csebuetnlp/xlsum", "spanish"), "mlsum": ("GEM/mlsum", "es")}  # (repositorio, configuración)
RAMA_PARQUET = "refs/convert/parquet"
COLUMNAS = {"texto": ["text", "article"], "resumen_ref": ["summary", "target"], "id": ["id", "gem_id"]}
SALIDA = config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["textos"]
LOG = config.DATA_PROCESSED / "log_textos.txt"
REVISION = config.DATA_PROCESSED / "revision_filtro.csv"


def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


def marcar_residuos(textos):
    """1 si el texto contiene alguna palabra clave de residuos (sin distinguir tildes ni mayúsculas)."""
    return textos.map(lambda t: int(bool(RE_RESIDUOS.search(sin_tildes(t))))).astype(int)


def estandarizar(df, fuente):
    """Deja las columnas id, fuente, particion, texto, resumen_ref y descarta filas vacías o repetidas."""
    def col(cands):
        return next((c for c in cands if c in df.columns), None)
    ct, cr, ci = col(COLUMNAS["texto"]), col(COLUMNAS["resumen_ref"]), col(COLUMNAS["id"])
    if not ct or not cr:
        raise ValueError(f"No se hallaron las columnas de texto y resumen. Columnas reales: {list(df.columns)}")
    out = pd.DataFrame({
        "id": df[ci].astype(str) if ci else df.index.astype(str),
        "fuente": fuente, "particion": "test",
        "texto": df[ct].astype(str).str.strip(), "resumen_ref": df[cr].astype(str).str.strip()})
    out = out[(out["texto"].str.len() > 0) & (out["resumen_ref"].str.len() > 0)]
    return out.drop_duplicates("texto").reset_index(drop=True)


def muestrear(df, n, semilla=SEMILLA, max_residuos=None):
    """n artículos: primero los de residuos (hasta `max_residuos`); se completa con otros (semilla fija)."""
    pos, neg = df[df["es_residuos"] == 1], df[df["es_residuos"] == 0]
    m = pos.sample(min(n, len(pos), max_residuos if max_residuos else n), random_state=semilla)
    if len(m) < n:
        m = pd.concat([m, neg.sample(min(n - len(m), len(neg)), random_state=semilla)])
    return m.sample(frac=1, random_state=semilla).reset_index(drop=True)


def elegir_archivos(archivos, configuracion):
    """Parquet de la partición test de una configuración, a partir de la lista de archivos del repositorio."""
    patron = re.compile(rf"(^|/){re.escape(configuracion.lower())}([/.-]|$)")
    def es_test(f):  # carpeta o archivo llamado exactamente «test»; se excluyen conjuntos aparte como «challenge_test_covid»
        partes = f.lower().split("/")
        return ("test" in partes[:-1] or partes[-1].startswith("test")) and not any("challenge" in p for p in partes)
    return sorted(f for f in archivos if f.endswith(".parquet") and es_test(f) and patron.search(f.lower()))


def leer_archivo(ruta):
    """Lee un archivo local de la partición test: .parquet, .csv, .jsonl o .json."""
    ruta = Path(ruta)
    sufijo = ruta.suffix.lower()
    if sufijo == ".parquet":
        return pd.read_parquet(ruta)
    if sufijo == ".csv":
        return pd.read_csv(ruta)
    try:
        return pd.read_json(ruta, lines=True)
    except ValueError:
        return pd.read_json(ruta)


def cargar(fuente, archivo=None):
    """Devuelve (DataFrame, descripción de la carga). Con `archivo` usa el archivo local (se asume partición test)."""
    if archivo:
        return leer_archivo(archivo), {"archivo_local": str(archivo)}
    from huggingface_hub import HfApi, hf_hub_download  # import tardío
    repo, configuracion = REPOS[fuente]
    todos = HfApi().list_repo_files(repo, repo_type="dataset", revision=RAMA_PARQUET)
    elegidos = elegir_archivos(todos, configuracion)
    if not elegidos:
        con_test = [f for f in todos if f.endswith(".parquet") and "test" in f.lower()]
        raise RuntimeError(f"Sin parquet de test para «{configuracion}» en {repo}. Parquet con «test» ({len(con_test)}): "
                           f"{con_test[:15]}; total de archivos: {len(todos)}")
    partes = [pd.read_parquet(hf_hub_download(repo, f, repo_type="dataset", revision=RAMA_PARQUET)) for f in elegidos]
    return pd.concat(partes, ignore_index=True), {"repo": repo, "rama": RAMA_PARQUET, "archivos": elegidos}


def procesar(fuente, n, log, archivo=None, max_residuos=None):
    try:
        crudo, kw = cargar(fuente, archivo)
    except Exception as e:  # noqa: BLE001
        log.append(f"{fuente}: FALLÓ la carga ({type(e).__name__}).\n{str(e)[:900]}")
        return None, None
    log.append(f"{fuente}: cargado con {kw}; {len(crudo)} filas y columnas {list(crudo.columns)}")
    df = estandarizar(crudo, fuente)
    df["es_residuos"] = marcar_residuos(df["texto"])
    pal_t, pal_r = df["texto"].str.split().str.len(), df["resumen_ref"].str.split().str.len()
    log.append(f"{fuente}: {len(df)} artículos válidos en test; con palabras de residuos = {int(df['es_residuos'].sum())} "
               f"({df['es_residuos'].mean()*100:.1f} %); palabras por texto (media) = {pal_t.mean():.0f}; "
               f"por resumen de referencia (media) = {pal_r.mean():.1f}")
    muestra = muestrear(df, n, max_residuos=max_residuos)
    log.append(f"{fuente}: muestra de evaluación = {len(muestra)} artículos, de ellos de residuos = {int(muestra['es_residuos'].sum())}")
    flag = df[df["es_residuos"] == 1]
    rev = flag.sample(min(25, len(flag)), random_state=SEMILLA) if len(flag) else flag
    rev = rev.assign(extracto=rev["texto"].str.slice(0, 300), relevante_manual="")[["id", "fuente", "extracto", "relevante_manual"]]
    return muestra, rev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500, help="artículos por fuente en la muestra de evaluación")
    ap.add_argument("--max_residuos", type=int, default=250,
                    help="tope de artículos de residuos por fuente (para que E1 y E2 sean comparables)")
    ap.add_argument("--fuente", choices=["xlsum", "mlsum", "ambas"], default="ambas")
    ap.add_argument("--xlsum_archivo", help="archivo local de test de XL-Sum (español)")
    ap.add_argument("--mlsum_archivo", help="archivo local de test de MLSUM (español)")
    a = ap.parse_args()
    log, muestras, revs = [], [], []
    for f in (["xlsum", "mlsum"] if a.fuente == "ambas" else [a.fuente]):
        m, r = procesar(f, a.n, log, getattr(a, f + "_archivo"), a.max_residuos)
        if m is not None:
            muestras.append(m)
            revs.append(r)
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    if muestras:
        pd.concat(muestras, ignore_index=True).to_csv(SALIDA, index=False)
        pd.concat(revs, ignore_index=True).to_csv(REVISION, index=False)
        log.append(f"Guardado {SALIDA.name} ({sum(len(m) for m in muestras)} filas; NO subir al repositorio) y {REVISION.name} "
                   "(rellena la columna relevante_manual con 1 o 0 para estimar la precisión del filtro)")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
