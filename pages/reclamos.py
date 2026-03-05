import streamlit as st
import pandas as as pd
from datetime import datetime
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="Sistema de Reclamos - OSECAC", layout="centered")

# --- CONFIGURACIÓN ---
FOLDER_ID_RECLAMOS = "1Ej7K9XGapPg802j-ssehKo4DjX_KlGKc"  # Tu carpeta
SHEET_ID_RECLAMOS = "1I6mCu3ko1R1-YOxS_9FHPt0TXnCbuYJXNxihZ0E_UZs"  # Tu planilla

# --- FUNCIÓN PARA SUBIR ARCHIVOS CON TU CUENTA PERSONAL ---
def subir_a_drive_personal(file_path, file_name):
    try:
        # Usar las mismas credenciales de servicio pero para autenticación personal
        creds_info = st.secrets["gcp_service_account"]
        
        # Crear credenciales con alcance de Drive
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_info,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Construir el servicio
        service = build('drive', 'v3', credentials=creds)
        
        # Subir archivo
        file_metadata = {
            'name': file_name,
            'parents': [FOLDER_ID_RECLAMOS]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Hacer público
        try:
            service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except:
            pass
            
        return file.get('webViewLink')
        
    except Exception as e:
        st.error(f"Error al subir archivo: {str(e)}")
        return None

# --- FUNCIÓN PARA GUARDAR EN SHEETS (igual que antes) ---
def guardar_en_sheets(fecha, agencia, sector, mensaje, link_archivo):
    try:
        creds_info = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID_RECLAMOS).sheet1
        sheet.append_row([fecha, agencia, sector, mensaje, link_archivo])
        return True
    except Exception as e:
        st.error(f"Error en Sheets: {str(e)}")
        return False

# --- CSS ---
st.markdown("""
<style>
.stApp { background-color: #0f172a; }
h1, h2, h3, h4, h5, h6, p, label { color: white !important; }
.stButton>button { background: #1e293b; color: white; border: 2px solid #38bdf8; }
.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox div { background-color: white; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("📩 Centro de Reclamos y Consultas")

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
                    link_archivo = subir_a_drive_personal(temp_path, archivo.name)
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
