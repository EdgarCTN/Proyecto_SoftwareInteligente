"""Comprueba que el modelo de imágenes carga y predice en ESTE entorno (versión de Python, TensorFlow y Keras).
Uso (desde la raíz):  python src/comprobar_modelo_imagenes.py [--imagen ruta/foto.jpg]
Las probabilidades con la imagen de prueba (gris uniforme) NO son un resultado: solo comprueban que el modelo funciona."""
import argparse
import os
import platform
import sys
from pathlib import Path

for _flujo in (sys.stdout, sys.stderr):                       # la consola de Windows (cp1252) no admite todos los caracteres
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--imagen", help="foto opcional para ver el top 3")
    args = parser.parse_args()
    print("Python", platform.python_version())
    try:
        import keras
        import tensorflow as tf
    except ImportError as e:
        print(f"FALLO: no se pudo importar TensorFlow/Keras ({e}).\nInstala con: pip install tensorflow. "
              "Si no hay versión para tu Python, crea un entorno con Python 3.11 o 3.12 y reinstala requirements.txt.")
        return 1
    print("TensorFlow", tf.__version__, "| Keras", keras.__version__, "(el modelo se entrenó con TensorFlow 2.21.0 y Keras 3.13.2)")
    from PIL import Image
    from app.modules import imagenes as im
    from app.utils.modelos import leer_meta, ruta_modelo
    try:
        meta = leer_meta(im.ARCHIVO_META)
        clases = im.leer_clases(meta)
        modelo = keras.models.load_model(ruta_modelo(im.ARCHIVO_MODELO))
    except Exception as e:  # noqa: BLE001
        print(f"FALLO al leer o cargar los archivos de models/: {type(e).__name__}: {e}")
        return 1
    print("Entrada del modelo:", modelo.input_shape, "| salida:", modelo.output_shape, "| clases:", len(clases))
    if modelo.output_shape[-1] != len(clases):
        print("FALLO: el número de salidas no coincide con las clases.")
        return 1
    tam = im.tam_entrada(meta)
    prueba = Image.new("RGB", (300, 200), (128, 128, 128))
    probs = im.predecir(modelo, prueba, tam)
    print(f"Suma de probabilidades con imagen de prueba: {probs.sum():.4f} (debe ser cercana a 1)")
    if args.imagen:
        img = im.abrir_imagen(Path(args.imagen).read_bytes())
        for c, p in im.top_k(im.predecir(modelo, img, tam), clases, 3):
            print(f"  {im.nombre_clase(c)}: {p:.1%}")
    print("OK: el modelo carga y predice en este entorno.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
