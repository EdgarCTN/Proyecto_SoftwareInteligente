"""Módulo 5 · Resumen de texto. TextRank por defecto; modelo abstractivo opcional (descarga el modelo del Hub, no entrena).
Las funciones puras de arriba no dependen de la interfaz; las usan las pruebas."""
import importlib.util
import json
import time
import traceback
from contextlib import nullcontext

import pandas as pd
import streamlit as st

import config
from app.utils import texto as tx
from app.utils.modelos import leer_meta

ARCHIVO_META = "resumen_meta.json"
# Modelo y revisión verificados en la ejecución del notebook 05 (REGISTRO 5); el meta puede sustituirlos
MODELO_ID = "csebuetnlp/mT5_multilingual_XLSum"
REVISION = "2437a524effdbadc327ced84595508f1e32025b3"
# Parámetros de generación: los mismos que se usaron en la evaluación
MAX_ENTRADA_TOKENS, MAX_SALIDA_TOKENS, NUM_BEAMS, NO_REPETIR_NGRAM = 512, 84, 4, 2
LIBRERIAS_ABSTRACTIVO = ["torch", "transformers", "sentencepiece"]

MIN_PALABRAS = 20
MAX_CARACTERES = 300_000
MAX_BYTES_ARCHIVO = 1_000_000
LIMITE_ORACIONES_TEXTRANK = 300     # por encima, se reduce por bloques antes de aplicar TextRank (el costo crece con el cuadrado)
PALABRAS_BLOQUE_EXTRACTIVO = 450
PALABRAS_BLOQUE_ABSTRACTIVO = 300   # ≈ cabe en 512 tokens (supuesto; la app avisa si algún bloque se recorta)
MAX_BLOQUES_ABSTRACTIVO = 10
# Medido en un PC de 4 núcleos sin GPU (REGISTRO 5): ≈ 15 s por bloque de ≈ 260 palabras; ≈ 77 s para 5 bloques (6 llamadas, incluida la final)
SEG_POR_LLAMADA_CPU = 15

TEXTO_EJEMPLO = (
    "La gestión de los residuos sólidos urbanos comienza en los hogares, los mercados y los comercios, donde se generan a diario grandes cantidades de basura. "
    "Para que el sistema funcione, cada tipo de residuo debería separarse desde el origen: los restos de comida y de jardín por un lado, los materiales "
    "aprovechables como papel, cartón, vidrio, metal y plástico por otro, y finalmente los residuos que no se pueden aprovechar. Cuando esta separación no "
    "se hace, los materiales reciclables se ensucian y pierden valor, y los residuos orgánicos terminan mezclados con el resto.\n\n"
    "Después de la separación vienen la recolección y el transporte. Los camiones recorren rutas que pueden diseñarse con poca información sobre cuánta basura "
    "hay realmente en cada zona, lo que provoca viajes innecesarios, combustible gastado y contenedores desbordados en los puntos de mayor demanda. Con datos "
    "históricos de generación se pueden planificar mejor las frecuencias de recojo y reducir esos costos.\n\n"
    "Los residuos orgánicos pueden transformarse en compost, que sirve como abono para parques y huertos. Los materiales reciclables se entregan a recicladores "
    "y a plantas de clasificación, donde la calidad de la separación inicial define cuánto se puede aprovechar. Lo que no se aprovecha termina en un relleno "
    "sanitario, que debe estar bien diseñado para controlar los líquidos y los gases que produce la descomposición.\n\n"
    "Muchas ciudades enfrentan además un problema de comunicación: los vecinos no siempre saben en qué contenedor va cada residuo. Las campañas claras, los "
    "colores de contenedor consistentes y la información disponible en el celular ayudan a que la separación sea más fácil y más frecuente."
)


# ---------- Funciones puras ----------
def leer_texto_subido(datos):
    """Decodifica los bytes de un .txt: UTF-8 (con o sin BOM) y, si falla, Windows-1252."""
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            return datos.decode(codificacion)
        except UnicodeDecodeError:
            continue
    return datos.decode("latin-1", errors="replace")


