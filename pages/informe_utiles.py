import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from io import BytesIO
import base64

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

# ========== FUNCIÓN PARA GENERAR PDF ==========
def generar_pdf(informe, mes_nombre, año):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            rightMargin=10*mm, leftMargin=10*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(name='Titulo', parent=styles['Title'], fontSize=14, alignment=1, spaceAfter=12)
    subtitulo_style = ParagraphStyle(name='Subtitulo', parent=styles['Normal'], fontSize=10, alignment=1, spaceAfter=20)
    
    # Título
    titulo = Paragraph(f"Informe de Pedidos de Útiles - {mes_nombre} {año}", titulo_style)
    elementos.append(titulo)
    elementos.append(Spacer(1, 5*mm))
    
    # Convertir DataFrame a lista de listas
    # Primero, obtener los nombres de las columnas (agencias) y filas (items)
    columnas = list(informe.columns)
    filas = list(informe.index)
    
    # Construir datos para la tabla
    data = []
    # Encabezados: primera fila con los nombres de agencias (incluyendo TOTAL AGENCIA)
    data.append(['Ítem / Agencia'] + columnas)
    # Agregar cada fila de ítem
    for idx in filas:
        row = [idx] + [informe.loc[idx, col] for col in columnas]
        data.append(row)
    
    # Crear tabla
    # Estimamos un ancho de columna: la primera columna más ancha, las demás iguales
    num_cols = len(columnas) + 1
    col_widths = [50*mm] + [25*mm] * (num_cols - 1)  # ajustable
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(style)
    
    elementos.append(table)
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

# Botón para generar informe
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
            mes_nombre = datetime(año, mes, 1).strftime('%B')
            st.success(f"✅ Informe generado para {mes_nombre} {año} (días {dia_inicio} al {dia_fin})")
            
            # Mostrar tabla en pantalla (ahora sí, bien visible)
            st.markdown('<div style="background-color: white; padding: 10px; border-radius: 5px;">', unsafe_allow_html=True)
            st.dataframe(informe.style.format("{:.0f}"), use_container_width=True, height=500)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón de descarga de PDF
            st.markdown("---")
            col_pdf = st.columns([1,2,1])
            with col_pdf[1]:
                if st.button("📥 DESCARGAR INFORME EN PDF", use_container_width=True):
                    # Generar PDF
                    pdf_buffer = generar_pdf(informe, mes_nombre, año)
                    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                    # Crear link de descarga
                    href = f'<a href="data:application/pdf;base64,{b64}" download="Informe_Utiles_{mes_nombre}_{año}.pdf" style="text-decoration: none; background-color: #28a745; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; display: inline-block; text-align: center;">📄 Haga clic aquí si la descarga no comienza automáticamente</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ PDF generado correctamente. La descarga debería comenzar automáticamente. Si no, usa el enlace de arriba.")
