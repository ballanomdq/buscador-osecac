import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        if '/edit' in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        return pd.read_csv(csv_url, dtype=str)
    except:
        return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_FABA = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
URL_OSECAC_BUSQ = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_faba = cargar_datos(URL_FABA)
df_osecac_busq = cargar_datos(URL_OSECAC_BUSQ)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}
    ]

# ================= CSS DEFINITIVO =================
st.markdown("""
<style>

/* OCULTAR ELEMENTOS */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }

/* FONDO GENERAL */
.stApp { 
    background-color: #0b0e14;
    background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #e2e8f0; 
}

/* ===== FIX REAL INPUT STREAMLIT ===== */

/* Fondo del input */
div[data-baseweb="base-input"],
div[data-baseweb="input"] {
    background-color: #000000 !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 8px !important;
}

/* Texto escrito */
div[data-baseweb="base-input"] input,
div[data-baseweb="input"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    caret-color: #000000 !important;
    font-weight: 600 !important;
}

/* Placeholder */
div[data-baseweb="base-input"] input::placeholder,
div[data-baseweb="input"] input::placeholder {
    color: #777777 !important;
}

/* Labels */
label, .stWidgetLabel p {
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
}

/* Radios */
div[role="radiogroup"] label p {
    color: #ffffff !important;
}

/* Animaciones */
@keyframes gradientBG { 
    0% { background-position: 0% 50%; } 
    50% { background-position: 100% 50%; } 
    100% { background-position: 0% 50%; } 
}

.block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

.ficha { 
    background-color: rgba(23, 32, 48, 0.9); 
    padding: 20px; 
    border-radius: 12px; 
    margin-bottom: 10px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.4); 
    border-left: 6px solid #ccc; 
    color: #ffffff !important; 
}

.ficha-tramite { border-left-color: #fbbf24; }
.ficha-agenda { border-left-color: #38bdf8; }
.ficha-practica { border-left-color: #10b981; } 
.ficha-faba { border-left-color: #f97316; }
.ficha-novedad { border-left-color: #ff4b4b; margin-top: 10px; }

.stExpander { 
    background-color: rgba(30, 41, 59, 0.6) !important; 
    border-radius: 12px !important; 
    margin-bottom: 8px !important; 
    border: 1px solid rgba(255,255,255,0.1) !important; 
}

</style>
""", unsafe_allow_html=True)

# ================= CABECERA =================
st.markdown('<h1 style="text-align:center;color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
st.markdown("---")

# ================= PRUEBA =================
st.text_input("🔍 Buscar...")
