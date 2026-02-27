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

# ===== CSS CORREGIDO =====
st.markdown("""
    <style>
    /* ===== OCULTAR ELEMENTOS POR DEFECTO ===== */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* ===== ANIMACIONES ===== */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes shine { 0% { left: -100%; opacity: 0; } 50% { opacity: 0.6; } 100% { left: 100%; opacity: 0; } }

    /* ===== FONDO PRINCIPAL ===== */
    .stApp {
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    /* ===== TÍTULOS ===== */
    h1, h2, h3, h4, h5, h6, .stMarkdown p, label {
        color: #ffffff !important;
    }

    /* ===== BOTONES DE LINK - CORREGIDOS ===== */
    .stLinkButton a {
        background-color: #2d3748 !important;  /* Gris oscuro uniforme */
        color: #ffffff !important;              /* Texto blanco */
        border: 1px solid #4299e1 !important;   /* Borde azul */
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        display: block;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stLinkButton a:hover {
        background-color: #4299e1 !important;   /* Azul en hover */
        color: #ffffff !important;               /* Texto SIGUE siendo blanco (no negro) */
        border-color: #4299e1 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
    }

    /* ===== CHECKBOXES ===== */
    .stCheckbox {
        color: #ffffff !important;
    }
    
    /* ===== LETRAS DEL NOMENCLADOR ===== */
    .letras-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 10px 0;
        padding: 10px;
        background: rgba(45, 55, 72, 0.5);
        border-radius: 10px;
        justify-content: center;
    }
    
    .letra-btn {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #2d3748;
        color: white;
        border: 1px solid #4299e1;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .letra-btn:hover {
        background: #4299e1;
        transform: scale(1.1);
    }
    
    .letra-btn-seleccionada {
        background: #4299e1;
        border-color: white;
    }

    /* ===== EXPANDERS ===== */
    .stExpander {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        border: 1px solid rgba(66, 153, 225, 0.2) !important;
    }

    /* ===== INPUTS ===== */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #4299e1 !important;
        border-radius: 8px !important;
    }
    input {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* ===== LAYOUT ===== */
    .block-container {
        max-width: 1000px !important;
        padding-top: 1.5rem !important;
    }
    .header-master {
        text-align: center;
        margin-bottom: 10px;
    }
    .capsula-header-mini {
        position: relative;
        padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 35px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        display: inline-block;
    }
    .titulo-mini {
        font-weight: 800;
        font-size: 1.4rem;
        color: #ffffff !important;
        margin: 0;
    }
    .shimmer-efecto {
        position: absolute;
        top: 0;
        width: 100px;
        height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent);
        transform: skewX(-20deg);
        animation: shine 4s infinite linear;
    }

    /* ===== FICHAS ===== */
    .ficha {
        background-color: rgba(23, 32, 48, 0.95) !important;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 6px solid #ccc;
        color: #ffffff !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #4299e1; }
    .ficha-practica { border-left-color: #10b981; }
    .ficha-especialista { border-left-color: #8b5cf6; }
    .ficha-novedad { border-left-color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: 
        return pd.DataFrame()

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
st.markdown('<div class="header-master"><div class="capsula-header-mini"><div class="shimmer-efecto"></div><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: 
    pass

st.markdown("---")

# 1. NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    
    # NOMENCLADOR IA con letras
    st.markdown("**NOMENCLADOR IA**")
    
    # Crear letras A-Z
    letras = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    
    # Dividir en filas de 13 letras cada una
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### FABA")
        # Checkboxes para FABA (A-M)
        for letra in letras[:13]:
            st.checkbox(f"□ {letra}", key=f"faba_{letra}")
    
    with col2:
        st.markdown("##### OSECAC")
        # Checkboxes para OSECAC (N-Z)
        for letra in letras[13:]:
            st.checkbox(f"□ {letra}", key=f"osecac_{letra}")
    
    st.markdown("---")
    
    # Buscadores
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.text_input("🔍 Buscar en FABA...", key="bus_faba")
        if st.session_state.get("bus_faba"):
            # Mostrar resultados de FABA
            mask = df_faba.apply(lambda row: all(p in str(row).lower() for p in st.session_state.bus_faba.lower().split()), axis=1)
            for i, row in df_faba[mask].iterrows():
                st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
    
    with col_b2:
        st.text_input("🔍 Buscar en OSECAC...", key="bus_osecac")
        if st.session_state.get("bus_osecac"):
            # Mostrar resultados de OSECAC
            mask = df_osecac_busq.apply(lambda row: all(p in str(row).lower() for p in st.session_state.bus_osecac.lower().split()), axis=1)
            for i, row in df_osecac_busq[mask].iterrows():
                st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with cols[1]:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
        st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# 4. GESTIONES
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha ficha-practica">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        re = df_especialistas[df_especialistas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in re.iterrows():
            st.markdown(f'<div class="ficha ficha-especialista">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 6. AGENDAS
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ PANEL"):
        if st.text_input("Clave de edición:", type="password", key="ed_pass") == "2026":
            with st.form("n_form", clear_on_submit=True):
                m = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
