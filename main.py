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

# 3. CSS PROFESIONAL (LOGO INTEGRADO)
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

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    .block-container { max-width: 1000px !important; padding-top: 2rem !important; }

    /* CARTEL CON LOGO ADENTRO */
    .capsula-unificada {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 40px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        overflow: hidden;
        margin: 0 auto;
        max-width: fit-content;
    }

    .titulo-mini {
        font-family: 'sans-serif';
        font-weight: 800;
        font-size: 1.5rem;
        color: #e2e8f0;
        margin: 0;
        z-index: 2;
    }

    .logo-integrado {
        height: 40px;
        z-index: 2;
    }

    .shimmer-efecto {
        position: absolute;
        top: 0;
        width: 100px;
        height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.3), transparent);
        transform: skewX(-20deg);
        animation: shine 4s infinite linear;
        z-index: 1;
    }

    .subtitulo-lema {
        color: #94a3b8;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 15px;
        text-align: center;
        margin-bottom: 30px;
    }

    /* FICHAS Y BUSCADORES (TU DISEÑO ORIGINAL) */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .titulo-tramite { color: #fbbf24; font-size: 1.4rem; font-weight: bold; margin-bottom: 10px; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .titulo-agenda { color: #38bdf8; font-size: 1.3rem; font-weight: bold; margin-bottom: 8px; }
    .cuerpo-ficha { white-space: pre-wrap; font-size: 15px; line-height: 1.6; color: #f1f5f9; }

    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    
    div.stLinkButton > a { border-radius: 8px !important; font-weight: 700 !important; text-transform: uppercase !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# === ENCABEZADO UNIFICADO (TODO EN UNO) ===
st.markdown("""
    <div style="text-align: center;">
        <div class="capsula-unificada">
            <div class="shimmer-efecto"></div>
            <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
            <img src="https://img.icons8.com/fluency/48/000000/shield.png" class="logo-integrado">
        </div>
        <div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>
    </div>
    """, unsafe_allow_html=True)

# NOTA: Como no puedo leer tu LOGO1.png localmente para meterlo en el HTML, 
# puse un icono de escudo azul de ejemplo. REEMPLAZÁ la URL de la imagen 
# por la ruta de tu logo si lo tenés online, o avisame.

st.markdown("---")

# ==========================================
# RESTO DEL PORTAL (ORIGINAL E INTACTO)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="search_tramites")
    if busqueda_t:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><div class="titulo-tramite">📋 {row["TRAMITE"]}</div><div class="cuerpo-ficha">{row["DESCRIPCIÓN Y REQUISITOS"]}</div></div>', unsafe_allow_html=True)
            st.link_button(f"📂 CARPETA {row['TRAMITE']}", str(row['LINK CARPETA / ARCHIVOS']))
st.markdown('</div>', unsafe_allow_html=True)
