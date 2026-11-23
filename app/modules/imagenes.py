"""Módulo de clasificación de imágenes de residuos. Carga el modelo ya entrenado (la app nunca entrena)."""
import html
import io
import json
import traceback

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageOps

import config
from app.estilos import intro
from app.utils.modelos import cargar_keras, leer_meta, ruta_modelo

ARCHIVO_MODELO = "clasificador_imagenes.keras"
ARCHIVO_CLASES = "clases_imagenes.json"
ARCHIVO_META = "imagenes_meta.json"
MAX_MB = 10


# ---------- Funciones puras (sin interfaz; las usan también el script de comprobación y las pruebas) ----------
def nombre_clase(clase):
    return config.NOMBRES_CLASES.get(clase, clase)


def leer_clases(meta):
    """Lee models/clases_imagenes.json y comprueba que coincida con las clases del meta (mismo orden)."""
    ruta = ruta_modelo(ARCHIVO_CLASES)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe models/{ARCHIVO_CLASES} (lo genera el notebook 03 en Colab).")
    clases = json.loads(ruta.read_text(encoding="utf-8"))
    if clases != meta.get("clases"):
        raise ValueError(f"{ARCHIVO_CLASES} no coincide con las clases de {ARCHIVO_META}; copia de nuevo los tres archivos de la misma ejecución.")
    return clases


def tam_entrada(meta):
    """(alto, ancho) de entrada del modelo, tomado del meta."""
    e = meta.get("features", {}).get("entrada", [224, 224, 3])
    return int(e[0]), int(e[1])


def abrir_imagen(datos):
    """Bytes -> imagen PIL RGB. Corrige la rotación EXIF de fotos de celular y pone un fondo blanco a las transparencias."""
    img = Image.open(io.BytesIO(datos))
    img.load()
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        fondo = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(fondo, rgba).convert("RGB")
    return img.convert("RGB")


def a_entrada(img, tam):
    """Imagen PIL -> lote (1, alto, ancho, 3) en píxeles 0-255. Redimensiona como en el entrenamiento
    (image_dataset_from_directory: tf.image.resize bilinear, sin recorte ni relleno); el escalado va dentro del modelo."""
    import tensorflow as tf
    x = tf.image.resize(np.asarray(img, dtype=np.uint8), tam, method="bilinear")
    return np.asarray(x, dtype="float32")[None, ...]


def predecir(modelo, img, tam):
    """Probabilidades por clase (en el orden de clases_imagenes.json)."""
    return np.asarray(modelo(a_entrada(img, tam), training=False))[0]


def top_k(probs, clases, k=3):
    idx = np.argsort(probs)[::-1][:k]
    return [(clases[i], float(probs[i])) for i in idx]


def clase_peligrosa(top):
    """Devuelve (clase, es_la_principal) si hay una clase peligrosa que merece aviso; si no, None."""
    for i, (c, p) in enumerate(top):
        if c in config.RESIDUOS_PELIGROSOS and (i == 0 or p >= config.UMBRAL_PELIGROSO_POSIBLE):
            return c, i == 0
    return None


def contenedor_de(clase, esquema_id):
    return config.CONTENEDORES[esquema_id]["clases"].get(clase)


def precision_recall(meta, clase):
    d = meta.get("por_clase_test", {}).get(clase)
    return (d["precision"], d["recall"], int(d["support"])) if d else None


def confundidas_con(meta, clase, k=2):
    """Clases reales cuyas imágenes de test el modelo predijo como `clase` (error), de mayor a menor."""
    clases = meta["clases"]
    m = np.array(meta["matriz_confusion_test"])
    j = clases.index(clase)
    col = [(int(m[i][j]), clases[i]) for i in range(len(clases)) if i != j and m[i][j] > 0]
    return sorted(col, reverse=True)[:k]


