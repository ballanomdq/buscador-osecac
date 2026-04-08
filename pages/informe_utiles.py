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

# ========== ESTILOS ==========
st.markdown("""
<style>
    .stApp { background-color: white !important; }
    .main .block-container { background-color: white !important; }
    /* Textos negros en toda la app */
    .stMarkdown, label, div, p, h1, h2, h3, h4, h5, h6, span {
        color: #000000 !important;
    }
    /* Botones */
    div.stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        border: none !important;
    }
    div.stButton > button:hover { background-color: #004999 !important; }
    #MainMenu, footer, header { display: none !important; }

    /* ── TABLA HTML PERSONALIZADA ── */
    .tabla-utiles {
        border-collapse: collapse;
        width: 100%;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 15px;
        margin-top: 10px;
    }
    /* Encabezado con texto VERTICAL */
    .tabla-utiles thead tr th {
        border: 2px solid #000000;
        padding: 6px 4px;
        text-align: center;
        vertical-align: bottom;
        background-color: #d0d0d0;
        font-weight: bold;
        color: #000000 !important;
        white-space: nowrap;
        font-size: 13px;
    }
    /* Texto vertical en encabezados de columnas (excepto la primera) */
    .tabla-utiles thead tr th.col-rotada {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        transform: rotate(180deg);
        height: 120px;
        width: 36px;
        min-width: 36px;
        max-width: 36px;
        padding: 8px 2px;
    }
    /* Primera columna (nombres de ítems) */
    .tabla-utiles thead tr th.col-item {
        min-width: 160px;
        text-align: left;
        padding-left: 8px;
    }
    /* Celdas de datos */
    .tabla-utiles tbody tr td {
        border: 1.5px solid #000000;
        padding: 5px 4px;
        text-align: center;
        color: #000000 !important;
        background-color: #ffffff;
        font-size: 14px;
    }
    /* Primera columna de datos (nombre del ítem) */
    .tabla-utiles tbody tr td:first-child {
        text-align: left;
        padding-left: 8px;
        font-weight: 600;
        background-color: #f0f0f0;
        color: #000000 !important;
        min-width: 160px;
    }
    /* Fila TOTAL AGENCIA (última fila) */
    .tabla-utiles tbody tr.fila-total td {
        background-color: #d0d0d0 !important;
        font-weight: bold !important;
        color: #000000 !important;
        font-size: 14px;
    }
    /* Columna TOTAL ÍTEM (última columna) */
    .tabla-utiles tbody tr td.col-total-item {
        background-color: #e8e8e8 !important;
        font-weight: bold !important;
        color: #000000 !important;
    }
    /* Celdas con valor 0: gris muy claro para distinguir */
    .tabla-utiles tbody tr td.cero {
        color: #bbbbbb !important;
    }
    /* Hover en filas */
    .tabla-utiles tbody tr:hover td {
        background-color: #f5f5f5 !important;
    }
    .tabla-utiles tbody tr:hover td:first-child {
        background-color: #e5e5e5 !important;
    }
    .tabla-utiles tbody tr.fila-total:hover td {
        background-color: #c4c4c4 !important;
    }
    /* Scroll horizontal */
    .tabla-contenedor {
        overflow-x: auto;
        width: 100%;
        border: 1px solid #cccccc;
        border-radius: 6px;
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

# ========== CARGAR DATOS ==========
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
                time.sleep(2 ** i)
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
    df = df[
        (df['fecha'].dt.year == anio) &
        (df['fecha'].dt.month == mes) &
        (df['fecha'].dt.day >= dia_inicio) &
        (df['fecha'].dt.day <= dia_fin)
    ]
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

    # ── Eliminar agencias que tienen todo en 0 ──
    cols_agencias = [c for c in df_pivot.columns if c != 'TOTAL ÍTEM']
    df_pivot = df_pivot[[c for c in df_pivot.columns
                          if c == 'TOTAL ÍTEM' or df_pivot[c].sum() > 0]]

    df_pivot['TOTAL ÍTEM'] = df_pivot.sum(axis=1)
    total_por_agencia = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL AGENCIA'] = total_por_agencia

    return df_pivot

# ========== TABLA HTML ==========
def tabla_html(df_pivot):
    """Genera HTML con encabezados verticales, texto 100% negro, ceros en gris."""
    columnas = df_pivot.columns.tolist()
    filas = df_pivot.index.tolist()

    # Encabezado
    thead = '<thead><tr>'
    thead += '<th class="col-item">ÍTEM</th>'
    for col in columnas:
        if col == 'TOTAL ÍTEM':
            thead += f'<th class="col-rotada" style="background-color:#c0c0c0;">{col}</th>'
        else:
            thead += f'<th class="col-rotada">{col}</th>'
    thead += '</tr></thead>'

    # Cuerpo
    tbody = '<tbody>'
    for idx, fila_nombre in enumerate(filas):
        es_total = (fila_nombre == 'TOTAL AGENCIA')
        clase_fila = ' class="fila-total"' if es_total else ''
        tbody += f'<tr{clase_fila}>'
        tbody += f'<td>{fila_nombre}</td>'
        for j, col in enumerate(columnas):
            val = df_pivot.loc[fila_nombre, col]
            val_int = int(val) if not pd.isna(val) else 0
            es_total_col = (col == 'TOTAL ÍTEM')
            clases_td = []
            if es_total_col:
                clases_td.append('col-total-item')
            if val_int == 0 and not es_total:
                clases_td.append('cero')
            clase_td = f' class="{" ".join(clases_td)}"' if clases_td else ''
            texto = str(val_int) if val_int != 0 else '·'
            tbody += f'<td{clase_td}>{texto}</td>'
        tbody += '</tr>'
    tbody += '</tbody>'

    html = f'''
    <div class="tabla-contenedor">
      <table class="tabla-utiles">
        {thead}
        {tbody}
      </table>
    </div>
    '''
    return html

# ========== GENERAR PDF ==========
def generar_pdf(df_pivot, titulo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        rightMargin=1*cm, leftMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )
    elementos = []
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo', parent=styles['Title'],
        fontSize=14, alignment=1, spaceAfter=10,
        textColor=colors.black
    )
    elementos.append(Paragraph(titulo, titulo_style))
    elementos.append(Spacer(1, 8))

    # Preparar datos de la tabla PDF
    columnas = df_pivot.columns.tolist()
    filas = df_pivot.index.tolist()

    # Encabezado con columnas rotadas usando Paragraph
    header_cell_style = ParagraphStyle(
        'HeaderRot', fontSize=7, textColor=colors.black,
        fontName='Helvetica-Bold', alignment=1
    )
    encabezado = [Paragraph('ÍTEM', header_cell_style)] + [
        Paragraph(col, header_cell_style) for col in columnas
    ]
    data = [encabezado]

    item_style = ParagraphStyle(
        'Item', fontSize=7, textColor=colors.black,
        fontName='Helvetica-Bold', alignment=0
    )
    cell_style = ParagraphStyle(
        'Cell', fontSize=7, textColor=colors.black,
        fontName='Helvetica', alignment=1
    )

    for fila_nombre in filas:
        fila = [Paragraph(str(fila_nombre), item_style)]
        for col in columnas:
            val = df_pivot.loc[fila_nombre, col]
            val_int = int(val) if not pd.isna(val) else 0
            texto = str(val_int) if val_int != 0 else '·'
            fila.append(Paragraph(texto, cell_style))
        data.append(fila)

    # Anchos de columna
    ancho_pagina = landscape(A4)[0] - 2*cm
    ancho_item = 4*cm
    ancho_resto = (ancho_pagina - ancho_item) / max(len(columnas), 1)
    col_widths = [ancho_item] + [ancho_resto] * len(columnas)

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    n_filas = len(data)
    n_cols = len(columnas) + 1

    estilos = [
        # Encabezado
        ('BACKGROUND',  (0, 0), (-1, 0),  colors.Color(0.75, 0.75, 0.75)),
        ('TEXTCOLOR',   (0, 0), (-1, 0),  colors.black),
        ('FONTNAME',    (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0),  7),
        ('ALIGN',       (0, 0), (-1, 0),  'CENTER'),
        ('VALIGN',      (0, 0), (-1, 0),  'BOTTOM'),
        # Cuerpo
        ('BACKGROUND',  (0, 1), (-1, n_filas-2), colors.white),
        ('TEXTCOLOR',   (0, 1), (-1, -1), colors.black),
        ('FONTSIZE',    (0, 1), (-1, -1), 7),
        ('ALIGN',       (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN',       (0, 1), (0, -1),  'LEFT'),
        ('VALIGN',      (0, 1), (-1, -1), 'MIDDLE'),
        # Primera columna (ítems) fondo gris claro
        ('BACKGROUND',  (0, 1), (0, n_filas-2), colors.Color(0.94, 0.94, 0.94)),
        ('FONTNAME',    (0, 1), (0, -1),  'Helvetica-Bold'),
        # Última columna (TOTAL ÍTEM)
        ('BACKGROUND',  (-1, 1), (-1, n_filas-2), colors.Color(0.88, 0.88, 0.88)),
        ('FONTNAME',    (-1, 1), (-1, -1), 'Helvetica-Bold'),
        # Última fila (TOTAL AGENCIA)
        ('BACKGROUND',  (0, -1), (-1, -1), colors.Color(0.75, 0.75, 0.75)),
        ('FONTNAME',    (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Grilla
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX',         (0, 0), (-1, -1), 1,   colors.black),
    ]
    tabla.setStyle(TableStyle(estilos))
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
    mes = st.selectbox(
        "📆 Mes", options=list(range(1, 13)),
        format_func=lambda x: datetime(2000, x, 1).strftime('%B'),
        index=datetime.today().month - 1
    )
with col3:
    dia_inicio = st.number_input("📅 Día desde", min_value=1, max_value=31, value=1)
with col4:
    dia_fin = st.number_input("📅 Día hasta", min_value=1, max_value=31, value=15)

agencias_seleccionadas = st.multiselect("🏢 Agencias (vacío = todas)", options=AGENCIAS_TODAS)

col_btn = st.columns([1, 2, 1])
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
            st.success(
                f"✅ Informe generado para "
                f"{datetime(año, mes, 1).strftime('%B %Y')} "
                f"(días {dia_inicio} al {dia_fin})"
            )


def mostrar_informe():
    informe = st.session_state.informe
    año, mes, dia_inicio, dia_fin = st.session_state.filtros

    # ── Tabla HTML con texto negro real ──
    st.markdown(tabla_html(informe), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Botón PDF ──
    titulo_pdf = f"Informe de Útiles - {datetime(año, mes, 1).strftime('%B %Y')}"
    pdf_buffer = generar_pdf(informe, titulo_pdf)
    st.download_button(
        label="📥 DESCARGAR INFORME EN PDF",
        data=pdf_buffer,
        file_name=f"Informe_Utiles_{datetime(año, mes, 1).strftime('%B_%Y')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )


if st.session_state.informe is not None:
    mostrar_informe()
