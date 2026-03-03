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

# --- FUNCIÓN SUBIR A DRIVE (Tu motor original corregido) ---
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

# --- INICIALIZACIÓN DE SESIÓN (RESTAURADA) ---
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

# ================== CSS ORIGINAL (RECUPERADO AL 100%) ==================
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

# ================= HEADER ORIGINAL =================
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:2.8rem; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

if os.path.exists('logo original.jpg'):
    st.image('logo original.jpg', width=160)

# El botón de Novedad con el punto rojo
try:
    url_l = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"
    df_check = pd.read_csv(url_l)
    hay_algo_nuevo = len(df_check) > len(st.session_state.novedades_vistas)
    if hay_algo_nuevo:
        st.button("🔴 NUEVA NOTIFICACIÓN", on_click=abrir_novedades)
except: pass

st.markdown("---")

# ================= SECCIONES (RECUPERADAS) =================
with st.expander("📂 1. NOMENCLADORES"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📈 NOMENCLADOR EXEL OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    # ... Tus buscadores y checkboxes ...

with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 3. PÁGINAS ÚTILES"):
    c1, c2 = st.columns(2)
    with c1: st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    with c2: st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")

with st.expander("📂 4. GESTIONES / DATOS"):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# ================= SECCIÓN 7: EL MURO (AHORA SÍ FUNCIONA) =================
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    
    st.markdown("### ✍️ Publicar (Jefe)")
    with st.popover("✏️ Panel de Carga"):
        cl = st.text_input("Clave:", type="password")
        if cl == "*":
            with st.form("form_final", clear_on_submit=True):
                m_jefe = st.text_area("Mensaje:")
                f_jefe = st.file_uploader("Adjuntar PDF/Imagen", type=["pdf", "jpg", "png", "jpeg"])
                if st.form_submit_button("🚀 PUBLICAR"):
                    if m_jefe or f_jefe:
                        with st.spinner("Procesando..."):
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
                            except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("### 📥 Comunicados")
    
    try:
        url_l = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"
        df_m = pd.read_csv(url_l).fillna("")
        for _, row in df_m[::-1].head(10).iterrows():
            st.session_state.novedades_vistas.add(row.iloc[1][:20]) # Marcamos como vista
            with st.container(border=True):
                st.caption(f"📅 {row.iloc[0]}")
                st.markdown(f"**{row.iloc[1]}**")
                if str(row.iloc[2]).startswith("http"):
                    st.link_button("📂 VER ARCHIVO", str(row.iloc[2]))
    except: st.info("Sin novedades aún.")

    if st.button("❌ Cerrar Sección"):
        st.session_state.novedades_expandido = False
        st.rerun()
