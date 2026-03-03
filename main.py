import streamlit as st
import gspread
from google.oauth2 import service_account
from datetime import datetime

# Función para conectar y escribir en TU archivo CHAT
def probar_conexion_chat():
    try:
        # Lee la llave que pegamos en los Secrets de Streamlit
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = service_account.Credentials.from_service_account_info(
            info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        
        # EL ID DE TU ARCHIVO "CHAT"
        ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"
        
        # Abre la primera hoja del archivo
        sheet = client.open_by_key(ID_EXCEL_CHAT).sheet1
        
        # Prepara los datos (Fecha y un mensaje de éxito)
        fecha_ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
        fila_nueva = [fecha_ahora, "¡SÍ! El portal se conectó con éxito", "OK"]
        
        # Agrega la fila al final del Excel
        sheet.append_row(fila_nueva)
        return True
    except Exception as e:
        st.error(f"Error al intentar escribir en el Excel: {e}")
        return False

# --- INTERFAZ DE LA APP ---
st.title("Prueba de Comunicación 📡")
st.write("Si todo está bien configurado, al presionar el botón verás aparecer una nueva fila en tu archivo CHAT.")

if st.button("ENVIAR MENSAJE DE PRUEBA AL EXCEL"):
    with st.spinner("Conectando con Google Sheets..."):
        if probar_conexion_chat():
            st.success("¡LO LOGRAMOS! Revisá tu archivo CHAT, debería haber una nueva fila.")
            st.balloons()
