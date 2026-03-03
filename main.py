import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
ID_CARPETA_DRIVE = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"
ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"
URL_LECTURA_CHAT = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"

def conectar_robot():
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds), build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

# --- 2. INTERFAZ DEL PORTAL ---
st.set_page_config(page_title="Portal OSECAC", layout="wide")

st.title("🚀 PORTAL DE GESTIÓN OSECAC")

# --- SECCIONES ANTERIORES (1 a 6) ---
# Aquí irían tus buscadores y demás herramientas que ya tenías.
# Si los borraste, podés pegarlos arriba de la sección 7.

# --- 3. SECCIÓN 7: NOVEDADES Y COMUNICADOS ---
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=True):
    
    st.markdown("### ✍️ Publicar Novedad")
    with st.form("form_novedades", clear_on_submit=True):
        mensaje = st.text_area("Escribí tu comunicado aquí:")
        adjuntos = st.file_uploader("Adjuntar archivos (Podés elegir varios):", accept_multiple_files=True)
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA")

        if enviar:
            if mensaje:
                client_sheets, service_drive = conectar_robot()
                if client_sheets and service_drive:
                    try:
                        links = []
                        # Subida de archivos
                        if adjuntos:
                            for arc in adjuntos:
                                meta = {'name': arc.name, 'parents': [ID_CARPETA_DRIVE]}
                                media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
                                f = service_drive.files().create(body=meta, media_body=media, fields='id, webViewLink').execute()
                                # Permiso público para evitar error de cuota 403
                                service_drive.permissions().create(fileId=f['id'], body={'type': 'anyone', 'role': 'viewer'}).execute()
                                links.append(f.get('webViewLink'))

                        # Guardar en Excel
                        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                        links_str = " | ".join(links) if links else "Sin adjuntos"
                        hoja = client_sheets.open_by_key(ID_EXCEL_CHAT).sheet1
                        hoja.append_row([fecha, mensaje, links_str])
                        
                        st.success("¡Publicado con éxito!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error técnico al subir: {e}")
            else:
                st.warning("Por favor, escribí un mensaje.")

    st.divider()

    # --- LECTURA DE NOVEDADES ---
    st.markdown("### 📬 Últimos Comunicados")
    try:
        df_novedades = pd.read_csv(URL_LECTURA_CHAT)
        if not df_novedades.empty:
            for i, fila in df_novedades.iloc[::-1].iterrows():
                with st.container(border=True):
                    col_texto, col_btn = st.columns([3, 1])
                    with col_texto:
                        st.caption(f"📅 {fila.iloc[0]}")
                        st.write(f"**{fila.iloc[1]}**")
                    with col_btn:
                        links_raw = str(fila.iloc[2])
                        if "http" in links_raw:
                            for l in links_raw.split(" | "):
                                st.link_button("📄 Ver Adjunto", l)
        else:
            st.info("No hay novedades registradas.")
    except:
        st.info("Esperando nuevos comunicados...")
