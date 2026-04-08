import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
import time

st.set_page_config(layout="wide", page_title="Informe de Útiles", initial_sidebar_state="collapsed")

# ========== ESTILOS FUERTES (blanco y negro, legible) ==========
st.markdown("""
<style>
    /* Fondo general blanco */
    .stApp {
        background-color: white !important;
    }
    .main .block-container {
        background-color: white !important;
    }
    /* Todos los textos negros */
    .stMarkdown, .stTitle, .stSubheader, label, .st-bb, .st-at, div, p, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    /* Tabla en pantalla: fondo blanco, texto negro, bordes negros, fuente grande */
    .dataframe {
        font-size: 18px !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
        border-collapse: collapse !important;
        width: 100% !important;
        background-color: white !important;
        color: black !important;
    }
    .dataframe th, .dataframe td {
        border: 2px solid #000000 !important;
        padding: 12px 8px !important;
        text-align: center !important;
        vertical-align: middle !important;
        background-color: white !important;
        color: black !important;
    }
    .dataframe th {
        background-color: #e6e6e6 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    /* Botones grandes */
    div.stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #004999 !important;
    }
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {
        display: none !important;
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

# ========== FUNCIÓN CARGAR DATOS CON REINTENTOS ==========
@st.cache_data(ttl=300)
def cargar_datos_utiles(retries=3):
    for i in range(retries):
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
            if i < retries - 1:
                time.sleep(2 ** i)  # espera exponencial
                continue
            else:
                st.error(f"Error al cargar datos después de {retries} intentos: {e}")
                return pd.DataFrame()
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

# ========== GENERAR PDF CON REPORTLAB ==========
def generar_pdf(df_pivot, titulo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=16, alignment=1, spaceAfter=12)
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=20)
    
    elementos.append(Paragraph(titulo, titulo_style))
    elementos.append(Spacer(1, 10))
    
    # Convertir DataFrame a lista de listas
    data = [df_pivot.columns.tolist()]  # encabezados
    for idx, row in df_pivot.iterrows():
        fila = [idx] + [int(v) if isinstance(v, (int, float)) else v for v in row.tolist()]
        data.append(fila)
    
    # Crear tabla
    tabla = Table(data)
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ])
    tabla.setStyle(estilo_tabla)
    elementos.append(tabla)
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

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

col_btn = st.columns([1,2,1])
with col_btn[1]:
    generar = st.button("📊 GENERAR INFORME", use_container_width=True)

# ========== ESTADO EN SESIÓN ==========
if 'informe' not in st.session_state:
    st.session_state.informe = None

# ========== GENERAR Y MOSTRAR ==========
if generar:
    with st.spinner("Cargando datos desde Google Sheets..."):
        df_raw = cargar_datos_utiles()
    if df_raw.empty:
        st.warning("No se pudieron cargar los datos. Revisá la conexión o intentá más tarde.")
    else:
        with st.spinner("Procesando pedidos..."):
            informe = procesar_informe(df_raw, mes, año, dia_inicio, dia_fin, agencias_seleccionadas)
        
        if informe is None:
            st.info("📭 No hay pedidos para los filtros seleccionados.")
            st.session_state.informe = None
        else:
            st.session_state.informe = informe
            st.session_state.filtros = (año, mes, dia_inicio, dia_fin)
            st.success(f"✅ Informe generado para {datetime(año, mes, 1).strftime('%B %Y')} (días {dia_inicio} al {dia_fin})")
            
            # Mostrar tabla en pantalla
            st.dataframe(informe.style.format("{:.0f}"), use_container_width=True, height=500)
            
            # Botón de descarga de PDF
            titulo_pdf = f"Informe de Útiles - {datetime(año, mes, 1).strftime('%B %Y')}"
            pdf_buffer = generar_pdf(informe, titulo_pdf)
            st.download_button(
                label="📥 DESCARGAR INFORME EN PDF",
                data=pdf_buffer,
                file_name=f"Informe_Utiles_{datetime(año, mes, 1).strftime('%B_%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# Si ya había un informe generado (por si el usuario no quiere generar de nuevo)
if st.session_state.informe is not None and not generar:
    st.dataframe(st.session_state.informe.style.format("{:.0f}"), use_container_width=True, height=500)
    año, mes, dia_inicio, dia_fin = st.session_state.filtros
    titulo_pdf = f"Informe de Útiles - {datetime(año, mes, 1).strftime('%B %Y')}"
    pdf_buffer = generar_pdf(st.session_state.informe, titulo_pdf)
    st.download_button(
        label="📥 DESCARGAR INFORME EN PDF",
        data=pdf_buffer,
        file_name=f"Informe_Utiles_{datetime(año, mes, 1).strftime('%B_%Y')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
