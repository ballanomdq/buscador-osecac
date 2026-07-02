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

# ==================== LIMPIAR TODO ====================
def reset_completo():
    """Limpia absolutamente todo como si fuera F5"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Recrear variables básicas
    st.session_state.bono_generado = False
    st.session_state.bono_nombre = ''
    st.session_state.bono_dni = ''
    st.session_state.bono_sector = ''
    st.session_state.bono_fecha = datetime.now()
    st.session_state.qr_base64 = ''
    st.session_state.logo_base64 = ''

# ==================== INICIALIZACIÓN ====================
if 'bono_generado' not in st.session_state:
    reset_completo()

# ==================== RESET POR URL ====================
if st.query_params.get("reset") == "true":
    reset_completo()
    st.query_params.clear()
    st.rerun()

# ==================== TÍTULO Y BOTÓN NUEVO ====================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🦷 GENERADOR DE BONO ODONTOLÓGICO")
with col2:
    if st.button("🔄 Nuevo Bono", use_container_width=True, type="secondary"):
        reset_completo()
        st.rerun()

st.markdown("Complete los datos del afiliado para generar el bono.")

# ==================== FORMULARIO CON KEYS ====================
with st.form("form_bono"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input(
            "👤 Nombre del Beneficiario", 
            placeholder="Ej: Juan Pérez",
            key="input_nombre"
        )
        dni = st.text_input(
            "🆔 DNI", 
            placeholder="Ej: 30.123.456",
            key="input_dni"
        )
    with col2:
        sector = st.text_input(
            "🏢 Sector / Agencia", 
            placeholder="Ej: Agencia Miramar",
            key="input_sector"
        )
        fecha_emision = st.date_input(
            "📅 Fecha de Emisión", 
            datetime.now(),
            key="input_fecha"
        )
   
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
if st.session_state.get('bono_generado', False):
    
    bono_html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        * {{margin:0;padding:0;box-sizing:border-box;}}
        body {{background:#f0f2f6; padding:15px; font-family:Arial,sans-serif;}}
        .bono-container {{background:white; padding:25px; border:2px solid #1a3c6e; border-radius:12px; max-width:580px; margin:auto; box-shadow:0 8px 16px rgba(0,0,0,0.15);}}
        .logo-container {{text-align:center; margin-bottom:10px;}}
        .logo-container img {{width:180px;}}
        .bono-titulo {{color:#1a3c6e; font-size:24px; font-weight:bold; text-align:center; border:3px solid #1a3c6e; padding:10px; border-radius:8px; background:#f0f7ff;}}
        .bono-subtitulo {{color:#cc0000; font-size:27px; font-weight:bold; text-align:center; margin:15px 0; background:#fef0f0; padding:8px; border-radius:4px;}}
        .bono-datos {{background:#f8fafc; padding:15px; border-radius:8px; border-left:5px solid #1a3c6e; margin:15px 0;}}
        .bono-qr {{text-align:center; margin:15px 0;}}
        .bono-qr img {{width:85px; height:85px;}}
        .btn-imprimir {{background:#1a3c6e; color:white; border:none; padding:12px 30px; font-size:18px; font-weight:bold; border-radius:8px; width:100%; margin-top:15px; cursor:pointer;}}
    </style>
    </head><body>
        <div id="bono" class="bono-container">
            <div class="logo-container">
                {f'<img src="data:image/png;base64,{st.session_state.logo_base64}" alt="Logo">' if st.session_state.get('logo_base64') else '<h2>OSECAC</h2>'}
            </div>
            <div class="bono-titulo">COSEGURO ODONTOLÓGICO</div>
            <div class="bono-subtitulo">⚠️ NO AFILIADO AL SEC ⚠️</div>
            <div class="bono-datos">
                <p><strong>NOMBRE:</strong> {st.session_state.bono_nombre.upper()}</p>
                <p><strong>DNI:</strong> {st.session_state.bono_dni}</p>
                <p><strong>SECTOR:</strong> {st.session_state.bono_sector.upper()}</p>
                <p><strong>FECHA:</strong> {st.session_state.bono_fecha.strftime("%d/%m/%Y")} - {datetime.now().strftime("%H:%M")}</p>
            </div>
            <div class="bono-qr">
                <img src="data:image/png;base64,{st.session_state.qr_base64}" alt="QR">
            </div>
        </div>
        <button class="btn-imprimir" onclick="capturarEImprimir()">🖨️ IMPRIMIR BONO</button>

        <script>
            function capturarEImprimir() {{
                html2canvas(document.getElementById('bono'), {{scale:2}}).then(canvas => {{
                    const win = window.open('');
                    win.document.write('<img src="'+canvas.toDataURL()+'" style="max-width:100%;"/>');
                    win.document.close();
                    setTimeout(()=>win.print(), 500);
                }});
            }}
        </script>
    </body></html>
    """
    components.html(bono_html, height=780, scrolling=True)

else:
    if generar:
        st.warning("⚠️ Complete todos los campos.")
