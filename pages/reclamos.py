import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from google.oauth2 import service_account
import gspread

st.set_page_config(page_title="Sistema de Reclamos - OSECAC", layout="centered")

# --- CONFIGURACIÓN ---
SHEET_ID_RECLAMOS = "1I6mCu3ko1R1-YOxS_9FHPt0TXnCbuYJXNxihZ0E_UZs"  # Tu planilla

# --- FUNCIÓN PARA GUARDAR EN SHEETS ---
def guardar_en_sheets(fecha, agencia, sector, mensaje, nombre_archivo):
    try:
        creds_info = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_info)
        sheet = gc.open_by_key(SHEET_ID_RECLAMOS).sheet1
        # Guardamos el nombre del archivo en lugar del link
        sheet.append_row([fecha, agencia, sector, mensaje, f"Archivo adjunto: {nombre_archivo}" if nombre_archivo else "Sin archivo"])
        return True
    except Exception as e:
        st.error(f"Error al guardar en Sheets: {str(e)}")
        return False

# --- FUNCIÓN PARA CREAR LINK DE DESCARGA ---
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">📥 Descargar archivo adjunto</a>'
    return href

# ================== CSS ORIGINAL (COMO EN MAIN.PY) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
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
div[data-baseweb="input"] { background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
input { color: #000000 !important; font-weight: bold !important; }
.block-container { max-width: 1100px !important; padding-top: 1rem !important; }
.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
}
.stFileUploader {
    background-color: #1e293b !important;
    border: 2px dashed #38bdf8 !important;
    border-radius: 10px !important;
    padding: 10px !important;
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
            nombre_archivo = ""
            download_link = ""
            
            if archivo is not None:
                # Guardar temporalmente
                temp_path = f"temp_{archivo.name}"
                with open(temp_path, "wb") as f:
                    f.write(archivo.getbuffer())
                
                # Crear link de descarga
                download_link = get_binary_file_downloader_html(temp_path, archivo.name)
                nombre_archivo = archivo.name
                
                # Limpiar
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # Guardar en Sheets
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            exito = guardar_en_sheets(fecha_actual, agencia, sector, mensaje, nombre_archivo)

            if exito:
                st.success("✅ ¡Reclamo guardado correctamente!")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)
                    st.info("📌 El archivo no se subió a Drive, pero podés descargarlo desde este enlace.")
            else:
                st.error("No se pudo guardar el reclamo. Revisá los permisos de la planilla.")

if st.button("⬅️ Volver al Buscador"):
    st.switch_page("main.py")
