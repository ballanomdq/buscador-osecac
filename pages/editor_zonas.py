import streamlit as st
import fitz
import io
import os
import base64

st.set_page_config(layout="wide")
st.title("🔴 Puntos Rojos Corregidos - Matriz Sincronizada")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

# COORDENADAS RECALCULADAS: Sincronizadas con la rotación de 270° del motor
coordenadas = [
    (75, 143),    # 1 - AREA FISCALIZACION
    (75, 521),    # 2 - INSPECTOR NOMBRE
    (75, 830),    # 3 - MES
    (75, 875),    # 4 - AÑO
    (75, 960),    # 5 - FOLIO
    (155, 110),   # 6 - EMPRESA 1 - RAZON SOCIAL
    (155, 335),   # 7 - EMPRESA 1 - NRO. DE CUIT
    (155, 460),   # 8 - EMPRESA 1 - ACTUACION NRO.
    (155, 510),   # 9 - EMPRESA 1 - FECHA VTO.
    (155, 580),   # 10 - EMPRESA 1 - PERIODO DESDE (MES)
    (155, 605),   # 11 - EMPRESA 1 - PERIODO HASTA (AÑO)
    (155, 680),   # 12 - EMPRESA 1 - DEUDA DETERMINADA
]

if st.button("🔴 GENERAR PDF CORREGIDO", type="primary"):
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    for i, (x, y) in enumerate(coordenadas):
        # 1. Dibujar círculo rojo en la posición de la matriz real
        page.draw_circle((x, y), 7, color=(1, 0, 0), fill=(1, 0, 0))
        
        # 2. Centrar levemente el número y estamparlo derecho con rotate=270
        page.insert_text(
            (x - 3, y - 3), 
            str(i+1), 
            fontsize=8, 
            color=(1, 1, 1),  # Blanco sobre rojo
            rotate=270        # Mantiene el número alineado a la lectura de la hoja
        )
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    st.success("✅ ¡Matriz recalculada exitosamente!")
    st.download_button("📥 DESCARGAR PDF CALIBRADO", data=output, file_name="puntos_corregidos_fijos.pdf", mime="application/pdf")
    
    output.seek(0)
    base64_pdf = base64.b64encode(output.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
