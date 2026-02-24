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

# --- CLAVE DE ACCESO PERSONALIZADA ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

# URLs DE DATOS
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
    st.session_state.historial_novedades = [{"mensaje": "Bienvenidos al portal oficial.", "fecha": "22/02/2026"}]

# 3. CSS: TU DISEÑO + ETIQUETAS EN NEGRO CLARO
st.markdown("""
    <style>
    [data-testid="stSidebar"], #MainMenu, footer, header { display: none !important; }
    
    /* FONDO ANIMADO */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* --- EL ARREGLO DE LOS BUSCADORES (BLANCO/NEGRO) --- */
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

    /* --- ETIQUETAS EN NEGRO PARA QUE SE VEAN BIEN --- */
    /* Seleccione origen, FABA, OSECAC, Buscar en nomencladores... */
    .stWidgetLabel p, label[data-testid="stWidgetLabel"] p, .stRadio label p {
        color: #000000 !important; /* Negro puro */
        font-weight: 800 !important; /* Extra negrita */
        background-color: rgba(255, 255, 255, 0.8); /* Un fondo sutil para resaltar */
        padding: 2px 10px;
        border-radius: 5px;
        display: inline-block;
    }

    /* ESTÉTICA DE FICHAS */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-practica { border-left-color: #10b981; } 
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    .buscador-gestion { border: 2px solid #fbbf24; border-radius: 12px; margin-bottom: 10px; }
    .buscador-practica { border: 2px solid #10b981; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.title("🏥 OSECAC MDP / AGENCIAS")
st.markdown("---")

# --- SECCIÓN 1: NOMENCLADORES ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=True):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.write("")
    opcion_busqueda = st.radio("Seleccione el origen de datos:", ["FABA", "OSECAC"], horizontal=True)
    busqueda_unificada = st.text_input("🔍 Buscar en nomencladores...", key="main_search")
    
    if busqueda_unificada:
        df_a_usar = df_faba if opcion_busqueda == "FABA" else df_osecac_busq
        if not df_a_usar.empty:
            mask = df_a_usar.apply(lambda row: any(busqueda_unificada.lower() in str(v).lower() for v in row), axis=1)
            resultados = df_a_usar[mask]
            for i, row in resultados.iterrows():
                st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# --- SECCIÓN 2: PEDIDOS ---
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# --- SECCIÓN 3: PÁGINAS ÚTILES ---
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/saes/")
    st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

# --- GESTIONES ---
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PRÁCTICAS ---
st.markdown('<div class="buscador-practica">', unsafe_allow_html=True)
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    busqueda_p = st.text_input("Buscá prácticas...", key="search_p")
    if busqueda_p:
        for df_actual in [df_practicas, df_especialistas]:
            if not df_actual.empty:
                res = df_actual[df_actual.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
                for i, row in res.iterrows():
                    st.markdown(f'<div class="ficha ficha-practica">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items()])}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- NOVEDADES ---
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
