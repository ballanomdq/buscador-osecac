import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE IDs (YA CONFIGURADOS PARA VOS) ---
ID_CARPETA_DRIVE = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"
ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"
# URL de lectura rápida (CSV)
URL_LECTURA_CHAT = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"

# --- FUNCIÓN PARA CONECTAR AL ROBOT ---
def conectar_robot():
    info = dict(st.secrets["gcp_service_account"])
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    creds = service_account.Credentials.from_service_account_info(info, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds), build('drive', 'v3', credentials=creds)

# --- SECCIÓN 7: NOVEDADES Y CHAT ---
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=True):
    
    # --- SUBSECCIÓN: PUBLICAR ---
    st.markdown("### ✍️ Publicar Novedad")
    with st.form("form_novedades", clear_on_submit=True):
        mensaje = st.text_area("Escribí tu comunicado aquí:", placeholder="Ej: Nueva resolución disponible...")
        adjuntos = st.file_uploader("Adjuntar archivos (Podés elegir varios):", accept_multiple_files=True)
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA")

        if enviar:
            if mensaje:
                try:
                    client_sheets, service_drive = conectar_robot()
                    links = []

                    # Subida de archivos a Drive
                    for arc in adjuntos:
                        meta = {'name': arc.name, 'parents': [ID_CARPETA_DRIVE]}
                        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
                        f = service_drive.files().create(body=meta, media_body=media, fields='id, webViewLink').execute()
                        # Permiso público de lectura
                        service_drive.permissions().create(fileId=f['id'], body={'type': 'anyone', 'role': 'viewer'}).execute()
                        links.append(f.get('webViewLink'))

                    # Guardar en Excel
                    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                    links_str = " | ".join(links) if links else "Sin adjuntos"
                    hoja = client_sheets.open_by_key(ID_EXCEL_CHAT).sheet1
                    hoja.append_row([fecha, mensaje, links_str])
                    
                    st.success("¡Publicado correctamente!")
                    st.balloons()
                    st.rerun() # Recarga para mostrar lo nuevo arriba
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Escribí un mensaje primero.")

    st.divider()

    # --- SUBSECCIÓN: VER NOVEDADES (LECTURA) ---
    st.markdown("### 📬 Últimos Comunicados")
    try:
        # Leemos el Excel
        df = pd.read_csv(URL_LECTURA_CHAT)
        if not df.empty:
            # Mostramos de más nuevo a más viejo
            for i, fila in df.iloc[::-1].iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"📅 {fila.iloc[0]}")
                        st.markdown(f"**{fila.iloc[1]}**")
                    with col2:
                        # Si hay links, crear botones
                        links_raw = str(fila.iloc[2])
                        if "http" in links_raw:
                            lista_links = links_raw.split(" | ")
                            for idx, l in enumerate(lista_links):
                                st.link_button(f"📄 Ver Adjunto {idx+1 if len(lista_links)>1 else ''}", l)
        else:
            st.info("No hay comunicados guardados.")
    except:
        st.error("Todavía no hay datos o el archivo está vacío.")