def texto_valido(texto):
    """(True, "") si el texto se puede resumir; si no, (False, motivo)."""
    if not str(texto).strip():
        return False, "Escribe, pega o sube un texto."
    n = tx.contar_palabras(texto)
    if n < MIN_PALABRAS:
        return False, f"El texto es muy corto ({n} palabras): hay poco que resumir. Usa al menos {MIN_PALABRAS}."
    if len(texto) > MAX_CARACTERES:
        return False, f"El texto es demasiado largo ({len(texto):,} caracteres; el límite es {MAX_CARACTERES:,})."
    return True, ""


def resumen_extractivo(texto, n):
    """TextRank con n oraciones. Devuelve (resumen, reducido); `reducido` es True si hubo que acortar por bloques antes."""
    actual, reducido = str(texto), False
    while len(tx.dividir_oraciones(actual)) > LIMITE_ORACIONES_TEXTRANK:
        bloques = tx.dividir_en_bloques(actual, PALABRAS_BLOQUE_EXTRACTIVO)
        nuevo = " ".join(tx.textrank(b, 1) for b in bloques)
        if len(nuevo) >= len(actual):
            break
        actual, reducido = nuevo, True
    return tx.textrank(actual, n), reducido


def bloques_para_abstractivo(texto):
    """Bloques de ≈ PALABRAS_BLOQUE_ABSTRACTIVO palabras; se conservan solo los primeros MAX_BLOQUES_ABSTRACTIVO. -> (bloques, recortado)"""
    bloques = tx.dividir_en_bloques(texto, PALABRAS_BLOQUE_ABSTRACTIVO)
    return bloques[:MAX_BLOQUES_ABSTRACTIVO], len(bloques) > MAX_BLOQUES_ABSTRACTIVO


def estimar_segundos_cpu(n_bloques):
    """Estimación gruesa del tiempo del abstractivo sin GPU: una llamada por bloque más una final si hay más de un bloque.
    Extrapolada de UNA medición (SEG_POR_LLAMADA_CPU); otro equipo puede ser más lento o más rápido."""
    return (n_bloques + (1 if n_bloques > 1 else 0)) * SEG_POR_LLAMADA_CPU


def librerias_faltantes():
    """Librerías del resumen abstractivo que no están instaladas."""
    return [n for n in LIBRERIAS_ABSTRACTIVO if importlib.util.find_spec(n) is None]


def _sin_gradiente():
    try:
        import torch
        return torch.no_grad()
    except ImportError:
        return nullcontext()


def generar_abstractivo(tok, modelo, dispositivo, texto):
    """Un resumen abstractivo de un texto (se trunca a MAX_ENTRADA_TOKENS tokens); mismos parámetros que en la evaluación."""
    entrada = tok([tx.normalizar_espacios(texto)], return_tensors="pt", truncation=True, max_length=MAX_ENTRADA_TOKENS).to(dispositivo)
    with _sin_gradiente():
        ids = modelo.generate(**entrada, max_new_tokens=MAX_SALIDA_TOKENS, num_beams=NUM_BEAMS, no_repeat_ngram_size=NO_REPETIR_NGRAM)
    return tok.batch_decode(ids, skip_special_tokens=True)[0].strip()


def resumen_abstractivo(tok, modelo, dispositivo, texto):
    """Resumen abstractivo; si el texto es largo, por bloques (se resumen los bloques y luego los resúmenes).
    Devuelve (resumen, info) con info = {bloques, recortado, bloques_truncados}."""
    bloques, recortado = bloques_para_abstractivo(texto)
    truncados = sum(len(tok(b)["input_ids"]) > MAX_ENTRADA_TOKENS for b in bloques)
    base = " ".join(bloques)
    final, _ = tx.resumen_jerarquico(base, lambda b: generar_abstractivo(tok, modelo, dispositivo, b), palabras=PALABRAS_BLOQUE_ABSTRACTIVO)
    return final, {"bloques": len(bloques), "recortado": recortado, "bloques_truncados": int(truncados)}


