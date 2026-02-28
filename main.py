import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import io

# 1. CONFIGURACIÓN DE PÁGINA (MODO MODERNO)
st.set_page_config(
    page_title="OSECAC MDP - Portal 2026", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. EL MOTOR DE ESTILO (CSS) ---
st.markdown("""
    <style>
    /* Fondo General Profundo */
    .stApp { background-color: #050914; color: #ffffff; }

    /* MENU LATERAL (SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #0b1e3b !important;
        border-right: 2px solid #2563eb;
    }
    
    /* BOTONES DEL MENU LATERAL */
    .stSidebar .stButton > button {
        width: 100% !important;
        background-color: transparent !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        text-align: left !important;
        padding: 10px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
    }
    .stSidebar .stButton > button:hover {
        background-color: #2563eb !important;
        color: white !important;
        border-color: white !important;
    }

    /* BOTONES "PASTILLA" CENTRALES (CHICOS, NO INVASIVOS) */
    div.stLinkButton > a {
        background-color: #003366 !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 20px !important;
        padding: 6px 18px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        display: inline-block !important;
        width: auto !important;
        transition: all 0.3s ease !important;
    }
    div.stLinkButton > a:hover {
        box-shadow: 0 0 12px #38bdf8 !important;
        transform: translateY(-1px) !important;
    }

    /* VENTANA DE NOVEDADES (TIPO CARD) */
    .novedad-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-left: 5px solid #2563eb;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }

    /* INPUTS BLANCOS (PARA QUE SE VEA LO QUE ESCRIBIS) */
    div[data-baseweb="input"] { background-color: white !important; border-radius: 8px !important; }
    input { color: black !important; font-weight: bold !important; }
    
    /* TITULOS */
    h1, h2, h3 { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

# URLs (Tus planillas)
URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcv (acortado para el ejemplo)",
}

# --- 4. SISTEMA DE NAVEGACIÓN ---
if 'seccion' not in st.session_state:
    st.session_state.seccion = "NOTIFICACIONES"
if 'novedades_pro' not in st.session_state:
    st.session_state.novedades_pro = [{"fecha": "27/02/2026", "titulo": "SISTEMA ONLINE", "msg": "Portal actualizado con éxito.", "file": None, "fname": ""}]

def ir_a(nombre):
    st.session_state.seccion = nombre

# --- 5. SIDEBAR (MENU MINIMALISTA) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>OSECAC</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("📢 NOTIFICACIONES"): ir_a("NOTIFICACIONES")
    if st.button("📂 NOMENCLADORES"): ir_a("NOMENCLADORES")
    if st.button("📝 PEDIDOS"): ir_a("PEDIDOS")
    if st.button("🌐 PÁGINAS ÚTILES"): ir_a("PAGINAS")
    if st.button("📞 AGENDAS"): ir_a("AGENDAS")
    st.markdown("---")
    pass_jefe = st.text_input("🔑 ACCESO JEFE", type="password")

# --- 6. CONTENIDO CENTRAL ---

# SECCIÓN: NOTIFICACIONES (LA NUEVA VENTANA)
if st.session_state.seccion == "NOTIFICACIONES":
    st.markdown("## 📢 Panel de Novedades")
    
    # PANEL DEL JEFE
    if pass_jefe == "2026":
        with st.expander("🛠️ PUBLICAR NUEVO (JEFE)"):
            with st.form("pub_jefe", clear_on_submit=True):
                t_n = st.text_input("Título:")
                m_n = st.text_area("Mensaje:")
                f_n = st.file_uploader("Adjuntar PDF o Imagen:", type=['pdf', 'jpg', 'png', 'jpeg'])
                if st.form_submit_button("LANZAR COMUNICADO"):
                    data_file = f_n.getvalue() if f_n else None
                    st.session_state.novedades_pro.insert(0, {
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "titulo": t_n.upper(),
                        "msg": m_n,
                        "file": data_file,
                        "fname": f_n.name if f_n else ""
                    })
                    st.rerun()

    # LISTADO DE NOVEDADES
    for n in st.session_state.novedades_pro:
        st.markdown(f"""
        <div class="novedad-box">
            <b style="color:#38bdf8;">{n['fecha']}</b><br>
            <h4 style="margin:5px 0;">{n['titulo']}</h4>
            <p style="font-size:15px;">{n['msg']}</p>
        </div>
        """, unsafe_allow_html=True)
        if n['file']:
            st.download_button(f"📥 Descargar: {n['fname']}", n['file'], file_name=n['fname'], key=n['fecha'])

# SECCIÓN: NOMENCLADORES
elif st.session_state.seccion == "NOMENCLADORES":
    st.markdown("## 📂 Consulta de Nomencladores")
    st.link_button("📘 NOMENCLADOR IA (ABRIR)", "https://notebooklm.google.com/...")
    st.markdown("---")
    st.text_input("🔍 Escribí para buscar en la base de datos...", key="bus_nom")

# SECCIÓN: PEDIDOS
elif st.session_state.seccion == "PEDIDOS":
    st.markdown("## 📝 Gestión de Pedidos")
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("🍼 LECHES", "https://docs.google.com/forms/...")
    with c2: st.link_button("📦 SUMINISTROS", "https://docs.google.com/forms/...")
    with c3: st.link_button("📊 ESTADO", "https://lookerstudio.google.com/...")

# SECCIÓN: PÁGINAS
elif st.session_state.seccion == "PAGINAS":
    st.markdown("## 🌐 Enlaces Externos")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com")
    with col2:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("🆔 CODEM", "https://servicioswww.anses.gob.ar/ooss2/")

# SECCIÓN: AGENDAS
elif st.session_state.seccion == "AGENDAS":
    st.markdown("## 📞 Agenda y Contactos")
    st.text_input("🔍 Buscar contacto...", key="bus_age")

# Pie de página
st.markdown("<br><hr><center><small>OSECAC MDP - Portal de Autogestión 2026</small></center>", unsafe_allow_html=True)
