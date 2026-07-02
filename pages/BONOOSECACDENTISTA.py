import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import qrcode
import os
import streamlit.components.v1 as components

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
    for key in list(st.session_state.keys()):
        if key.startswith('bono_') or key in ['qr_base64', 'logo_base64']:
            del st.session_state[key]
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
    st.session_state.bono_fecha = datetime.now()
    st.session_state.qr_base64 = ''
    st.session_state.logo_base64 = ''

# ==================== RESET ====================
if st.query_params.get("reset") == "true":
    limpiar_formulario()
    st.query_params.clear()
    st.rerun()

# ==================== TÍTULO Y BOTÓN NUEVO ====================
col_title, col_nuevo = st.columns([4, 1])
with col_title:
    st.title("🦷 GENERADOR DE BONO ODONTOLÓGICO")

with col_nuevo:
    if st.button("🔄 Nuevo Bono", use_container_width=True):
        limpiar_formulario()
        st.rerun()

st.markdown("Complete los datos del afiliado para generar el bono.")

# ==================== FORMULARIO ====================
with st.form("form_bono"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("👤 Nombre del Beneficiario", placeholder="Ej: Juan Pérez")
        dni = st.text_input("🆔 DNI", placeholder="Ej: 30.123.456")
    with col2:
        sector = st.text_input("🏢 Sector / Agencia", placeholder="Ej: Agencia Miramar")
        fecha_emision = st.date_input("📅 Fecha de Emisión", datetime.now())
   
    generar = st.form_submit_button("📋 GENERAR BONO", use_container_width=True)

# ==================== GENERACIÓN ====================
if generar and nombre and dni and sector:
    st.session_state.bono_nombre = nombre
    st.session_state.bono_dni = dni
    st.session_state.bono_sector = sector
    st.session_state.bono_fecha = fecha_emision
    st.session_state.bono_generado = True
   
    qr_data = f"OSECAC|BONO|{nombre}|{dni}|{sector}|{fecha_emision}|{datetime.now().timestamp()}"
    st.session_state.qr_base64 = generar_qr_base64(qr_data)
   
    logo_path = "LOGOAMEC.png"
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), "LOGOAMEC.png")
    st.session_state.logo_base64 = get_image_base64(logo_path)
   
    st.rerun()

# ==================== MOSTRAR BONO ====================
if st.session_state.bono_generado and st.session_state.bono_nombre:
    
    nombre_val = st.session_state.bono_nombre
    dni_val = st.session_state.bono_dni
    sector_val = st.session_state.bono_sector
    fecha_val = st.session_state.bono_fecha
    qr_base64 = st.session_state.qr_base64
    logo_base64 = st.session_state.logo_base64
   
    fecha_str = fecha_val.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")

    bono_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            * {{margin:0;padding:0;box-sizing:border-box;}}
            body {{font-family:Arial,sans-serif; background:#f0f2f6; padding:20px; display:flex; justify-content:center;}}
            .bono-container {{
                background:white; padding:25px 30px; border-radius:12px; 
                box-shadow:0 8px 16px rgba(0,0,0,0.15); max-width:580px; 
                border:2px solid #1a3c6e;
            }}
            .logo-container {{text-align:center; margin-bottom:10px;}}
            .logo-container img {{width:180px;}}
            .bono-titulo {{color:#1a3c6e; font-size:24px; font-weight:bold; text-align:center; 
                border:3px solid #1a3c6e; padding:10px; margin:10px 0; border-radius:8px; background:#f0f7ff;}}
            .bono-subtitulo {{color:#cc0000; font-size:28px; font-weight:bold; text-align:center; 
                margin:15px 0; text-transform:uppercase; background:#fef0f0; padding:8px; border-radius:4px;}}
            .bono-datos {{background:#f8fafc; padding:15px 20px; border-radius:8px; margin:15px 0; 
                border-left:5px solid #1a3c6e;}}
            .bono-qr {{text-align:center; margin:15px 0;}}
            .bono-qr img {{width:90px; height:90px;}}
            .bono-footer {{display:flex; justify-content:space-around; margin-top:20px; padding-top:15px; border-top:2px dashed #1a3c6e;}}
            .btn-imprimir {{
                background:#1a3c6e; color:white; border:none; padding:12px 30px; font-size:18px; 
                font-weight:bold; border-radius:8px; cursor:pointer; margin-top:15px; width:100%;
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
                <div style="text-align:center; border-top:2px dashed #1a3c6e; padding-top:8px; width:120px;">
                    SELLO
                </div>
                <div style="text-align:center; border-top:2px dashed #1a3c6e; padding-top:8px; width:120px;">
                    FIRMA
                </div>
            </div>
        </div>

        <button class="btn-imprimir" onclick="capturarEImprimir()">🖨️ IMPRIMIR BONO</button>

        <script>
            function capturarEImprimir() {{
                html2canvas(document.getElementById('bono-para-imprimir'), {{scale: 2}}).then(canvas => {{
                    const win = window.open('');
                    win.document.write('<img src="' + canvas.toDataURL() + '" style="max-width:100%;"/>');
                    win.document.close();
                    setTimeout(() => win.print(), 500);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    components.html(bono_html, height=850, scrolling=True)

else:
    if generar:
        st.warning("⚠️ Complete todos los campos.")
    else:
        st.info("Complete los datos y presione GENERAR BONO.")
