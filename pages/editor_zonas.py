import streamlit as st
import os
import fitz  # PyMuPDF
import io
from datetime import datetime

st.set_page_config(page_title="Prueba de Relleno de PDF", layout="centered")

st.title("🎯 Prueba de Relleno de PDF")
st.markdown("Este script **descarga el PDF y lo rellena con números** para verificar posiciones.")

# Ruta del PDF en el repositorio
PDF_PATH = "PLANILLA INSPECTORES.pdf"

# Coordenadas tentativas (X, Y) en puntos (1 punto = 1/72 pulgada)
# A4 apaisado = 842 x 595 puntos
# Estas coordenadas son aproximadas; habrá que ajustarlas
COORDENADAS = {
    1: (100, 500),   # Área de fiscalización ("MAR DEL PLATA")
    2: (300, 500),   # Nombre del inspector
    3: (100, 450),   # MES
    4: (200, 450),   # AÑO
    5: (700, 500),   # FOLIO
    6: (100, 400),   # Empresa 1 - Razón Social
    7: (250, 400),   # Empresa 1 - CUIT
    8: (350, 400),   # Empresa 1 - ACTA
    9: (450, 400),   # Empresa 1 - VTO
    10: (550, 400),  # Empresa 1 - DESDE
    11: (650, 400),  # Empresa 1 - HASTA
    12: (750, 400),  # Empresa 1 - DEUDA
    # Empresa 2 (desplazamiento vertical de 40 puntos)
    13: (100, 360),
    14: (250, 360),
    15: (350, 360),
    16: (450, 360),
    17: (550, 360),
    18: (650, 360),
    19: (750, 360),
    # Empresa 3
    20: (100, 320),
    21: (250, 320),
    22: (350, 320),
    23: (450, 320),
    24: (550, 320),
    25: (650, 320),
    26: (750, 320),
}

def rellenar_pdf_con_numeros():
    """Abre el PDF original, escribe números en las coordenadas y devuelve el PDF modificado"""
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    # Abrir el PDF original
    doc = fitz.open(PDF_PATH)
    page = doc[0]  # Primera página
    
    # Configurar texto
    fontsize = 12
    color = (1, 0, 0)  # Rojo para que se destaque
    
    # Escribir cada número en su coordenada
    for num, (x, y) in COORDENADAS.items():
        # fitz usa coordenadas Y desde abajo, hay que convertir
        y_convertida = page.rect.height - y
        page.insert_text((x, y_convertida), str(num), fontsize=fontsize, color=color)
    
    # Guardar en memoria
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

# Verificar que el PDF existe
if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}'")
    st.info(f"Archivos en el directorio actual: {os.listdir('.')}")
    st.stop()

st.success(f"✅ PDF encontrado: {PDF_PATH}")

if st.button("📄 GENERAR PDF CON NÚMEROS", type="primary", use_container_width=True):
    try:
        with st.spinner("Rellenando PDF con números..."):
            pdf_buffer = rellenar_pdf_con_numeros()
        
        st.success("✅ PDF generado correctamente")
        
        st.download_button(
            label="📥 DESCARGAR PDF RELLENADO",
            data=pdf_buffer,
            file_name=f"prueba_numeros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.markdown("""
### 📌 Instrucciones:
1. Apretá el botón **"GENERAR PDF CON NÚMEROS"**
2. Descargá y abrí el PDF
3. **Decime qué números están mal ubicados** y en qué dirección hay que moverlos (ej: "el 1 debería estar más arriba", "el 6 debería estar más a la izquierda")
4. Con tu feedback, ajusto las coordenadas exactas
""")
