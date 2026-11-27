"""Mide el arranque de la app en este equipo (Fase 8 B).  Uso (desde la raíz):  python src/medir_arranque.py [--repeticiones 3] [--puerto 8599]
1) Proceso nuevo: tiempo de importar Streamlit, primera ejecución de la página completa y segunda (AppTest, sin navegador).
2) Servidor: tiempo hasta que `streamlit run app/main.py` responde en /_stcore/health (no incluye abrir el navegador).
Guarda data/processed/m8_arranque.json. Los tiempos dependen del equipo, de la caché del disco y de lo que haya abierto."""
import argparse
import json
import platform
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa cp1252

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "processed" / "m8_arranque.json"

CODIGO = r"""
import json, sys, time
t0 = time.perf_counter()
from streamlit.testing.v1 import AppTest
t1 = time.perf_counter()
at = AppTest.from_file(sys.argv[1], default_timeout=600).run()
t2 = time.perf_counter()
at.run()
t3 = time.perf_counter()
print("RESULTADO " + json.dumps({"importar_streamlit_s": t1 - t0, "primera_ejecucion_s": t2 - t1, "segunda_ejecucion_s": t3 - t2,
      "excepciones": len(at.exception), "errores": len(at.error)}))
"""


def proceso_nuevo():
    r = subprocess.run([sys.executable, "-c", CODIGO, str(RAIZ / "app" / "main.py")], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for linea in r.stdout.splitlines():
        if linea.startswith("RESULTADO "):
            return json.loads(linea[len("RESULTADO "):])
    raise RuntimeError("No se obtuvo resultado.\n" + (r.stderr or r.stdout)[-1500:])


def puerto_libre(puerto):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", puerto)) != 0


def servidor(puerto, limite=180):
    if not puerto_libre(puerto):
        raise RuntimeError(f"El puerto {puerto} está ocupado; usa --puerto con otro número.")
    cmd = [sys.executable, "-m", "streamlit", "run", str(RAIZ / "app" / "main.py"), "--server.headless", "true",
           "--server.port", str(puerto), "--browser.gatherUsageStats", "false"]
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        while time.perf_counter() - t0 < limite:
            if p.poll() is not None:
                raise RuntimeError("El servidor terminó antes de responder.")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{puerto}/_stcore/health", timeout=2) as r:
                    if r.read().decode().strip() == "ok":
                        return time.perf_counter() - t0
            except Exception:  # noqa: BLE001  (aún no responde)
                time.sleep(0.25)
        raise RuntimeError(f"El servidor no respondió en {limite} s.")
    finally:
        p.terminate()
        try:
            p.wait(15)
        except subprocess.TimeoutExpired:
            p.kill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--puerto", type=int, default=8599)
    a = ap.parse_args()
    import streamlit
    res = {"equipo": {"so": platform.platform(), "python": platform.python_version(), "streamlit": streamlit.__version__},
           "proceso_nuevo": [], "servidor_listo_s": []}
    for i in range(1, a.repeticiones + 1):
        r = proceso_nuevo()
        res["proceso_nuevo"].append(r)
        print(f"[{i}/{a.repeticiones}] proceso nuevo: importar {r['importar_streamlit_s']:.2f} s | 1.ª ejecución {r['primera_ejecucion_s']:.2f} s | "
              f"2.ª {r['segunda_ejecucion_s']:.2f} s | excepciones {r['excepciones']} | errores {r['errores']}", flush=True)
    for i in range(1, a.repeticiones + 1):
        s = servidor(a.puerto)
        res["servidor_listo_s"].append(s)
        print(f"[{i}/{a.repeticiones}] servidor listo en {s:.2f} s", flush=True)
    SALIDA.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Guardado:", SALIDA.relative_to(RAIZ))
    print("Pega la salida completa de arriba en el chat.")


if __name__ == "__main__":
    main()
