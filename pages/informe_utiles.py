import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

st.set_page_config(layout="wide", page_title="Informe de Útiles")

# ========== ESTILOS FUERTES PARA VISIBILIDAD ==========
st.markdown("""
<style>
    /* Fondo general claro, texto negro */
    .stApp {
        background-color: white !important;
    }
    .stMarkdown, .stTitle, .stSubheader, label, .st-bb {
        color: black !important;
    }
    /* Tabla en pantalla: bordes negros, fondo blanco, letra negra grande */
    .dataframe {
        font-size: 18px !important;
        font-family: Arial, sans-serif !important;
        border-collapse: collapse !important;
        width: 100% !important;
        background-color: white !important;
        color: black !important;
    }
    .dataframe th, .dataframe td {
        border: 2px solid #000000 !important;
        padding: 10px 8px !important;
        text-align: center !important;
        vertical-align: middle !important;
        background-color: white !important;
        color: black !important;
    }
    .dataframe th {
        background-color: #f0f0f0 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    /* Botón grande y vistoso */
    div.stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        margin-top: 20px !important;
    }
    div.stButton > button:hover {
        background-color: #004999 !important;
        transform: scale(1.02);
    }
    /* Ocultar elementos de Streamlit que molestan */
    #MainMenu, footer, header {
        display: none !important;
    }
    /* Para la impresión: títulos verticales y hoja A4 apaisada */
    @media print {
        body {
            margin: 0.5cm;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .stApp, .stMarkdown, .stButton, .stSelectbox, .stNumberInput, .stMultiSelect, .stTitle, .stSubheader {
            display: none !important;
        }
        .printable-area {
            display: block !important;
        }
        .dataframe {
            font-size: 11pt !important;
            width: 100% !important;
        }
        .dataframe th {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            height: 120px;
            white-space: nowrap;
            font-size: 10pt !important;
            background-color: #e0e0e0 !important;
            color: black !important;
            border: 1px solid black !important;
        }
        .dataframe td {
            border: 1px solid black !important;
            padding: 4px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== TÍTULO ==========
st.title("📊 INFORME DE PEDIDOS DE ÚTILES")
st.markdown("---")

# ========== CONFIGURACIÓN ==========
SPREADSHEET_ID = "1eaujMJahDPn7YBpHeGKG_pSIvxjosnD6f2MHXLfngbI"
SHEET_NAME = "Respuestas de formulario 1"

AGENCIAS_TODAS = [
    "MIRAMAR", "M CHIQUITA", "MECHONGUE", "GESELL", "DOLORES", "MONOLITO",
    "PINAMAR", "S CLEMENTE", "MAR DE AJO", "MAIPU", "S TERESITA", "MADARIAGA",
    "PIRAN", "VIDAL"
]

# ========== FUNCIÓN CARGAR DATOS ==========
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

# ========== PROCESAR INFORME ==========
def procesar_informe(df, mes, anio, dia_inicio, dia_fin, agencias_seleccionadas):
    fecha_col = 'FECHA' if 'FECHA' in df.columns else 'Marca temporal'
    df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['fecha'])
    
    df = df[(df['fecha'].dt.year == anio) & 
            (df['fecha'].dt.month == mes) &
            (df['fecha'].dt.day >= dia_inicio) &
            (df['fecha'].dt.day <= dia_fin)]
    
    if agencias_seleccionadas:
        df = df[df['AGENCIA'].isin(agencias_seleccionadas)]
    
    if df.empty:
        return None
    
    excluir = [
        'Marca temporal', 'FECHA', '¿A dónde pertenece?', 'AGENCIA', 'SECTOR',
        'MODELO_SOPORTE', 'OTROS PEDIDOS ARREGLADO', 'OTROS PEDIDOS',
        'MODELO DE IMPRESORA', 'TONER CANTIDAD', 'fecha'
    ]
    items = [
        col for col in df.columns 
        if col not in excluir 
        and not col.startswith('OTROS') 
        and not col.startswith('MODELO')
        and col != 'fecha'
    ]
    
    for item in items:
        df[item] = pd.to_numeric(df[item], errors='coerce').fillna(0)
    
    df_agrupado = df.groupby('AGENCIA')[items].sum().reset_index()
    df_pivot = df_agrupado.set_index('AGENCIA').T
    df_pivot['TOTAL ÍTEM'] = df_pivot.sum(axis=1)
    total_por_agencia = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL AGENCIA'] = total_por_agencia
    
    return df_pivot

# ========== FILTROS ==========
st.subheader("🔍 Filtros de búsqueda")
col1, col2, col3, col4 = st.columns(4)
with col1:
    año = st.number_input("📅 Año", min_value=2020, max_value=2030, value=2026, step=1)
with col2:
    mes = st.selectbox("📆 Mes", options=list(range(1,13)), 
                       format_func=lambda x: datetime(2000, x, 1).strftime('%B'), 
                       index=datetime.today().month-1)
with col3:
    dia_inicio = st.number_input("📅 Día desde", min_value=1, max_value=31, value=1)
with col4:
    dia_fin = st.number_input("📅 Día hasta", min_value=1, max_value=31, value=15)

agencias_seleccionadas = st.multiselect("🏢 Agencias (vacío = todas)", options=AGENCIAS_TODAS)

# Botón para generar informe (grande y centrado)
col_btn = st.columns([1,2,1])
with col_btn[1]:
    generar = st.button("📊 GENERAR INFORME", use_container_width=True)

# ========== GENERACIÓN Y VISUALIZACIÓN ==========
if generar:
    df_raw = cargar_datos_utiles()
    if df_raw.empty:
        st.warning("No se pudieron cargar los datos. Revisá la conexión a Google Sheets.")
    else:
        with st.spinner("Procesando pedidos..."):
            informe = procesar_informe(df_raw, mes, año, dia_inicio, dia_fin, agencias_seleccionadas)
        
        if informe is None:
            st.info("📭 No hay pedidos para los filtros seleccionados.")
            st.session_state['informe'] = None
        else:
            st.session_state['informe'] = informe
            st.session_state['filtros'] = (año, mes, dia_inicio, dia_fin)
            st.success(f"✅ Informe generado para {datetime(año, mes, 1).strftime('%B %Y')} (días {dia_inicio} al {dia_fin})")
            
            # Mostrar tabla dentro de un div que será visible en impresión
            st.markdown('<div class="printable-area">', unsafe_allow_html=True)
            st.dataframe(informe.style.format("{:.0f}"), use_container_width=True, height=500)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón grande para descargar PDF (abrir diálogo de impresión)
            st.markdown("---")
            col_pdf = st.columns([1,2,1])
            with col_pdf[1]:
                if st.button("📥 DESCARGAR INFORME EN PDF", use_container_width=True):
                    # Cambiamos el título de la página para que el PDF tenga nombre sugerido
                    mes_nombre = datetime(año, mes, 1).strftime('%B_%Y')
                    nombre_sugerido = f"Informe_Utiles_{mes_nombre}.pdf"
                    st.markdown(f"""
                        <script>
                            document.title = "{nombre_sugerido}";
                            window.print();
                        </script>
                    """, unsafe_allow_html=True)
