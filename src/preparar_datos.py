"""Descarga, verificación (V1-V4 de C3) y limpieza de DS1 (What a Waste) y DS2 (DSNY).
Uso, desde la raíz:  python src/preparar_datos.py <descargar|verificar|preparar|todo> [--forzar]
Fuentes: Banco Mundial (What a Waste, CC-BY-4.0) y NYC Open Data / DSNY (Monthly Tonnage)."""
import argparse
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import config  # noqa: E402

# ---------- Parámetros editables ----------
DS1_URLS = [
    "https://datacatalogfiles.worldbank.org/ddh-published/0039597/DR0049199/country_level_data.csv",
    "https://development-data-hub-s3-public.s3.amazonaws.com/ddhfiles/140602/country_level_data_0.csv",
]
DS2_URLS = ["https://data.cityofnewyork.us/api/v3/views/ebb7-mvp5/export.csv?accessType=DOWNLOAD"]
RAW_DS1 = config.DATA_RAW / "wab" / "country_level_data.csv"
RAW_DS2 = config.DATA_RAW / "dsny" / "dsny_monthly_tonnage.csv"
VERIF_TXT = config.DATA_PROCESSED / "verificacion_ds1_ds2.txt"
LOG_TXT = config.DATA_PROCESSED / "log_preparacion.txt"

UNIDAD_DS2 = "ton_mes"  # cambiar a "ton_dia" solo si la verificación (V3) lo indica
# Subcadenas (en minúsculas, sin símbolos) con que se detectan las columnas de DS2 [VERIFICAR con V3]
SUBCADENAS_MATERIAL = {"refuse": ["refuse"], "paper": ["paper"], "mgp": ["mgp"], "organics": ["organic"]}
EXCLUIR_EN_MATERIAL = ["diversion", "rate", "percent", "capture"]
# Eventos documentados en C3/M2 (el fin de COVID es PROVISIONAL: se define con el EDA)
COVID_INICIO, COVID_FIN = "2020-03-01", "2021-12-01"
ORG_SUSPENDE, ORG_REANUDA = "2020-05-01", "2021-10-01"
TEXTO_DS1 = ["iso3c", "pais", "region_id", "income_id"]
CLAVES_DS1 = ["iso3c", "pais", "poblacion", "residuos_total_ton_anio"]
MAPA_DS1 = {
    "country_name": "pais",
    "population_population_number_of_people": "poblacion",
    "total_msw_total_msw_generated_tons_year": "residuos_total_ton_anio",
}


# ---------- Utilidades ----------
def leer_csv(ruta):
    """Lee un CSV probando codificaciones comunes."""
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(ruta, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo leer {ruta} con utf-8 ni latin-1")


def clave(nombre):
    return re.sub(r"[^a-z0-9]", "", str(nombre).lower())


def descargar_uno(urls, destino, forzar):
    if destino.exists() and destino.stat().st_size > 1000 and not forzar:
        return f"OK (ya existía) {destino.relative_to(RAIZ)}"
    destino.parent.mkdir(parents=True, exist_ok=True)
    errores = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EcoCiudad-IA, uso academico)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                datos = r.read()
            if len(datos) < 1000 or datos.lstrip()[:1] == b"<":
                raise ValueError("la respuesta no parece un CSV (¿HTML o pide credenciales?)")
            destino.write_bytes(datos)
            return f"OK descargado {destino.relative_to(RAIZ)} ({len(datos)/1e6:.2f} MB) desde {url}"
        except Exception as e:  # noqa: BLE001
            errores.append(f"{url} -> {type(e).__name__}: {e}")
    return ("FALLÓ la descarga automática:\n    " + "\n    ".join(errores)
            + f"\n    Descarga el CSV a mano desde el navegador y guárdalo como {destino.relative_to(RAIZ)}")


def descargar(forzar=False):
    print("DS1:", descargar_uno(DS1_URLS, RAW_DS1, forzar))
    print("DS2:", descargar_uno(DS2_URLS, RAW_DS2, forzar))


# ---------- DS1 ----------
def renombrar_ds1(df):
    """Renombra columnas de What a Waste a nombres cortos sin tildes (mapa registrado en ESTRUCTURA)."""
    nuevo = {}
    for c in df.columns:
        base = c[:-8] + "_pct" if c.endswith("_percent") else c
        if c in MAPA_DS1:
            nuevo[c] = MAPA_DS1[c]
        elif c.startswith("composition_"):
            nuevo[c] = "comp_" + base[len("composition_"):]
        elif c.startswith("waste_treatment_"):
            nuevo[c] = "trat_" + base[len("waste_treatment_"):]
        elif c.startswith("waste_collection_coverage_"):
            nuevo[c] = "cobertura_" + base[len("waste_collection_coverage_"):]
        elif c.startswith("special_waste_"):
            nuevo[c] = "especial_" + base[len("special_waste_"):]
        else:
            nuevo[c] = c
    if len(set(nuevo.values())) != len(nuevo):  # colisión: se conservan los nombres originales
        return df, {}
    return df.rename(columns=nuevo), nuevo


