import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# 2. CSS para Centrar y achicar los contenedores
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f8fafc;
    }

    /* ESTO ACHICA LOS MENÚS Y LOS CENTRA EN PC */
    .stExpander {
        max-width: 800px !important; /* Ancho máximo para que no se estiren al infinito */
        margin-left: auto !important;
        margin-right: auto !important;
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    /* BOTONES INTERNOS MÁS ESTILIZADOS */
    div.stLinkButton > a {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        transition: all 0.3s ease !important;
        font-weight: bold !important;
        text-align: center !important;
        display: block !important;
    }
    
    div.stLinkButton > a:hover {
        border-color: #38bdf8 !important;
        transform: scale(1.02) !important;
    }

    /* CENTRAR TÍTULO Y BUSCADOR */
    h1, .stSubheader, .stTextInput {
        max-width: 800px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# NOMENCLADORES (CENTRADOS)
# ==========================================
with st.expander("📖 NOMENCLADORES"):
    col1, col2, col3 = st.columns(3)
    with col1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
    with col2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)
    with col3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)

# ==========================================
# PEDIDOS (CENTRADOS)
# ==========================================
with st.expander("📦 PEDIDOS"):
    col4, col5, col6 = st.columns(3)
    with col4: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)
    with col5: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
    with col6: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ... El código del buscador sigue aquí abajo ...
