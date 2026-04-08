import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import base64

st.set_page_config(layout="wide", page_title="Informe de Útiles")

# Inyectamos CSS para mejorar la tabla en pantalla y para la impresión
st.markdown("""
<style>
    /* Estilo para la tabla en pantalla */
    .stDataFrame {
        font-size: 18px !important;
    }
    .dataframe {
        font-size: 18px !important;
        border-collapse: collapse !important;
        width: 100%;
    }
    .dataframe th, .dataframe td {
        border: 2px solid #cccccc !important;
        padding: 12px 8px !important;
        text-align: center !important;
        vertical-align: middle !important;
    }
    .dataframe th {
        background-color: #1e293b !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Estilos específicos para la impresión (PDF) */
    @media print {
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            margin: 1cm;
        }
        .stApp, .stMarkdown, .stButton, .stSelectbox, .stNumberInput, .stMultiSelect {
            display: none !important;
        }
        /* Mostrar solo la tabla */
        .print-only {
            display: block !important;
        }
        .dataframe {
            font-size: 12pt !important;
            width: 100% !important;
            border-collapse: collapse !important;
        }
        .dataframe th, .dataframe td {
            border: 1px solid black !important;
            padding: 6px 4px !important;
            text-align: center !important;
        }
        .dataframe th {
            background-color: #e0e0e0 !important;
            color: black !important;
            font-weight: bold;
            /* Rotar texto verticalmente para ahorrar ancho */
            writing-mode: vertical-rl;
            text-orientation: mixed;
            height: 120px;
            white-space: nowrap;
        }
        /* Asegurar que la tabla no se corte */
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

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

# ========== FILTROS EN LA PÁGINA ==========
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

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    generar = st.button("📊 GENERAR INFORME", type="primary", use_container_width=True)
with col_btn2:
    # Botón para imprimir/PDF (solo se activa si ya hay un informe generado)
    imprimir = st.button("🖨️ Imprimir / Guardar PDF", use_container_width=True, disabled=not st.session_state.get('informe_listo', False))

# ========== CARGA Y GENERACIÓN ==========
df_raw = cargar_datos_utiles()

if generar:
    if df_raw.empty:
        st.warning("No se pudieron cargar los datos. Revisá la conexión a Google Sheets.")
    else:
        with st.spinner("Procesando pedidos..."):
            informe = procesar_informe(df_raw, mes, año, dia_inicio, dia_fin, agencias_seleccionadas)
        
        if informe is None:
            st.info("📭 No hay pedidos para los filtros seleccionados.")
            st.session_state['informe_listo'] = False
        else:
            st.session_state['informe'] = informe
            st.session_state['informe_listo'] = True
            st.success(f"✅ Informe generado para {datetime(año, mes, 1).strftime('%B %Y')} (días {dia_inicio} al {dia_fin})")
            
            # Mostrar tabla con estilo mejorado (en pantalla)
            st.markdown('<div class="print-only">', unsafe_allow_html=True)
            st.dataframe(informe.style.format("{:.0f}"), use_container_width=True, height=600)
            st.markdown('</div>', unsafe_allow_html=True)

# Si ya hay un informe guardado en sesión, mostrarlo (para que persista al hacer clic en imprimir)
if st.session_state.get('informe_listo', False) and not generar:
    informe = st.session_state['informe']
    st.success(f"✅ Informe actual (puedes imprimirlo)")
    st.dataframe(informe.style.format("{:.0f}"), use_container_width=True, height=600)

# Lógica para imprimir (abre diálogo de impresión del navegador)
if imprimir and st.session_state.get('informe_listo', False):
    # Inyectamos JavaScript para abrir la ventana de impresión
    st.markdown("""
        <script>
            window.print();
        </script>
    """, unsafe_allow_html=True)
