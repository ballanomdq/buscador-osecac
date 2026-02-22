import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# --- CLAVE DE ACCESO PERSONALIZADA ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS (CSV DESDE GOOGLE SHEETS)
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# URLs de las planillas
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)

# Inicializar historial de novedades si no existe
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP. Las novedades aparecerán aquí.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS: DISEÑO PERSONALIZADO
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
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 12px rgba(255, 75, 75, 0); }
    }

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

    /* ====== CORRECCIÓN DE BOTONES (PROBLEMA BLANCO) ====== */
    .stButton > button,
    .stLinkButton > a {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
    }

    .stButton > button:active,
    .stLinkButton > a:active {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }

    .stButton > button:focus,
    .stLinkButton > a:focus {
        background-color: #1e293b !important;
        color: #ffffff !important;
        outline: none !important;
        box-shadow: 0 0 0 2px #38bdf8 !important;
    }
    /* ====================================================== */

    .punto-alerta {
        width: 12px; height: 12px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 12px;
        animation: pulso 1.5s infinite;
        vertical-align: middle;
    }

    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini {
        position: relative; padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5);
        overflow: hidden; margin-bottom: 12px; display: inline-block;
    }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; z-index: 2; position: relative; }
    .shimmer-efecto {
        position: absolute; top: 0; width: 100px; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent);
        transform: skewX(-20deg); animation: shine 4s infinite linear; z-index: 1;
    }

    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .ficha-practica { border-left: 6px solid #10b981; }
    .ficha-novedad { border-left: 6px solid #ff4b4b; margin-top: 10px; }

    .novedad-fecha-grande { font-size: 16px; color: #ff4b4b; font-weight: bold; display: block; margin-bottom: 5px; }
    .novedad-texto { font-size: 18px; line-height: 1.4; color: #ffffff; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-practica { border: 2px solid #10b981 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-novedades { border: 2px solid #ff4b4b !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown("""
    <div class="header-master">
        <div class="capsula-header-mini">
            <div class="shimmer-efecto"></div>
            <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except:
    pass

st.markdown("---")
