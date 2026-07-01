import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CSS MEJORADO (vista previa) ====================
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
        display: none !important;
    }
    .stApp {
        background-color: #f0f2f6 !important;
    }
    
    /* Contenedor del bono en pantalla (íntegramente visible) */
    .bono-container {
        background: white;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        max-width: 580px;
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
        border: 2px solid #1a3c6e;
        page-break-after: avoid;
        box-sizing: border-box;
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
    .bono-sello, .bono-firma {
        text-align: center;
        border-top: 2px dashed #1a3c6e;
        padding-top: 10px;
        width: 120px;
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
    .bono-fecha-impresion {
        font-size: 10px;
        color: #94a3b8;
        text-align: right;
        margin-top: 8px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .logo-container img {
        width: 180px;  /* LOGO GRANDE */
        height: auto;
    }
    .no-print { 
        display: block; 
    }
    
    /* Ocultar el sidebar y elementos innecesarios */
    [data-testid="stSidebar"] { display: none !important; }
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

def limpiar_formulario():
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
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
    st.rerun()

if st.session_state.bono_generado and st.session_state.bono_nombre:
    
    nombre_val = st.session_state.bono_nombre
    dni_val = st.session_state.bono_dni
    sector_val = st.session_state.bono_sector
    fecha_val = st.session_state.bono_fecha
    
    # Generar QR para vista previa e impresión
    qr_data = f"OSECAC|BONO|{nombre_val}|{dni_val}|{sector_val}|{fecha_val}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr_base64(qr_data)
    
    # Logo (ruta correcta)
    logo_path = "logo osecac.png"
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), "logo osecac.png")
    logo_base64 = get_image_base64(logo_path)
    
    fecha_str = fecha_val.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")
    
    # ==================== BONO HTML (vista previa) ====================
    bono_html = f"""
    <div id="bono-para-imprimir" class="bono-container" style="background:white; padding:20px 25px; max-width:580px; margin:0 auto; border:2px solid #1a3c6e; border-radius:12px; font-family:Arial, sans-serif; box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
        <div style="text-align:center; margin-bottom:10px;">
            {f'<img src="data:image/png;base64,{logo_base64}" style="width:180px; height:auto;" alt="OSECAC">' if logo_base64 else '<h2>OSECAC</h2>'}
        </div>
        <div style="color:#1a3c6e; font-size:24px; font-weight:bold; text-align:center; border:3px solid #1a3c6e; padding:10px; margin:10px 0; border-radius:8px; background:#f0f7ff;">
            COSEGURO ODONTOLÓGICO
        </div>
        <div style="color:#cc0000; font-size:28px; font-weight:bold; text-align:center; margin:15px 0; text-transform:uppercase; background:#fef0f0; padding:8px 0; border-radius:4px;">
            ⚠️ NO AFILIADO AL SEC ⚠️
        </div>
        <div style="background:#f8fafc; padding:15px 20px; border-radius:8px; margin:15px 0; border-left:5px solid #1a3c6e;">
            <p style="margin:8px 0; font-size:16px; color:#1e293b;"><strong>👤 NOMBRE:</strong> {nombre_val.upper()}</p>
            <p style="margin:8px 0; font-size:16px; color:#1e293b;"><strong>🆔 DNI:</strong> {dni_val}</p>
            <p style="margin:8px 0; font-size:16px; color:#1e293b;"><strong>🏢 SECTOR:</strong> {sector_val.upper()}</p>
            <p style="margin:8px 0; font-size:16px; color:#1e293b;"><strong>📅 FECHA EMISIÓN:</strong> {fecha_str} - {hora_str}</p>
        </div>
        <div style="text-align:center; margin:10px 0;">
            <img src="data:image/png;base64,{qr_base64}" style="width:80px; height:80px;" alt="QR">
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin-top:20px; padding-top:15px; border-top:2px dashed #1a3c6e;">
            <div style="text-align:center; border-top:2px dashed #1a3c6e; padding-top:10px; width:120px; color:#1a3c6e; font-size:14px; font-weight:bold;">SELLO</div>
            <div style="text-align:center; border-top:2px dashed #1a3c6e; padding-top:10px; width:120px; color:#1a3c6e; font-size:14px; font-weight:bold;">FIRMA</div>
        </div>
        <div style="font-size:10px; color:#94a3b8; text-align:right; margin-top:8px;">
            Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        </div>
    </div>
    """
    
    # Mostrar el bono (visible)
    st.markdown("---")
    st.markdown('<div class="no-print"><h3>📄 Previsualización del Bono</h3></div>', unsafe_allow_html=True)
    st.markdown(bono_html, unsafe_allow_html=True)
    
    # ==================== COMPONENTE PARA IMPRIMIR CON html2canvas ====================
    # Este componente captura el contenedor del bono y lo imprime
    components.html(f"""
        <div style="margin-top:10px; text-align:center;">
            <button id="btn-imprimir" style="
                background: #1a3c6e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.2s;
                width: 100%;
                max-width: 300px;
            " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                🖨️ IMPRIMIR BONO
            </button>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
            document.getElementById('btn-imprimir').addEventListener('click', function() {{
                const element = document.getElementById('bono-para-imprimir');
                // Asegurar que el elemento tenga fondo blanco para la captura
                html2canvas(element, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    allowTaint: true,
                    logging: false,
                }}).then(canvas => {{
                    // Crear una ventana nueva para mostrar la imagen e imprimir
                    const win = window.open('');
                    win.document.write('<html><head><title>Imprimir Bono</title></head><body style="margin:0; padding:0; text-align:center;">');
                    win.document.write('<img src="' + canvas.toDataURL() + '" style="max-width:100%; height:auto;" />');
                    win.document.write('</body></html>');
                    win.document.close();
                    // Esperar a que cargue la imagen y luego imprimir
                    setTimeout(function() {{
                        win.focus();
                        win.print();
                    }}, 500);
                }}).catch(error => {{
                    alert('Error al capturar el bono. Intente de nuevo.');
                    console.error(error);
                }});
            }});
        </script>
    """, height=100)
    
    # Botón para limpiar y empezar de nuevo
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    if st.button("🔄 NUEVO BONO", use_container_width=True):
        limpiar_formulario()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
