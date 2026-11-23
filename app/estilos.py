"""Estilos visuales de la interfaz: hoja de estilos, cabecera, introducción de módulo y pie de página."""
from html import escape

import streamlit as st

import config

CSS = """
<style>
.stApp { font-family: "Segoe UI", "Helvetica Neue", Roboto, Arial, sans-serif; }
.block-container, [data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 3rem; }
footer, #MainMenu { visibility: hidden; }

h2, h3, h4 { color: #0f3d2e; letter-spacing: -0.01em; }

.eco-hero { background: linear-gradient(120deg, #0f3d2e 0%, #1b7f5c 100%); border-radius: 14px;
            padding: 28px 34px; margin-bottom: 20px; }
.eco-chip { display: inline-block; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.35);
            color: #ffffff; border-radius: 999px; padding: 2px 14px; font-size: 0.8rem; letter-spacing: 0.03em; margin-bottom: 12px; }
.eco-title { color: #ffffff; font-size: 2.2rem; font-weight: 700; line-height: 1.15; letter-spacing: -0.02em; margin: 0 0 8px 0; }
.eco-sub { color: #d7efe4; font-size: 1.02rem; margin: 0; max-width: 780px; }

.eco-intro { border-left: 4px solid #1b7f5c; background: #f2f6f4; border-radius: 0 10px 10px 0;
             padding: 14px 20px; margin: 8px 0 18px 0; }
.eco-intro-title { color: #0f3d2e; font-size: 1.25rem; font-weight: 700; margin: 0 0 4px 0; }
.eco-intro-text { color: #41524c; margin: 0; }

[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #d9e6df; }
button[data-baseweb="tab"] { padding: 10px 18px; font-weight: 600; }

[data-testid="stMetric"] { background: #ffffff; border: 1px solid #d9e6df; border-radius: 12px;
                           padding: 14px 18px; box-shadow: 0 1px 2px rgba(15,61,46,0.06); }
[data-testid="stMetricLabel"] { color: #5b6b66; }
[data-testid="stExpander"] { border: 1px solid #d9e6df; border-radius: 10px; }
[data-testid="stAlert"] { border-radius: 10px; }
[data-testid="stDataFrame"] { border: 1px solid #d9e6df; border-radius: 10px; }

.eco-footer { text-align: center; color: #6b7b75; font-size: 0.85rem; margin-top: 2.5rem;
              padding-top: 1rem; border-top: 1px solid #e3ece7; }
</style>
"""


def aplicar():
    """Inyecta la hoja de estilos en la página."""
    st.markdown(CSS, unsafe_allow_html=True)


def cabecera():
    """Banner superior con el nombre del proyecto y el grupo."""
    st.markdown(
        f'<div class="eco-hero"><div class="eco-chip">{escape(config.GRUPO)}</div>'
        f'<div class="eco-title">{escape(config.NOMBRE_PROYECTO)}</div>'
        f'<p class="eco-sub">{escape(config.DESCRIPCION_PROYECTO)}</p></div>',
        unsafe_allow_html=True,
    )


def intro(titulo, descripcion):
    """Título y descripción breve al inicio de cada módulo."""
    st.markdown(
        f'<div class="eco-intro"><div class="eco-intro-title">{escape(titulo)}</div>'
        f'<p class="eco-intro-text">{escape(descripcion)}</p></div>',
        unsafe_allow_html=True,
    )


def pie():
    """Pie de página con el grupo y el curso."""
    st.markdown(
        f'<div class="eco-footer">{escape(config.NOMBRE_PROYECTO)}. {escape(config.GRUPO)}, {escape(config.CURSO)}.</div>',
        unsafe_allow_html=True,
    )
