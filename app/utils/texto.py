"""Utilidades de texto del módulo 5 (resumen): oraciones, Lead-n, TextRank, bloques y ROUGE.
Solo usa la biblioteca estándar y numpy (sin descargas). Las usan el notebook 05 y la app."""
import math
import re
import unicodedata
from collections import Counter

import numpy as np

# Prefijos de palabras (sin tildes) de «residuos»; igual que PALABRAS_RESIDUOS de src/preparar_textos.py
PALABRAS_RESIDUOS = ["residuo", "basura", "basurero", "botadero", "reciclaj", "reciclar", "plastico",
                     "vertedero", "relleno sanitario", "desecho", "compostaje"]
_RE_RESIDUOS = re.compile(r"\b(" + "|".join(PALABRAS_RESIDUOS) + ")")

# Palabras vacías frecuentes del español (sin tildes) para TextRank; lista propia y breve
_VACIAS = set("""de la que el en y a los del se las por un para con no una su al lo como mas pero sus le ya o este
si porque esta entre cuando muy sin sobre tambien me hasta hay donde quien desde todo nos durante todos uno les ni
contra otros ese eso ante ellos e esto mi antes algunos unos yo otro otras otra tanto esa estos mucho quienes nada
muchos cual poco ella estar estas algunas algo nosotros es son ha han fue ser sido era segun asi tras""".split())

# Fin de oración: signo final (con cierre opcional) + espacio + inicio de otra oración (mayúscula, número, ¿ ¡, comillas)
_RE_ORACION = re.compile(r'(?:(?<=[.!?…])|(?<=[.!?…]["»”’)\]]))\s+(?=[¿¡"«“‘(\[]?[A-ZÁÉÍÓÚÜÑ0-9])')
_RE_ABREV = re.compile(r"\b(?:Sr|Sra|Srta|Dr|Dra|Ud|Uds|Av|Lic|Ing|Prof|Gral|Sta|Sto|pág|núm|EE)\.$", re.IGNORECASE)
_RE_INICIAL = re.compile(r"\b[A-ZÁÉÍÓÚÑ]\.$")


def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


def normalizar_espacios(texto):
    """Quita saltos de línea sueltos y espacios repetidos (conserva los párrafos como un solo espacio)."""
    return re.sub(r"\s+", " ", str(texto)).strip()


def dividir_oraciones(texto):
    """Separa en oraciones con una heurística (no usa NLTK). Une cortes tras abreviaturas e iniciales."""
    oraciones = []
    for parrafo in re.split(r"\n\s*\n", str(texto)):
        parrafo = normalizar_espacios(parrafo)
        if not parrafo:
            continue
        piezas = _RE_ORACION.split(parrafo)
        actual = ""
        for p in piezas:
            actual = f"{actual} {p}".strip() if actual else p
            if _RE_ABREV.search(actual) or _RE_INICIAL.search(actual):
                continue  # el corte fue tras una abreviatura: se une con la pieza siguiente
            oraciones.append(actual)
            actual = ""
        if actual:
            oraciones.append(actual)
    return oraciones


def contar_palabras(texto):
    return len(str(texto).split())


def ratio_compresion(resumen, original):
    """Palabras del resumen ÷ palabras del original (0 si el original está vacío)."""
    n = contar_palabras(original)
    return contar_palabras(resumen) / n if n else 0.0


def contar_palabras_residuos(texto):
    """Cuántas veces aparece alguna palabra clave de residuos (sin distinguir tildes ni mayúsculas)."""
    return len(_RE_RESIDUOS.findall(sin_tildes(str(texto))))


def datos_no_respaldados(resumen, original):
    """Cifras y palabras con mayúscula del resumen que NO aparecen en el original (sin distinguir tildes ni mayúsculas).
    Es una pista de posibles datos inventados por un modelo abstractivo, no una verificación: puede marcar de más
    (p. ej. «EE. UU.» frente a «Estados Unidos») y no detecta errores en palabras comunes."""
    base = set(re.findall(r"[^\W_]+", sin_tildes(str(original))))
    marcadas, vistas = [], set()
    for m in re.finditer(r"[^\W_]+", str(resumen)):
        w = m.group(0)
        k = sin_tildes(w)
        if not (w[0].isdigit() or w[0].isupper()) or k in base or k in vistas or k in _VACIAS:
            continue
        vistas.add(k)
        marcadas.append(w)
    return marcadas


# ---------- Extractivos ----------
def lead_n(texto, n=3):
    """Lead-n: las primeras n oraciones (baseline fuerte en noticias)."""
    return " ".join(dividir_oraciones(texto)[:n])


def _tokens_textrank(oracion):
    return [w for w in re.findall(r"[^\W\d_]{3,}", sin_tildes(oracion)) if w not in _VACIAS]


