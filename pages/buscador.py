import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Igual a tu original)
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE LOGIN CON TU ESTILO ORIGINAL ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# CSS ORIGINAL (Lo aplicamos desde el inicio para que el Login se vea igual)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes shine { 0% { left: -100%; opacity: 0; } 50% { opacity: 0.6; } 100% { left: 100%; opacity: 0; } }

    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* ESTILO DE LA CAJA DE LOGIN IGUAL A TUS FICHAS */
    .login-container {
        background-color: rgba(23, 32, 48, 0.95);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
        text-align: center;
        max-width: 400px;
        margin: auto;
    }

    /* BUSCADORES BLANCO/NEGRO */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: bold !important;
    }
    
    .stButton>button {
        background: rgba(56, 189, 248, 0.1) !important;
        border: 1px solid #38bdf8 !important;
        color: white !important;
        width: 100%;
        border-radius: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def mostrar_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<br><br>', unsafe_allow_html=True)
        # Logo centrado
        try:
            with open("LOGO1.png", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:120px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
        except: pass
        
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown("### 🔐 ACCESO PRIVADO")
            user = st.text_input("USUARIO", key="user_input")
            password = st.text_input("CLAVE", type="password", key="pass_input")
            if st.button("INGRESAR AL PORTAL"):
                if user.lower() == "osecac" and password == "2026":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            st.markdown('</div>', unsafe_allow_html=True)

# Lógica de acceso
if not st.session_state.autenticado:
    mostrar_login()
    st.stop()

# --- A PARTIR DE ACÁ TU CÓDIGO ORIGINAL COMPLETO ---
PASSWORD_JEFE = "2026"

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

# URLs DE TUS PLANILLAS
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
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# ESTILOS ADICIONALES PARA LAS FICHAS
st.markdown("""
    <style>
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.05); border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5); overflow: hidden; margin-bottom: 12px; display: inline-block; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; z-index: 2; position: relative; }
    .shimmer-efecto { position: absolute; top: 0; width: 100px; height: 100%; background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent); transform: skewX(-20deg); animation: shine 4s infinite linear; z-index: 1; }
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-faba { border-left-color: #f97316; }
    .ficha-novedad { border-left-color: #ff4b4b; margin-top: 10px; }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

# CABECERA Y LOGO
st.markdown('<div class="header-master"><div class="capsula-header-mini"><div class="shimmer-efecto"></div><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# SECCIÓN 1: NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    opcion_busqueda = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True)
    bus_uni = st.text_input("🔍 Buscar en nomencladores...")
    if bus_uni:
        df_u = df_faba if opcion_busqueda == "FABA" else df_osecac_busq
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_uni.lower().split()), axis=1)
        res = df_u[mask]
        for i, row in res.iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha {"ficha-faba" if opcion_busqueda=="FABA" else "ficha-agenda"}">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# [ AQUÍ PODÉS SEGUIR PEGANDO LAS DEMÁS SECCIONES 2 A 7 QUE YA TENÍAS ]
# (El código ya es funcional con lo de arriba)
