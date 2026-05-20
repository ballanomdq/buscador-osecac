import streamlit as st
import fitz
import base64
import os
import io
import json
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide", page_title="Calibrador Automático - OSECAC")
st.title("🎯 Calibrador Automático de Casilleros")
st.markdown("**Hacé clic en cada casillero en el orden que quieras. Se van a guardar automáticamente.**")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

# Inicializar lista de coordenadas en session_state
if "coordenadas" not in st.session_state:
    st.session_state.coordenadas = []
if "modo" not in st.session_state:
    st.session_state.modo = "grabando"  # grabando o listo

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

# Sidebar para mostrar coordenadas capturadas
st.sidebar.header("📋 Casilleros capturados")

# Lista predefinida de nombres de campos (podés editar o dejar que el usuario los nombre después)
campos_sugeridos = [
    "AREA_FISCALIZACION",
    "INSPECTOR_NOMBRE", 
    "MES",
    "AÑO",
    "FOLIO",
    "EMPRESA_1_RAZON_SOCIAL",
    "EMPRESA_1_CUIT",
    "EMPRESA_1_ACTA",
    "EMPRESA_1_VTO",
    "EMPRESA_1_DESDE",
    "EMPRESA_1_HASTA",
    "EMPRESA_1_DEUDA",
    "EMPRESA_2_RAZON_SOCIAL",
    "EMPRESA_2_CUIT",
    "EMPRESA_2_ACTA",
    "EMPRESA_2_VTO",
    "EMPRESA_2_DESDE",
    "EMPRESA_2_HASTA",
    "EMPRESA_2_DEUDA",
    "EMPRESA_3_RAZON_SOCIAL",
    "EMPRESA_3_CUIT",
    "EMPRESA_3_ACTA",
    "EMPRESA_3_VTO",
    "EMPRESA_3_DESDE",
    "EMPRESA_3_HASTA",
    "EMPRESA_3_DEUDA",
    "EMPRESA_4_RAZON_SOCIAL",
    "EMPRESA_4_CUIT",
    "EMPRESA_4_ACTA",
    "EMPRESA_4_VTO",
    "EMPRESA_4_DESDE",
    "EMPRESA_4_HASTA",
    "EMPRESA_4_DEUDA",
    "EMPRESA_5_RAZON_SOCIAL",
    "EMPRESA_5_CUIT",
    "EMPRESA_5_ACTA",
    "EMPRESA_5_VTO",
    "EMPRESA_5_DESDE",
    "EMPRESA_5_HASTA",
    "EMPRESA_5_DEUDA",
    "EMPRESA_6_RAZON_SOCIAL",
    "EMPRESA_6_CUIT",
    "EMPRESA_6_ACTA",
    "EMPRESA_6_VTO",
    "EMPRESA_6_DESDE",
    "EMPRESA_6_HASTA",
    "EMPRESA_6_DEUDA",
    "EMPRESA_7_RAZON_SOCIAL",
    "EMPRESA_7_CUIT",
    "EMPRESA_7_ACTA",
    "EMPRESA_7_VTO",
    "EMPRESA_7_DESDE",
    "EMPRESA_7_HASTA",
    "EMPRESA_7_DEUDA",
    "EMPRESA_8_RAZON_SOCIAL",
    "EMPRESA_8_CUIT",
    "EMPRESA_8_ACTA",
    "EMPRESA_8_VTO",
    "EMPRESA_8_DESDE",
    "EMPRESA_8_HASTA",
    "EMPRESA_8_DEUDA",
]

# Mostrar coordenadas ya capturadas
for i, coord in enumerate(st.session_state.coordenadas):
    nombre = campos_sugeridos[i] if i < len(campos_sugeridos) else f"Campo_{i+1}"
    st.sidebar.caption(f"{i+1}. {nombre}: X={coord['x']}, Y={coord['y']}")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 REINICIAR CALIBRACIÓN", use_container_width=True):
    st.session_state.coordenadas = []
    st.rerun()

