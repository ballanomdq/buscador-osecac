import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import plotly.express as px
import base64

st.set_page_config(layout="wide", page_title="Informe de Útiles")

st.title("📊 INFORME DE PEDIDOS DE ÚTILES")
st.markdown("---")

st.write("✅ 1. Llegamos hasta aquí")

# ========== CONFIGURACIÓN ==========
SPREADSHEET_ID = "1eaujMJahDPn7YBpHeGKG_pSIvxjosnD6f2MHXLfngbI"
SHEET_NAME = "Respuestas de formulario 1"

st.write("✅ 2. Configuración cargada")

# ========== FUNCIÓN PARA CARGAR DATOS ==========
@st.cache_data(ttl=300)
def cargar_datos_utiles():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

st.write("✅ 3. Función definida")

# Intentar cargar datos para ver si hay error inmediato
df_raw = cargar_datos_utiles()
st.write(f"✅ 4. Datos cargados: {len(df_raw)} filas")

# ========== INTERFAZ DE USUARIO ==========
st.sidebar.write("### 🧪 Barra lateral visible")
with st.sidebar:
    st.header("🔍 Filtros")
    año = st.number_input("Año", min_value=2020, max_value=2030, value=2026, step=1)
    mes = st.selectbox("Mes", options=list(range(1,13)), 
                       format_func=lambda x: datetime(2000, x, 1).strftime('%B'), 
                       index=datetime.today().month-1)
    dia_inicio = st.number_input("Día desde", min_value=1, max_value=31, value=1)
    dia_fin = st.number_input("Día hasta", min_value=1, max_value=31, value=15)
    agencias_seleccionadas = st.multiselect("Agencias (vacío = todas)", 
                                            options=["MIRAMAR", "M CHIQUITA", "MECHONGUE", "GESELL", "DOLORES", "MONOLITO",
                                                     "PINAMAR", "S CLEMENTE", "MAR DE AJO", "MAIPU", "S TERESITA", "MADARIAGA",
                                                     "PIRAN", "VIDAL"])
    generar = st.button("📊 GENERAR INFORME", type="primary")

st.write("✅ 5. Barra lateral creada correctamente")

if generar:
    st.write("✅ Botón presionado. Procesando...")
    # Aquí iría el procesamiento, pero lo omitimos por ahora
    st.info("Informe aún no implementado en modo prueba")