def puntajes_textrank(oraciones, amortiguacion=0.85, iteraciones=100, tolerancia=1e-6):
    """PageRank sobre el grafo de oraciones; similitud = palabras comunes / (log|Si| + log|Sj|) (Mihalcea y Tarau, 2004).
    Requiere al menos 2 palabras útiles por oración para tener similitud; las demás quedan sin aristas."""
    n = len(oraciones)
    if n == 0:
        return np.array([])
    conj = [set(_tokens_textrank(o)) for o in oraciones]
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if len(conj[i]) >= 2 and len(conj[j]) >= 2:
                comunes = len(conj[i] & conj[j])
                if comunes:
                    W[i, j] = W[j, i] = comunes / (math.log(len(conj[i])) + math.log(len(conj[j])))
    suma = W.sum(axis=1)
    P = np.where(suma[:, None] > 0, W / np.where(suma[:, None] > 0, suma[:, None], 1), 1.0 / n)  # sin aristas: salto uniforme
    r = np.full(n, 1.0 / n)
    for _ in range(iteraciones):
        nuevo = (1 - amortiguacion) / n + amortiguacion * (P.T @ r)
        if np.abs(nuevo - r).sum() < tolerancia:
            r = nuevo
            break
        r = nuevo
    return r


def textrank(texto, n=3):
    """TextRank extractivo: las n oraciones de mayor puntaje, en el orden original del texto."""
    oraciones = dividir_oraciones(texto)
    if len(oraciones) <= n:
        return " ".join(oraciones)
    p = puntajes_textrank(oraciones)
    elegidas = sorted(sorted(range(len(oraciones)), key=lambda i: (-p[i], i))[:n])
    return " ".join(oraciones[i] for i in elegidas)


# ---------- Textos largos ----------
def dividir_en_bloques(texto, palabras=450):
    """Agrupa oraciones consecutivas en bloques de unas `palabras` palabras (una oración enorme se parte por palabras)."""
    bloques, actual, n_act = [], [], 0
    for o in dividir_oraciones(texto):
        trozos = [o]
        if contar_palabras(o) > 2 * palabras:
            w = o.split()
            trozos = [" ".join(w[i:i + palabras]) for i in range(0, len(w), palabras)]
        for t in trozos:
            nt = contar_palabras(t)
            if actual and n_act + nt > palabras:
                bloques.append(" ".join(actual))
                actual, n_act = [], 0
            actual.append(t)
            n_act += nt
    if actual:
        bloques.append(" ".join(actual))
    return bloques


def resumen_jerarquico(texto, resumir, palabras=450, max_niveles=3):
    """Resume por bloques y luego resume los resúmenes. `resumir` es una función texto -> resumen.
    Devuelve (resumen_final, niveles) con los resúmenes parciales de cada nivel. Si tras `max_niveles` aún hay
    más de un bloque, el último resumen puede recibir más texto del que el modelo admite (el modelo lo trunca)."""
    niveles, actual = [], str(texto)
    for _ in range(max_niveles):
        bloques = dividir_en_bloques(actual, palabras)
        if len(bloques) <= 1:
            break
        parciales = [resumir(b) for b in bloques]
        niveles.append(parciales)
        actual = " ".join(parciales)
    return resumir(actual), niveles


# ---------- ROUGE propio (F1) ----------
def tokenizar(texto):
    """Tokenizador para ROUGE en español: minúsculas y secuencias de letras/dígitos Unicode (conserva tildes y ñ)."""
    return re.findall(r"[^\W_]+", str(texto).lower())


def _f1(coinciden, n_hip, n_ref):
    if not coinciden or not n_hip or not n_ref:
        return 0.0
    p, r = coinciden / n_hip, coinciden / n_ref
    return 2 * p * r / (p + r)


def _rouge_n(ref, hip, n):
    cr = Counter(zip(*[ref[i:] for i in range(n)]))
    ch = Counter(zip(*[hip[i:] for i in range(n)]))
    return _f1(sum((cr & ch).values()), sum(ch.values()), sum(cr.values()))


def _lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        act = [0]
        for j, y in enumerate(b, 1):
            act.append(prev[j - 1] + 1 if x == y else max(prev[j], act[-1]))
        prev = act
    return prev[-1]


def rouge_f1(referencia, hipotesis):
    """ROUGE-1, ROUGE-2 y ROUGE-L (F1, entre 0 y 1) con `tokenizar`. ROUGE-L usa la subsecuencia común más larga."""
    ref, hip = tokenizar(referencia), tokenizar(hipotesis)
    return {"rouge1": _rouge_n(ref, hip, 1), "rouge2": _rouge_n(ref, hip, 2),
            "rougeL": _f1(_lcs(ref, hip), len(hip), len(ref))}
