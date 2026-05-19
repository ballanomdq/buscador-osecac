import streamlit as st
import io
import fitz  # PyMuPDF
from datetime import datetime

st.set_page_config(page_title="Prueba sobre PDF Original", layout="centered")

st.title("🎯 Prueba de Puntería sobre PDF Original")
st.markdown("Este script escribe números SOBRE TU PDF ORIGINAL para verificar las posiciones.")

# Coordenadas que vos sacaste (en píxeles)
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

DESPLAZAMIENTO_VERTICAL = 45  # Ajustar según necesidad

# Ruta del PDF original (asegurate que esté en la misma carpeta)
PDF_ORIGINAL = "EJEMPLO INFORME MENSUAL DE INSPECTORES 101150.pdf"

def escribir_numeros_en_pdf():
    # Abrir el PDF original
    doc = fitz.open(PDF_ORIGINAL)
    page = doc[0]  # Primera página
    
    # Configurar estilo del texto
    fontsize = 14
    color_texto = (1, 0, 0)  # Rojo para que se vea
    
    # Escribir números en las coordenadas
    # 1: ÁREA DE FISCALIZACION
    x, y = coordenadas["AREA_FISCALIZACION"]
    page.insert_text((x, y), "1", fontsize=fontsize, color=color_texto)
    
    # 2: INSPECTOR NOMBRE
    x, y = coordenadas["INSPECTOR_NOMBRE"]
    page.insert_text((x, y), "2", fontsize=fontsize, color=color_texto)
    
    # 3: MES
    x, y = coordenadas["MES"]
    page.insert_text((x, y), "3", fontsize=fontsize, color=color_texto)
    
    # 4: AÑO
    x, y = coordenadas["AÑO"]
    page.insert_text((x, y), "4", fontsize=fontsize, color=color_texto)
    
    # 5: FOLIO
    x, y = coordenadas["FOLIO"]
    page.insert_text((x, y), "5", fontsize=fontsize, color=color_texto)
    
    # 6: EMPRESA 1 - RAZON SOCIAL
    x, y = coordenadas["EMPRESA_1_RAZON_SOCIAL"]
    page.insert_text((x, y), "6", fontsize=fontsize, color=color_texto)
    
    # 7: EMPRESA 1 - CUIT
    x, y = coordenadas["EMPRESA_1_CUIT"]
    page.insert_text((x, y), "7", fontsize=fontsize, color=color_texto)
    
    # 8: EMPRESA 1 - ACTA
    x, y = coordenadas["EMPRESA_1_ACTA"]
    page.insert_text((x, y), "8", fontsize=fontsize, color=color_texto)
    
    # 9: EMPRESA 1 - VTO
    x, y = coordenadas["EMPRESA_1_VTO"]
    page.insert_text((x, y), "9", fontsize=fontsize, color=color_texto)
    
    # 10: EMPRESA 1 - DESDE
    x, y = coordenadas["EMPRESA_1_DESDE"]
    page.insert_text((x, y), "10", fontsize=fontsize, color=color_texto)
    
    # 11: EMPRESA 1 - HASTA
    x, y = coordenadas["EMPRESA_1_HASTA"]
    page.insert_text((x, y), "11", fontsize=fontsize, color=color_texto)
    
    # 12: EMPRESA 1 - DEUDA
    x, y = coordenadas["EMPRESA_1_DEUDA"]
    page.insert_text((x, y), "12", fontsize=fontsize, color=color_texto)
    
    # Empresa 2 (13-19)
    y_base = coordenadas["EMPRESA_1_RAZON_SOCIAL"][1] + DESPLAZAMIENTO_VERTICAL
    x_base = coordenadas["EMPRESA_1_RAZON_SOCIAL"][0]
    page.insert_text((x_base, y_base), "13", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_CUIT"][0], y_base), "14", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_ACTA"][0], y_base), "15", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_VTO"][0], y_base), "16", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_DESDE"][0], y_base), "17", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_HASTA"][0], y_base), "18", fontsize=fontsize, color=color_texto)
    page.insert_text((coordenadas["EMPRESA_1_DEUDA"][0], y_base), "19", fontsize=fontsize, color=color_texto)
    
    # Guardar en memoria
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    doc.close()
    output_buffer.seek(0)
    return output_buffer

# Verificar que el PDF existe
import os
if not os.path.exists(PDF_ORIGINAL):
    st.error(f"❌ No se encuentra el archivo '{PDF_ORIGINAL}'")
    st.info(f"Asegurate de que el PDF esté en la misma carpeta que este script. Archivos encontrados: {os.listdir('.')}")
    st.stop()

if st.button("📄 GENERAR PDF CON NÚMEROS (sobre tu PDF original)", type="primary", use_container_width=True):
    with st.spinner("Escribiendo números en el PDF..."):
        pdf_buffer = escribir_numeros_en_pdf()
        
        st.success("✅ PDF generado correctamente")
        
        st.download_button(
            label="📥 DESCARGAR PDF CON NÚMEROS",
            data=pdf_buffer,
            file_name=f"prueba_coordenadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")
st.markdown("""
### 📌 Instrucciones:
1. Asegurate que el archivo **`EJEMPLO INFORME MENSUAL DE INSPECTORES 101150.pdf`** esté en la misma carpeta
2. Apretá el botón **"GENERAR PDF CON NÚMEROS"**
3. Descargá y abrí el PDF
4. Verificá dónde aparece cada número:
   - **1** : Área de fiscalización
   - **2** : Nombre inspector  
   - **3** : MES
   - **4** : AÑO
   - **5** : FOLIO
   - **6-12** : Empresa 1
   - **13-19** : Empresa 2
5. **Decime qué número está mal ubicado y te digo cómo ajustarlo**
""")
