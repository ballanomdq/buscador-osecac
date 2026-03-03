import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import time

# --- 1. CONFIGURACIÓN DE CONEXIÓN (La llave mágica) ---
def guardar_novedad_en_sheet(fecha, mensaje, link):
    try:
        # Esto lee tus secretos de Streamlit
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        
        # ID de tu Excel
        ID_EXCEL = "1vQYQEeH8WWh8EK3ee3HLnSmW0VHPu9LTfXsCRdGuVPoIAa-qzdSZxjwfjq2UgitFU0MG2mRdX8wCzEb"
        sheet = client.open_by_key(ID_EXCEL).sheet1
        
        # Agregamos la fila: Fecha, Mensaje, Link
        sheet.append_row([fecha, mensaje, link])
        return True
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return False

# --- 2. INTERFAZ DE PRUEBA ---
st.title("🧪 Prueba de Novedades Permanente")

# Formulario de carga
with st.expander("✏️ CARGAR NUEVA NOVEDAD", expanded=True):
    with st.form("form_prueba"):
        msg = st.text_area("Escribí algo:")
        boton = st.form_submit_button("📢 PUBLICAR")
        
        if boton:
            if msg:
                fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
                with st.spinner("Guardando en Google Sheets..."):
                    exito = guardar_novedad_en_sheet(fecha_hoy, msg, "sin_link")
                
                if exito:
                    st.success("✅ ¡Se guardó en el Excel!")
                    time.sleep(1)
                    st.rerun() # Esto obliga a la app a recargar y mostrar lo nuevo
            else:
                st.warning("Escribí un mensaje primero.")

st.markdown("---")

# Visualización de lo que hay en el Excel
st.subheader("📢 Novedades leídas del Excel")

# URL de lectura pública (CSV)
URL_LECTURA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQYQEeH8WWh8EK3ee3HLnSmW0VHPu9LTfXsCRdGuVPoIAa-qzdSZxjwfjq2UgitFU0MG2mRdX8wCzEb/pub?gid=0&single=true&output=csv"

try:
    # Agregamos un parámetro aleatorio para evitar que el navegador guarde cache viejo
    df = pd.read_csv(f"{URL_LECTURA}&cache={time.time()}")
    if not df.empty:
        for i, row in df.iloc[::-1].iterrows(): # De más nuevo a más viejo
            st.info(f"📅 {row.iloc[0]}\n\n{row.iloc[1]}")
    else:
        st.write("El Excel está vacío.")
except Exception as e:
    st.error(f"No se pudo leer el Excel: {e}")
