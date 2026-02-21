import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: FONDO BLANCO Y COLORES AJUSTADOS
st.markdown("""
    <style>
    /* Fondo de la página blanco y letras oscuras */
    .stApp { background-color: #ffffff; color: #1e293b; }
    .block-container { max-width: 850px !important; padding-top: 1.5rem !important; }

    /* Ajuste para que el logo no se corte */
    [data-testid="stImage"] img {
        object-fit: contain;
    }

    /* ESTILO BASE BOTONES */
    div.stLinkButton > a {
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 10px 15px !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
    }

    /* --- NOMENCLADORES (Azul Profesional sobre blanco) --- */
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] {
        color: #0369a1 !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #f0f9ff !important;
    }

    /* --- PEDIDOS (Tus colores hermosos, ajustados para fondo blanco) --- */
    /* Rosa para Leches */
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"] { 
        color: #be185d !important;
        border: 1px solid #fbcfe8 !important;
        background-color: #fdf2f8 !important;
    }
    /* Verde para Suministros */
    div.stLinkButton > a[href*="MlwRSUf6dAww"] { 
        color: #047857 !important;
        border: 1px solid #a7f3d0 !important;
        background-color: #ecfdf5 !important;
    }
    /* Violeta para Estado */
    div.stLinkButton > a[href*="21d6f3bf-24c1"] { 
        color: #6d28d9 !important;
        border: 1px solid #ddd6fe !important;
        background-color: #f5f3ff !important;
    }

    div.stLinkButton > a:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }

    /* Estilo de las cajas desplegables */
    .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #1e293b !important;
    }
    
    /* Buscador */
    .stTextInput > div > div > input { background-color: #f8fafc !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important; }
    
    h1 { font-weight: 900; color: #0f172a; margin: 0; font-size: 1.8rem !important; }
    h3 { color: #334155; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA: LOGO IZQUIERDA Y TÍTULO ===
# El [2, 5] da un poco más de aire al logo a la izquierda
col_logo, col_titulo = st.columns([2, 5])

with col_logo:
    try:
        # Asegurate que sea LOGO.jpg o LOGO.png según lo que subiste
        st.image("LOGO.jpg", width=180)
    except:
        st.write(" ")

with col_titulo:
    st.title("OSECAC MDQ / AGENCIAS")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MENÚS
# ==========================================
with st.expander("NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("PEDIDOS"):
    col_l, col_s, col_e = st.columns(3)
    with col_l: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    with col_s: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    with col_e: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BUSCADOR AGENDAS/MAILS
# ==========================================
@st.cache_data
def cargar_datos():
    try:
        url_unica = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        df = pd.read_csv(url_unica)
        return df
    except:
        return pd.DataFrame()