def tabla_evaluacion(meta):
    """DataFrame legible con la evaluación guardada en el meta (vacío si no hay)."""
    filas = pd.DataFrame(meta.get("evaluacion", []))
    if filas.empty:
        return filas
    filas["principal"] = filas["metodo"].isin(meta.get("metodos_principales", []))
    return filas.sort_values(["fuente", "principal", "rougeL"], ascending=[True, False, False]).reset_index(drop=True)


def figura_comparacion(tabla):
    """Barras AGRUPADAS de ROUGE-L por método y fuente (apiladas sumarían dos F1 y engañarían)."""
    from app.utils.graficos import grafico_barras
    fig = grafico_barras(tabla[tabla["principal"]], "metodo", "rougeL", "ROUGE-L (F1 medio) de los métodos principales", color="fuente")
    fig.update_layout(barmode="group", xaxis_title="Método", yaxis_title="ROUGE-L (F1 medio)", legend_title_text="Fuente")
    return fig


def frases_bootstrap(meta):
    """Frases sobre la diferencia de ROUGE-L frente a Lead-2 (con su intervalo), construidas desde el meta."""
    base = (meta.get("metodos_principales") or ["Lead-2"])[0]
    frases = []
    for clave, b in meta.get("bootstrap_vs_lead", {}).items():
        fuente, metodo = clave.split("|", 1)
        lo, hi = b["ic95"]
        veredicto = "la diferencia se distingue de cero" if b["excluye_cero"] else "la diferencia NO se distingue de cero"
        frases.append(f"{fuente} · {metodo} frente a {base}: ΔROUGE-L = {b['dif_media']:+.4f} (IC 95 %: {lo:+.4f} a {hi:+.4f}); {veredicto}.")
    return frases


# ---------- Interfaz ----------
@st.cache_resource(show_spinner="Cargando el modelo (la primera vez se descargan unos 2.3 GB)…")
def _cargar_abstractivo(modelo_id, revision):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(modelo_id, revision=revision)
    modelo = AutoModelForSeq2SeqLM.from_pretrained(modelo_id, revision=revision).eval()
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    return tok, modelo.to(dispositivo), dispositivo


def _cargar_ejemplo():
    st.session_state["texto_entrada"] = TEXTO_EJEMPLO


def _leer_meta_si_existe():
    try:
        return leer_meta(ARCHIVO_META)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as e:
        st.error(f"No se pudo leer models/{ARCHIVO_META}: {e}")
        return None


