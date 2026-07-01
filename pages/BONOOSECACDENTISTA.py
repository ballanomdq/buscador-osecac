import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
    
    /* Contenedor del bono en pantalla */
    .bono-container {
        background: white;
        padding: 20px 30px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        max-width: 650px;
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
        border: 2px solid #1a3c6e;
    }
    .bono-titulo {
        color: #1a3c6e;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        border: 3px solid #1a3c6e;
        padding: 10px;
        margin: 10px 0;
        border-radius: 8px;
        letter-spacing: 2px;
        background: #f0f7ff;
    }
    .bono-subtitulo {
        color: #cc0000;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: #fef0f0;
        padding: 8px 0;
        border-radius: 4px;
    }
    .bono-datos {
        background: #f8fafc;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 5px solid #1a3c6e;
    }
    .bono-datos p {
        margin: 8px 0;
        font-size: 16px;
        color: #1e293b;
    }
    .bono-datos strong {
        color: #0b2a4a;
    }
    .bono-footer {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 20px;
        padding-top: 15px;
        border-top: 2px dashed #1a3c6e;
    }
    .bono-sello {
        text-align: center;
        border-top: 2px dashed #1a3c6e;
        padding-top: 10px;
        width: 120px;
        color: #1a3c6e;
        font-size: 14px;
        font-weight: bold;
    }
    .bono-firma {
        text-align: center;
        border-top: 2px dashed #1a3c6e;
        padding-top: 10px;
        width: 180px;
        color: #1a3c6e;
        font-size: 14px;
        font-weight: bold;
    }
    .bono-qr {
        text-align: center;
        margin: 10px 0;
    }
    .bono-qr img {
        width: 80px;
        height: 80px;
    }
    .bono-pie {
        text-align: center;
        margin-top: 15px;
        font-size: 10px;
        color: #94a3b8;
        border-top: 1px solid #e2e8f0;
        padding-top: 10px;
    }
    .bono-fecha-impresion {
        font-size: 10px;
        color: #94a3b8;
        text-align: right;
        margin-top: 5px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .logo-container img {
        width: 160px;  /* LOGO GRANDE */
        height: auto;
    }
    .no-print { 
        display: block; 
    }
    
    /* ====== ESTILOS PARA IMPRESIÓN ====== */
    @media print {
        /* Ocultar TODO lo que no sea el bono */
        body * {
            visibility: hidden !important;
        }
        /* Mostrar solo el bono y sus hijos */
        .bono-container, .bono-container * {
            visibility: visible !important;
        }
        .bono-container {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            border: none !important;
            box-shadow: none !important;
            padding: 20px !important;
            border-radius: 0 !important;
            background: white !important;
        }
        .no-print {
            display: none !important;
        }
        .stApp {
            background: white !important;
        }
        header, footer, [data-testid="stSidebar"] {
            display: none !important;
        }
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
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=2)
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generar_pdf_reportlab(nombre, dni, sector, fecha, qr_base64, logo_base64):
    """Genera un PDF del bono usando reportlab (sin emojis, diseño mejorado)"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    # --- LOGO GRANDE ---
    if logo_base64:
        try:
            logo_data = base64.b64decode(logo_base64)
            logo_img = ImageReader(BytesIO(logo_data))
            # Logo más grande: 120px de ancho
            c.drawImage(logo_img, (width - 120)/2, height - 70, width=120, height=45, preserveAspectRatio=True)
        except:
            pass

    # --- TÍTULO CON RECUADRO ---
    c.setStrokeColorRGB(0.1, 0.24, 0.43)  # #1a3c6e
    c.setFillColorRGB(0.1, 0.24, 0.43)
    c.setFont("Helvetica-Bold", 16)
    # Dibujar rectángulo
    c.rect(20, height - 105, width - 40, 30, stroke=1, fill=0)
    c.drawCentredString(width/2, height - 88, "COSEGURO ODONTOLÓGICO")
    
    # --- SUBTÍTULO ROJO ---
    c.setFillColorRGB(0.8, 0, 0)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 140, "NO AFILIADO AL SEC")
    c.setFillColorRGB(0, 0, 0)
    
    # --- DATOS (SIN EMOJIS) ---
    c.setFont("Helvetica", 12)
    y = height - 180
    c.drawString(30, y, f"Nombre: {nombre.upper()}")
    y -= 22
    c.drawString(30, y, f"DNI: {dni}")
    y -= 22
    c.drawString(30, y, f"Sector: {sector.upper()}")
    y -= 22
    c.drawString(30, y, f"Fecha de Emisión: {fecha.strftime('%d/%m/%Y')}")
    
    # --- QR ---
    if qr_base64:
        qr_data = base64.b64decode(qr_base64)
        qr_img = ImageReader(BytesIO(qr_data))
        c.drawImage(qr_img, width - 100, y - 40, width=70, height=70)

    # --- SELLO Y FIRMA (solo línea punteada y texto) ---
    # Sello
    c.setDash(3,3)
    c.line(30, y - 80, 150, y - 80)
    c.setDash()
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(90, y - 100, "SELLO")
    
    # Firma
    c.setDash(3,3)
    c.line(width - 170, y - 80, width - 30, y - 80)
    c.setDash()
    c.drawCentredString(width - 100, y - 100, "FIRMA")
    
    # --- PIE DE PÁGINA ---
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 40, "Válido solo para prestaciones odontológicas. No válido como comprobante de pago.")
    c.drawRightString(width - 20, 20, f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
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
    # Generar PDF de una vez
    qr_data = f"OSECAC|BONO|{nombre}|{dni}|{sector}|{fecha_emision}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr_base64(qr_data)
    logo_base64 = get_image_base64("logo osecac.png")
    st.session_state.pdf_bytes = generar_pdf_reportlab(
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
    
    # ==================== BONO HTML (para pantalla e impresión) ====================
    bono_html = f"""
    <div class="bono-container" id="bono-para-imprimir">
        <div class="logo-container">
            {f'<img src="data:image/png;base64,{logo_base64}" alt="OSECAC">' if logo_base64 else '<h2>OSECAC</h2>'}
        </div>
        <div class="bono-titulo">COSEGURO ODONTOLÓGICO</div>
        <div class="bono-subtitulo">⚠️ NO AFILIADO AL SEC ⚠️</div>
        <div class="bono-datos">
            <p><strong>👤 NOMBRE:</strong> {nombre_val.upper()}</p>
            <p><strong>🆔 DNI:</strong> {dni_val}</p>
            <p><strong>🏢 SECTOR:</strong> {sector_val.upper()}</p>
            <p><strong>📅 FECHA EMISIÓN:</strong> {fecha_str} - {hora_str}</p>
        </div>
        <div class="bono-qr">
            <img src="data:image/png;base64,{qr_base64}" alt="QR">
        </div>
        <div class="bono-footer">
            <div class="bono-sello">SELLO</div>
            <div class="bono-firma">FIRMA</div>
        </div>
        <div class="bono-pie">Válido solo para prestaciones odontológicas. No válido como comprobante de pago.</div>
        <div class="bono-fecha-impresion">Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
    </div>
    """
    
    # Mostrar previsualización
    st.markdown("---")
    st.markdown('<div class="no-print"><h3>📄 Previsualización del Bono</h3></div>', unsafe_allow_html=True)
    st.markdown(bono_html, unsafe_allow_html=True)
    
    # ==================== BOTONES DE ACCIÓN (solo uno "GENERAR" + "IMPRIMIR") ====================
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 NUEVO BONO", use_container_width=True):
            limpiar_formulario()
    
    with col2:
        # Botón de IMPRIMIR (con components.html y window.print)
        components.html("""
            <button onclick="window.print()" style="
                width: 100%;
                padding: 12px;
                background: #1a3c6e;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.2s;
            " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                🖨️ IMPRIMIR BONO
            </button>
        """, height=60)
    
    with col3:
        # Botón de DESCARGAR PDF (ya generado)
        if st.session_state.pdf_bytes:
            st.download_button(
                label="📄 DESCARGAR PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"bono_{nombre_val.replace(' ', '_')}_{dni_val}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("Generando PDF...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mensaje informativo
    st.info("🔒 **Código QR**: Contiene los datos del afiliado y la fecha de emisión. Sirve como verificación de autenticidad.")

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
