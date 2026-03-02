import streamlit as st
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import time

# --- CONFIGURACIÓN DRIVE ---
# Asegúrate de que este ID sea correcto
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w" 

st.set_page_config(page_title="Test Subida Drive")
st.title("🧪 Test de Subida a Google Drive")

# --- FUNCIÓN DE SUBIDA MODIFICADA PARA DETECTAR ERRORES ---
def subir_a_drive_debug(file_path, file_name):
    try:
        # TUS TOKENS ACTUALES
        REFRESH_TOKEN = "1//04wm475WZT5NrCgYIARAAGAQSNwF-L9IrV1Wnk6hUFxlYb0yoyKnATPFKvPc_2QCZ4bkqmuWnBVreI6v5DFKr-u8q6lCJfZFLwOg"
        ACCESS_TOKEN = "ya29.a0ATkoCc5F9aJgCfAbzdQvZYGc_wCBLgiWOyTwOjWDj1vsMAPc8stwgbHXOhxPdcghSqKXJx8mtmp_WA6kZAO_2aENwpQE-3CzcHvTiYkUTKdDfxxE5BddS7QrB0SESbasc9vshiLDAdq6wErDbgIAiU835mB7hGX-LDCSVKD4L68cpFhHco6eeRdHVRnC2kJ4D7fkuS8aCgYKARgSARQSFQHGX2MiLUw0IpD5eh_zyfX7QeL-og0206"

        creds = OAuthCredentials(
            token=ACCESS_TOKEN,
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id="407408718192.apps.googleusercontent.com",
            client_secret="",
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        # FORZAR REFRESH PARA VER SI AQUÍ ESTÁ EL PROBLEMA
        if creds.refresh_token:
            st.info("Intentando actualizar token...")
            creds.refresh(Request())
            st.success("Token actualizado con éxito")
        
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)

        st.info("Subiendo archivo...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

        try:
            service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        except:
            pass

        return file.get('webViewLink')

    except Exception as e:
        # ESTO ES LO IMPORTANTE: Imprime el error completo
        print("--- ERROR DETALLADO DE GOOGLE DRIVE ---")
        print(e)                
        print("---------------------------------------")
        st.exception(e) # Muestra el error en pantalla sin borrarlo rápido
        return None

# --- UI PARA PROBAR ---
st.markdown("### Selecciona un archivo para probar")
uploaded_file = st.file_uploader("Archivo de prueba", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    if st.button("🚀 Subir archivo a Drive"):
        # Crear un archivo temporal
        temp_path = f"test_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Llamar a la función de subida
        link = subir_a_drive_debug(temp_path, uploaded_file.name)
        
        if link:
            st.success(f"¡Subido con éxito! Link: {link}")
        else:
            st.error("La subida falló.")
        
        # Limpiar
        if os.path.exists(temp_path):
            os.remove(temp_path)