def preparar_ds1(log):
    df, mapa = renombrar_ds1(leer_csv(RAW_DS1))
    log.append(f"DS1: {df.shape[0]} filas x {df.shape[1]} columnas leídas; {sum(k != v for k, v in mapa.items())} columnas renombradas")
    faltan = [c for c in CLAVES_DS1 if c not in df.columns]
    if faltan:
        raise SystemExit(f"DS1: faltan columnas clave {faltan}. Columnas reales: {list(df.columns)}\n"
                         "Pásame esta lista con «Ajustar: ...» para corregir MAPA_DS1.")
    n_sin_iso = int(df["iso3c"].isna().sum())
    df = df.dropna(subset=["iso3c"])
    n_dup = int(df.duplicated("iso3c").sum())
    df = df.drop_duplicates("iso3c", keep="first")
    log.append(f"DS1: filas eliminadas sin iso3c = {n_sin_iso}; duplicadas por iso3c = {n_dup}")
    for c in df.columns:  # numéricas: convertir lo que venga como texto
        if c not in TEXTO_DS1 and df[c].dtype == object:
            antes = df[c].notna().sum()
            df[c] = pd.to_numeric(df[c], errors="coerce")
            perdidos = int(antes - df[c].notna().sum())
            if perdidos:
                log.append(f"DS1: {c}: {perdidos} valores no numéricos pasados a vacío")
    ok = (df["poblacion"] > 0) & df["residuos_total_ton_anio"].notna() & (df["residuos_total_ton_anio"] >= 0)
    df["gpc_kg_hab_dia"] = np.where(ok, df["residuos_total_ton_anio"] * 1000 / 365 / df["poblacion"], np.nan)
    log.append(f"DS1: gpc_kg_hab_dia derivada = ton_anio*1000/365/población; calculable en {int(ok.sum())} de {len(df)} países")
    primeras = [c for c in ["iso3c", "pais", "region_id", "income_id", "gdp", "poblacion",
                            "residuos_total_ton_anio", "gpc_kg_hab_dia"] if c in df.columns]
    df = df[primeras + [c for c in df.columns if c not in primeras]]
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["paises"], index=False)
    log.append(f"DS1: guardado {config.ARCHIVOS_PROCESADOS['paises']} ({df.shape[0]} filas x {df.shape[1]} columnas)")


# ---------- DS2 ----------
def detectar_ds2(df):
    """Detecta columnas de fecha, borough, distrito y materiales por subcadenas de sus nombres."""
    claves = {c: clave(c) for c in df.columns}
    def primera(*subs):
        for c, k in claves.items():
            if any(s in k for s in subs):
                return c
        return None
    det = {"fecha": primera("month", "date"), "borough": primera("borough"),
           "distrito": primera("communitydistrict", "district")}
    det["materiales"] = {
        m: [c for c, k in claves.items() if any(s in k for s in subs) and not any(x in k for x in EXCLUIR_EN_MATERIAL)]
        for m, subs in SUBCADENAS_MATERIAL.items()
    }
    return det


def parsear_fecha(serie):
    """Devuelve el primer día del mes; acepta 'AAAA / MM' y formatos que pandas reconozca."""
    t = serie.astype(str).str.strip()
    m = t.str.extract(r"^(\d{4})\D+(\d{1,2})")
    f = pd.to_datetime(m[0] + "-" + m[1].str.zfill(2) + "-01", errors="coerce")
    if f.notna().mean() < 0.9:
        f = pd.to_datetime(t, errors="coerce").dt.to_period("M").dt.to_timestamp()
    return f


def a_numero(serie):
    return pd.to_numeric(serie.astype(str).str.replace(",", "", regex=False), errors="coerce")


