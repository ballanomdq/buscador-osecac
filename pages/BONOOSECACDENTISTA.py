import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os

st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS para el bono y para ocultar elementos al imprimir
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
        display: none !important;
    }
    .stApp { background-color: #f0f2f6 !important; }
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
        border-bottom: 3px solid #1a3c6e;
        padding-bottom: 8px;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .bono-subtitulo {
        color: #cc0000;
        font-size: 26px;
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
    .bono-datos p { margin: 6px 0; font-size: 15px; color: #1e293b; }
    .bono-datos strong { color: #0b2a4a; }
    .bono-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 18px;
        padding-top: 12px;
        border-top: 2px dashed #1a3c6e;
    }
    .bono-sello {
        border: 2px solid #1a3c6e;
        padding: 8px 16px;
        text-align: center;
        color: #1a3c6e;
        font-size: 11px;
        border-radius: 6px;
        background: #f8fafc;
        min-width: 100px;
    }
    .bono-firma {
        border-top: 2px solid #1a3c6e;
        width: 180px;
        text-align: center;
        padding-top: 6px;
        font-size: 11px;
        color: #1e293b;
    }
    .bono-qr { text-align: center; margin: 8px 0; }
    .bono-qr img { width: 70px; height: 70px; }
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
    .logo-container { text-align: center; margin-bottom: 6px; }
    .logo-container img { width: 100px; height: auto; }
    .btn-imprimir, .btn-pdf {
        display: inline-block;
        background: linear-gradient(145deg, #1a3c6e, #0f2b4f);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
        text-align: center;
        text-decoration: none;
        cursor: pointer;
        transition: 0.2s;
        margin-bottom: 10px;
    }
    .btn-pdf { background: linear-gradient(145deg, #16a34a, #15803d); }
    .btn-imprimir:hover { transform: scale(1.02); background: #0f2b4f; }
    .btn-pdf:hover { transform: scale(1.02); background: #15803d; }
    .no-print { display: block; }
    @media print {
        .no-print { display: none !important; }
        .bono-container {
            border: none !important;
            box-shadow: none !important;
            padding: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Funciones auxiliares ---
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

# --- Estado de sesión (sin claves de widgets) ---
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
if 'bono_html' not in st.session_state:
    st.session_state.bono_html = ''

def limpiar_formulario():
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
    st.session_state.bono_html = ''
    st.rerun()

# --- Formulario ---
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.title("🦷 BONO ODONTOLÓGICO")
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

# --- Lógica de generación ---
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

    # HTML del bono (solo el contenido)
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
            <div class="bono-sello">SELLO<br><span style="font-size:9px;">(Lugar para el sello)</span></div>
            <div class="bono-firma">FIRMA DEL AFILIADO<br><span style="font-size:9px;">(Acepto condiciones)</span></div>
        </div>
        <div class="bono-pie">Válido solo para prestaciones odontológicas. No válido como comprobante de pago.</div>
        <div class="bono-fecha-impresion">Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
    </div>
    """
    st.session_state.bono_html = bono_html

    # --- Mostrar bono ---
    st.markdown("---")
    st.markdown('<div class="no-print"><h3>📄 Bono generado</h3></div>', unsafe_allow_html=True)
    st.markdown(bono_html, unsafe_allow_html=True)

    # --- Botones de acción con JavaScript para imprimir y descargar PDF ---
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        # Botón de impresión directa con window.print()
        st.components.v1.html("""
        <button onclick="window.print()" style="
            width:100%;
            padding:12px;
            background:#1a3c6e;
            color:white;
            border:none;
            border-radius:10px;
            font-size:16px;
            font-weight:bold;
            cursor:pointer;
            transition: 0.2s;
        " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            🖨️ IMPRIMIR BONO
        </button>
        """, height=60)

    with col2:
        # Botón para descargar PDF usando html2pdf.js (librería cliente)
        st.components.v1.html(f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js" integrity="sha512-GsLlZN/3F2ErC5ifS5QtgpiJtWd43JWSuIgh7mbzZ8zBps+dvLusV+eNQATqgA/HdeKFVgA5v3S/cIrLF7QnIg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <button id="descargar-pdf" style="
            width:100%;
            padding:12px;
            background:#16a34a;
            color:white;
            border:none;
            border-radius:10px;
            font-size:16px;
            font-weight:bold;
            cursor:pointer;
            transition: 0.2s;
        " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            📄 DESCARGAR PDF
        </button>
        <script>
            document.getElementById('descargar-pdf').addEventListener('click', function() {{
                var element = document.querySelector('.bono-container');
                if (element) {{
                    // Clonar el elemento para evitar conflictos con estilos de Streamlit
                    var clone = element.cloneNode(true);
                    // Remover estilos que puedan afectar la generación del PDF
                    clone.style.margin = '0 auto';
                    clone.style.padding = '20px';
                    clone.style.backgroundColor = 'white';
                    clone.style.boxShadow = 'none';
                    clone.style.border = '1px solid #ccc';
                    // Crear un contenedor temporal
                    var wrapper = document.createElement('div');
                    wrapper.style.width = '600px';
                    wrapper.style.margin = '0 auto';
                    wrapper.appendChild(clone);
                    document.body.appendChild(wrapper);
                    // Generar PDF
                    html2pdf()
                        .from(wrapper)
                        .set({{
                            margin:        [0.5, 0.5, 0.5, 0.5],
                            filename:     'bono_{nombre_val.replace(' ', '_')}_{dni_val}.pdf',
                            image:        {{ type: 'jpeg', quality: 0.98 }},
                            html2canvas:  {{ scale: 2, letterRendering: true, useCORS: true, logging: false }},
                            jsPDF:        {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
                        }})
                        .save()
                        .then(function() {{
                            // Limpiar el contenedor temporal
                            document.body.removeChild(wrapper);
                        }});
                }} else {{
                    alert('No se encontró el bono para descargar.');
                }}
            }});
        </script>
        """, height=100)

    st.markdown('</div>', unsafe_allow_html=True)
    st.info("🔒 **Código QR**: Contiene los datos del afiliado y la fecha de emisión. Sirve como verificación de autenticidad.")

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
