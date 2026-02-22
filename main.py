import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

# 3. CSS: DISEÑO ANTERIOR CON BRILLO MÁS INTENSO
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Brillo un poco más rápido e intenso */
    @keyframes shine {
        0% { left: -100%; opacity: 0; }
        50% { opacity: 0.6; }
        100% { left: 100%; opacity: 0; }
    }

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    .block-container { max-width: 1000px !important; padding-top: 2rem !important; }

    /* Contenedor para Cartel y Logo juntos */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 10px;
    }

    .capsula-header-mini {
        position: relative;
        padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 35px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        overflow: hidden;
    }

    .titulo-mini {
        font-family: 'sans-serif';
        font-weight: 800;
        font-size: 1.5rem;
        color: #e2e8f0;
        margin: 0;
        position: relative;
        z-index: 2;
    }

    /* La luz que recorre (Más intensa) */
    .shimmer-efecto {
        position: absolute;
        top: 0;
        width: 80px;
        height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent);
        transform: skewX(-20deg);
        animation: shine 4s infinite linear;
        z-index: 1;
    }

    .subtitulo-lema {
        color: #94a3b8;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 10px;
        text-align: center;
    }

    /* Estilos de tus fichas y buscadores */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA COMPACTA CON LOGO A LA DERECHA ===
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# Cartel con brillo
st.markdown("""
    <div class="capsula-header-mini">
        <div class="shimmer-efecto"></div>
        <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
    </div>
    """, unsafe_allow_html=True)

# Logo1.png a la derecha
try:
    st.image("LOGO1.png", width=70)
except:
    st.write("")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# RESTO DEL CÓDIGO (BOTONES Y BUSCADORES)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

# Buscadores
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="t")
    if busqueda_t:
        st.markdown(f'<div class="ficha ficha-tramite">Resultado para: {busqueda_t}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    busqueda_a = st.text_input("Buscá contactos...", key="a")
    if busqueda_a:
        st.markdown(f'<div class="ficha ficha-agenda">Resultado para: {busqueda_a}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
