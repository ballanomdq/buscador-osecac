import streamlit as st
import fitz
import base64
import os
import io
import json
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide", page_title="Calibrador Avanzado - OSECAC")
st.title("🎯 Calibrador de Casilleros con Visualización en Vivo")
st.markdown("**Hacé clic en el PDF, apretá AGREGAR, y mirá si el número aparece donde corresponde.**")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

# Inicializar session state
if "coordenadas" not in st.session_state:
    st.session_state.coordenadas = []  # lista de {"nombre": "", "x": 0, "y": 0}
if "prox_nombre" not in st.session_state:
    st.session_state.prox_nombre = 1

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

# ==================================================
# FUNCIÓN PARA GENERAR PDF CON NÚMEROS
# ==================================================
def generar_pdf_con_numeros():
    """Genera un PDF con números escritos en todas las coordenadas guardadas"""
    doc_out = fitz.open(PDF_PATH)
    page_out = doc_out[0]
    
    for i, coord in enumerate(st.session_state.coordenadas):
        nombre = coord.get("nombre", f"campo_{i+1}")
        x = coord["x"]
        y = coord["y"]
        # Escribir el número de orden (no el nombre, para que sea más visible)
        page_out.insert_text(
            (x, alto_pdf - y),  # convertir Y porque fitz usa Y desde abajo
            str(i+1),
            fontsize=10,
            color=(1, 0, 0),  # rojo
            rotate=0
        )
    
    output = io.BytesIO()
    doc_out.save(output)
    doc_out.close()
    output.seek(0)
    return output

# ==================================================
# SIDEBAR: Lista de coordenadas guardadas
# ==================================================
st.sidebar.header("📋 Coordenadas guardadas")

for i, coord in enumerate(st.session_state.coordenadas):
    nombre = coord.get("nombre", f"Campo {i+1}")
    st.sidebar.caption(f"{i+1}. {nombre}: X={coord['x']}, Y={coord['y']}")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 REINICIAR TODO", use_container_width=True):
    st.session_state.coordenadas = []
    st.session_state.prox_nombre = 1
    st.rerun()

# ==================================================
# FORMULARIO PARA AGREGAR COORDENADA
# ==================================================
st.markdown("### 📍 Capturar nueva coordenada")
st.markdown("1. **Hacé clic en el PDF** de abajo")
st.markdown("2. **Completá el nombre del campo** (opcional)")
st.markdown("3. **Apretá AGREGAR**")
st.markdown("4. **Mirá el PDF de verificación** para confirmar que el número aparece donde corresponde")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    nombre_campo = st.text_input("Nombre del campo (opcional)", placeholder="Ej: AREA_FISCALIZACION, EMPRESA_1_CUIT, etc.")

with col2:
    x_coord = st.number_input("Coordenada X", value=0, step=1, key="x_input")

with col3:
    y_coord = st.number_input("Coordenada Y", value=0, step=1, key="y_input")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("➕ AGREGAR COORDENADA", use_container_width=True):
        if x_coord > 0 or y_coord > 0:
            nuevo_nombre = nombre_campo if nombre_campo else f"Campo_{len(st.session_state.coordenadas)+1}"
            st.session_state.coordenadas.append({
                "nombre": nuevo_nombre,
                "x": x_coord,
                "y": y_coord
            })
            # Limpiar campos
            st.session_state.x_input = 0
            st.session_state.y_input = 0
            st.rerun()

with col_btn2:
    if st.button("🗑️ ELIMINAR ÚLTIMA", use_container_width=True):
        if st.session_state.coordenadas:
            st.session_state.coordenadas.pop()
            st.rerun()

with col_btn3:
    if st.session_state.coordenadas:
        json_data = json.dumps(st.session_state.coordenadas, indent=2)
        st.download_button(
            label="📥 DESCARGAR JSON",
            data=json_data,
            file_name=f"coordenadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ==================================================
# VISOR DEL PDF (con captura de clics)
# ==================================================
st.markdown("### 🖱️ Hacé clic acá para capturar coordenadas")

# HTML/JS para capturar clics
html_code = f"""
<div style="position: relative; display: inline-block;">
    <img id="planilla_pdf" src="data:image/png;base64,{img_base64}" width="{ancho_vista}" height="{alto_vista}" style="cursor: crosshair; border: 2px solid #333; border-radius: 8px;"/>
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
        
        // Actualizar los campos de Streamlit (usando input events)
        const xInput = parent.document.querySelector('input[aria-label="Coordenada X"]');
        const yInput = parent.document.querySelector('input[aria-label="Coordenada Y"]');
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

st.components.v1.html(html_code, height=alto_vista + 50, scrolling=True)

# ==================================================
# VISOR DEL PDF GENERADO (para verificar)
# ==================================================
if st.session_state.coordenadas:
    st.markdown("### 🔍 Verificación: PDF con números")
    st.markdown("Este PDF muestra el número de orden en cada coordenada que guardaste.")
    
    col_v1, col_v2 = st.columns([1, 1])
    
    with col_v1:
        if st.button("🔄 ACTUALIZAR VISTA PREVIA", use_container_width=True):
            st.rerun()
    
    with col_v2:
        pdf_buffer = generar_pdf_con_numeros()
        st.download_button(
            label="📥 DESCARGAR PDF DE VERIFICACIÓN",
            data=pdf_buffer,
            file_name=f"verificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Mostrar vista previa del PDF generado
    pdf_buffer_preview = generar_pdf_con_numeros()
    base64_pdf = base64.b64encode(pdf_buffer_preview.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
else:
    st.info("💡 Agregá coordenadas para ver la verificación en PDF")
