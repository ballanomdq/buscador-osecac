import streamlit as st
import os
import fitz  # PyMuPDF
import io
from datetime import datetime

st.set_page_config(page_title="Prueba de Relleno de PDF", layout="centered")
st.title("🎯 Prueba de Relleno de PDF")
st.markdown("Este script **descarga el PDF y lo rellena con números** para verificar posiciones exactas.")

# NOTA: Cambié el nombre al que tenés en tu script
PDF_PATH = "PLANILLA INSPECTORES.pdf"

# COORDENADAS REALES (X, Y) para A4 Vertical (595 x 842)
# El origen (0,0) está ARRIBA a la izquierda.
COORDENADAS = {
    # --- CABECERA ---
    1: (170, 75),   # Nombre del Inspector
    2: (490, 75),   # MES Y AÑO
    3: (555, 75),   # FOLIO

    # --- FILA 1 ---
    4: (20, 155),   # Empresa 1 - Razón Social / Dirección
    5: (170, 155),  # Empresa 1 - CUIT
    6: (240, 155),  # Empresa 1 - ACTA (AV/RT/AC)
    7: (280, 155),  # Empresa 1 - Nro Actuación
    8: (320, 155),  # Empresa 1 - VTO
    9: (360, 155),  # Empresa 1 - Cantidad Empleados
    10: (390, 155), # Empresa 1 - Período Verificado DESDE (Mes/Año)
    11: (445, 155), # Empresa 1 - Deuda Determinada ($)

    # --- FILA 2 (Desplazamiento vertical de +45 puntos hacia abajo) ---
    12: (20, 200),  # Empresa 2 - Razón Social
    13: (170, 200), # Empresa 2 - CUIT
    14: (280, 200), # Empresa 2 - Nro Actuación
    15: (320, 200), # Empresa 2 - VTO
    16: (390, 200), # Empresa 2 - Período Verificado
    17: (445, 200), # Empresa 2 - Deuda Determinada

    # --- FILA 3 ---
    18: (20, 245),  # Empresa 3 - Razón Social
    19: (170, 245), # Empresa 3 - CUIT
    20: (280, 245), # Empresa 3 - Nro Actuación
    21: (320, 245), # Empresa 3 - VTO
    22: (390, 245), # Empresa 3 - Período Verificado
    23: (445, 245), # Empresa 3 - Deuda Determinada

    # --- CAMPOS INFERIORES ---
    24: (25, 560),  # OBSERVACIONES
    25: (360, 560), # LUGAR Y FECHA
    26: (430, 560), # FIRMA INSPECTOR
}

def rellenar_pdf_con_numeros():
    """Abre el PDF original, escribe números en las coordenadas reales y devuelve el buffer"""
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]  # Primera página
    
    fontsize = 10
    color = (1, 0, 0)  # Rojo bien visible
    
    for num, (x, y) in COORDENADAS.items():
        # ATENCIÓN: En PyMuPDF (fitz), el origen ya es TOP-LEFT para text insertion.
        # Quitamos la conversión invertida que rompía todo.
        page.insert_text((x, y), str(num), fontsize=fontsize, color=color)
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

# Verificar que el PDF existe en el servidor de Streamlit
if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}'")
    st.info(f"Archivos en el directorio actual: {os.listdir('.')}")
    st.stop()

st.success(f"✅ PDF encontrado: {PDF_PATH}")

if st.button("📄 GENERAR PDF CON NÚMEROS", type="primary", use_container_width=True):
    try:
        with st.spinner("Rellenando PDF con números oficiales..."):
            pdf_buffer = rellenar_pdf_con_numeros()
        
        st.success("✅ PDF generado con coordenadas reales")
        
        st.download_button(
            label="📥 DESCARGAR PDF RELLENADO",
            data=pdf_buffer,
            file_name=f"prueba_coordenadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error crítico en el proceso: {e}")
