"""Fija en requirements.txt las versiones realmente instaladas (no inventa ninguna).
Uso (con el entorno activado):  python src/fijar_versiones.py"""
import re
import sys
from importlib import metadata
from pathlib import Path

ruta = Path(__file__).resolve().parent.parent / "requirements.txt"
salida, fijados, faltan = [], [], []

for linea in ruta.read_text(encoding="utf-8").splitlines():
    texto = linea.strip()
    if not texto or texto.startswith("#"):
        salida.append(linea)
        continue
    nombre = re.split(r"[<>=!~\[ ;]", texto, maxsplit=1)[0]
    try:
        version = metadata.version(nombre)
        salida.append(f"{nombre}=={version}")
        fijados.append(f"{nombre}=={version}")
    except metadata.PackageNotFoundError:
        salida.append(linea)
        faltan.append(nombre)

ruta.write_text("\n".join(salida) + "\n", encoding="utf-8")
print(f"Python {sys.version.split()[0]}")
print("Fijados:", ", ".join(fijados) if fijados else "ninguno")
if faltan:
    print("NO instalados (siguen sin versión):", ", ".join(faltan))
