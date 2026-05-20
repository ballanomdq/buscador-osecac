import streamlit as st
import fitz
import base64
import os
from PIL import Image
import io

st.set_page_config(layout="wide")
st.title("📍 Buscá la coordenada exacta")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra {PDF_PATH}")
    st.stop()

doc = fitz.open(PDF_PATH)
page = doc[0]
ancho = page.rect.width
alto = page.rect.height

escala = 1.5
pix = page.get_pixmap(matrix=fitz.Matrix(escala, escala))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode()
ancho_vista = int(ancho * escala)
alto_vista = int(alto * escala)

html = f"""
<img src="data:image/png;base64,{img_base64}" width="{ancho_vista}" style="cursor: crosshair; border: 1px solid #ccc;" id="pdf_img"/>
<div id="coords" style="margin-top: 10px; font-size: 18px; font-family: monospace;">Hacé clic en el PDF</div>
<script>
    const img = document.getElementById('pdf_img');
    const coordsDiv = document.getElementById('coords');
    const factorX = {ancho} / {ancho_vista};
    const factorY = {alto} / {alto_vista};
    
    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * factorX);
        const y = Math.round((e.clientY - rect.top) * factorY);
        coordsDiv.innerHTML = '✅ X=' + x + ' | Y=' + y;
    }});
</script>
"""

st.components.v1.html(html, height=alto_vista + 100)
