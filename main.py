import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# CSS para botones compactos y centrados
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        /* AQUÍ PODÉS PONER TU IMAGEN DE FONDO LUEGO */
        color: #f8fafc;
    }

    /* Estilo de los contenedores (Expander) */
    .stExpander {
        background-color: rgba(30, 41, 59, 0.7) !important; /* Semitransparente para que se vea el fondo */
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    /* BOTONES COMPACTOS Y CENTRADOS */
    div.stLinkButton {
        text-align: center;
    }

    div.stLinkButton > a {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        
        /* MAGIA: Ancho fijo y centrado */
        width: 250px !important; 
        margin: 10px auto !important;
        
        transition: all 0.3s ease !important;
        display: inline-block !important; /* Evita que ocupe todo el ancho */
        text-decoration: none !important;
        font-weight: bold !important;
    }
    
    div.stLinkButton > a:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0px 0px 15px rgba(56, 189, 248, 0.3) !important;
        transform: scale(1.05);
    }

    h1 { text-align: center; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# Logo (Opcional si ya lo tenés)
# st.image("logo.png", width=100)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# SECCIÓN 1: NOMENCLADORES
# ==========================================
with st.expander("📖 NOMENCLADORES"):
    # Usamos columnas para que se vean uno al lado del otro pero sin estirarse
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=False)
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=False)
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=False)

# ==========================================
# SECCIÓN 2: PEDIDOS
# ==========================================
with st.expander("📦 PEDIDOS"):
    c4, c5, c6 = st.columns(3)
    with c4: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=False)
    with c5: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=False)
    with c6: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=False)

st.markdown("<br>", unsafe_allow_html=True)

# (El resto del código del buscador se mantiene igual...)
