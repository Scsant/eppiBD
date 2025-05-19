# app/main.py

import streamlit as st
from components.requisicao_form import requisicao_form
from pathlib import Path

# ✅ PRIMEIRA CHAMADA OBRIGATÓRIA
st.set_page_config(page_title="Requisição de EPIs", layout="centered")

# Pode vir depois da configuração
def load_css():
    css_path = Path(__file__).parent / "styles" / "custom.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
requisicao_form()
