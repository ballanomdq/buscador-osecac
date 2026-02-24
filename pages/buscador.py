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

# --- CLAVE DE ACCESO ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

# URLs (Tus bases originales)
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
    st.session_state.historial_novedades = [{"mensaje": "Portal oficial de Agencias.", "fecha": "22/02/2026"}]

# 3. CSS: ESTILO SUAVE Y LUMINOSO (SIN CUADRADOS RÍGIDOS)
st.markdown("""
    <style>
    [data-testid="stSidebar"], #MainMenu, footer, header { display: none !important; }
    
    /* FONDO ANIMADO ORIGINAL */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* BUSCADORES: Limpios, blancos y con letra negra */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    input {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }

    /* ETIQUETAS: Estilo suave, sin fondo cuadrado, solo sombra de texto para legibilidad */
    .stWidgetLabel p, .stRadio label p {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0px 0px 8px rgba(0,0,0,0.8); /* Esto hace que la letra blanca se vea sobre cualquier fondo */
        letter-spacing: 0.5px;
    }

    /* FICHAS: Estilo redondeado y suave */
    .ficha { 
        background-color: rgba(30, 41, 59, 0.7); 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 12px; 
        border-left: 4px solid #38bdf8; 
        backdrop-filter: blur(5px);
    }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-practica { border-left-color: #10b981; }

    /* CONTENEDORES DE BUSCADORES */
    .buscador-container {
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# === TÍTULO PRINCIPAL ===
st.markdown("<h1 style='text-align: center; color: white;'>🏥 OSECAC MDP / AGENCIAS</h1>", unsafe_allow_html=True)

# --- 1. NOMENCLADORES ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=True):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    opcion = st.radio("Seleccione el origen de datos:", ["FABA", "OSECAC"], horizontal=True)
    busq = st.text_input("🔍 Buscar en nomencladores...", key="nomen")
    if busq:
        df = df_faba if opcion == "FABA" else df_osecac_busq
        res = df[df.astype(str).apply(lambda x: x.str.contains(busq, case=False)).any(axis=1)]
        for _, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# --- 2. PEDIDOS ---
with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# --- 3. PÁGINAS ÚTILES ---
with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    cols = st.columns(2)
    with cols[0]:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with cols[1]:
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/saes/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

# --- 4. GESTIONES (Con el borde de color sutil) ---
st.markdown("<div style='border-left: 3px solid #fbbf24; padding-left: 10px;'>", unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busq_t = st.text_input("Buscá trámites...", key="tram")
    if busq_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busq_t.lower(), na=False)]
        for _, r in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {r["TRAMITE"]}</b><br>{r["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. PRÁCTICAS ---
st.markdown("<div style='border-left: 3px solid #10b981; padding-left: 10px;'>", unsafe_allow_html=True)
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**"):
    busq_p = st.text_input("Buscá prácticas...", key="prac")
    if busq_p:
        for d in [df_practicas, df_especialistas]:
            if not d.empty:
                res = d[d.astype(str).apply(lambda x: x.str.contains(busq_p, case=False)).any(axis=1)]
                for _, r in res.iterrows():
                    st.markdown(f'<div class="ficha ficha-practica">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in r.items()])}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. NOVEDADES ---
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-left-color: #ff4b4b;">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
