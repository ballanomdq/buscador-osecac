import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS ---
def editar_celda_google_sheets(sheet_url, fila_idx, columna_nombre, nuevo_valor):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)
        headers = worksheet.row_values(1)
        col_idx = headers.index(columna_nombre) + 1
        worksheet.update_cell(fila_idx + 2, col_idx, str(nuevo_valor))
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# 2. CSS - DISEÑO "PASTILLA" COMPACTA Y PROFESIONAL
st.markdown("""
    <style>
    /* Ocultar basura de Streamlit */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Fondo Azul Noche */
    .stApp { 
        background: radial-gradient(circle, #091220 0%, #050914 100%) !important;
    }

    /* --- BOTONES ESTILO PASTILLA (PEQUEÑOS Y NO INVASIVOS) --- */
    /* Este es el truco para que no sean gigantes */
    div.stLinkButton {
        display: inline-block !important; 
        width: auto !important;
        margin-right: 15px !important;
        margin-top: 10px !important;
    }

    div.stLinkButton > a {
        background-color: #002855 !important; /* Azul OSECAC Profundo */
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important; /* Borde celeste fino */
        border-radius: 20px !important;       /* Forma redondeada */
        padding: 6px 20px !important;         /* Tamaño compacto */
        font-size: 14px !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5) !important;
    }

    /* Efecto al pasar el mouse: Brillo sin cambiar color */
    div.stLinkButton > a:hover {
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.7) !important;
        transform: translateY(-2px) !important;
        border-color: #ffffff !important;
    }

    /* Forzar que el texto no cambie nunca a negro/gris */
    div.stLinkButton > a p { color: #ffffff !important; margin: 0 !important; }

    /* --- EXPANDERS CON CABECERA BLANCA --- */
    .stExpander { 
        background-color: #ffffff !important; 
        border-radius: 12px !important; 
        margin-bottom: 10px !important;
    }
    .stExpander details summary p {
        color: #002855 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    .stExpander details div[data-testid="stExpanderDetails"] {
        background-color: #091220 !important; /* Interior oscuro para contraste */
        border-radius: 0 0 12px 12px !important;
        padding: 20px !important;
    }

    /* --- INPUTS --- */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    input { color: #000000 !important; font-weight: bold !important; }

    /* --- FICHAS DE RESULTADOS --- */
    .ficha { 
        background-color: #16213e !important;
        padding: 15px; border-radius: 10px; margin-bottom: 8px; 
        border-left: 6px solid #38bdf8; color: #ffffff !important;
    }
    .ficha-tramite { border-left-color: #fbbf24 !important; }
    .ficha-agenda { border-left-color: #38bdf8 !important; }

    /* Header y Título */
    .header-master { text-align: center; margin-bottom: 20px; }
    .capsula-header { 
        padding: 10px 30px; 
        background: rgba(0, 40, 85, 0.5); 
        border-radius: 30px; 
        border: 2px solid #38bdf8; 
        display: inline-block; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/edit",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=1119565576",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/edit",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/edit"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

# --- HEADER ---
st.markdown('<div class="header-master"><div class="capsula-header"><h2 style="color:white; margin:0; font-size:1.5rem;">OSECAC MDP / AGENCIAS</h2></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:80px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

# --- CONTENIDO ---

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.write("---")
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    with c1:
        pop_f = st.popover("✏️")
        cl_f = pop_f.text_input("Clave FABA:", type="password", key="p_f")
    with c2: sel_faba = st.checkbox("FABA", value=True, key="chk_f")
    with c3:
        pop_o = st.popover("✏️")
        cl_o = pop_o.text_input("Clave OSECAC:", type="password", key="p_o")
    with c4: sel_osecac = st.checkbox("OSECAC", value=False, key="chk_o")

    opcion = "OSECAC" if sel_osecac else "FABA"
    cl_actual = cl_o if sel_osecac else cl_f
    df_u = df_osecac_busq if sel_osecac else df_faba
    url_u = URLs["osecac"] if sel_osecac else URLs["faba"]

    bus_nom = st.text_input(f"🔍 Buscar en {opcion}...", key="bus_n")
    if bus_nom:
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_nom.lower().split()), axis=1)
        for i, row in df_u[mask].iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 3. PÁGINAS ÚTILES", expanded=False):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
    st.link_button("🆔 CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    st.link_button("💻 OSECAC", "https://www.osecac.org.ar/")

# 4. GESTIONES
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS", expanded=False):
    bus_p = st.text_input("Buscá prácticas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha"><b>PRÁCTICA:</b> {row["PRÁCTICA"]}</div>', unsafe_allow_html=True)

# 6. AGENDAS
with st.expander("📞 6. AGENDAS / MAILS", expanded=False):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-agenda">{row["NOMBRE"]} - {row.get("MAIL", "")}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 7. NOVEDADES", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-left-color: #ff4b4b;">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
