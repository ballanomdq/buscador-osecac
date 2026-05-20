import streamlit as st
import fitz
import io
import os
import base64

st.set_page_config(layout="wide")
st.title("🔴 Puntos Rojos - PDF Rotado 270°")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

# Tus coordenadas exactas de la herramienta
coordenadas = [
    (37, 143),    # 1 - AREA FISCALIZACION
    (521, 165),   # 2 - INSPECTOR NOMBRE
    (144, 459),   # 3 - MES
    (302, 459),   # 4 - AÑO
    (853, 456),   # 5 - FOLIO
    (224, 540),   # 6 - EMPRESA 1 - RAZON SOCIAL
    (348, 541),   # 7 - EMPRESA 1 - CUIT
    (405, 542),   # 8 - EMPRESA 1 - ACTA
    (422, 541),   # 9 - EMPRESA 1 - VTO
    (525, 542),   # 10 - EMPRESA 1 - DESDE
    (559, 542),   # 11 - EMPRESA 1 - HASTA
    (600, 540),   # 12 - EMPRESA 1 - DEUDA
]

if st.button("🔴 GENERAR PDF CORREGIDO", type="primary"):
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    for i, (x, y) in enumerate(coordenadas):
        # 1. Dibujar círculo rojo (no necesita rotate)
        page.draw_circle((x, y), 5, color=(1, 0, 0), fill=(1, 0, 0))
        
        # 2. Escribir el número con rotate=270 para que se vea derecho
        page.insert_text(
            (x - 3, y - 3), 
            str(i+1), 
            fontsize=8, 
            color=(1, 1, 1),  # blanco sobre fondo rojo
            rotate=270        # ← CLAVE: compensa la rotación del PDF
        )
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    st.success("✅ PDF generado con rotate=270")
    st.download_button("📥 DESCARGAR", data=output, file_name="puntos_corregidos.pdf", mime="application/pdf")
    
    output.seek(0)
    base64_pdf = base64.b64encode(output.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
