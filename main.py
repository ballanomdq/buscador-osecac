import streamlit as st
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
from PIL import Image
import io
import json

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIÓN PARA SUBIR ARCHIVOS ---
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
        st.error(f"Error técnico: {str(e)}")
        return None

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00", "archivo_links": []}]
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = {st.session_state.historial_novedades[0]["id"]}
if 'pass_novedades_valida' not in st.session_state:
    st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state:
    st.session_state.novedades_expandido = False

def toggle_faba():
    st.session_state.osecac_check = not st.session_state.faba_check

def toggle_osecac():
    st.session_state.faba_check = not st.session_state.osecac_check

def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] details[open] summary { border: 2px solid #ff4b4b !important; box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; color: #ffffff !important; }
.stLinkButton a { background-color: rgba(30, 41, 59, 0.8) !important; color: #ffffff !important; border: 1px solid rgba(56,189,248,0.5) !important; border-radius: 10px !important; text-decoration: none !important; }
.stLinkButton a:hover { background-color: #38bdf8 !important; color: #000000 !important; }
div[data-baseweb="input"] { background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
input { color: #000000 !important; font-weight: bold !important; }
.block-container { max-width: 1100px !important; padding-top: 1rem !important; }
.stButton > button {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
}
.stButton > button:has(span:contains("🔴")) {
    background: linear-gradient(145deg, #ff4b4b, #ff0000) !important;
    border: 2px solid #ff4b4b !important;
    animation: parpadeo 1.2s infinite;
}
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
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

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:2.8rem; color:#ffffff; margin-bottom:1.2rem;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

# LOGO
col_logo = st.columns([1,1,1])
with col_logo[1]:
    if os.path.exists('logo original.jpg'):
        st.image('logo original.jpg', use_container_width=True)

st.markdown('<div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin:1rem 0;">', unsafe_allow_html=True)

# LÓGICA NOVEDADES NUEVAS
ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
hay_novedades_nuevas = ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas

# --- BOTONES DE ACCIÓN ---
col_btns = st.columns([1,1,1], gap="small")
with col_btns[0]:
    if hay_novedades_nuevas:
        st.button("🔴 NOVEDAD", use_container_width=True, on_click=abrir_novedades)
    else:
        st.button("📢 NOVEDADES", use_container_width=True, on_click=abrir_novedades)

with col_btns[1]:
    # PLAN B: Enlace directo a la subpágina
    st.link_button("📩 IR A RECLAMOS", "https://buscador-osecac.streamlit.app/reclamos", use_container_width=True)

with col_btns[2]:
    popover_novedades = st.popover("✏️ Administrar", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
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
        st.write("### Administrar Novedades")
        accion = st.radio("Acción:", ["➕ Agregar", "🗑️ Eliminar"])
        if accion == "➕ Agregar":
            with st.form("nueva_novedad_form"):
                m = st.text_area("Mensaje:")
                up = st.file_uploader("Adjuntos:", accept_multiple_files=True)
                if st.form_submit_button("📢 PUBLICAR"):
                    links = []
                    if up:
                        for f in up:
                            temp = f"temp_{f.name}"
                            with open(temp, "wb") as file: file.write(f.getbuffer())
                            l = subir_a_drive(temp, f.name)
                            if l: links.append(l)
                            if os.path.exists(temp): os.remove(temp)
                    st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "archivo_links": links})
                    st.rerun()
        elif accion == "🗑️ Eliminar":
            idx = st.selectbox("Seleccionar:", range(len(st.session_state.historial_novedades)), format_func=lambda x: st.session_state.historial_novedades[x]['mensaje'][:30])
            if st.button("🗑️ ELIMINAR"):
                st.session_state.historial_novedades.pop(idx)
                st.rerun()

# ================== SECCIONES PRINCIPALES ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
    with c2: st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)
    
    df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
    term = st.text_input("🔍 Buscar código o descripción:")
    if term:
        res = df_u[df_u.apply(lambda r: term.lower() in str(r).lower(), axis=1)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items()])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 3. PÁGINAS ÚTILES", expanded=False):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

# 4. GESTIONES
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 7. NOVEDADES (Aparición por botón)
if st.session_state.novedades_expandido:
    st.markdown("---")
    st.markdown("### 📢 COMUNICADOS")
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-left:5px solid #ff4b4b;"><b>{n["fecha"]}</b><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
        if n.get("archivo_links"):
            for l in n["archivo_links"]: st.link_button("📂 Ver Adjunto", l)
    if st.button("❌ Cerrar"):
        st.session_state.novedades_expandido = False
        st.rerun()
