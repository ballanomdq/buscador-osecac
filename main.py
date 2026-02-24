import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE LOGUEO Y CARGA DINÁMICA ---
if 'cargado' not in st.session_state:
    st.session_state.cargado = False

# 2. CSS: TU DISEÑO + ANIMACIONES DE ENTRADA
st.markdown("""
    <style>
    /* OCULTAR PANEL LATERAL */
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* TU FONDO ANIMADO ORIGINAL */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* ANIMACIÓN DE CARGA (SISTEMA) */
    .loader-text {
        font-family: 'Courier New', Courier, monospace;
        color: #38bdf8;
        text-align: center;
        margin-top: 20%;
    }
    
    /* EFECTO DE APARICIÓN SUAVE DEL CONTENIDO */
    .fade-in {
        animation: fadeIn 2s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* ESTILO BUSCADOR BLANCO/NEGRO */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    input { color: #000000 !important; font-weight: bold !important; }

    /* ESTÉTICA FICHAS */
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.1); border-radius: 35px; border: 1px solid #38bdf8; display: inline-block; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; }
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-novedad { border-left-color: #ff4b4b; }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PANTALLA DE CARGA DINÁMICA ---
if not st.session_state.cargado:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown('<div class="loader-text">', unsafe_allow_html=True)
        # Intento de poner el logo en la carga
        try:
            with open("LOGO1.png", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:100px; filter: drop-shadow(0 0 10px #38bdf8);"></center>', unsafe_allow_html=True)
        except: pass
        
        st.markdown("### ⚙️ INICIALIZANDO PORTAL OSECAC...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulación de carga de archivos
        pasos = ["Conectando con Google Sheets...", "Cargando Nomencladores...", "Sincronizando Agendas...", "Verificando Credenciales...", "Sistema Listo."]
        for i, paso in enumerate(pasos):
            status_text.markdown(f"<p style='text-align:center;'>{paso}</p>", unsafe_allow_html=True)
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.6) # Velocidad de la animación
            
    st.session_state.cargado = True
    placeholder.empty()
    st.rerun()

# --- COMIENZO DEL PORTAL (FADE IN) ---
st.markdown('<div class="fade-in">', unsafe_allow_html=True)

# 3. CLAVE DE ACCESO PERSONALIZADA
PASSWORD_JEFE = "2026"

# CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

# URLs DE TUS PLANILLAS
URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# CABECERA
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

# LOGO
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# SECCIÓN 1: NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    opcion_busqueda = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True)
    busqueda_unificada = st.text_input("🔍 Buscar en nomencladores...", key="main_search")
    
    if busqueda_unificada:
        df_a_usar = df_faba if opcion_busqueda == "FABA" else df_osecac_busq
        palabras = busqueda_unificada.lower().split()
        mask = df_a_usar.apply(lambda row: all(p in str(row).lower() for p in palabras), axis=1)
        for i, row in df_a_usar[mask].iterrows():
            datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
            st.markdown(f'<div class="ficha">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# SECCIÓN 2: PEDIDOS
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# SECCIÓN 4: GESTIONES
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# SECCIÓN 6: AGENDAS
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# SECCIÓN 7: NOVEDADES
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ PANEL DE CONTROL"):
        if st.text_input("Clave de edición:", type="password") == PASSWORD_JEFE:
            with st.form("form_nov", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("📢 PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(datetime.now().timestamp()), "mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # Cierre del fade-in
