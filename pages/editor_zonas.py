import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import os

st.set_page_config(layout="centered")
st.title("🔢 Numerador de Campos")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

if st.button("GENERAR PDF NUMERADO"):
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)
    
    fields = reader.get_fields()
    datos = {}
    for i, nombre in enumerate(fields.keys(), 1):
        datos[nombre] = str(i)
    
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    
    st.download_button("📥 DESCARGAR", data=output, file_name="numerado.pdf", mime="application/pdf")
