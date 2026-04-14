import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import json
import math
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

# Estilos Visuales
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; color: white; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h2 style="color:white;margin:0;">Fiscalización - Deuda Presunta</h2></div>', unsafe_allow_html=True)

# Mapeo de Columnas
MAPEO_EXCEL_A_TABLA = {
    'DELEGACION': 'delegacion', 'LOCALIDAD': 'localidad', 'CUIT': 'cuit',
    'RAZON SOCIAL': 'razon_social', 'DEUDA PRESUNTA': 'deuda_presunta',
    'CP': 'cp', 'CALLE': 'calle', 'NUMERO': 'numero', 'PISO': 'piso',
    'DPTO': 'dpto', 'FECHARELDEPENDENCIA': 'fechareldependencia',
    'EMAIL': 'email', 'TEL_DOM_LEGAL': 'tel_dom_legal', 'TEL_DOM_REAL': 'tel_dom_real',
    'ULTIMA ACTA': 'ultima_acta', 'DESDE': 'desde', 'HASTA': 'hasta',
    'DETECTADO': 'detectado', 'ESTADO': 'estado', 'FECHA_PAGO_OBL': 'fecha_pago_obl',
    'EMPL 10-2025': 'empl_10_2025', 'EMP 11-2025': 'emp_11_2025',
    'EMPL 12-2025': 'empl_12_2025', 'ACTIVIDAD': 'actividad', 'SITUACION': 'situacion'
}

def limpiar_valor(valor):
    """Convierte valores problemáticos a None o formatos compatibles con JSON"""
    if pd.isna(valor) or valor is None: return None
    if isinstance(valor, float):
        if math.isnan(valor) or math.isinf(valor): return None
        if valor.is_integer(): return int(valor)
        return valor
    if isinstance(valor, (pd.Timestamp, datetime)): return valor.isoformat()
    if isinstance(valor, str) and valor.strip() == '': return None
    return valor

tab1, tab2, tab3 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Datos", "📧 Solicitar Actas"])

with tab1:
    uploaded_file = st.file_uploader("Subir Excel", type=["xls", "xlsx"])
    
    if uploaded_file:
        try:
            # 1. Leer archivo
            engine = 'xlrd' if uploaded_file.name.endswith('.xls') else 'openpyxl'
            df_raw = pd.read_excel(uploaded_file, engine=engine)
            
            # 2. BLINDAJE ANTI-NAN: Reemplazar todos los vacíos antes de procesar
            df_raw = df_raw.replace({np.nan: None, float('nan'): None})
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            # 3. Mapear columnas
            df_final = pd.DataFrame()
            for col_excel, col_tabla in MAPEO_EXCEL_A_TABLA.items():
                if col_excel in df_raw.columns:
                    df_final[col_tabla] = df_raw[col_excel].apply(limpiar_valor)
                else:
                    st.error(f"Falta columna: {col_excel}")
                    st.stop()

            # 4. Datos adicionales
            df_final['leg'] = None
            df_final['vto'] = None
            df_final['mail_enviado'] = 'NO'
            df_final['acta'] = None
            df_final['fecha_carga'] = datetime.now().isoformat()
            df_final['estado_gestion'] = 'PENDIENTE'

            st.success(f"Registros listos: {len(df_final)}")
            
            if st.button("Confirmar Carga en Base de Datos", type="primary"):
                with st.spinner("Subiendo..."):
                    # Convertimos a lista de diccionarios y realizamos una última limpieza
                    registros = df_final.to_dict(orient='records')
                    
                    # Insertar en bloques para evitar saturar la conexión
                    for i in range(0, len(registros), 50):
                        lote = registros[i:i+50]
                        supabase.table("padron_deuda_presunta").insert(lote).execute()
                    
                    st.balloons()
                    st.markdown('<div class="success-box">¡Carga Exitosa!</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error técnico: {str(e)}")

with tab2:
    st.markdown("### Editor de Registros")
    res = supabase.table("padron_deuda_presunta").select("*").execute()
    if res.data:
        df_edit = pd.DataFrame(res.data)
        columnas = ['id', 'cuit', 'razon_social', 'leg', 'vto', 'estado_gestion']
        st.data_editor(df_edit[columnas], disabled=['id', 'cuit', 'razon_social'], key="editor")
    else:
        st.info("No hay datos.")

with tab3:
    st.info("Sección de envío de emails próximamente.")
