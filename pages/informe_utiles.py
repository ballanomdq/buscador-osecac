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

st.markdown("""
<style>
    .stApp { background-color: white !important; }
    .main .block-container { background-color: white !important; }
    .stMarkdown, label, div, p, h1, h2, h3, h4, h5, h6, span {
        color: #000000 !important;
    }
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

    /* ── TABLA: NO se estira, toma solo el ancho necesario ── */
    .tabla-contenedor {
        overflow-x: auto;
        width: 100%;
    }
    .tabla-utiles {
        border-collapse: collapse;
        /* width: auto → la tabla ocupa solo lo que necesita */
        width: auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }
    /* Encabezado: primera columna (ÍTEM) */
    .tabla-utiles thead tr th.col-item {
        border: 2px solid #000000;
        padding: 6px 10px;
        text-align: left;
        vertical-align: bottom;
        background-color: #d0d0d0;
        font-weight: bold;
        color: #000000 !important;
        white-space: nowrap;
        /* Ancho fijo ajustado al texto más largo */
        min-width: 180px;
        max-width: 220px;
    }
    /* Encabezado: columnas de agencia y total → texto VERTICAL */
    .tabla-utiles thead tr th.col-rotada {
        border: 2px solid #000000;
        padding: 8px 4px;
        text-align: center;
        vertical-align: bottom;
        background-color: #d0d0d0;
        font-weight: bold;
        color: #000000 !important;
        /* Texto vertical */
        writing-mode: vertical-rl;
        text-orientation: mixed;
        transform: rotate(180deg);
        height: 110px;
        /* Columnas angostas: solo el ancho del texto rotado */
        width: 34px;
        min-width: 34px;
        max-width: 40px;
        font-size: 12px;
        white-space: nowrap;
    }
    /* Celda TOTAL ÍTEM: un poco más ancha */
    .tabla-utiles thead tr th.col-total {
        background-color: #b8b8b8 !important;
        width: 42px;
        min-width: 42px;
    }
    /* Celdas de datos — compactas */
    .tabla-utiles tbody tr td {
        border: 1px solid #000000;
        padding: 4px 6px;
        text-align: center;
        color: #000000 !important;
        background-color: #ffffff;
        font-size: 13px;
        white-space: nowrap;
    }
    /* Primera columna de datos (nombre del ítem) */
    .tabla-utiles tbody tr td.td-item {
        text-align: left;
        padding-left: 8px;
        font-weight: 600;
        background-color: #f0f0f0;
        color: #000000 !important;
        white-space: nowrap;
    }
    /* Última columna (TOTAL ÍTEM) */
    .tabla-utiles tbody tr td.td-total {
        background-color: #e0e0e0 !important;
        font-weight: bold !important;
        color: #000000 !important;
    }
    /* Fila TOTAL AGENCIA */
    .tabla-utiles tbody tr.fila-total td {
        background-color: #c8c8c8 !important;
        font-weight: bold !important;
        color: #000000 !important;
    }
    /* Ceros: punto gris para no saturar la vista */
    .tabla-utiles tbody tr td.cero {
        color: #cccccc !important;
        font-size: 11px;
    }
    .tabla-utiles tbody tr:hover td { background-color: #f5f5f5 !important; }
    .tabla-utiles tbody tr:hover td.td-item { background-color: #e8e8e8 !important; }
    .tabla-utiles tbody tr.fila-total:hover td { background-color: #b8b8b8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Título ──────────────────────────────────────────────────────────────────
st.title("📊 INFORME DE PEDIDOS DE ÚTILES")
st.markdown("---")

# ── Config ──────────────────────────────────────────────────────────────────
SPREADSHEET_ID = "1eaujMJahDPn7YBpHeGKG_pSIvxjosnD6f2MHXLfngbI"
SHEET_NAME     = "Respuestas de formulario 1"

AGENCIAS_TODAS = [
    "MIRAMAR", "M CHIQUITA", "MECHONGUE", "GESELL", "DOLORES", "MONOLITO",
    "PINAMAR", "S CLEMENTE", "MAR DE AJO", "MAIPU", "S TERESITA", "MADARIAGA",
    "PIRAN", "VIDAL"
]

# ── Carga de datos ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos_utiles(retries=3):
    for i in range(retries):
        try:
            creds_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(
                creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            client = gspread.authorize(creds)
            sheet  = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
            data   = sheet.get_all_records()
            df     = pd.DataFrame(data)
            df.columns = df.columns.str.replace('\n', ' ').str.strip()
            return df
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)
            else:
                st.error(f"Error al cargar datos después de {retries} intentos: {e}")
                return pd.DataFrame()
    return pd.DataFrame()

# ── Procesamiento ────────────────────────────────────────────────────────────
def procesar_informe(df, mes, anio, dia_inicio, dia_fin, agencias_seleccionadas):
    fecha_col = 'FECHA' if 'FECHA' in df.columns else 'Marca temporal'
    df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['fecha'])
    df = df[
        (df['fecha'].dt.year  == anio) &
        (df['fecha'].dt.month == mes)  &
        (df['fecha'].dt.day   >= dia_inicio) &
        (df['fecha'].dt.day   <= dia_fin)
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
    df_pivot    = df_agrupado.set_index('AGENCIA').T

    # Eliminar agencias con todo en 0
    df_pivot = df_pivot[[c for c in df_pivot.columns if df_pivot[c].sum() > 0]]

    # Agregar totales
    df_pivot['TOTAL ÍTEM']    = df_pivot.sum(axis=1)
    total_row                 = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL AGENCIA'] = total_row

    # Eliminar ítems donde el total también es 0
    df_pivot = df_pivot[df_pivot['TOTAL ÍTEM'] > 0]

    return df_pivot

# ── Tabla HTML compacta ──────────────────────────────────────────────────────
def tabla_html(df_pivot):
    columnas = df_pivot.columns.tolist()   # agencias + TOTAL ÍTEM
    filas    = df_pivot.index.tolist()

    # Encabezado
    thead = '<thead><tr>'
    thead += '<th class="col-item">ÍTEM</th>'
    for col in columnas:
        extra = ' col-total' if col == 'TOTAL ÍTEM' else ''
        thead += f'<th class="col-rotada{extra}">{col}</th>'
    thead += '</tr></thead>'

    # Cuerpo
    tbody = '<tbody>'
    for fila_nombre in filas:
        es_total_fila = (fila_nombre == 'TOTAL AGENCIA')
        cls_fila = ' class="fila-total"' if es_total_fila else ''
        tbody += f'<tr{cls_fila}>'
        tbody += f'<td class="td-item">{fila_nombre}</td>'
        for col in columnas:
            val     = df_pivot.loc[fila_nombre, col]
            val_int = int(val) if not pd.isna(val) else 0
            es_total_col = (col == 'TOTAL ÍTEM')
            if es_total_col:
                tbody += f'<td class="td-total">{val_int}</td>'
            elif val_int == 0 and not es_total_fila:
                tbody += '<td class="cero">·</td>'
            else:
                tbody += f'<td>{val_int}</td>'
        tbody += '</tr>'
    tbody += '</tbody>'

    return f'''
    <div class="tabla-contenedor">
      <table class="tabla-utiles">
        {thead}
        {tbody}
      </table>
    </div>
    '''

# ── Generar PDF ──────────────────────────────────────────────────────────────
def generar_pdf(df_pivot, titulo):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        rightMargin=1*cm, leftMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )
    elementos = []
    styles    = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Titulo', parent=styles['Title'],
        fontSize=13, alignment=1, spaceAfter=8, textColor=colors.black
    )
    elementos.append(Paragraph(titulo, titulo_style))
    elementos.append(Spacer(1, 6))

    columnas = df_pivot.columns.tolist()
    filas    = df_pivot.index.tolist()

    h_style = ParagraphStyle('H', fontSize=6, textColor=colors.black,
                              fontName='Helvetica-Bold', alignment=1)
    i_style = ParagraphStyle('I', fontSize=7, textColor=colors.black,
                              fontName='Helvetica-Bold', alignment=0)
    c_style = ParagraphStyle('C', fontSize=7, textColor=colors.black,
                              fontName='Helvetica', alignment=1)

    encabezado = [Paragraph('ÍTEM', i_style)] + [Paragraph(col, h_style) for col in columnas]
    data       = [encabezado]

    for fila_nombre in filas:
        fila = [Paragraph(str(fila_nombre), i_style)]
        for col in columnas:
            val     = df_pivot.loc[fila_nombre, col]
            val_int = int(val) if not pd.isna(val) else 0
            texto   = str(val_int) if val_int != 0 else '·'
            fila.append(Paragraph(texto, c_style))
        data.append(fila)

    ancho_pagina = landscape(A4)[0] - 2*cm
    ancho_item   = 4.5*cm
    ancho_col    = (ancho_pagina - ancho_item) / max(len(columnas), 1)
    col_widths   = [ancho_item] + [ancho_col] * len(columnas)

    tabla   = Table(data, colWidths=col_widths, repeatRows=1)
    n_filas = len(data)

    tabla.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0),  (-1, 0),           colors.Color(0.75, 0.75, 0.75)),
        ('TEXTCOLOR',   (0, 0),  (-1, -1),           colors.black),
        ('FONTNAME',    (0, 0),  (-1, 0),            'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0),  (-1, 0),            6),
        ('ALIGN',       (1, 0),  (-1, 0),            'CENTER'),
        ('VALIGN',      (0, 0),  (-1, 0),            'BOTTOM'),
        ('BACKGROUND',  (0, 1),  (0, n_filas-2),     colors.Color(0.93, 0.93, 0.93)),
        ('FONTNAME',    (0, 1),  (0, -1),            'Helvetica-Bold'),
        ('BACKGROUND',  (-1, 1), (-1, n_filas-2),    colors.Color(0.87, 0.87, 0.87)),
        ('FONTNAME',    (-1, 1), (-1, -1),           'Helvetica-Bold'),
        ('BACKGROUND',  (0, -1), (-1, -1),           colors.Color(0.75, 0.75, 0.75)),
        ('FONTNAME',    (0, -1), (-1, -1),           'Helvetica-Bold'),
        ('ALIGN',       (1, 1),  (-1, -1),           'CENTER'),
        ('ALIGN',       (0, 1),  (0, -1),            'LEFT'),
        ('VALIGN',      (0, 1),  (-1, -1),           'MIDDLE'),
        ('GRID',        (0, 0),  (-1, -1),           0.5, colors.black),
        ('BOX',         (0, 0),  (-1, -1),           1,   colors.black),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# ── Filtros ──────────────────────────────────────────────────────────────────
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

if 'informe' not in st.session_state:
    st.session_state.informe = None

# ── Generar ──────────────────────────────────────────────────────────────────
if generar:
    with st.spinner("Cargando datos desde Google Sheets..."):
        df_raw = cargar_datos_utiles()
    if df_raw.empty:
        st.warning("No se pudieron cargar los datos.")
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
                f"✅ Informe generado — {datetime(año, mes, 1).strftime('%B %Y')} "
                f"(días {dia_inicio} al {dia_fin})"
            )

# ── Mostrar ──────────────────────────────────────────────────────────────────
def mostrar_informe():
    informe           = st.session_state.informe
    año, mes, d1, d2  = st.session_state.filtros
    n_agencias        = len([c for c in informe.columns if c != 'TOTAL ÍTEM'])
    n_items           = len(informe) - 1  # sin la fila de totales

    st.markdown(
        f"**{n_agencias} agencia(s) con pedidos · {n_items} ítem(s) solicitado(s)**",
        unsafe_allow_html=True
    )
    st.markdown(tabla_html(informe), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