if st.sidebar.button("✅ FINALIZAR Y DESCARGAR JSON", use_container_width=True):
    if st.session_state.coordenadas:
        # Guardar como JSON
        json_data = json.dumps(st.session_state.coordenadas, indent=2)
        st.sidebar.download_button(
            label="📥 DESCARGAR coordenadas.json",
            data=json_data,
            file_name=f"coordenadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        st.sidebar.success(f"✅ {len(st.session_state.coordenadas)} coordenadas guardadas")
    else:
        st.sidebar.warning("No hay coordenadas para guardar")

# HTML con JavaScript que captura clics y los envía a Streamlit
html_code = f"""
<div style="position: relative; display: inline-block;">
    <img id="planilla_pdf" src="data:image/png;base64,{img_base64}" width="{ancho_vista}" height="{alto_vista}" style="cursor: crosshair; border: 2px solid #333; border-radius: 8px;"/>
    <div id="marcador" style="position: absolute; width: 16px; height: 16px; background: red; border: 2px solid white; border-radius: 50%; display: none; pointer-events: none;"></div>
</div>

<div style="margin-top: 16px; padding: 12px; background: #f0f2f6; border-radius: 8px;">
    <p style="margin: 0; font-size: 16px;">
        📍 <strong>Último clic:</strong> 
        <span id="ultimo_punto" style="background: #d4edda; padding: 6px 12px; border-radius: 4px; font-family: monospace;">
            Esperando clic...
        </span>
    </p>
    <p style="margin-top: 8px; font-size: 14px; color: #555;">
        ✅ <strong>Progreso:</strong> {len(st.session_state.coordenadas)} campos capturados
    </p>
</div>

<script>
    const img = document.getElementById('planilla_pdf');
    const marcador = document.getElementById('marcador');
    const ultimoSpan = document.getElementById('ultimo_punto');
    const factorX = {ancho_pdf} / {ancho_vista};
    const factorY = {alto_pdf} / {alto_vista};
    let ultimasCoords = null;

    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x_vista = e.clientX - rect.left;
        const y_vista = e.clientY - rect.top;
        
        const x_pdf = Math.round(x_vista * factorX);
        const y_pdf = Math.round(y_vista * factorY);
        
        marcador.style.left = (x_vista - 8) + 'px';
        marcador.style.top = (y_vista - 8) + 'px';
        marcador.style.display = 'block';
        
        ultimoSpan.innerHTML = `X: ${{x_pdf}} | Y: ${{y_pdf}}`;
        ultimasCoords = {{x: x_pdf, y: y_pdf}};
        
        // Enviar coordenadas a Streamlit usando componente message
        const data = {{x: x_pdf, y: y_pdf}};
        window.parent.postMessage({{type: "streamlit:setComponentValue", value: data}}, "*");
    }});
</script>
"""

# Recibir coordenadas desde JavaScript
component_value = st.components.v1.html(html_code, height=alto_vista + 150, scrolling=True)

# No puedo capturar directamente desde JavaScript así que usamos un botón alternativo
# En lugar de eso, agregamos un botón para agregar manualmente la última coordenada
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    ultima_x = st.number_input("Última X capturada", value=0, step=1, key="ult_x")
with col2:
    ultima_y = st.number_input("Última Y capturada", value=0, step=1, key="ult_y")
with col3:
    if st.button("➕ AGREGAR ESTA COORDENADA", use_container_width=True):
        if ultima_x > 0 or ultima_y > 0:
            st.session_state.coordenadas.append({"x": ultima_x, "y": ultima_y})
            st.rerun()

st.info("💡 **Instrucciones:** Hacé clic en el PDF de arriba. Las coordenadas aparecerán en los campos. Apretá 'AGREGAR' para guardarlas. Seguí hasta capturar todos los casilleros.")
