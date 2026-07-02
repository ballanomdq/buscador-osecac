import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os
import streamlit.components.v1 as components
import urllib.parse

# Configuración de página
st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
if 'qr_base64' not in st.session_state:
    st.session_state.qr_base64 = ''
if 'logo_base64' not in st.session_state:
    st.session_state.logo_base64 = ''

def limpiar_formulario():
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
    st.session_state.qr_base64 = ''
    st.session_state.logo_base64 = ''
    st.rerun()

# ==================== LÓGICA DE LIMPIEZA POR URL ====================
# Si la URL tiene ?reset=true, limpiar el estado y redirigir sin el parámetro
query_params = st.query_params
if query_params.get("reset") == "true":
    limpiar_formulario()
    # Limpiar el parámetro de la URL usando st.query_params.clear()
    st.query_params.clear()
    # Forzar recarga sin parámetros (esto reinicia el script)
    st.rerun()

# ==================== FORMULARIO ====================
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

# ==================== LÓGICA DE GENERACIÓN ====================
if generar and nombre and dni and sector:
    # Guardar datos
    st.session_state.bono_nombre = nombre
    st.session_state.bono_dni = dni
    st.session_state.bono_sector = sector
    st.session_state.bono_fecha = fecha_emision
    st.session_state.bono_generado = True
    
    # Generar QR
    qr_data = f"OSECAC|BONO|{nombre}|{dni}|{sector}|{fecha_emision}|{datetime.now().timestamp()}"
    st.session_state.qr_base64 = generar_qr_base64(qr_data)
    
    # Obtener logo (NUEVO LOGO: LOGOAMEC.png)
    logo_path = "LOGOAMEC.png"  # <--- CAMBIADO A LOGOAMEC.png
    if not os.path.exists(logo_path):
        # Si no está en la raíz, buscar en el directorio del archivo
        logo_path = os.path.join(os.path.dirname(__file__), "LOGOAMEC.png")
    st.session_state.logo_base64 = get_image_base64(logo_path)
    
    st.rerun()

# ==================== MOSTRAR BONO (TODO DENTRO DE components.html) ====================
if st.session_state.bono_generado and st.session_state.bono_nombre:
    
    nombre_val = st.session_state.bono_nombre
    dni_val = st.session_state.bono_dni
    sector_val = st.session_state.bono_sector
    fecha_val = st.session_state.bono_fecha
    qr_base64 = st.session_state.qr_base64
    logo_base64 = st.session_state.logo_base64
    
    fecha_str = fecha_val.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")
    
    # Construir el HTML completo del bono (con estilos y botón de impresión dentro del mismo iframe)
    bono_completo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bono OSECAC</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                background-color: #f0f2f6;
                font-family: Arial, sans-serif;
                padding: 20px;
            }}
            .bono-container {{
                background: white;
                padding: 25px 30px;
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
                max-width: 580px;
                width: 100%;
                border: 2px solid #1a3c6e;
                margin-bottom: 25px;
            }}
            .logo-container {{
                text-align: center;
                margin-bottom: 10px;
            }}
            .logo-container img {{
                width: 180px;
                height: auto;
            }}
            .bono-titulo {{
                color: #1a3c6e;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                border: 3px solid #1a3c6e;
                padding: 10px;
                margin: 10px 0;
                border-radius: 8px;
                background: #f0f7ff;
            }}
            .bono-subtitulo {{
                color: #cc0000;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                margin: 15px 0;
                text-transform: uppercase;
                background: #fef0f0;
                padding: 8px 0;
                border-radius: 4px;
            }}
            .bono-datos {{
                background: #f8fafc;
                padding: 15px 20px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 5px solid #1a3c6e;
            }}
            .bono-datos p {{
                margin: 8px 0;
                font-size: 16px;
                color: #1e293b;
            }}
            .bono-datos strong {{
                color: #0b2a4a;
            }}
            .bono-footer {{
                display: flex;
                justify-content: space-around;
                align-items: center;
                margin-top: 20px;
                padding-top: 15px;
                border-top: 2px dashed #1a3c6e;
            }}
            .bono-sello, .bono-firma {{
                text-align: center;
                border-top: 2px dashed #1a3c6e;
                padding-top: 10px;
                width: 120px;
                color: #1a3c6e;
                font-size: 14px;
                font-weight: bold;
            }}
            .bono-qr {{
                text-align: center;
                margin: 10px 0;
            }}
            .bono-qr img {{
                width: 80px;
                height: 80px;
            }}
            .bono-fecha-impresion {{
                font-size: 10px;
                color: #94a3b8;
                text-align: right;
                margin-top: 8px;
            }}
            .btn-imprimir {{
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
                margin: 0 auto;
                display: block;
            }}
            .btn-imprimir:hover {{
                transform: scale(1.02);
                background: #0f2b4f;
            }}
            .btn-nuevo {{
                background: #6c757d;
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
                margin: 10px auto 0;
                display: block;
            }}
            .btn-nuevo:hover {{
                transform: scale(1.02);
                background: #5a6268;
            }}
            .botones {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
                width: 100%;
                max-width: 300px;
            }}
        </style>
    </head>
    <body>
        <div id="bono-para-imprimir" class="bono-container">
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
            <div class="bono-fecha-impresion">Impreso: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
        </div>
        
        <div class="botones">
            <button class="btn-imprimir" onclick="capturarEImprimir()">🖨️ IMPRIMIR BONO</button>
            <button class="btn-nuevo" onclick="nuevoBono()">🔄 NUEVO BONO</button>
        </div>
        
        <script>
            function capturarEImprimir() {{
                const element = document.getElementById('bono-para-imprimir');
                html2canvas(element, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    allowTaint: true,
                    logging: false,
                }}).then(canvas => {{
                    const win = window.open('');
                    win.document.write('<html><head><title>Imprimir Bono</title></head><body style="margin:0; padding:0; text-align:center;">');
                    win.document.write('<img src="' + canvas.toDataURL() + '" style="max-width:100%; height:auto;" />');
                    win.document.write('</body></html>');
                    win.document.close();
                    setTimeout(function() {{
                        win.focus();
                        win.print();
                    }}, 500);
                }}).catch(error => {{
                    alert('Error al capturar el bono. Intente de nuevo.');
                    console.error(error);
                }});
            }}
            
            function nuevoBono() {{
                // Redirigir a la misma página con ?reset=true para limpiar el estado
                window.location.href = window.location.href.split('?')[0] + '?reset=true';
            }}
        </script>
    </body>
    </html>
    """
    
    # Mostrar el bono completo dentro de components.html
    components.html(bono_completo_html, height=900, scrolling=True)
    
else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos.")
    else:
        st.info("📝 Complete los datos y presione 'GENERAR BONO'.")
