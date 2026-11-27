"""Página de inicio: qué hace la app, estado de los módulos y avisos de uso responsable (sin cifras de resultados)."""
import streamlit as st

import config
from app.utils.diagnostico import revisar_todos

QUE_HACE = {
    "prediccion": "Estima la generación de residuos por persona y día de un país a partir de su PIB, población y región.",
    "series": "Pronostica las toneladas mensuales de residuos de la ciudad de Nueva York (datos de una sola ciudad).",
    "imagenes": "Reconoce el tipo de residuo en una foto y sugiere a qué contenedor iría.",
    "clustering": "Agrupa países según su perfil de generación y composición de residuos.",
    "resumen": "Resume textos largos (extractivo siempre; abstractivo opcional).",
}


def render():
    st.header("♻️ Bienvenido a " + config.NOMBRE_PROYECTO)
    st.write("Aplicación académica con cinco módulos de inteligencia artificial sobre **gestión de residuos urbanos**. "
             "Elige una pestaña. Cada módulo muestra sus propias métricas y limitaciones en su sección «Modelo y métricas».")

    filas = ["| Módulo | Qué hace | Estado |", "|---|---|---|"]
    revision = {r["id"]: r for r in revisar_todos()}
    for m in config.MODULOS:
        r = revision[m["id"]]
        estado = "✅ listo" if r["listo"] else "⚠️ faltan archivos"
        filas.append(f"| {m['titulo']} | {QUE_HACE.get(m['id'], '')} | {estado} |")
    st.markdown("\n".join(filas))
    faltan = [f"`{f}`" for r in revision.values() for f in r["faltan"]]
    if faltan:
        st.warning("Archivos que faltan: " + ", ".join(faltan) + ". El resto de la aplicación sigue funcionando.")

    st.subheader("Antes de usarla")
    st.markdown(
        "- **Es una ayuda a la decisión, no una decisión.** Las estimaciones tienen error y pueden fallar; revisa siempre el resultado.\n"
        "- **Privacidad:** no subas fotos con personas, rostros ni documentos, ni textos con datos personales.\n"
        "- **Sesgos y alcance de los datos:** los modelos aprenden de datos públicos con vacíos. La predicción y el clustering usan "
        "países, no ciudades; las series temporales son solo de Nueva York; las fotos provienen de conjuntos públicos con fondos "
        "y objetos que pueden diferir de los de tu entorno. No generalices sin evidencia.\n"
        "- **Resumen abstractivo:** puede inventar o cambiar datos. Contrasta con el original.\n"
        "- **Licencias:** los conjuntos de datos y modelos tienen licencias propias (algunos de uso no comercial). "
        "Consulta la sección «Fuentes» de cada módulo y el informe técnico antes de reutilizarlos."
    )
    with st.expander("Aviso completo"):
        st.write(config.AVISO_USO)
    st.caption("Proyecto del curso Software Inteligente (UNMSM, 2026-2). Todas las métricas mostradas provienen de ejecuciones reales "
               "guardadas en `models/*_meta.json`; la app no entrena modelos.")
