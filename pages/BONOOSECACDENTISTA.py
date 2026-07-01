import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CSS MEJORADO ====================
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
        display: none !important;
    }
    .stApp {
        background-color: #f0f2f6 !important;
    }
    
    /* Contenedor del bono en pantalla - COMPACTO */
    .bono-container {
        background: white;
        padding: 12px 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 500px;  /* más angosto */
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
        border: 2px solid #1a3c6e;
        page-break-after: avoid;
    }
    .bono-titulo {
        color: #1a3c6e;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #1a3c6e;
        padding: 5px;
        margin: 6px 0;
        border-radius: 6px;
        letter-spacing: 1px;
        background: #f0f7ff;
    }
    .bono-subtitulo {
        color: #cc0000;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin: 8px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: #fef0f0;
        padding: 4px 0;
        border-radius: 4px;
    }
    .bono-datos {
        background: #f8fafc;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 8px 0;
        border-left: 4px solid #1a3c6e;
    }
    .bono-datos p {
        margin: 4px 0;
        font-size: 13px;
        color: #1e293b;
    }
    .bono-datos strong {
        color: #0b2a4a;
    }
    .bono-footer {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 2px dashed #1a3c6e;
    }
    .bono-sello {
        text-align: center;
        border-top: 2px dashed #1a3c6e;
        padding-top: 6px;
        width: 80px;
        color: #1a3c6e;
        font-size: 12px;
        font-weight: bold;
    }
    .bono-firma {
        text-align: center;
        border-top: 2px dashed #1a3c6e;
        padding-top: 6px;
        width: 120px;
        color: #1a3c6e;
        font-size: 12px;
        font-weight: bold;
    }
    .bono-qr {
        text-align: center;
        margin: 4px 0;
    }
    .bono-qr img {
        width: 60px;
        height: 60px;
    }
    .bono-fecha-impresion {
        font-size: 8px;
        color: #94a3b8;
        text-align: right;
        margin-top: 3px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 4px;
    }
    .logo-container img {
        width: 140px;  /* Logo GRANDE pero compacto */
        height: auto;
    }
    .no-print { 
        display: block; 
    }
    
    /* ====== ESTILOS PARA IMPRESIÓN (A4 o media hoja) ====== */
    @media print {
        body * { visibility: hidden !important; }
        .bono-container, .bono-container * { visibility: visible !important; }
        .bono-container {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            border: none !important;
            box-shadow: none !important;
            padding: 8px 10px !important;
            border-radius: 0 !important;
            background: white !important;
            margin: 0 auto !important;
        }
        .no-print { display: none !important; }
        .stApp { background: white !important; }
        header, footer, [data-testid="stSidebar"] { display: none !important; }
        .bono-titulo { font-size: 16px !important; }
        .bono-subtitulo { font-size: 18px !important; }
        .bono-datos p { font-size: 12px !important; }
        .bono-sello, .bono-firma { font-size: 10px !important; }
        .bono-qr img { width: 50px !important; height: 50px !important; }
        .logo-container img { width: 120px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES AUXILIARES ====================
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def generar_qr_base64(datos):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=1)
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generar_pdf_compacto(nombre, dni, sector, fecha, qr_base64, logo_base64):
    """Genera un PDF compacto (márgenes reducidos, todo junto) que cabe en A4 sin cortes"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Márgenes pequeños (1.2 cm)
    margen = 12 * mm

    # --- LOGO GRANDE (en el PDF) ---
    if logo_base64:
        try:
            logo_data = base64.b64decode(logo_base64)
            logo_img = ImageReader(BytesIO(logo_data))
            logo_ancho = 100  # más grande
            logo_alto = logo_ancho * (logo_img.getHeight() / logo_img.getWidth())
            c.drawImage(logo_img, (width - logo_ancho) / 2, height - margen - logo_alto - 5,
                        width=logo_ancho, height=logo_alto, preserveAspectRatio=True)
        except:
            pass

    # --- TÍTULO ---
    c.setStrokeColorRGB(0.1, 0.24, 0.43)
    c.setFillColorRGB(0.1, 0.24, 0.43)
    c.setFont("Helvetica-Bold", 14)
    y_titulo = height - margen - 55
    c.rect(margen, y_titulo - 12, width - 2*margen, 24, stroke=1, fill=0)
    c.drawCentredString(width/2, y_titulo, "COSEGURO ODONTOLÓGICO")

    # --- SUBTÍTULO ---
    c.setFillColorRGB(0.8, 0, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, y_titulo - 35, "NO AFILIADO AL SEC")
    c.setFillColorRGB(0, 0, 0)

    # --- DATOS (más juntos) ---
    c.setFont("Helvetica", 10)
    y_datos = y_titulo - 60
    c.drawString(margen + 10, y_datos, f"NOMBRE: {nombre.upper()}")
    y_datos -= 16
    c.drawString(margen + 10, y_datos, f"DNI: {dni}")
    y_datos -= 16
    c.drawString(margen + 10, y_datos, f"SECTOR: {sector.upper()}")
    y_datos -= 16
    c.drawString(margen + 10, y_datos, f"FECHA EMISIÓN: {fecha.strftime('%d/%m/%Y')}")

    # --- QR ---
    if qr_base64:
        qr_data = base64.b64decode(qr_base64)
        qr_img = ImageReader(BytesIO(qr_data))
        c.drawImage(qr_img, width - margen - 55, y_datos - 30, width=50, height=50)

    # --- SELLO Y FIRMA (más juntos) ---
    y_footer = y_datos - 55
    c.setDash(3, 3)
    c.line(margen + 10, y_footer, margen + 70, y_footer)
    c.setDash()
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(margen + 40, y_footer - 12, "SELLO")

    c.setDash(3, 3)
    c.line(width - margen - 100, y_footer, width - margen - 10, y_footer)
    c.setDash()
    c.drawCentredString(width - margen - 55, y_footer - 12, "FIRMA")

    # --- FECHA IMPRESIÓN ---
    c.setFont("Helvetica", 8)
    c.drawRightString(width - margen, margen + 10, f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    c.save()
    return buffer.getvalue()

# ==================== INICIALIZAR ESTADO ====================
if 'bono_generado' not in st.session_state:
    st.session_state.bono_generado = False
if 'bono_nombre' not in st.session_state:
    st.session_state.bono_nombre = ''
if 'bono_dni' not in st.session_state:
    st.session_state.bono_dni = ''
if 'bono_sector' not in st.session_state:
    st.session_state.bono_sector = ''
if 'bono_fecha' not in st.session_state:
    st.session_state.bono_fecha = datetime.now()
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None

def limpiar_formulario():
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
    st.session_state.pdf_bytes = None
    st.rerun()

# ==================== FORMULARIO ====================
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.title("🦷 GENERADOR DE BONO ODONTOLÓGICO")
st.markdown("Complete los datos del afiliado para generar el bono.")

with st.form("form_bono"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("👤 Nombre del Beneficiario", placeholder="Ej: Juan Pérez")
        dni = st.text_input("🆔 DNI", placeholder="Ej: 30.123.456")
    with col2:
        sector = st.text_input("🏢 Sector / Agencia", placeholder="Ej: Agencia Miramar")
        fecha_emision = st.date_input("📅 Fecha de Emisión", datetime.now())
    
    generar = st.form_submit_button("📋 GENERAR BONO", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==================== LÓGICA DE GENERACIÓN ====================
if generar and nombre and dni and sector:
    st.session_state.bono_nombre = nombre
    st.session_state.bono_dni = dni
    st.session_state.bono_sector = sector
    st.session_state.bono_fecha = fecha_emision
    st.session_state.bono_generado = True
    # Generar QR
    qr_data = f"OSECAC|BONO|{nombre}|{dni}|{sector}|{fecha_emision}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr_base64(qr_data)
    logo_base64 = get_image_base64("logo osecac.png")
    # Generar PDF compacto
    st.session_state.pdf_bytes = generar_pdf_compacto(
        nombre, dni, sector, fecha_emision, qr_base64, logo_base64
    )
    st.rerun()

if st.session_state.bono_generado and st.session_state.bono_nombre:
    
    nombre_val = st.session_state.bono_nombre
    dni_val = st.session_state.bono_dni
    sector_val = st.session_state.bono_sector
    fecha_val = st.session_state.bono_fecha
    
    # Generar QR para mostrar en pantalla
    qr_data = f"OSECAC|BONO|{nombre_val}|{dni_val}|{sector_val}|{fecha_val}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr_base64(qr_data)
    logo_base64 = get_image_base64("logo osecac.png")
    
    fecha_str = fecha_val.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")
    
    # ==================== BONO HTML COMPACTO ====================
    bono_html = f"""
    <div class="bono-container" id="bono-para-imprimir">
        <div class="logo-container">
            {f'<img src="data:image/png;base64,{logo_base64}" alt="OSECAC">' if logo_base64 else '<h2>OSECAC</h2>'}
        </div>
        <div class="bono-titulo">COSEGURO ODONTOLÓGICO</div>
        <div class="bono-subtitulo">⚠️ NO AFILIADO AL SEC ⚠️</div>
        <div class="bono-datos">
            <p><strong>NOMBRE:</strong> {nombre_val.upper()}</p>
            <p><strong>DNI:</strong> {dni_val}</p>
            <p><strong>SECTOR:</strong> {sector_val.upper()}</p>
            <p><strong>FECHA EMISIÓN:</strong> {fecha_str} - {hora_str}</p>
        </div>
        <div class="bono-qr">
            <img src="data:image/png;base64,{qr_base64}" alt="QR">
        </div>
        <div class="bono-footer">
            <div class="bono-sello">SELLO</div>
            <div class="bono-firma">FIRMA</div>
        </div>
        <div class="bono-fecha-impresion">Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
    </div>
    """
    
    # Mostrar previsualización
    st.markdown("---")
    st.markdown('<div class="no-print"><h3>📄 Previsualización del Bono</h3></div>', unsafe_allow_html=True)
    st.markdown(bono_html, unsafe_allow_html=True)
    
    # ==================== BOTONES ====================
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.pdf_bytes:
            st.download_button(
                label="📄 DESCARGAR PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"bono_{nombre_val.replace(' ', '_')}_{dni_val}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    with col2:
        if st.button("🔄 GENERAR OTRO BONO", use_container_width=True):
            limpiar_formulario()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("✅ Bono generado correctamente. Descarga el PDF o imprímelo desde la previsualización.")

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
