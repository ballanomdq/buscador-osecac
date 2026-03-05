import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread

st.set_page_config(page_title="Sistema de Reclamos - OSECAC", layout="centered")

# --- CONFIGURACIÓN ---
# IMPORTANTE: Esta carpeta debe estar en un DRIVE COMPARTIDO (Shared Drive)
FOLDER_ID_RECLAMOS = "ID_DE_LA_CARPETA_EN_DRIVE_COMPARTIDO"  # <--- CAMBIÁ ESTO
SHEET_ID_RECLAMOS = "1I6mCu3ko1R1-YOxS_9FHPt0TXnCbuYJXNxihZ0E_UZs"

# --- FUNCIÓN PARA SUBIR ARCHIVOS A DRIVE (compatible con Shared Drive) ---
def subir_a_drive(file_path, file_name):
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': file_name, 
            'parents': [FOLDER_ID_RECLAMOS]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink',
            supportsAllDrives=True  # <--- necesario para Shared Drives
        ).execute()
        # Hacer público (opcional)
        try:
            service.permissions().create(
                fileId=file.get('id'), 
                body={'type': 'anyone', 'role': 'reader'},
                supportsAllDrives=True
            ).execute()
        except:
            pass
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error al subir archivo: {str(e)}")
        return None

# --- FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS ---
def guardar_en_sheets(fecha, agencia, sector, mensaje, link_archivo):
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID_RECLAMOS).sheet1
        nueva_fila = [fecha, agencia, sector, mensaje, link_archivo]
        sheet.append_row(nueva_fila)
        return True
    except Exception as e:
        st.error(f"Error al guardar en la planilla: {str(e)}")
        return False

# --- CSS MÍNIMO para que se vea bien ---
st.markdown("""
<style>
.stApp { background-color: #0f172a; }
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: white !important; }
.stButton > button {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
}
.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📩 Centro de Reclamos y Consultas")
st.write("Seleccioná tu agencia y el sector para iniciar el trámite.")

agencias = [
    "MAIPU", "S TERESITA", "MAR DE AJO", "MIRAMAR", "PINAMAR",
    "S CLEMENTE", "MECHONGUE", "DOLORES", "M CHIQUITA", "GESELL",
    "VIDAL", "PIRAN", "MADARIAGA"
]

sectores = [
    "auditoria medica", "contaduria", "reintegros", "medicamentos",
    "empadronamiento", "despacho", "sistemas", "fiscalizacion",
    "personal", "Sebastian Lopez"
]

with st.form("form_reclamo"):
    agencia = st.selectbox("Agencia", agencias)
    sector = st.selectbox("Sector Destino", sectores)
    mensaje = st.text_area("Detalle del Reclamo/Consulta")
    archivo = st.file_uploader("Adjuntar documentación (PDF/Imagen)", type=["pdf", "jpg", "png"])
    
    enviar = st.form_submit_button("ENVIAR RECLAMO")
    
    if enviar:
        if not mensaje:
            st.error("Por favor, escribí un mensaje.")
        else:
            link_archivo = ""
            if archivo is not None:
                with st.spinner("Subiendo archivo a Drive..."):
                    temp_path = f"temp_{archivo.name}"
                    with open(temp_path, "wb") as f:
                        f.write(archivo.getbuffer())
                    link_archivo = subir_a_drive(temp_path, archivo.name)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    if link_archivo:
                        st.success("✅ Archivo subido correctamente")
                    else:
                        st.warning("No se pudo subir el archivo")
            
            with st.spinner("Guardando reclamo en la planilla..."):
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
                exito = guardar_en_sheets(fecha_actual, agencia, sector, mensaje, link_archivo)
                
            if exito:
                st.success(f"✅ ¡Reclamo guardado!")
                if link_archivo:
                    st.markdown(f"📎 [Ver archivo adjunto]({link_archivo})")
            else:
                st.error("No se pudo guardar el reclamo")

if st.button("⬅️ Volver al Buscador"):
    st.switch_page("main.py")
