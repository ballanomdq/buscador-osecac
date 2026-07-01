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
import tempfile

# Configuración de página
st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CSS MEJORADO ====================
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit en pantalla */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
        display: none !important;
    }
    .stApp {
        background-color: #f0f2f6 !important;
    }
    
    /* Contenedor del bono en pantalla */
    .bono-container {
        background: white;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        max-width: 600px;
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
        border: 1px solid #d0d7de;
    }
    .bono-titulo {
        color: #1a3c6e;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #1a3c6e;
        border-radius: 8px;
        padding: 8px 0;
        margin-bottom: 10px;
        background: #f0f6ff;
        letter-spacing: 1px;
    }
    .bono-subtitulo {
        color: #cc0000;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0 15px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: #fef0f0;
        padding: 6px 0;
        border-radius: 4px;
    }
    .bono-datos {
        background: #f8fafc;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #1a3c6e;
    }
    .bono-datos p {
        margin: 6px 0;
        font-size: 15px;
        color: #1e293b;
    }
    .bono-datos strong {
        color: #0b2a4a;
    }
    .bono-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 18px;
        padding-top: 12px;
        border-top: 2px dashed #1a3c6e;
    }
    .bono-sello {
        border: 2px dashed #1a3c6e;
        padding: 20px 16px;
        text-align: center;
        color: #1a3c6e;
        font-size: 11px;
        border-radius: 6px;
        background: #f8fafc;
        min-width: 100px;
    }
    .bono-firma {
        border-top: 2px dashed #1a3c6e;
        width: 180px;
        text-align: center;
        padding-top: 20px;
        font-size: 11px;
        color: #1e293b;
    }
    .bono-qr {
        text-align: center;
        margin: 8px 0;
    }
    .bono-qr img {
        width: 70px;
        height: 70px;
    }
    .bono-pie {
        text-align: center;
        margin-top: 12px;
        font-size: 9px;
        color: #94a3b8;
        border-top: 1px solid #e2e8f0;
        padding-top: 8px;
    }
    .bono-fecha-impresion {
        font-size: 9px;
        color: #94a3b8;
        text-align: right;
        margin-top: 4px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 6px;
    }
    .logo-container img {
        width: 120px;
        height: auto;
    }
    .no-print { 
        display: block; 
    }
    .bono-diente {
        font-size: 30px;
        margin-right: 8px;
    }
    
    /* ====== ESTILOS PARA IMPRESIÓN ====== */
    @media print {
        body * {
            visibility: hidden !important;
        }
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
            padding: 15px 20px !important;
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
    """Genera un PDF del bono usando reportlab con diseño mejorado"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5
    
    # Configurar fuente
    c.setFont("Helvetica", 10)
    
    # --- LOGO (más grande) ---
    if logo_base64:
        try:
            logo_data = base64.b64decode(logo_base64)
            logo_img = ImageReader(BytesIO(logo_data))
            c.drawImage(logo_img, (width - 100)/2, height - 55, width=100, height=40, preserveAspectRatio=True)
        except:
            pass
    
    # --- TÍTULO CON RECUADRO ---
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.1, 0.23, 0.43)  # Azul OSECAC
    c.rect(20, height - 85, width - 40, 30, stroke=1, fill=0)
    c.drawCentredString(width/2, height - 68, "COSEGURO ODONTOLÓGICO")
    c.setFillColorRGB(0, 0, 0)
    
    # --- SUBTÍTULO ROJO ---
    c.setFillColorRGB(0.8, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 115, "⚠️ NO AFILIADO AL SEC ⚠️")
    c.setFillColorRGB(0, 0, 0)
    
    # --- DATOS ---
    c.setFont("Helvetica", 11)
    y = height - 150
    c.drawString(20, y, f"Nombre del Beneficiario: {nombre.upper()}")
    y -= 20
    c.drawString(20, y, f"DNI: {dni}")
    y -= 20
    c.drawString(20, y, f"Sector / Agencia: {sector.upper()}")
    y -= 20
    c.drawString(20, y, f"Fecha de Emisión: {fecha.strftime('%d/%m/%Y')}")
    
    # --- QR ---
    if qr_base64:
        qr_data = base64.b64decode(qr_base64)
        qr_img = ImageReader(BytesIO(qr_data))
        c.drawImage(qr_img, width - 75, y - 25, width=60, height=60)
    
    # --- SELLO (línea punteada) ---
    sello_y = y - 100
    c.setDash(1, 3)
    c.rect(20, sello_y, 100, 50, stroke=1, fill=0)
    c.setDash()
    c.setFont("Helvetica", 10)
    c.drawCentredString(70, sello_y + 15, "SELLO")
    c.drawCentredString(70, sello_y + 5, "(Lugar para el sello)")
    
    # --- FIRMA (línea punteada) ---
    firma_y = sello_y
    c.setDash(1, 3)
    c.line(width - 180, firma_y + 40, width - 20, firma_y + 40)
    c.setDash()
    c.setFont("Helvetica", 10)
    c.drawCentredString((width - 180 + width - 20)/2, firma_y + 25, "FIRMA DEL AFILIADO")
    c.drawCentredString((width - 180 + width - 20)/2, firma_y + 15, "(Acepto las condiciones)")
    
    # --- PIE DE PÁGINA ---
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, 30, "Válido solo para prestaciones odontológicas. No válido como comprobante de pago.")
    c.drawRightString(width - 20, 15, f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.setFillColorRGB(0, 0, 0)
    
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
st.title("🦷 BONO ODONTOLÓGICO")
st.markdown("Complete los datos del afiliado para generar el bono.")

with st.form("form_bono"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Beneficiario", placeholder="Ej: Juan Pérez")
        dni = st.text_input("DNI", placeholder="Ej: 30.123.456")
    with col2:
        sector = st.text_input("Sector / Agencia", placeholder="Ej: Agencia Miramar")
        fecha_emision = st.date_input("Fecha de Emisión", datetime.now())
    
    generar = st.form_submit_button("📋 GENERAR BONO", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==================== LÓGICA DE GENERACIÓN ====================
if generar and nombre and dni and sector:
    st.session_state.bono_nombre = nombre
    st.session_state.bono_dni = dni
    st.session_state.bono_sector = sector
    st.session_state.bono_fecha = fecha_emision
    st.session_state.bono_generado = True
    st.rerun()

if st.session_state.bono_generado and st.session_state.bono_nombre:
    
    nombre_val = st.session_state.bono_nombre
    dni_val = st.session_state.bono_dni
    sector_val = st.session_state.bono_sector
    fecha_val = st.session_state.bono_fecha
    
    # Generar QR
    qr_data = f"OSECAC|BONO|{nombre_val}|{dni_val}|{sector_val}|{fecha_val}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr_base64(qr_data)
    
    # Logo
    logo_path = "logo osecac.png"
    logo_base64 = get_image_base64(logo_path)
    
    fecha_str = fecha_val.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")
    
    # ==================== BONO HTML (para pantalla e impresión) ====================
    bono_html = f"""
    <div class="bono-container" id="bono-para-imprimir">
        <div class="logo-container">
            {f'<img src="data:image/png;base64,{logo_base64}" alt="OSECAC">' if logo_base64 else '<h2>OSECAC</h2>'}
        </div>
        <div class="bono-titulo">🦷 COSEGURO ODONTOLÓGICO</div>
        <div class="bono-subtitulo">⚠️ NO AFILIADO AL SEC ⚠️</div>
        <div class="bono-datos">
            <p><strong>Nombre del Beneficiario:</strong> {nombre_val.upper()}</p>
            <p><strong>DNI:</strong> {dni_val}</p>
            <p><strong>Sector / Agencia:</strong> {sector_val.upper()}</p>
            <p><strong>Fecha de Emisión:</strong> {fecha_str} - {hora_str}</p>
        </div>
        <div class="bono-qr">
            <img src="data:image/png;base64,{qr_base64}" alt="QR">
        </div>
        <div class="bono-footer">
            <div class="bono-sello">SELLO</div>
            <div class="bono-firma">FIRMA DEL AFILIADO</div>
        </div>
        <div class="bono-pie">Válido solo para prestaciones odontológicas. No válido como comprobante de pago.</div>
        <div class="bono-fecha-impresion">Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
    </div>
    """
    
    # Mostrar previsualización
    st.markdown("---")
    st.markdown('<div class="no-print"><h3>📄 Previsualización del Bono</h3></div>', unsafe_allow_html=True)
    st.markdown(bono_html, unsafe_allow_html=True)
    
    # ==================== GENERAR PDF (si no está generado) ====================
    if st.session_state.pdf_bytes is None:
        st.session_state.pdf_bytes = generar_pdf_reportlab(
            nombre_val, dni_val, sector_val, fecha_val, qr_base64, logo_base64
        )
    
    # ==================== BOTONES DE ACCIÓN ====================
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 NUEVO BONO", use_container_width=True):
            limpiar_formulario()
    
    with col2:
        # Botón que abre el PDF en una nueva pestaña para imprimir
        if st.session_state.pdf_bytes:
            # Convertir a base64 para incrustar en un enlace
            pdf_b64 = base64.b64encode(st.session_state.pdf_bytes).decode()
            pdf_data_url = f"data:application/pdf;base64,{pdf_b64}"
            st.markdown(f"""
                <a href="{pdf_data_url}" target="_blank" style="
                    display: inline-block;
                    width: 100%;
                    padding: 10px;
                    background: #1a3c6e;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                    text-decoration: none;
                    cursor: pointer;
                    transition: 0.2s;
                " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                    🖨️ IMPRIMIR BONO
                </a>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.pdf_bytes:
            st.download_button(
                label="📄 DESCARGAR PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"bono_{nombre_val.replace(' ', '_')}_{dni_val}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mensaje informativo
    st.info("🔒 **Código QR**: Contiene los datos del afiliado y la fecha de emisión. Sirve como verificación de autenticidad.")

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
