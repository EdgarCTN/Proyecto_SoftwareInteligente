"""Verificación de las imágenes: DS3 (Garbage Classification V2) y DS4 (TrashNet).
Cuenta clases, detecta archivos dañados, tamaños y duplicados (idénticos por MD5 y muy parecidos por hash perceptual),
dentro de cada conjunto y entre DS3 y DS4. Escribe data/processed/verificacion_imagenes.txt y duplicados_ds3_ds4.csv.
Uso, desde la raíz:  python src/verificar_imagenes.py --ds3 RUTA_DS3 [--ds4 RUTA_DS4]
(RUTA_DS3 debe apuntar a UNA sola versión del dataset; imprime las carpetas para que elijas)."""
import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import config  # noqa: E402

EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASES_TRASHNET = ["glass", "paper", "cardboard", "plastic", "metal", "trash"]
SALIDA_TXT = config.DATA_PROCESSED / "verificacion_imagenes.txt"
SALIDA_DUP = config.DATA_PROCESSED / "duplicados_ds3_ds4.csv"


def dhash(img):
    """Hash perceptual de 64 bits (diferencias horizontales sobre 9x8 en gris)."""
    g = np.asarray(img.convert("L").resize((9, 8), Image.Resampling.LANCZOS), dtype=int)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def analizar(raiz):
    """DataFrame con una fila por imagen: ruta relativa, clase (carpeta madre), tamaño y hashes; y lista de dañadas."""
    raiz = Path(raiz)
    filas, daniadas = [], []
    for p in sorted(raiz.rglob("*")):
        if p.suffix.lower() not in EXT or not p.is_file():
            continue
        rel = p.relative_to(raiz).as_posix()
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                w, h = im.size
                filas.append({"ruta": rel, "clase": p.parent.name, "w": w, "h": h,
                              "md5": hashlib.md5(p.read_bytes()).hexdigest(), "dhash": dhash(im)})
        except Exception as e:  # noqa: BLE001
            daniadas.append(f"{rel} ({type(e).__name__})")
    return pd.DataFrame(filas, columns=["ruta", "clase", "w", "h", "md5", "dhash"]), daniadas


def informe(nombre, raiz, df, daniadas, L):
    L.append(f"\n=== {nombre}: {raiz} ===")
    L.append(f"imágenes legibles: {len(df)}; dañadas: {len(daniadas)}" + (f" (primeras: {daniadas[:5]})" if daniadas else ""))
    if df.empty:
        L.append("No se encontraron imágenes. " + ("La ruta no existe." if not Path(raiz).exists()
                 else "La carpeta existe pero no tiene imágenes (¿falta descargar o descomprimir?)."))
        return
    carpetas = df.assign(carpeta=df["ruta"].map(lambda r: str(Path(r).parent.as_posix()))).groupby("carpeta").size()
    L.append(f"carpetas con imágenes: {len(carpetas)}" + ("  (más de 30: se muestran 30)" if len(carpetas) > 30 else ""))
    L += [f"  {c}: {n}" for c, n in carpetas.head(30).items()]
    particiones = {x for r in df["ruta"] for x in Path(r).parts[:-1] if x.lower() in {"train", "val", "valid", "validation", "test"}}
    L.append(f"carpetas de partición detectadas: {sorted(particiones) or 'ninguna'}")
    L.append("conteo por clase (carpeta madre): " + "; ".join(f"{c}={n}" for c, n in df["clase"].value_counts().items()))
    L.append(f"ancho: mín {df['w'].min()}, mediana {int(df['w'].median())}, máx {df['w'].max()}; "
             f"alto: mín {df['h'].min()}, mediana {int(df['h'].median())}, máx {df['h'].max()}")
    for col, etiqueta in (("md5", "idénticas (MD5)"), ("dhash", "muy parecidas (hash perceptual)")):
        extra = int(df.duplicated(col).sum())
        L.append(f"duplicados internos {etiqueta}: {extra} imágenes sobrantes")


def cruzar(df3, df4, L):
    """Imágenes de DS4 que también aparecen en DS3. Devuelve el DataFrame de coincidencias."""
    piezas = []
    for col, tipo in (("md5", "md5"), ("dhash", "dhash")):
        m = df4.merge(df3, on=col, suffixes=("_ds4", "_ds3"))[["ruta_ds3", "ruta_ds4"]].assign(tipo=tipo)
        piezas.append(m)
    cruce = pd.concat(piezas, ignore_index=True).drop_duplicates(["ruta_ds3", "ruta_ds4", "tipo"])
    n4 = cruce["ruta_ds4"].nunique()
    L.append("\n=== DS3 frente a DS4 ===")
    L.append(f"imágenes de DS4 con coincidencia en DS3: {n4} de {len(df4)} ({n4/max(len(df4),1)*100:.1f} %); "
             f"por MD5: {cruce[cruce['tipo']=='md5']['ruta_ds4'].nunique()}, por hash perceptual: {cruce[cruce['tipo']=='dhash']['ruta_ds4'].nunique()}")
    c3, c4 = set(df3["clase"].str.lower()), set(df4["clase"].str.lower())
    L.append(f"clases con el mismo nombre en DS3 y DS4: {sorted(c3 & c4) or 'ninguna'}")
    L.append(f"clases de TrashNet que no están por nombre en DS3: {sorted(set(CLASES_TRASHNET) - c3)} (el mapeo se define en el notebook de entrenamiento)")
    return cruce


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds3", required=True)
    ap.add_argument("--ds4")
    a = ap.parse_args()
    L = []
    df3, d3 = analizar(a.ds3)
    informe("DS3", a.ds3, df3, d3, L)
    if a.ds4:
        df4, d4 = analizar(a.ds4)
        informe("DS4", a.ds4, df4, d4, L)
        if not df3.empty and not df4.empty:
            cruce = cruzar(df3.rename(columns={"ruta": "ruta_ds3"}), df4.rename(columns={"ruta": "ruta_ds4"}), L)
            config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
            cruce.to_csv(SALIDA_DUP, index=False)
            L.append(f"(coincidencias guardadas en {SALIDA_DUP.relative_to(RAIZ).as_posix()})")
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    SALIDA_TXT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
