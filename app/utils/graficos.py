"""Gráficos reutilizables (plotly) y visualización de métricas desde *_meta.json."""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def tabla_metricas(meta):
    """DataFrame Métrica/Valor a partir de meta['metricas'] (None se muestra como 'pendiente')."""
    filas = [(k, "pendiente" if v is None else v) for k, v in meta.get("metricas", {}).items()]
    return pd.DataFrame(filas, columns=["Métrica", "Valor"])


def mostrar_metricas(meta):
    """Muestra las métricas del modelo (st.metric) y sus notas de limitación."""
    import streamlit as st
    metricas = meta.get("metricas", {})
    if not metricas:
        st.info("Este modelo no tiene métricas registradas.")
        return
    st.caption(f"Modelo: {meta.get('modelo', 'sin nombre')}. Fecha: {meta.get('fecha', 's/f')}")
    columnas = st.columns(len(metricas))
    for col, (nombre, valor) in zip(columnas, metricas.items()):
        col.metric(nombre, "pendiente" if valor is None else f"{valor:.4g}" if isinstance(valor, (int, float)) else str(valor))
    if meta.get("notas"):
        st.caption(f"Limitaciones: {meta['notas']}")


def grafico_barras(df, x, y, titulo="", color=None):
    fig = px.bar(df, x=x, y=y, color=color, title=titulo)
    fig.update_layout(margin=dict(t=50, b=20))
    return fig


def grafico_dispersion_2d(df, x, y, color=None, hover=None, titulo=""):
    """Dispersión 2D (p. ej. países proyectados en 2 componentes, coloreados por clúster)."""
    fig = px.scatter(df, x=x, y=y, color=color, hover_name=hover, title=titulo)
    fig.update_layout(margin=dict(t=50, b=20))
    return fig


def grafico_pronostico(historico, pronostico, inferior=None, superior=None, titulo="", unidad=""):
    """Serie histórica + pronóstico (+ banda de intervalo). Entradas: pd.Series con índice de fechas."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historico.index, y=historico.values, name="Histórico", mode="lines"))
    fig.add_trace(go.Scatter(x=pronostico.index, y=pronostico.values, name="Pronóstico", mode="lines",
                             line=dict(dash="dash")))
    if inferior is not None and superior is not None:
        fig.add_trace(go.Scatter(x=list(superior.index) + list(inferior.index[::-1]),
                                 y=list(superior.values) + list(inferior.values[::-1]),
                                 fill="toself", line=dict(width=0), name="Intervalo", opacity=0.25))
    fig.update_layout(title=titulo, yaxis_title=unidad, margin=dict(t=50, b=20))
    return fig
