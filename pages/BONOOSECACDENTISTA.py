import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Configuración de la página
st.set_page_config(
    page_title="Bono Odontológico - OSECAC",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar y elementos de Streamlit
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
    display: none !important;
}
.stApp {
    background-color: #f0f2f6 !important;
}
.bono-container {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    max-width: 600px;
    margin: 0 auto;
    font-family: 'Arial', sans-serif;
}
.bono-titulo {
    color: #1a3c6e;
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    border-bottom: 3px solid #1a3c6e;
    padding-bottom: 10px;
}
.bono-subtitulo {
    color: #cc0000;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
    margin: 15px 0;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.bono-datos {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
.bono-datos p {
    margin: 8px 0;
    font-size: 16px;
}
.bono-datos strong {
    color: #1a3c6e;
}
.bono-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 2px dashed #1a3c6e;
}
.bono-sello {
    border: 2px solid #1a3c6e;
    padding: 10px 20px;
    text-align: center;
    color: #1a3c6e;
    font-size: 12px;
    border-radius: 5px;
    background: #f8f9fa;
}
.bono-firma {
    border-top: 2px solid #000;
    width: 200px;
    text-align: center;
    padding-top: 5px;
    font-size: 12px;
}
.bono-fecha {
    font-size: 12px;
    color: #666;
    text-align: right;
}
.bono-qr {
    text-align: center;
    margin: 10px 0;
}
@media print {
    .stApp {
        background: white !important;
    }
    .stButton, .stTextInput, .stSelectbox {
        display: none !important;
    }
    .no-print {
        display: none !important;
    }
    .bono-container {
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        max-width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Función para convertir imagen a base64
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Función para generar QR
def generar_qr(datos):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=2,
    )
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ================= FORMULARIO =================
st.markdown('<div class="no-print">', unsafe_allow_html=True)

st.title("🦷 BONO ODONTOLÓGICO")
st.markdown("### Complete los datos del afiliado")

with st.form("form_bono"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("👤 Nombre del Beneficiario", placeholder="Ej: Juan Pérez")
        dni = st.text_input("🆔 DNI", placeholder="Ej: 30.123.456")
    
    with col2:
        sector = st.text_input("🏢 Sector / Agencia", placeholder="Ej: Agencia Miramar")
        fecha_emision = st.date_input("📅 Fecha de Emisión", datetime.now())
    
    # Botón para generar el bono
    generar = st.form_submit_button("📋 GENERAR BONO", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ================= GENERACIÓN DEL BONO =================
if generar and nombre and dni and sector:
    
    # Datos para el QR (para evitar falsificaciones)
    qr_data = f"OSECAC|BONO|{nombre}|{dni}|{sector}|{fecha_emision}|{datetime.now().timestamp()}"
    qr_base64 = generar_qr(qr_data)
    
    # Logo de OSECAC
    logo_path = "logo osecac.png"
    logo_base64 = get_image_base64(logo_path)
    
    # Fecha formateada
    fecha_str = fecha_emision.strftime("%d/%m/%Y")
    hora_str = datetime.now().strftime("%H:%M")
    
    # ================= BONO HTML =================
    bono_html = f"""
    <div class="bono-container" id="bono-para-imprimir">
        
        <!-- LOGO -->
        <div style="text-align: center; margin-bottom: 10px;">
            {f'<img src="data:image/png;base64,{logo_base64}" style="width: 120px; height: auto;">' if logo_base64 else 'OSECAC'}
        </div>
        
        <!-- TÍTULO -->
        <div class="bono-titulo">
            COSEGURO ODONTOLÓGICO
        </div>
        
        <!-- SUBTÍTULO DESTACADO -->
        <div class="bono-subtitulo">
            ⚠️ NO AFILIADO AL SEC ⚠️
        </div>
        
        <!-- DATOS DEL AFILIADO -->
        <div class="bono-datos">
            <p><strong>👤 NOMBRE DEL BENEFICIARIO:</strong> {nombre.upper()}</p>
            <p><strong>🆔 DNI:</strong> {dni}</p>
            <p><strong>🏢 SECTOR / AGENCIA:</strong> {sector.upper()}</p>
            <p><strong>📅 FECHA DE EMISIÓN:</strong> {fecha_str} - {hora_str}</p>
        </div>
        
        <!-- QR -->
        <div class="bono-qr">
            <img src="data:image/png;base64,{qr_base64}" style="width: 80px; height: 80px;">
            <p style="font-size: 10px; color: #666; margin: 2px 0;">Código de verificación único</p>
        </div>
        
        <!-- FOOTER: SELLO + FIRMA -->
        <div class="bono-footer">
            <div class="bono-sello">
                SELLO<br>
                <span style="font-size: 10px;">(Lugar para el sello)</span>
            </div>
            <div class="bono-firma">
                FIRMA DEL AFILIADO<br>
                <span style="font-size: 10px;">(Acepto las condiciones)</span>
            </div>
        </div>
        
        <!-- PIE DE PÁGINA -->
        <div style="text-align: center; margin-top: 15px; font-size: 10px; color: #999; border-top: 1px solid #ddd; padding-top: 8px;">
            Este documento es válido solo para prestaciones odontológicas.<br>
            No es válido como comprobante de pago. Verificar vigencia en sistema.
        </div>
        
        <!-- FECHA DE IMPRESIÓN -->
        <div class="bono-fecha">
            Impreso el: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        </div>
    </div>
    """
    
    # Mostrar el bono
    st.markdown("---")
    st.markdown("### 📄 Bono Generado")
    st.markdown(bono_html, unsafe_allow_html=True)
    
    # ================= BOTONES DE ACCIÓN =================
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    
    col_imprimir, col_limpiar = st.columns(2)
    
    with col_imprimir:
        # Botón para imprimir
        st.markdown(f"""
        <button onclick="window.print()" style="
            background: linear-gradient(145deg, #1a3c6e, #0f2b4f);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
        ">
            🖨️ IMPRIMIR BONO
        </button>
        """, unsafe_allow_html=True)
    
    with col_limpiar:
        if st.button("🔄 NUEVO BONO", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advertencia
    st.info("💡 **Consejo:** Al imprimir, seleccione 'Guardar como PDF' para tener una copia digital.")

else:
    if generar:
        st.warning("⚠️ Por favor, complete TODOS los campos antes de generar el bono.")
    else:
        st.info("📝 Complete los datos del afiliado y presione 'GENERAR BONO'.")

# ================= INSTRUCCIONES =================
with st.expander("ℹ️ Instrucciones de uso"):
    st.markdown("""
    ### Cómo usar este bono:
    
    1. **Complete todos los campos** del formulario.
    2. **Presione "GENERAR BONO"** para crear el documento.
    3. **Revise que los datos sean correctos** antes de imprimir.
    4. **Presione "IMPRIMIR BONO"** para enviar a la impresora.
    5. **El QR** sirve como código de verificación único.
    6. **El afiliado debe firmar** en el espacio correspondiente.
    7. **El profesional debe sellar** en el espacio indicado.
    
    ### Medidas de seguridad:
    - ✅ Cada bono tiene un **QR único** generado en el momento.
    - ✅ Incluye **fecha y hora exacta** de emisión.
    - ✅ El diseño institucional dificulta la falsificación.
    - ✅ Se recomienda **no fotocopiar** este documento.
    """)
