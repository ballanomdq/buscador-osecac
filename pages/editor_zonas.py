import streamlit as st
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

st.set_page_config(page_title="Prueba de Puntería PDF", layout="centered")

st.title("🎯 Prueba de Posicionamiento en PDF")
st.markdown("Este PDF muestra números en las posiciones donde se escribirán los datos.")

# Coordenadas base (en puntos, 1 punto = 1/72 pulgada)
# A4 landscape = 842 x 595 puntos
coordenadas = {
    "AREA_FISCALIZACION": (37, 143),
    "INSPECTOR_NOMBRE": (521, 165),
    "MES": (144, 459),
    "AÑO": (302, 459),
    "FOLIO": (853, 456),
    "EMPRESA_1_RAZON_SOCIAL": (144, 459),
    "EMPRESA_1_CUIT": (224, 540),
    "EMPRESA_1_ACTA": (405, 542),
    "EMPRESA_1_VTO": (422, 541),
    "EMPRESA_1_DESDE": (525, 542),
    "EMPRESA_1_HASTA": (559, 542),
    "EMPRESA_1_DEUDA": (600, 540),
}

# Desplazamiento vertical entre empresas (en puntos)
DESPLAZAMIENTO_VERTICAL = 38

# Generar PDF con números de posición
def generar_pdf_prueba():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)  # 842 x 595
    
    # Dibujar números en las posiciones
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(1, 0, 0)  # Rojo para que se vea bien
    
    # Número 1: Área de fiscalización
    x, y = coordenadas["AREA_FISCALIZACION"]
    c.drawString(x, height - y, "1")
    
    # Número 2: Nombre inspector
    x, y = coordenadas["INSPECTOR_NOMBRE"]
    c.drawString(x, height - y, "2")
    
    # Número 3: MES
    x, y = coordenadas["MES"]
    c.drawString(x, height - y, "3")
    
    # Número 4: AÑO
    x, y = coordenadas["AÑO"]
    c.drawString(x, height - y, "4")
    
    # Número 5: FOLIO
    x, y = coordenadas["FOLIO"]
    c.drawString(x, height - y, "5")
    
    # Empresa 1 (6 al 12)
    x, y = coordenadas["EMPRESA_1_RAZON_SOCIAL"]
    c.drawString(x, height - y, "6")
    
    x, y = coordenadas["EMPRESA_1_CUIT"]
    c.drawString(x, height - y, "7")
    
    x, y = coordenadas["EMPRESA_1_ACTA"]
    c.drawString(x, height - y, "8")
    
    x, y = coordenadas["EMPRESA_1_VTO"]
    c.drawString(x, height - y, "9")
    
    x, y = coordenadas["EMPRESA_1_DESDE"]
    c.drawString(x, height - y, "10")
    
    x, y = coordenadas["EMPRESA_1_HASTA"]
    c.drawString(x, height - y, "11")
    
    x, y = coordenadas["EMPRESA_1_DEUDA"]
    c.drawString(x, height - y, "12")
    
    # Empresa 2 (13 al 19) - mismo X, Y + desplazamiento
    y_base = coordenadas["EMPRESA_1_RAZON_SOCIAL"][1] + DESPLAZAMIENTO_VERTICAL
    
    x = coordenadas["EMPRESA_1_RAZON_SOCIAL"][0]
    c.drawString(x, height - y_base, "13")
    
    x = coordenadas["EMPRESA_1_CUIT"][0]
    c.drawString(x, height - y_base, "14")
    
    x = coordenadas["EMPRESA_1_ACTA"][0]
    c.drawString(x, height - y_base, "15")
    
    x = coordenadas["EMPRESA_1_VTO"][0]
    c.drawString(x, height - y_base, "16")
    
    x = coordenadas["EMPRESA_1_DESDE"][0]
    c.drawString(x, height - y_base, "17")
    
    x = coordenadas["EMPRESA_1_HASTA"][0]
    c.drawString(x, height - y_base, "18")
    
    x = coordenadas["EMPRESA_1_DEUDA"][0]
    c.drawString(x, height - y_base, "19")
    
    # Empresa 3 (20 al 26)
    y_base = coordenadas["EMPRESA_1_RAZON_SOCIAL"][1] + (DESPLAZAMIENTO_VERTICAL * 2)
    
    x = coordenadas["EMPRESA_1_RAZON_SOCIAL"][0]
    c.drawString(x, height - y_base, "20")
    
    x = coordenadas["EMPRESA_1_CUIT"][0]
    c.drawString(x, height - y_base, "21")
    
    x = coordenadas["EMPRESA_1_ACTA"][0]
    c.drawString(x, height - y_base, "22")
    
    x = coordenadas["EMPRESA_1_VTO"][0]
    c.drawString(x, height - y_base, "23")
    
    x = coordenadas["EMPRESA_1_DESDE"][0]
    c.drawString(x, height - y_base, "24")
    
    x = coordenadas["EMPRESA_1_HASTA"][0]
    c.drawString(x, height - y_base, "25")
    
    x = coordenadas["EMPRESA_1_DEUDA"][0]
    c.drawString(x, height - y_base, "26")
    
    # Empresa 4 al 8 (27 al 55) - seguiría el mismo patrón
    for i in range(4, 9):
        y_base = coordenadas["EMPRESA_1_RAZON_SOCIAL"][1] + (DESPLAZAMIENTO_VERTICAL * (i-1))
        num_actual = 19 + (i-2) * 7
        c.drawString(coordenadas["EMPRESA_1_RAZON_SOCIAL"][0], height - y_base, str(num_actual))
        c.drawString(coordenadas["EMPRESA_1_CUIT"][0], height - y_base, str(num_actual+1))
        c.drawString(coordenadas["EMPRESA_1_ACTA"][0], height - y_base, str(num_actual+2))
        c.drawString(coordenadas["EMPRESA_1_VTO"][0], height - y_base, str(num_actual+3))
        c.drawString(coordenadas["EMPRESA_1_DESDE"][0], height - y_base, str(num_actual+4))
        c.drawString(coordenadas["EMPRESA_1_HASTA"][0], height - y_base, str(num_actual+5))
        c.drawString(coordenadas["EMPRESA_1_DEUDA"][0], height - y_base, str(num_actual+6))
    
    c.save()
    buffer.seek(0)
    return buffer

# Botón para generar y descargar
if st.button("📄 GENERAR PDF DE PRUEBA", type="primary", use_container_width=True):
    with st.spinner("Generando PDF..."):
        pdf_buffer = generar_pdf_prueba()
        
        st.success("✅ PDF generado correctamente")
        
        st.download_button(
            label="📥 DESCARGAR PDF CON NÚMEROS",
            data=pdf_buffer,
            file_name=f"prueba_posiciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")
st.markdown("""
### 📌 Instrucciones:
1. Apretá el botón **"GENERAR PDF DE PRUEBA"**
2. Descargá y abrí el PDF
3. Verificá que los números estén en los lugares correctos:
   - **1** : Área de fiscalización (debe ir "MAR DEL PLATA")
   - **2** : Nombre del inspector
   - **3** : MES
   - **4** : AÑO  
   - **5** : FOLIO
   - **6** : Razón social empresa 1
   - **7** : CUIT empresa 1
   - **8** : ACTA empresa 1
   - **9** : VTO empresa 1
   - **10** : DESDE empresa 1
   - **11** : HASTA empresa 1
   - **12** : DEUDA empresa 1
   - **13-19**: Empresa 2
   - **20-26**: Empresa 3
   - etc.
4. **Decime qué números están mal ubicados y te ajusto las coordenadas**
""")
