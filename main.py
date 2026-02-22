import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

# 3. CSS GENERAL
st.markdown("""
<style>
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes shine {
    0% { left: -100%; opacity: 0; }
    50% { opacity: 0.6; }
    100% { left: 100%; opacity: 0; }
}

@keyframes glowPulse {
    0% { box-shadow: 0 0 5px #38bdf8; }
    50% { box-shadow: 0 0 18px #38bdf8; }
    100% { box-shadow: 0 0 5px #38bdf8; }
}

.stApp { 
    background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #e2e8f0; 
}

.block-container { 
    max-width: 1000px !important; 
    padding-top: 1.5rem !important; 
}

/* HEADER */
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-bottom: 5px;
}

.capsula-header-mini {
    position: relative;
    padding: 10px 30px;
    background: rgba(56, 189, 248, 0.05);
    border-radius: 30px;
    border: 1px solid rgba(56, 189, 248, 0.5);
    overflow: hidden;
    text-align: center;
}

.titulo-mini {
    font-weight: 800;
    font-size: 1.5rem;
    margin: 0;
    z-index: 2;
    position: relative;
}

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

/* LOGO EFECTO */
.logo-osecac {
    width: 75px;
    border-radius: 50%;
    animation: glowPulse 3s infinite ease-in-out;
    transition: transform 0.3s ease;
}

.logo-osecac:hover {
    transform: scale(1.08);
}

.subtitulo-lema {
    color: #94a3b8;
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 8px;
    text-align: center;
    margin-bottom: 20px;
}

/* FICHAS */
.ficha {
    background-color: rgba(23, 32, 48, 0.9);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

.ficha-tramite { border-left: 6px solid #fbbf24; }
.titulo-tramite { color: #fbbf24; font-size: 1.4rem; font-weight: bold; margin-bottom: 10px; }

.ficha-agenda { border-left: 6px solid #38bdf8; }
.titulo-agenda { color: #38bdf8; font-size: 1.3rem; font-weight: bold; margin-bottom: 8px; }

.cuerpo-ficha {
    white-space: pre-wrap;
    font-size: 15px;
    line-height: 1.6;
    color: #f1f5f9;
}

div.stLinkButton > a {
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    padding: 12px !important;
    width: 100% !important;
    text-align: center !important;
}

.stExpander { 
    background-color: rgba(30, 41, 59, 0.6) !important; 
    border-radius: 12px !important; 
    margin-bottom: 8px !important;
}

.buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
.buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }

</style>
""", unsafe_allow_html=True)

# HEADER CON LOGO INTEGRADO
st.markdown("""
<div class="header-container">
    <div class="capsula-header-mini">
        <div class="shimmer-efecto"></div>
        <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
    </div>
    <img src="LOGO1.png" class="logo-osecac">
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>', unsafe_allow_html=True)
st.markdown("---")

# SECCIONES
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/")
        st.link_button("🏛️ AFIP", "https://www.afip.gob.ar/")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://www.anses.gob.ar/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/")
    with c3:
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
        st.link_button("🧪 PORTAL MEDICAMENTOS", "#")