def _resumir(meta):
    st.write("Pega un texto en español o sube un `.txt`. El resumen es una ayuda para leer más rápido; **no reemplaza leer el documento**.")
    c1, c2 = st.columns([3, 1])
    with c2:
        st.button("Usar un texto de ejemplo", on_click=_cargar_ejemplo, help="Texto escrito para el proyecto sobre gestión de residuos.")
        archivo = st.file_uploader("…o sube un .txt (máx. 1 MB)", type=["txt"], help="Streamlit muestra su límite general de 200 MB, pero este módulo solo acepta archivos de hasta 1 MB.")
    texto_subido = ""
    if archivo is not None:
        if archivo.size > MAX_BYTES_ARCHIVO:
            st.error(f"El archivo pesa más de {MAX_BYTES_ARCHIVO // 1_000_000} MB.")
        else:
            texto_subido = leer_texto_subido(archivo.getvalue())
    with c1:
        pegado = st.text_area("Texto a resumir", key="texto_entrada", height=260, placeholder="Pega aquí el texto…")
    texto = texto_subido or pegado
    if texto_subido and pegado.strip():
        st.caption("Se usa el archivo subido; quita el archivo para usar el texto pegado.")

    faltan = librerias_faltantes()
    opciones = ["Extractivo (TextRank): copia las oraciones más importantes"]
    if not faltan:
        opciones.append("Abstractivo (mT5 XL-Sum): reescribe con un modelo")
    metodo = st.radio("Método", opciones, horizontal=False)
    es_abstractivo = metodo.startswith("Abstractivo")
    if faltan:
        st.caption("El método abstractivo es opcional y no está disponible porque faltan: " + ", ".join(faltan)
                   + ". Se instala con `pip install -r requirements-abstractivo.txt` (ver el manual de instalación).")
    if es_abstractivo:
        st.warning("El modelo puede **inventar o alterar datos** (nombres, cifras, quién hizo qué). Compáralo siempre con el original. "
                   "Primera vez: descarga de unos 2.3 GB. Medido en un PC de 4 núcleos sin GPU: unos 15 s para un texto de ≈ 260 palabras "
                   "(el primero, ≈ 30 s más por el calentamiento), ≈ 77 s para ≈ 1 300 palabras y hasta ≈ 2.5 GB de memoria. "
                   "En una GPU de Colab fueron unos 0.4 s por artículo.")
        n_oraciones = None
    else:
        n_oraciones = st.slider("Oraciones del resumen", 1, 8, 3)

    if not st.button("Resumir", type="primary"):
        return
    ok, motivo = texto_valido(texto)
    if not ok:
        st.warning(motivo)
        return
    inicio, t_carga = time.perf_counter(), 0.0
    if es_abstractivo:
        try:
            t0 = time.perf_counter()
            tok, modelo, dispositivo = _cargar_abstractivo((meta or {}).get("abstractivo", {}).get("modelo_hub", {}).get("id") or MODELO_ID,
                                                           (meta or {}).get("abstractivo", {}).get("modelo_hub", {}).get("sha") or REVISION)
        except Exception as e:  # noqa: BLE001 (sin internet, sin memoria, etc.)
            st.error(f"No se pudo cargar el modelo abstractivo: {e}. Prueba con el método extractivo.")
            return
        t_carga = time.perf_counter() - t0
        inicio = time.perf_counter()   # el tiempo de resumen NO incluye la descarga ni la carga del modelo
        previstos, _ = bloques_para_abstractivo(texto)
        estimado = estimar_segundos_cpu(len(previstos))
        if dispositivo == "cpu" and estimado > 30:
            st.info(f"Sin GPU, este texto ({len(previstos)} bloques) tardaría unos {estimado / 60:.1f} min (estimación extrapolada de una medición; tu equipo puede ser distinto).")
        with st.spinner(f"Generando el resumen ({dispositivo})…"):
            resumen, info = resumen_abstractivo(tok, modelo, dispositivo, texto)
        if info["recortado"]:
            st.warning(f"El texto es largo: solo se resumieron los primeros {info['bloques']} bloques (≈ {info['bloques'] * PALABRAS_BLOQUE_ABSTRACTIVO} palabras).")
        if info["bloques_truncados"]:
            st.warning(f"{info['bloques_truncados']} bloque(s) superan los {MAX_ENTRADA_TOKENS} tokens del modelo y se recortaron: parte del texto no se leyó.")
        if info["bloques"] > 1:
            st.caption("Para textos largos se resume por bloques y luego se resumen los resúmenes; este procedimiento **no se evaluó con ROUGE**.")
    else:
        resumen, reducido = resumen_extractivo(texto, n_oraciones)
        dispositivo = "CPU"
        if reducido:
            st.caption("El texto es muy largo: primero se tomó una oración por bloque y luego se aplicó TextRank. Este procedimiento no se evaluó con ROUGE.")
    segundos = time.perf_counter() - inicio

    st.subheader("Resumen")
    st.write(resumen)
    m = st.columns(3)
    m[0].metric("Palabras del original", f"{tx.contar_palabras(texto):,}")
    m[1].metric("Palabras del resumen", f"{tx.contar_palabras(resumen):,}")
    m[2].metric("Tiempo de resumen", f"{segundos:.1f} s")
    if t_carga > 2:
        st.caption(f"Carga del modelo: {t_carga:.0f} s (la primera vez incluye la descarga; después queda en memoria y no se repite). No está sumada arriba.")
    if es_abstractivo:
        raros = tx.datos_no_respaldados(resumen, texto)
        if raros:
            st.warning("Cifras o nombres del resumen que **no aparecen en el texto original**: " + ", ".join(raros)
                       + ". Es una pista, no una verificación: puede marcar de más, y no detecta errores en palabras comunes.")
        else:
            st.caption("Todas las cifras y nombres del resumen aparecen en el texto original (esto no garantiza que el resumen sea fiel).")


