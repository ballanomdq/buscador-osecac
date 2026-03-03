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

# --- FUNCIÓN SUBIR A DRIVE (Tu motor original) ---
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

# --- INICIALIZACIÓN DE SESIÓN ---
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

# ================== CSS (Mantenido) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
.ficha { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; }
.stButton > button { background: linear-gradient(145deg, #1e293b, #0f172a) !important; color: white !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
.stButton > button:hover { background: #38bdf8 !important; color: black !important; }
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

# Secciones 1 a 6 siguen cargando sus datos...
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])
df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; color:white; font-size:2.8rem;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
if os.path.exists('logo original.jpg'):
    st.image('logo original.jpg', width=160)

if st.button("📢 VER NOVEDADES DEL JEFE", on_click=abrir_novedades):
    pass
st.markdown("---")

# ================= SECCIONES (Resumen) =================
with st.expander("📂 1. NOMENCLADORES"):
    st.info("Utilice el buscador para encontrar códigos y valores.")

with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

# ... Aquí irían las secciones 3, 4, 5 y 6 que ya tienes configuradas ...

# ================= SECCIÓN 7: EL MURO DE COMUNICADOS DEFINITIVO =================
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=st.session_state.novedades_expandido):
    
    st.markdown("### ✍️ Publicar Comunicado (Acceso Jefe)")
    
    # 1. FORMULARIO DE CARGA
    with st.popover("🔐 Habilitar Publicación"):
        pass_jefe = st.text_input("Ingrese Clave:", type="password")
        if pass_jefe == "*":
            with st.form("form_nuevo_comunicado", clear_on_submit=True):
                msg = st.text_area("Mensaje:")
                archivo = st.file_uploader("Adjuntar PDF o Imagen", type=["pdf", "jpg", "png", "jpeg"])
                
                if st.form_submit_button("🚀 PUBLICAR PARA TODAS LAS AGENCIAS"):
                    if msg or archivo:
                        with st.spinner("Subiendo archivo y guardando..."):
                            link_final = ""
                            if archivo:
                                t_path = f"temp_{archivo.name}"
                                with open(t_path, "wb") as f: f.write(archivo.getbuffer())
                                link_final = subir_a_drive(t_path, archivo.name)
                                if os.path.exists(t_path): os.remove(t_path)
                            
                            try:
                                info = dict(st.secrets["gcp_service_account"])
                                info["private_key"] = info["private_key"].replace("\\n", "\n")
                                creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
                                client = gspread.authorize(creds)
                                sh = client.open_by_key(ID_EXCEL_CHAT).worksheet("CHAT")
                                sh.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), msg, link_final])
                                st.success("✅ ¡Comunicado publicado!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error de conexión: {e}")
        else:
            st.info("Ingrese clave para publicar.")

    st.markdown("---")
    st.markdown("### 📋 Historial de Comunicados")

    # 2. LECTURA DEL MURO (Pública y sin fallos)
    try:
        url_lectura = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"
        df_muro = pd.read_csv(url_lectura).fillna("")
        
        if not df_muro.empty:
            for _, row in df_muro[::-1].head(10).iterrows():
                with st.container(border=True):
                    st.caption(f"📅 {row.iloc[0]}")
                    st.markdown(f"**{row.iloc[1]}**")
                    if str(row.iloc[2]).startswith("http"):
                        st.link_button("📂 VER / DESCARGAR ADJUNTO", str(row.iloc[2]))
        else:
            st.info("No hay novedades publicadas aún.")
    except:
        st.info("El muro aparecerá cuando se realice la primera publicación.")

    if st.button("❌ Cerrar Sección"):
        st.session_state.novedades_expandido = False
        st.rerun()
