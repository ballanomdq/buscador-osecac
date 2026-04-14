import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import math
import numpy as np

# Configuración de página
st.set_page_config(page_title="Fiscalización - OSECAC", layout="wide")

# Conexión a Supabase
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

# Estilos
st.markdown("""<style>.main-header { background-color: #1e293b; padding: 1rem; border-radius: 8px; border-left: 5px solid #3b82f6; color: white; }</style>""", unsafe_allow_html=True)
st.markdown('<div class="main-header"><h2>Fiscalización - Control Total</h2></div>', unsafe_allow_html=True)

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

def ultra_limpieza(d):
    """Limpia diccionarios de cualquier valor NaN o Infinitos para que Supabase no explote"""
    for k, v in d.items():
        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                d[k] = None
        elif pd.isna(v):
            d[k] = None
    return d

tab1, tab2, tab3 = st.tabs(["📊 Carga Blindada", "✏️ Editor", "📧 Actas"])

with tab1:
    uploaded_file = st.file_uploader("Subir Padrón", type=["xls", "xlsx"])
    if uploaded_file:
        try:
            engine = 'xlrd' if uploaded_file.name.endswith('.xls') else 'openpyxl'
            df_raw = pd.read_excel(uploaded_file, engine=engine)
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            df_final = pd.DataFrame()
            for col_excel, col_tabla in MAPEO_EXCEL_A_TABLA.items():
                if col_excel in df_raw.columns:
                    df_final[col_tabla] = df_raw[col_excel]
                else:
                    st.error(f"Falta: {col_excel}")
                    st.stop()

            # Rellenar campos vacíos por defecto
            df_final['leg'] = ""
            df_final['vto'] = None
            df_final['mail_enviado'] = 'NO'
            df_final['acta'] = ""
            df_final['fecha_carga'] = datetime.now().isoformat()
            df_final['estado_gestion'] = 'PENDIENTE'

            st.info(f"Registros detectados: {len(df_final)}")
            
            if st.button("🚀 INICIAR CARGA SEGURA"):
                with st.spinner("Limpiando y subiendo..."):
                    # LA CLAVE: Convertimos a diccionarios y limpiamos CADA UNO
                    lista_dicts = df_final.to_dict(orient='records')
                    registros_limpios = [ultra_limpieza(r) for r in lista_dicts]
                    
                    # Subir por bloques
                    for i in range(0, len(registros_limpios), 50):
                        lote = registros_limpios[i:i+50]
                        supabase.table("padron_deuda_presunta").insert(lote).execute()
                    
                    st.success("¡Carga terminada con éxito!")
                    st.balloons()
        except Exception as e:
            st.error(f"Error detectado: {e}")

with tab2:
    st.write("Datos en la base:")
    res = supabase.table("padron_deuda_presunta").select("id, cuit, razon_social, leg, vto").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data))
