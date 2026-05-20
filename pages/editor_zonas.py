import streamlit as st
import fitz  # PyMuPDF
import base64
import os
import io
from PIL import Image

st.set_page_config(layout="wide", page_title="Inspector Profesional OSECAC")
st.title("🎯 Detector Binario de Coordenadas PDF")
st.markdown("Hacé clic en cualquier parte de la planilla para obtener las coordenadas exactas de inyección.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}'")
    st.stop()

# 1. GENERAR IMAGEN EN MEMORIA PARA EL NAVEGADOR
doc = fitz.open(PDF_PATH)
page = doc[0]
ancho_pdf = page.rect.width
alto_pdf = page.rect.height

# Render a resolución estándar para mapeo directo 1:1
pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode()

# Calcular proporciones de visualización
ancho_vista = int(ancho_pdf * 1.5)
alto_vista = int(alto_pdf * 1.5)

# 2. BARRA LATERAL CON DETECTOR MANUAL Y VERIFICACIÓN
st.sidebar.header("📊 Valores Registrados")
x_manual = st.sidebar.number_input("X Seleccionado", min_value=0, max_value=int(ancho_pdf), value=100)
y_manual = st.sidebar.number_input("Y Seleccionado", min_value=0, max_value=int(alto_pdf), value=100)
angulo_rot = st.sidebar.selectbox("Ángulo de Texto (Prueba)", [270, 90, 0, 180])

if st.sidebar.button("⚙️ GENERAR PDF DE PRUEBA", use_container_width=True):
    try:
        doc_test = fitz.open(PDF_PATH)
        page_test = doc_test[0]
        page_test.insert_text(
            (x_manual, y_manual),
            "TEST-101",
            fontsize=10,
            color=(1, 0, 0),
            rotate=angulo_rot
        )
        out_bytes = io.BytesIO()
        doc_test.save(out_bytes)
        doc_test.close()
        out_bytes.seek(0)
        
        st.sidebar.download_button(
            label="📥 DESCARGAR COMPROBACIÓN",
            data=out_bytes,
            file_name="comprobacion_casillero.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 3. INTERFAZ DE CLIC DINÁMICO (HTML5 + JAVASCRIPT NATIVO)
# Esto captura el evento del mouse en tiempo real directamente en el cliente
html_code = f"""
<div style="position: relative; display: inline-block;">
    <img id="planilla_pdf" src="data:image/png;base64,{img_base64}" width="{ancho_vista}" height="{alto_vista}" style="cursor: crosshair; border: 2px solid #ccc;"/>
    <div id="marcador" style="position: absolute; width: 10px; height: 10px; background: red; border-radius: 50%; display: none; pointer-events: none;"></div>
</div>

<p style="font-family: sans-serif; font-size: 14px; margin-top: 10px; color: #333;">
    <strong>Último Click en Pantalla -> </strong> 
    <span id="coordenadas_vista" style="background: #fffbdf; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #e6db55;">
        Haz clic en la imagen superior para medir
    </span>
</p>

<script>
    const img = document.getElementById('planilla_pdf');
    const marcador = document.getElementById('marcador');
    const txt = document.getElementById('coordenadas_vista');
    
    // Proporciones matemáticas para devolver el punto real del PDF (atendiendo a la escala 1.5)
    const factorX = {ancho_pdf} / {ancho_vista};
    const factorY = {alto_pdf} / {alto_vista};

    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x_vista = e.clientX - rect.left;
        const y_vista = e.clientY - rect.top;
        
        // Conversión exacta a puntos de mapa PDF real
        const x_pdf = Math.round(x_vista * factorX);
        const y_pdf = Math.round(y_vista * factorY);
        
        // Mover el punto rojo visualmente en la pantalla web
        marcador.style.left = (x_vista - 5) + 'px';
        marcador.style.top = (y_vista - 5) + 'px';
        marcador.style.display = 'block';
        
        // Escribir el resultado para el usuario
        txt.innerHTML = "Coordenada PDF Real sugerida para colocar en el menú de la izquierda: <strong>X: " + x_pdf + " | Y: " + y_pdf + "</strong>";
    }});
</script>
"""

# Renderizamos el módulo interactivo en el centro de tu aplicación
st.components.v1.html(html_code, height=alto_vista + 80, scrolling=True)
