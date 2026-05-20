import streamlit as st
import fitz
import io
import os
import base64
from datetime import datetime

st.set_page_config(layout="centered", page_title="Prueba de Escritura en PDF")
st.title("✍️ Prueba de Escritura en PDF - Coordenada Corregida")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

if st.button("📝 ESCRIBIR 'MAR DEL PLATA'", type="primary", use_container_width=True):
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Coordenada que sacaste con el calibrador
    x = 140
    y = 61  # Esta es la coordenada directa, sin conversión especial
    
    # Escribir en la coordenada
    page.insert_text(
        (x, y),
        "MAR DEL PLATA",
        fontsize=8,
        color=(1, 0, 0),
        rotate=0
    )
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    st.success("✅ PDF generado correctamente")
    st.download_button(
        label="📥 DESCARGAR PDF",
        data=output,
        file_name=f"prueba_escritura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Vista previa
    output.seek(0)
    base64_pdf = base64.b64encode(output.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>', unsafe_allow_html=True)
