import streamlit as st
import fitz
import io
import os
import base64

st.set_page_config(layout="centered")
st.title("✍️ Escritor de PDF")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

st.markdown("### Usá las coordenadas que te da el calibrador")

col1, col2 = st.columns(2)
with col1:
    x = st.number_input("Coordenada X", value=140, step=1)
with col2:
    y = st.number_input("Coordenada Y", value=61, step=1)

texto = st.text_input("Texto a escribir", value="MAR DEL PLATA")

if st.button("📝 ESCRIBIR EN PDF", type="primary"):
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    altura = page.rect.height
    
    # IMPORTANTE: convertir Y porque fitz usa Y desde abajo
    y_convertida = altura - y
    
    page.insert_text((x, y_convertida), texto, fontsize=9, color=(1, 0, 0))
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    st.success("✅ Listo")
    st.download_button("📥 DESCARGAR PDF", data=output, file_name="prueba.pdf", mime="application/pdf")
    
    # Vista previa
    output.seek(0)
    base64_pdf = base64.b64encode(output.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