def _caja(hex_color, texto):
    """Recuadro de color (solo textos fijos de config, escapados)."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    txt = "#111" if 0.299 * r + 0.587 * g + 0.114 * b > 150 else "#fff"
    borde = "#9e9e9e" if hex_color.lower() == "#ffffff" else hex_color
    return (f'<div style="background:{hex_color};color:{txt};border:2px solid {borde};border-radius:8px;'
            f'padding:10px 14px;font-weight:600">{html.escape(texto)}</div>')


@st.cache_data(show_spinner=False)
def _probabilidades(datos, tam):
    """Cachea por foto: cambiar de esquema de contenedores no vuelve a clasificar."""
    return predecir(cargar_keras(ARCHIVO_MODELO), abrir_imagen(datos), tam)


# ---------- Interfaz ----------
def _clasificar(meta, clases):
    esquemas = config.CONTENEDORES
    ids = list(esquemas)
    pre = ids.index(config.ESQUEMA_PREDETERMINADO) if config.ESQUEMA_PREDETERMINADO in ids else 0
    esquema_id = st.selectbox("Esquema de colores de contenedores", ids, index=pre, format_func=lambda i: esquemas[i]["nombre"])
    st.caption(esquemas[esquema_id]["fuente"])
    st.info("Sube la foto de **un solo residuo**, con buena luz y sin personas, rostros ni datos personales visibles. "
            "La imagen se procesa en esta sesión y no se guarda.")
    archivo = st.file_uploader("Sube una foto (jpg o png)", type=["jpg", "jpeg", "png"])
    if archivo is None:
        st.caption("Aún no hay foto.")
        return
    if archivo.size > MAX_MB * 1024 * 1024:
        st.error(f"La imagen pesa más de {MAX_MB} MB. Sube una más liviana.")
        return
    datos = archivo.getvalue()
    try:
        img = abrir_imagen(datos)
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudo leer la imagen ({e}). Prueba con otro archivo jpg o png.")
        return
    try:
        with st.spinner("Clasificando…"):
            probs = _probabilidades(datos, tam_entrada(meta))
    except ImportError:
        st.error("Falta TensorFlow para clasificar imágenes. Ejecuta: pip install tensorflow (ver README si falla con tu versión de Python).")
        return
    top = top_k(probs, clases, 3)
    clase, p = top[0]
    baja = p < config.UMBRAL_CONFIANZA
    izq, der = st.columns(2)
    with izq:
        st.image(img, caption="Foto subida")
    with der:
        if baja:
            st.warning(f"Confianza baja: la mejor estimación es «{nombre_clase(clase)}» con {p:.0%}. No sugiero contenedor. "
                       "Prueba otra foto: un solo objeto, de frente, con buena luz y fondo simple.")
        else:
            st.subheader(nombre_clase(clase))
            st.metric("Confianza del modelo", f"{p:.1%}")
        for c, pr in top:
            st.progress(float(pr), text=f"{nombre_clase(c)}: {pr:.1%}")
        pel = clase_peligrosa(top)
        if pel:
            cp, principal = pel
            st.error(f"{'Residuo' if principal else 'Posible residuo'} peligroso ({nombre_clase(cp)}). No lo tires a la basura común ni lo "
                     "perfores o aplastes. Entrégalo en un punto de acopio autorizado.")
        if not baja:
            info = contenedor_de(clase, esquema_id)
            if info is None:
                st.info("Este esquema no define contenedor para esa clase.")
            else:
                st.markdown(_caja(info["hex"], f"Contenedor sugerido: {info['color'].capitalize()}, {info['contenedor']}"), unsafe_allow_html=True)
                if info["nota"]:
                    st.caption(info["nota"])
                st.caption("Esta sugerencia sale de " + ("la norma citada en el esquema." if info["origen"] == "norma" else "un criterio del proyecto, no de la norma."))
    with st.expander("¿Qué tan fiable es este resultado?"):
        st.write("El modelo siempre elige una de las 10 clases: si la imagen no es un residuo (o no se ve bien), igual dará una respuesta, a veces con confianza alta.")
        pr_r = precision_recall(meta, clase)
        if pr_r:
            st.write(f"En el test de DS3, cuando el modelo predijo «{nombre_clase(clase)}» acertó en el {pr_r[0]:.0%} de los casos y encontró "
                     f"el {pr_r[1]:.0%} de las imágenes reales de esa clase (n = {pr_r[2]}).")
        conf = confundidas_con(meta, clase)
        if conf:
            st.write("Cuando se equivocó diciendo «" + nombre_clase(clase) + "», las imágenes eran sobre todo de: "
                     + ", ".join(f"{nombre_clase(c)} ({n})" for n, c in conf) + ".")
        m = meta.get("metricas", {})
        if "accuracy_ds4" in m:
            st.write(f"Con fotos de otro origen (DS4, {meta['prueba_externa']['n_ds4']} imágenes y 6 clases) la exactitud bajó a "
                     f"{m['accuracy_ds4']:.0%}; con fotos tomadas por ti puede ser peor. Úsalo como ayuda, no como decisión final.")
        st.dataframe(pd.DataFrame({"Clase": [nombre_clase(c) for c in clases], "Probabilidad": [f"{x:.1%}" for x in probs]}), hide_index=True)


def _matriz(meta, clases):
    opciones = {"Test de DS3 (10 clases)": (meta["matriz_confusion_test"], clases)}
    ext = meta.get("prueba_externa", {})
    if ext.get("matriz_ds4"):
        opciones[f"DS4 (6 clases, n = {ext['n_ds4']})"] = (ext["matriz_ds4"], ext["clases_comunes"])
    eleccion = st.radio("Matriz de confusión", list(opciones), horizontal=True)
    m, nombres = opciones[eleccion]
    m = np.array(m)
    norm = m / np.maximum(m.sum(axis=1, keepdims=True), 1)
    etiquetas = [nombre_clase(c) for c in nombres]
    fig = go.Figure(go.Heatmap(z=norm, x=etiquetas, y=etiquetas, text=m, texttemplate="%{text}", colorscale="Blues", zmin=0, zmax=1,
                               colorbar=dict(title="Fracción de la fila")))
    fig.update_layout(xaxis_title="Predicho", yaxis_title="Real", yaxis_autorange="reversed", margin=dict(t=30, b=20))
    st.plotly_chart(fig)
    st.caption("Cada fila es la clase real; el color muestra qué fracción de esa fila se predijo en cada columna y el número es la cantidad.")


def _modelo(meta, clases):
    m, ext, lim = meta.get("metricas", {}), meta.get("prueba_externa", {}), meta.get("limpieza", {})
    st.caption(f"Modelo: {meta.get('modelo', 's/n')}. Fecha: {meta.get('fecha', 's/f')}. Datos: {meta.get('dataset', 's/d')}")
    c = st.columns(4)
    c[0].metric("Exactitud en test DS3 (10 clases)", f"{m.get('accuracy', float('nan')):.1%}")
    c[1].metric("Macro-F1 en test DS3", f"{m.get('macro_f1', float('nan')):.3f}")
    c[2].metric("Exactitud en DS4 (6 clases)", f"{m.get('accuracy_ds4', float('nan')):.1%}")
    c[3].metric("Macro-F1 en DS4", f"{m.get('macro_f1_ds4', float('nan')):.3f}")
    if "brecha_accuracy" in m:
        st.write(f"Con las mismas 6 clases, el test de DS3 da {m['accuracy_test_6clases']:.1%} de exactitud y DS4 {m['accuracy_ds4']:.1%}: una brecha de "
                 f"{m['brecha_accuracy']:.1%} (macro-F1: {m['brecha_macro_f1']:.3f}). Es la pérdida al pasar a fotos de otro origen.")
    st.subheader("Comparación de variantes")
    comp = pd.DataFrame(meta.get("comparacion_variantes", []))
    if not comp.empty:
        comp["ganador"] = comp["variante"] == meta.get("ganador")
        st.dataframe(comp.rename(columns={"variante": "Variante", "epocas": "Épocas", "segundos": "Segundos", "params_entrenables": "Parámetros entrenables",
                                          "val_accuracy": "Exactitud val", "val_macro_f1": "Macro-F1 val", "test_accuracy": "Exactitud test",
                                          "test_macro_f1": "Macro-F1 test", "ganador": "Elegida"}), hide_index=True)
        st.caption("Regla de elección fijada antes de entrenar: mayor macro-F1 de validación (el test no interviene). Una sola ejecución por variante.")
    st.subheader("Resultados por clase (test DS3)")
    por = meta.get("por_clase_test", {})
    st.dataframe(pd.DataFrame([{"Clase": nombre_clase(k), "Precisión": round(v["precision"], 3), "Recall": round(v["recall"], 3),
                                "F1": round(v["f1-score"], 3), "Imágenes": int(v["support"])} for k, v in por.items()]), hide_index=True)
    _matriz(meta, clases)
    with st.expander("Datos, limpieza y limitaciones"):
        d3, d4 = lim.get("ds3", {}), lim.get("ds4", {})
        st.write(f"DS3 (Garbage Classification V2, versión «original»): {d3.get('original')} imágenes; se quitaron {d3.get('duplicados_eliminados')} duplicadas y "
                 f"{d3.get('conflicto_etiqueta_eliminadas')} con etiquetas en conflicto. Partición {meta.get('n_entrenamiento')} / {meta.get('n_validacion')} / {meta.get('n_prueba')} "
                 "(entrenamiento / validación / prueba).")
        por4 = ext.get("ds4_por_clase", {})
        st.write(f"DS4 (TrashNet): {d4.get('original')} imágenes; {d4.get('solapadas_con_ds3_excluidas')} coinciden con DS3 y se excluyeron, así que la prueba externa "
                 f"tiene solo {ext.get('n_ds4')} imágenes ("
                 + ", ".join(f"{k}: {int(v['support'])}" for k, v in por4.items()) + "). Las métricas de clases con pocas imágenes son poco fiables.")
        st.write(meta.get("notas", ""))


def render():
    intro("Clasificación de imágenes de residuos",
          "Sube la foto de un residuo y el modelo estima de qué tipo es y a qué contenedor iría. Es una ayuda orientativa, no una decisión final.")
    try:
        meta = leer_meta(ARCHIVO_META)
        clases = leer_clases(meta)
        if not ruta_modelo(ARCHIVO_MODELO).exists():
            raise FileNotFoundError(f"No existe models/{ARCHIVO_MODELO}.")
    except FileNotFoundError as e:
        st.info(f"Este módulo aún no tiene modelo entrenado. {e}")
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudieron leer los archivos del modelo: {e}")
        return
    try:
        pestanas = st.tabs(["Clasificar una foto", "Modelo y métricas"])
        with pestanas[0]:
            _clasificar(meta, clases)
        with pestanas[1]:
            _modelo(meta, clases)
        with st.expander("Fuentes de datos y limitaciones"):
            st.write("Entrenado con DS3 (Kaggle, *Garbage Classification V2*, `sumn2u/garbage-classification-v2`) y probado también con DS4 (TrashNet, "
                     "repositorio `garythung/trashnet`; copia en Kaggle `feyzazkefe/trashnet`). Las imágenes no se redistribuyen: consulta la licencia de "
                     "cada una en su página. Los colores de contenedor del esquema del proyecto son una convención propia; los de Perú resumen la NTP 900.058:2019 "
                     "y deben contrastarse con el texto oficial.")
    except Exception as e:  # noqa: BLE001
        st.error(f"El módulo de imágenes falló: {e}")
        with st.expander("Detalle técnico del error"):
            st.code(traceback.format_exc())
