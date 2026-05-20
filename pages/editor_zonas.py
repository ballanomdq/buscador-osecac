import streamlit as st
import fitz
import base64
import os
import io
from PIL import Image

st.set_page_config(layout="wide", page_title="Capturador de Coordenadas")
st.title("🎯 Capturador de Coordenadas - Hacé clic y se guarda automáticamente")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

# Inicializar lista de coordenadas
if "puntos" not in st.session_state:
    st.session_state.puntos = []

# Cargar PDF
doc = fitz.open(PDF_PATH)
page = doc[0]
ancho = page.rect.width
alto = page.rect.height

# Render imagen
escala = 1.5
pix = page.get_pixmap(matrix=fitz.Matrix(escala, escala))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode()
ancho_vista = int(ancho * escala)
alto_vista = int(alto * escala)

# HTML con JavaScript que captura clics y los envía a Streamlit
html_code = f"""
<img src="data:image/png;base64,{img_base64}" width="{ancho_vista}" style="cursor: crosshair; border: 2px solid #333;" id="pdf_img"/>
<div id="coords" style="margin-top: 10px; font-size: 16px; background: #e8f4e8; padding: 8px; border-radius: 5px;">
    🔍 Hacé clic en el PDF para capturar coordenada
</div>
<script>
    const img = document.getElementById('pdf_img');
    const coordsDiv = document.getElementById('coords');
    const factorX = {ancho} / {ancho_vista};
    const factorY = {alto} / {alto_vista};
    let ultimaX = 0;
    let ultimaY = 0;

    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * factorX);
        const y = Math.round((e.clientY - rect.top) * factorY);
        ultimaX = x;
        ultimaY = y;
        coordsDiv.innerHTML = '✅ Último clic: X=' + x + ' | Y=' + y;
        
        // Enviar a Streamlit
        const input = document.createElement('input');
        input.type = 'text';
        input.value = x + ',' + y;
        input.style.display = 'none';
        document.body.appendChild(input);
        input.dispatchEvent(new Event('change', {{bubbles: true}}));
        document.body.removeChild(input);
    }});
</script>
"""

st.components.v1.html(html_code, height=alto_vista + 100)

# Mostrar coordenadas capturadas
st.markdown("---")
st.markdown("### 📋 PUNTOS CAPTURADOS:")

# Botón para agregar el último clic manualmente
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    x_manual = st.number_input("X", value=0, step=1, key="x_manual")
with col2:
    y_manual = st.number_input("Y", value=0, step=1, key="y_manual")
with col3:
    if st.button("➕ AGREGAR ESTE PUNTO", use_container_width=True):
        if x_manual > 0 or y_manual > 0:
            st.session_state.puntos.append({
                "num": len(st.session_state.puntos) + 1,
                "x": x_manual,
                "y": y_manual
            })
            st.rerun()

# Mostrar lista de puntos
for p in st.session_state.puntos:
    st.code(f"{p['num']} - X={p['x']}, Y={p['y']}")

# Botones de acción
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🗑️ ELIMINAR ÚLTIMO", use_container_width=True):
        if st.session_state.puntos:
            st.session_state.puntos.pop()
            st.rerun()
with col_b:
    if st.button("🔄 REINICIAR TODO", use_container_width=True):
        st.session_state.puntos = []
        st.rerun()
with col_c:
    if st.session_state.puntos:
        import json
        json_data = json.dumps(st.session_state.puntos, indent=2)
        st.download_button(
            label="📥 DESCARGAR JSON",
            data=json_data,
            file_name="coordenadas.json",
            mime="application/json",
            use_container_width=True
        )