def ds2_largo(df, det, log):
    if not det["fecha"] or not any(det["materiales"].values()):
        raise SystemExit(f"DS2: no se detectaron columnas. Detección: {det}. Columnas reales: {list(df.columns)}\n"
                         "Pásame esta lista con «Ajustar: ...» para corregir las subcadenas.")
    fecha = parsear_fecha(df[det["fecha"]])
    log.append(f"DS2: fechas interpretables = {fecha.notna().mean()*100:.1f}% (columna «{det['fecha']}»)")
    borough = df[det["borough"]].astype(str).str.strip() if det["borough"] else pd.Series("NA", index=df.index)
    if det["distrito"]:
        d = df[det["distrito"]].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        distrito = np.where(d.str.match(r"^[A-Za-z]"), d, borough + "-" + d.str.zfill(2))
    else:
        distrito = borough
    piezas = []
    for mat, cols in det["materiales"].items():
        if not cols:
            continue
        ton = pd.concat([a_numero(df[c]) for c in cols], axis=1).sum(axis=1, min_count=1)
        piezas.append(pd.DataFrame({"fecha": fecha, "distrito": distrito, "borough": borough,
                                    "material": mat, "toneladas": ton}))
        log.append(f"DS2: material {mat} = suma de {cols}")
    largo = pd.concat(piezas, ignore_index=True)
    n0 = len(largo)
    largo = largo.dropna(subset=["fecha", "toneladas"])
    log.append(f"DS2: filas eliminadas por fecha o toneladas vacías = {n0 - len(largo)} de {n0}")
    n_dup = int(largo.duplicated(["fecha", "distrito", "material"]).sum())
    if n_dup:
        largo = largo.groupby(["fecha", "distrito", "borough", "material"], as_index=False)["toneladas"].sum()
        log.append(f"DS2: {n_dup} filas repetidas (fecha, distrito, material) agregadas por suma")
    if UNIDAD_DS2 == "ton_dia":
        largo["toneladas"] = largo["toneladas"] * largo["fecha"].dt.days_in_month
        log.append("DS2: conversión aplicada toneladas/día -> toneladas/mes (UNIDAD_DS2 = ton_dia)")
    return largo.sort_values(["fecha", "distrito", "material"]).reset_index(drop=True)


def _desde_sostenida(indice, ok):
    """Texto con el primer mes desde el cual la condición `ok` se cumple hasta el final."""
    malos = indice[~np.asarray(ok)]
    if len(malos) == 0:
        return f"completa en todos los meses ({indice.min():%Y-%m} a {indice.max():%Y-%m})"
    desde = malos.max() + pd.offsets.MonthBegin(1)
    if desde > indice.max():
        return "no se mantiene hasta el último mes"
    return f"sostenida desde {desde:%Y-%m} ({len(malos)} meses incompletos antes o durante)"


def serie_ciudad(largo, log):
    s = largo.pivot_table(index="fecha", columns="material", values="toneladas", aggfunc="sum")
    nd = largo.groupby("fecha")["distrito"].nunique()
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="MS"))
    s.index.name = "fecha"
    huecos = int(s.isna().all(axis=1).sum())
    log.append(f"DS2: serie de ciudad {s.index.min():%Y-%m} a {s.index.max():%Y-%m}; meses sin datos = {huecos}")
    s["n_distritos"] = nd.reindex(s.index)
    max_d = int(s["n_distritos"].max())
    s["cobertura_completa"] = (s["n_distritos"] == max_d).astype(int)  # 1 = mes con el máximo de distritos
    log.append(f"DS2: cobertura máxima = {max_d} distritos; {_desde_sostenida(s.index, s['cobertura_completa'] == 1)}")
    for mat in largo["material"].unique():  # cobertura por material (el total solo es comparable con cobertura completa)
        ndm = largo[largo["material"] == mat].groupby("fecha")["distrito"].nunique().reindex(s.index)
        mdm = int(ndm.max())
        log.append(f"DS2: {mat}: máximo de distritos con dato = {mdm}; {_desde_sostenida(s.index, ndm.fillna(0) >= mdm)}")
    s["dias_mes"] = s.index.days_in_month
    idx = s.index
    s["covid"] = ((idx >= COVID_INICIO) & (idx <= COVID_FIN)).astype(int)
    s["organicos_programa"] = (~((idx >= ORG_SUSPENDE) & (idx < ORG_REANUDA))).astype(int)
    log.append(f"DS2: covid=1 de {COVID_INICIO} a {COVID_FIN} (fin PROVISIONAL); organicos_programa=0 de {ORG_SUSPENDE} a antes de {ORG_REANUDA}")
    if s["n_distritos"].nunique() > 1:
        log.append(f"DS2: AVISO n_distritos por mes varía entre {int(s['n_distritos'].min())} y {int(s['n_distritos'].max())} (revisar antes de sumar)")
    return s.reset_index()


def preparar_ds2(log):
    df = leer_csv(RAW_DS2)
    log.append(f"DS2: {df.shape[0]} filas x {df.shape[1]} columnas leídas")
    det = detectar_ds2(df)
    largo = ds2_largo(df, det, log)
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    largo.to_csv(config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["dsny_distritos"], index=False)
    log.append(f"DS2: guardado {config.ARCHIVOS_PROCESADOS['dsny_distritos']} ({len(largo)} filas)")
    serie_ciudad(largo, log).to_csv(config.DATA_PROCESSED / config.ARCHIVOS_PROCESADOS["serie_ciudad"], index=False)
    log.append(f"DS2: guardado {config.ARCHIVOS_PROCESADOS['serie_ciudad']}")