def _evaluacion(meta):
    if meta is None:
        st.info(f"Aún no está `models/{ARCHIVO_META}`: se genera al ejecutar `notebooks/05_resumen.ipynb`. El resumen de la otra pestaña funciona sin él.")
        return
    st.caption(f"Ganador por la regla fijada: {meta.get('modelo', 's/n')} · Fecha: {meta.get('fecha', 's/f')} · Datos: {meta.get('dataset', 's/d')}")
    st.write(f"**Regla:** {meta.get('regla_seleccion', 's/d')}.")
    tabla = tabla_evaluacion(meta)
    if tabla.empty:
        st.info("El meta no trae la tabla de evaluación.")
        return
    cols = {"fuente": "Fuente", "metodo": "Método", "n": "Artículos", "rouge1": "ROUGE-1", "rouge2": "ROUGE-2", "rougeL": "ROUGE-L",
            "rougeL_desv": "Desv. ROUGE-L", "palabras_hip": "Palabras del resumen", "ratio": "Ratio de compresión", "seg_por_doc": "Segundos por texto"}
    st.dataframe(tabla[list(cols)].rename(columns=cols).round(4), hide_index=True)
    st.plotly_chart(figura_comparacion(tabla))
    st.subheader("¿Qué tan seguras son las diferencias?")
    for frase in frases_bootstrap(meta):
        st.write("• " + frase)
    st.caption("Intervalos por bootstrap pareado sobre los mismos artículos. Una diferencia cuyo intervalo incluye 0 no permite decir que un método sea mejor.")
    with st.expander("Límites de esta evaluación"):
        st.write(meta.get("notas", ""))
        st.write("• Las referencias son resúmenes de una sola frase, por eso los ROUGE son bajos para todos los métodos; compáralos entre sí, no con otros trabajos.")
        st.write("• Las longitudes difieren mucho entre métodos y ROUGE (F1) depende de la longitud.")
        st.write("• Se evaluó con noticias (BBC y El País), no con normas ni documentos técnicos de residuos.")
        st.write("• El modelo abstractivo se entrenó con XL-Sum: la fuente XL-Sum le favorece y MLSUM es la comparación más justa.")
        st.write("• En una revisión manual de 6 ejemplos, el abstractivo contradijo el texto en 2, afirmó cosas que el texto impreso no respalda en otros 2 y copió la primera oración en 2 (ver REGISTRO 5 del proyecto).")


def render():
    st.header("📝 Resumen de texto")
    meta = _leer_meta_si_existe()
    try:
        pestanas = st.tabs(["Resumir un texto", "Evaluación y límites"])
        with pestanas[0]:
            _resumir(meta)
        with pestanas[1]:
            _evaluacion(meta)
        with st.expander("Aviso de uso responsable y fuentes"):
            st.write(config.AVISO_USO)
            st.write("No pegues textos con datos personales: el texto se procesa en el equipo donde corre la app y no se guarda. "
                     "TextRank: Mihalcea y Tarau (2004), implementación propia. Modelo abstractivo: `csebuetnlp/mT5_multilingual_XLSum` (licencia "
                     "`cc-by-nc-sa-4.0` según su ficha; uso no comercial). Evaluación con XL-Sum (Hasan et al., 2021) y MLSUM (Scialom et al., 2020); "
                     "ROUGE (Lin, 2004). Los textos de esos conjuntos no se redistribuyen.")
    except Exception as e:  # noqa: BLE001
        st.error(f"El módulo de resumen falló: {e}")
        with st.expander("Detalle técnico del error"):
            st.code(traceback.format_exc())
