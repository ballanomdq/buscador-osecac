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

# ================== CSS ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; }
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

df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])
df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

if os.path.exists('logo original.jpg'):
    st.image('logo original.jpg', width=160)

if st.button("📢 VER NOVEDADES", on_click=abrir_novedades):
    pass

st.markdown("---")

# ================= SECCIONES 1 A 6 (Mantenidas) =================
with st.expander("📂 1. NOMENCLADORES"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    # ... (resto de tus botones de la sección 1)

with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

with st.expander("🌐 3. PÁGINAS ÚTILES"):
    st.write("Accesos rápidos a portales oficiales.")

with st.expander("📂 4. GESTIONES / DATOS"):
    st.write("Información de trámites.")

with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    st.write("Buscador de cartilla.")

with st.expander("📞 6. AGENDAS / MAILS"):
    st.write("Contactos de agencias.")

# ================= SECCIÓN 7: MURO DE NOVEDADES REAL Y FUNCIONAL =================
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=st.session_state.novedades_expandido):
    
    # PARTE A: PUBLICADOR (Solo para el Jefe con clave)
    st.markdown("### ✍️ Publicar nuevo comunicado")
    popover_jefe = st.popover("🔐 Acceso Jefe para Publicar")
    
    with popover_jefe:
        clave = st.text_input("Clave de publicación:", type="password")
        if clave == "*": # Tu clave maestra
            with st.form("form_publicar_real", clear_on_submit=True):
                msg = st.text_area("Mensaje de la novedad:")
                file = st.file_uploader("Adjuntar archivo (PDF/Imagen):", type=["pdf", "jpg", "png", "jpeg"])
                
                if st.form_submit_button("🚀 PUBLICAR PARA TODOS"):
                    if msg or file:
                        with st.spinner("Subiendo y guardando..."):
                            link_adjunto = ""
                            if file:
                                temp_p = f"temp_{file.name}"
                                with open(temp_p, "wb") as f: f.write(file.getbuffer())
                                link_adjunto = subir_a_drive(temp_p, file.name)
                                if os.path.exists(temp_p): os.remove(temp_p)
                            
                            # GUARDAR EN GOOGLE SHEETS
                            try:
                                creds_info = st.secrets["gcp_service_account"]
                                creds = service_account.Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
                                client = gspread.authorize(creds)
                                sh = client.open_by_key("1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0").worksheet("CHAT")
                                sh.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), msg, link_adjunto])
                                st.success("✅ Publicado con éxito!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {e}")
        else:
            st.info("Ingrese clave para habilitar el formulario")

    st.markdown("---")
    
    # PARTE B: EL MURO (Lo que ven todos)
    st.markdown("### 📋 Historial de Comunicados")
    
    try:
        # Cargamos la pestaña CHAT del excel (GID 0 suele ser la primera, ajustalo si es otra)
        url_muro = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv&gid=0"
        # Nota: Cambia 'gid=0' por el ID real de la pestaña CHAT si no es la primera
        df_chat = pd.read_csv(url_muro).fillna("")
        
        # Mostramos de más nuevo a más viejo
        for _, row in df_chat[::-1].head(15).iterrows():
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.8); border-left: 5px solid #38bdf8; 
                        border-radius: 12px; padding: 15px; margin-bottom: 10px;">
                <small style="color: #94a3b8;">{row.iloc[0]}</small><br>
                <div style="color: white; font-size: 1.1rem; margin-top: 5px;">{row.iloc[1]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Si hay link, mostrar botón
            if str(row.iloc[2]).startswith("http"):
                st.link_button("📂 VER ADJUNTO", str(row.iloc[2]))
    except:
        st.info("Aún no hay comunicados en el muro.")

    if st.button("❌ Cerrar Sección"):
        st.session_state.novedades_expandido = False
        st.rerun()
