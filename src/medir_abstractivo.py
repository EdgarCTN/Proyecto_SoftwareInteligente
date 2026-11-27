"""Mide el resumen abstractivo en TU equipo: tiempo de carga, tiempo de generación y memoria (sin Administrador de tareas).
Uso, desde la raíz del proyecto:  python src/medir_abstractivo.py
Para medir la memoria instala antes (herramienta de medición, no de la app):  pip install psutil
No entrena nada. Si el modelo no está en la caché de Hugging Face, lo descarga (≈ 2.33 GB). Guarda data/processed/m5_medicion_cpu.json.
Tarda varios minutos en CPU: la primera generación y el texto largo son lo más lento."""
import json
import logging
import os
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
logging.getLogger("streamlit").setLevel(logging.ERROR)  # silencia avisos de Streamlit al importar el módulo de la app

import config  # noqa: E402
from app.modules import resumen as rs  # noqa: E402
from app.utils import texto as tx  # noqa: E402

try:
    import psutil
    _PROCESO = psutil.Process(os.getpid())
except ImportError:
    psutil = None

CASO_CORTO, CASO_LARGO = "ejemplo (un bloque)", "ejemplo repetido 5 veces (varios bloques)"
REPETICIONES = {CASO_CORTO: 2, CASO_LARGO: 1}


def memoria_mib():
    """(actual, pico) en MiB del proceso; (None, None) sin psutil. El pico solo lo da Windows."""
    if psutil is None:
        return None, None
    info = _PROCESO.memory_info()
    pico = getattr(info, "peak_wset", None)
    return round(info.rss / 2**20), (round(pico / 2**20) if pico else None)


def main():
    # La consola de Windows (cp1252) no codifica todos los símbolos: se fuerza UTF-8 (Git Bash lo muestra bien) y se avanza línea a línea
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:  # noqa: BLE001
        pass
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    try:  # menos ruido en la consola: solo errores de transformers (los avisos ya se conocen, REGISTRO 5)
        from transformers import logging as hf_logging
        hf_logging.set_verbosity_error()
    except Exception:  # noqa: BLE001
        pass

    equipo = {"sistema": platform.platform(), "python": platform.python_version(), "nucleos_logicos": os.cpu_count(),
              "hilos_torch": torch.get_num_threads(), "gpu": bool(torch.cuda.is_available()), "psutil": psutil is not None}
    print("MEDICIÓN equipo:", json.dumps(equipo, ensure_ascii=False))
    if psutil is None:
        print("MEDICIÓN aviso: sin psutil no se mide la memoria (pip install psutil).")

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(rs.MODELO_ID, revision=rs.REVISION)
    modelo = AutoModelForSeq2SeqLM.from_pretrained(rs.MODELO_ID, revision=rs.REVISION).eval()
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    modelo.to(dispositivo)
    t_carga = time.perf_counter() - t0
    mem_carga = memoria_mib()
    print(f"MEDICIÓN carga del modelo (con el modelo ya descargado): {t_carga:.1f} s | memoria tras cargar (MiB): {mem_carga[0]}")

    t0 = time.perf_counter()
    rs.resumen_abstractivo(tok, modelo, dispositivo, rs.TEXTO_EJEMPLO)
    t_calentamiento = time.perf_counter() - t0   # la primera generación suele ser más lenta; no se promedia
    print(f"MEDICIÓN calentamiento (primera generación, no se promedia): {t_calentamiento:.1f} s")

    casos = {CASO_CORTO: rs.TEXTO_EJEMPLO, CASO_LARGO: " ".join([rs.TEXTO_EJEMPLO] * 5)}
    resultados = {}
    for nombre, texto in casos.items():
        tiempos, ultimo = [], None
        print(f"MEDICIÓN midiendo: {nombre} ({tx.contar_palabras(texto)} palabras)...")
        for _ in range(REPETICIONES[nombre]):
            t0 = time.perf_counter()
            resumen, info = rs.resumen_abstractivo(tok, modelo, dispositivo, texto)
            tiempos.append(round(time.perf_counter() - t0, 2))
            ultimo = (resumen, info)
        resultados[nombre] = {"palabras_texto": tx.contar_palabras(texto), "bloques": ultimo[1]["bloques"], "tiempos_s": tiempos,
                              "palabras_resumen": tx.contar_palabras(ultimo[0]), "resumen": ultimo[0],
                              "no_respaldados": tx.datos_no_respaldados(ultimo[0], texto)}
        print(f"MEDICIÓN {nombre}: bloques = {ultimo[1]['bloques']} | tiempos (s) = {tiempos}")
        print(f"MEDICIÓN   resumen: {ultimo[0]}")
    mem_final = memoria_mib()
    print(f"MEDICIÓN memoria al final (MiB): actual = {mem_final[0]} | pico = {mem_final[1]}")

    salida = {"fecha": time.strftime("%Y-%m-%d"), "equipo": equipo, "modelo": rs.MODELO_ID, "revision": rs.REVISION, "dispositivo": dispositivo,
              "carga_s": round(t_carga, 1), "calentamiento_s": round(t_calentamiento, 1), "memoria_tras_carga_mib": mem_carga[0],
              "memoria_final_mib": mem_final[0], "memoria_pico_mib": mem_final[1], "casos": resultados,
              "nota": "El texto largo es el ejemplo repetido: solo sirve para medir tiempo, no la calidad."}
    destino = config.DATA_PROCESSED / "m5_medicion_cpu.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("MEDICIÓN guardado en", destino)


if __name__ == "__main__":
    main()