def preparar():
    log = []
    for nombre, ruta, fn in (("DS1", RAW_DS1, preparar_ds1), ("DS2", RAW_DS2, preparar_ds2)):
        if not ruta.exists():
            log.append(f"{nombre}: NO existe {ruta.relative_to(RAIZ)}; ejecuta «descargar» o colócalo a mano")
            continue
        fn(log)
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    LOG_TXT.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


# ---------- Verificación V1-V4 ----------
def verificar():
    L = []
    L.append("=== V4: archivos descargados ===")
    for n, r in (("DS1", RAW_DS1), ("DS2", RAW_DS2)):
        L.append(f"{n}: {'existe, %.2f MB' % (r.stat().st_size/1e6) if r.exists() else 'NO existe'} ({r.relative_to(RAIZ)})")
    if RAW_DS1.exists():
        df = leer_csv(RAW_DS1)
        L += ["", "=== DS1 (V1, V2) ===", f"shape: {df.shape}", "columnas: " + ", ".join(map(str, df.columns))]
        vac = (df.isna().mean() * 100).sort_values(ascending=False)
        L.append("vacíos % (12 peores): " + "; ".join(f"{c}={v:.0f}" for c, v in vac.head(12).items()))
        L.append("columnas con 'capita': " + (", ".join(c for c in df.columns if "capita" in str(c).lower()) or "ninguna"))
        L.append("columnas con year/source/ref/date: " + (", ".join(c for c in df.columns if re.search(r"year|source|ref|date", str(c).lower())) or "ninguna"))
        if "iso3c" in df.columns:
            L.append(f"iso3c únicos = {df['iso3c'].nunique()}, duplicados = {int(df.duplicated('iso3c').sum())}, vacíos = {int(df['iso3c'].isna().sum())}")
        claves_ver = [c for c in ["iso3c", "country_name", "income_id", "gdp", "population_population_number_of_people",
                                  "total_msw_total_msw_generated_tons_year"] if c in df.columns]
        L.append("head(3) columnas clave:\n" + df[claves_ver].head(3).to_string())
    if RAW_DS2.exists():
        df = leer_csv(RAW_DS2)
        det = detectar_ds2(df)
        L += ["", "=== DS2 (V3) ===", f"shape: {df.shape}", "columnas: " + ", ".join(map(str, df.columns)),
              f"detección: fecha={det['fecha']}, borough={det['borough']}, distrito={det['distrito']}",
              f"materiales detectados: {det['materiales']}"]
        if det["fecha"]:
            L.append(f"muestra de fecha cruda: {df[det['fecha']].head(3).tolist()}")
            f = parsear_fecha(df[det["fecha"]])
            L.append(f"fechas interpretables: {f.notna().mean()*100:.1f}%; rango {f.min():%Y-%m} a {f.max():%Y-%m}")
            faltan = pd.date_range(f.min(), f.max(), freq="MS").difference(pd.DatetimeIndex(f.dropna().unique()))
            L.append(f"meses sin ninguna fila: {len(faltan)} " + (f"(primeros: {[d.strftime('%Y-%m') for d in faltan[:5]]})" if len(faltan) else ""))
            por_mes = df.groupby(f).size()
            L.append(f"filas por mes: mín={por_mes.min()}, máx={por_mes.max()}")
        if det["distrito"]:
            L.append(f"distritos únicos ({det['distrito']}): {df[det['distrito']].nunique()}; muestra: {df[det['distrito']].dropna().unique()[:6].tolist()}")
        if det["fecha"] and det["materiales"]["refuse"]:
            ref = pd.concat([a_numero(df[c]) for c in det["materiales"]["refuse"]], axis=1).sum(axis=1, min_count=1)
            L.append(f"refuse: mediana por fila = {ref.median():.1f}; máx = {ref.max():.1f}")
            tot = ref.groupby(f.dt.year).sum()
            L.append("refuse total por año (suma de filas, unidades del CSV): " + "; ".join(f"{int(a)}={v:,.0f}" for a, v in tot.items()))
        otras = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not any(c in v for v in det["materiales"].values())]
        L.append("columnas numéricas NO asignadas a un material: " + (", ".join(map(str, otras)) or "ninguna"))
    texto = "\n".join(L)
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    VERIF_TXT.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    print(f"\n(Guardado en {VERIF_TXT.relative_to(RAIZ)})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Preparación de datos tabulares (DS1 y DS2)")
    ap.add_argument("accion", choices=["descargar", "verificar", "preparar", "todo"])
    ap.add_argument("--forzar", action="store_true", help="volver a descargar aunque exista el archivo")
    a = ap.parse_args()
    if a.accion in ("descargar", "todo"):
        descargar(a.forzar)
    if a.accion in ("verificar", "todo"):
        verificar()
    if a.accion in ("preparar", "todo"):
        preparar()
