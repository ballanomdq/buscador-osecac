import streamlit as st
import pandas as pd
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NUEVA DIRECCIÓN DE NOVEDADES (TU EXCEL PUBLICADO) ---
URL_NOVEDADES_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQYQEeH8WWh8EK3ee3HLnSmW0VHPu9LTfXsCRdGuVPoIAa-qzdSZxjwfjq2UgitFU0MG2mRdX8wCzEb/pub?gid=0&single=true&output=csv"

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIÓN DEFINITIVA Y PERMANENTE ---
def subir_a_drive(file_path, file_name):
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        try:
            service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        except:
            pass
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error técnico permanente: {str(e)}")
        return None

# --- INICIALIZACIÓN DE SESIÓN ---
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = set()
if 'pass_novedades_valida' not in st.session_state:
    st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state:
    st.session_state.novedades_expandido = False

def toggle_faba():
    if st.session_state.faba_check: st.session_state.osecac_check = False
    else: st.session_state.osecac_check = True

def toggle_osecac():
    if st.session_state.osecac_check: st.session_state.faba_check = False
    else: st.session_state.faba_check = True

def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS (IGUAL AL TUYO) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] details[open] summary { border: 2px solid #ff4b4b !important; box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; color: #ffffff !important; }
.stLinkButton a { background-color: rgba(30, 41, 59, 0.8) !important; color: #ffffff !important; border: 1px solid rgba(56,189,248,0.5) !important; border-radius: 10px !important; }
div[data-baseweb="input"] { background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
input { color: #000000 !important; font-weight: bold !important; }
.stButton > button { background: linear-gradient(145deg, #1e293b, #0f172a) !important; color: white !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
.stButton > button:has(span:contains("🔴")) { background: linear-gradient(145deg, #ff4b4b, #ff0000) !important; border: 2px solid #ff4b4b !important; animation: parpadeo 1.2s infinite; }
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/edit",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/edit",
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/edit",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=1119565576",
}

df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])
df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
# Cargamos novedades desde tu link CSV
df_novedades = cargar_datos(URL_NOVEDADES_CSV)

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; color:white; font-size:2.8rem;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

col_head1, col_head2 = st.columns([1,1])
with col_head1:
    if not df_novedades.empty:
        st.button("🔴 NOVEDAD", on_click=abrir_novedades)

with col_head2:
    popover_novedades = st.popover("✏️ Cargar Novedades")

st.markdown("---")

# ================= POPOVER CARGAR NOVEDADES =================
with popover_novedades:
    st.markdown("### 🔐 Clave Administración")
    if not st.session_state.pass_novedades_valida:
        with st.form("form_novedades_admin"):
            cl_admin = st.text_input("Ingrese Clave:", type="password")
            if st.form_submit_button("✅ OK"):
                if cl_admin == "*":
                    st.session_state.pass_novedades_valida = True
                    st.rerun()
                else: st.error("❌ Clave incorrecta")
    else:
        st.success("✅ Acceso concedido")
        st.write("Para agregar novedades permanentes, usa el Formulario o el Excel compartido.")
        st.info("Esta sección ahora lee directamente de tu Google Sheets.")

# ================== RESTO DE LA APP (TUS EXPANDERS) ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📈 NOMENCLADOR EXEL OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    st.link_button("📈 NOMENCLADOR EXEL FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns([0.4, 1, 0.4, 1])
    with c1:
        if st.checkbox("FABA", key="faba_check", on_change=toggle_faba): pass
    with c4:
        if st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac): pass
    
    term = st.text_input("🔍 Buscar término...", key="bus_nom")
    if st.button("Buscar") and term:
        df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in term.lower().split()), axis=1)
        res = df_u[mask]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# 4. GESTIONES / DATOS
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 7. NOVEDADES (LA PARTE QUE CAMBIÓ PARA LEER TU EXCEL)
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    st.markdown("## 📢 Últimos Comunicados")
    st.markdown("---")
    
    if df_novedades.empty:
        st.info("No hay novedades publicadas en el Excel.")
    else:
        # Recorremos tu Excel (df_novedades) del más nuevo al más viejo
        for i, row in df_novedades.iloc[::-1].iterrows():
            msg = row.get('Mensaje', '')
            fecha = row.get('Fecha', 'Reciente')
            link = row.get('Archivo', None)
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1e293b, #0f172a);
                        border-left: 8px solid #ff4b4b;
                        border-radius: 16px;
                        padding: 25px;
                        margin: 20px 0;">
                <div style="color: #94a3b8; font-size: 0.9rem;">📅 {fecha}</div>
                <div style="color: white; font-size: 1.2rem; white-space: pre-wrap;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if pd.notna(link) and str(link).startswith('http'):
                st.markdown(f'<a href="{link}" target="_blank" style="background: #38bdf8; color: black; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold;">📂 Ver archivo adjunto</a>', unsafe_allow_html=True)

    if st.button("❌ Cerrar Novedades"):
        st.session_state.novedades_expandido = False
        st.rerun()
