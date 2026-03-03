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

# --- CONFIGURACIÓN DRIVE Y EXCEL ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"
ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"

# --- FUNCIÓN SUBIR A DRIVE (Corregida para limpiar la clave) ---
def subir_a_drive(file_path, file_name):
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        try:
            service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        except: pass
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error en Drive: {str(e)}")
        return None

# --- INICIALIZACIÓN DE SESIÓN (RESTAURADA TOTAL) ---
if 'novedades_vistas' not in st.session_state: st.session_state.novedades_vistas = set()
if 'pass_novedades_valida' not in st.session_state: st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state: st.session_state.novedades_expandido = False

def toggle_faba():
    st.session_state.osecac_check = not st.session_state.faba_check
def toggle_osecac():
    st.session_state.faba_check = not st.session_state.osecac_check
def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS ORIGINAL (RECUPERADO) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] details[open] summary { border: 2px solid #ff4b4b !important; box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; color: #ffffff !important; }
.stButton > button {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-size: 1rem !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background: #38bdf8 !important;
    color: black !important;
    transform: scale(1.05) !important;
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

# ================= HEADER ORIGINAL =================
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:2.8rem; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
if os.path.exists('logo original.jpg'):
    st.image('logo original.jpg', width=160)

# Botón parpadeante
st.button("🔴 NOVEDAD", on_click=abrir_novedades)
st.markdown("---")

# ================= SECCIÓN 1: NOMENCLADORES (RESTAURADA) =================
with st.expander("📂 1. NOMENCLADORES"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📈 NOMENCLADOR EXEL OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    st.link_button("📈 NOMENCLADOR EXEL FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    
    c1, c2, c3, c4 = st.columns([0.4, 1, 0.4, 1])
    with c2: st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
    with c4: st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)
    
    opcion = "OSECAC" if st.session_state.osecac_check else "FABA"
    df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
    
    term = st.text_input(f"🔍 Escriba término de búsqueda en {opcion}...", key="busqueda_input")
    if term:
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in term.lower().split()), axis=1)
        results = df_u[mask]
        for i, row in results.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# ================= SECCIONES 2 A 6 (RESTAURADAS) =================
with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 3. PÁGINAS ÚTILES"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")

with st.expander("📂 4. GESTIONES / DATOS"):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha">📑 <b>PRÁCTICA:</b> {row["PRÁCTICA"]}</div>', unsafe_allow_html=True)

with st.expander("📞 6. AGENDAS / MAILS"):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# ================= SECCIÓN 7: EL CHAT (CON FIX PARA JWT) =================
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    st.markdown("### ✍️ Publicar Comunicado (Jefe)")
    with st.popover("🔐 Acceso"):
        clave = st.text_input("Clave:", type="password")
        if clave == "*":
            with st.form("form_chat", clear_on_submit=True):
                m_jefe = st.text_area("Mensaje:")
                f_jefe = st.file_uploader("Adjunto:", type=["pdf", "jpg", "png", "jpeg"])
                if st.form_submit_button("🚀 PUBLICAR"):
                    if m_jefe or f_jefe:
                        with st.spinner("Subiendo..."):
                            link_f = ""
                            if f_jefe:
                                tp = f"temp_{f_jefe.name}"
                                with open(tp, "wb") as f: f.write(f_jefe.getbuffer())
                                link_f = subir_a_drive(tp, f_jefe.name)
                                if os.path.exists(tp): os.remove(tp)
                            try:
                                info = dict(st.secrets["gcp_service_account"])
                                info["private_key"] = info["private_key"].replace("\\n", "\n")
                                creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
                                client = gspread.authorize(creds)
                                sh = client.open_by_key(ID_EXCEL_CHAT).worksheet("CHAT")
                                sh.append_row([datetime.now().strftime("%d/%m %H:%M"), m_jefe, link_f])
                                st.success("¡Publicado!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"Error de Firma JWT: Revisa tus Secrets. Detalle: {e}")

    st.markdown("---")
    try:
        url_l = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"
        df_m = pd.read_csv(url_l).fillna("")
        for _, row in df_m[::-1].head(10).iterrows():
            with st.container(border=True):
                st.caption(f"📅 {row.iloc[0]}")
                st.markdown(f"**{row.iloc[1]}**")
                if str(row.iloc[2]).startswith("http"):
                    st.link_button("📂 VER ARCHIVO", str(row.iloc[2]))
    except: st.info("Sin comunicados.")
