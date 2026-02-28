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

# --- SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{
        "id": "0",
        "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.",
        "fecha": "22/02/2026 00:00"
    }]

# ================= ESTILO 2026 MODERNO =================
st.markdown("""
<style>

/* Ocultar menú y sidebar */
[data-testid="stSidebar"], 
[data-testid="stSidebarNav"],
#MainMenu, footer, header {
    display: none !important;
}

/* Fondo moderno sin animaciones */
.stApp {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
}

/* Texto general */
.stMarkdown p, label {
    color: #ffffff !important;
}

/* === EXPANDERS CORREGIDOS DEFINITIVAMENTE === */

div[data-testid="stExpander"] details summary {
    background-color: rgba(30, 41, 59, 0.85) !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    padding: 14px 18px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}

/* Hover */
div[data-testid="stExpander"] details summary:hover {
    background-color: rgba(56, 189, 248, 0.25) !important;
}

/* Cuando está abierto */
div[data-testid="stExpander"] details[open] summary {
    background-color: rgba(56, 189, 248, 0.35) !important;
}

/* Quitar fondo blanco interno */
div[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
}

/* Tarjetas modernas */
.ficha {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    color: #ffffff !important;
}

/* Bordes de color */
.ficha-tramite { border-left: 6px solid #fbbf24; }
.ficha-agenda { border-left: 6px solid #38bdf8; }
.ficha-practica { border-left: 6px solid #10b981; }
.ficha-especialista { border-left: 6px solid #8b5cf6; }
.ficha-novedad { border-left: 6px solid #ff4b4b; }

/* Botones link */
.stLinkButton a {
    background-color: rgba(30, 41, 59, 0.8) !important;
    color: #ffffff !important;
    border: 1px solid rgba(56,189,248,0.5) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}

.stLinkButton a:hover {
    background-color: #38bdf8 !important;
    color: #000000 !important;
}

/* Inputs */
div[data-baseweb="input"] {
    background-color: #ffffff !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
}

input {
    color: #000000 !important;
    font-weight: bold !important;
}

.block-container {
    max-width: 1100px !important;
    padding-top: 2rem !important;
}

/* Header */
.header-master {
    text-align: center;
    margin-bottom: 20px;
}

.titulo-mini {
    font-weight: 800;
    font-size: 1.5rem;
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-master">
    <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
</div>
""", unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <center>
            <img src="data:image/png;base64,{img_b64}" 
            style="width:90px; margin-bottom:25px;">
        </center>
    """, unsafe_allow_html=True)
except:
    pass

st.markdown("---")

# ================= EXPANDERS DE EJEMPLO =================

with st.expander("📂 1. NOMENCLADORES"):
    st.write("Contenido...")

with st.expander("📝 2. PEDIDOS"):
    st.write("Contenido...")

with st.expander("🌐 3. PÁGINAS ÚTILES"):
    st.write("Contenido...")

with st.expander("📂 4. GESTIONES / DATOS"):
    st.write("Contenido...")

with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    st.write("Contenido...")

with st.expander("📞 6. AGENDAS / MAILS"):
    st.write("Contenido...")

with st.expander("📢 7. NOVEDADES", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(
            f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>',
            unsafe_allow_html=True
        )
