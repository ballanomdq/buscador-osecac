import streamlit as st
import fitz
import base64
import os
import io
import json
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide", page_title="Calibrador Simple - OSECAC")
st.title("🎯 Calibrador de Casilleros - Versión Simple")
st.markdown("**Hacé clic en el PDF. Las coordenadas aparecerán abajo. Copialas manualmente.**")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

# Inicializar lista de coordenadas
if "coordenadas" not in st.session_state:
    st.session_state.coordenadas = []

# Cargar PDF
doc = fitz.open(PDF_PATH)
page = doc[0]
ancho_pdf = page.rect.width
alto_pdf = page.rect.height

# Render imagen
escala = 1.5
pix = page.get_pixmap(matrix=fitz.Matrix(escala, escala))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode()
ancho_vista = int(ancho_pdf * escala)
alto_vista = int(alto_pdf * escala)

# HTML con JavaScript para capturar clics
html_code = f"""
<div style="position: relative; display: inline-block;">
    <img id="planilla_pdf" src="data:image/png;base64,{img_base64}" width="{ancho_vista}" height="{alto_vista}" style="cursor: crosshair; border: 2px solid #333;"/>
    <div id="marcador" style="position: absolute; width: 16px; height: 16px; background: red; border: 2px solid white; border-radius: 50%; display: none; pointer-events: none;"></div>
</div>

<script>
    const img = document.getElementById('planilla_pdf');
    const marcador = document.getElementById('marcador');
    const factorX = {ancho_pdf} / {ancho_vista};
    const factorY = {alto_pdf} / {alto_vista};

    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x_vista = e.clientX - rect.left;
        const y_vista = e.clientY - rect.top;
        
        const x_pdf = Math.round(x_vista * factorX);
        const y_pdf = Math.round(y_vista * factorY);
        
        marcador.style.left = (x_vista - 8) + 'px';
        marcador.style.top = (y_vista - 8) + 'px';
        marcador.style.display = 'block';
        
        // Mostrar coordenadas en el div
        const coordsDiv = document.getElementById('coords_actuales');
        if (coordsDiv) {{
            coordsDiv.innerHTML = '<strong>X: ' + x_pdf + ' | Y: ' + y_pdf + '</strong>';
        }}
        
        // Actualizar campos ocultos (para que Streamlit los capture)
        const xInput = parent.document.querySelector('input[aria-label="X capturada"]');
        const yInput = parent.document.querySelector('input[aria-label="Y capturada"]');
        if (xInput) {{
            xInput.value = x_pdf;
            xInput.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}
        if (yInput) {{
            yInput.value = y_pdf;
            yInput.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}
    }});
</script>
"""

st.components.v1.html(html_code, height=alto_vista + 50)

# Mostrar coordenadas actuales
st.markdown("---")
st.markdown("### 📍 Último clic:")

col1, col2 = st.columns(2)
with col1:
    x_actual = st.number_input("X capturada", value=0, step=1, key="x_actual")
with col2:
    y_actual = st.number_input("Y capturada", value=0, step=1, key="y_actual")

# Botón para agregar
col3, col4 = st.columns(2)
with col3:
    nombre = st.text_input("Nombre del campo (ej: AREA_FISCALIZACION)", key="nombre_campo")
with col4:
    if st.button("➕ AGREGAR COORDENADA", use_container_width=True):
        if x_actual > 0 or y_actual > 0:
            st.session_state.coordenadas.append({
                "nombre": nombre if nombre else f"campo_{len(st.session_state.coordenadas)+1}",
                "x": x_actual,
                "y": y_actual
            })
            st.success(f"✅ Agregado: X={x_actual}, Y={y_actual}")
            st.rerun()

# Mostrar lista de coordenadas guardadas
st.markdown("---")
st.markdown("### 📋 Coordenadas guardadas")

for i, coord in enumerate(st.session_state.coordenadas):
    st.caption(f"{i+1}. {coord['nombre']}: X={coord['x']}, Y={coord['y']}")

# Botón para descargar JSON
if st.session_state.coordenadas:
    st.markdown("---")
    json_data = json.dumps(st.session_state.coordenadas, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 DESCARGAR JSON",
        data=json_data,
        file_name=f"coordenadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
