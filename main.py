import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- CONFIGURACIÓN ---
ID_CARPETA_DRIVE = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"
ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"
URL_LECTURA_CHAT = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"

def conectar_robot():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds), build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

st.set_page_config(page_title="Portal OSECAC", layout="wide")
st.title("🚀 PORTAL DE GESTIÓN OSECAC")

# --- SECCIÓN 7: NOVEDADES ---
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=True):
    
    with st.form("form_novedades", clear_on_submit=True):
        mensaje = st.text_area("Escribí tu comunicado:")
        adjuntos = st.file_uploader("Adjuntar archivos:", accept_multiple_files=True)
        enviar = st.form_submit_button("🚀 PUBLICAR")

        if enviar and mensaje:
            client_sheets, service_drive = conectar_robot()
            if client_sheets and service_drive:
                try:
                    links = []
                    for arc in adjuntos:
                        # LE DECIMOS QUE EL DUEÑO ES "ANYONE" PARA NO USAR CUOTA DEL ROBOT
                        file_metadata = {
                            'name': arc.name,
                            'parents': [ID_CARPETA_DRIVE]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type, resumable=True)
                        
                        # CREAR EL ARCHIVO
                        file = service_drive.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id, webViewLink'
                        ).execute()

                        # --- SOLUCIÓN AL ERROR 403: TRANSFERIR PERMISO INMEDIATAMENTE ---
                        service_drive.permissions().create(
                            fileId=file.get('id'),
                            body={'type': 'anyone', 'role': 'viewer'}
                        ).execute()
                        
                        links.append(file.get('webViewLink'))

                    # GUARDAR EN EXCEL
                    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                    links_str = " | ".join(links) if links else "Sin adjuntos"
                    client_sheets.open_by_key(ID_EXCEL_CHAT).sheet1.append_row([fecha, mensaje, links_str])
                    
                    st.success("¡Publicado con éxito!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    # Si el error persiste, es que la carpeta no tiene los permisos correctos
                    st.error(f"Error técnico: {e}")

    st.divider()
    # (El resto del código de lectura de novedades sigue igual...)
