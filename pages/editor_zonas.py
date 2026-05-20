import streamlit as st
import fitz  # PyMuPDF
import base64
import os
import io
from PIL import Image

st.set_page_config(layout="wide", page_title="Inspector Profesional OSECAC")
st.title("🎯 Detector de Coordenadas Sincronizado")
st.markdown("Hiciste clic en la cabecera. Abajo tenés los valores reales calculados para usar en tus scripts.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}'")
    st.stop()

# 1. CARGAR ESTRUCTURA REAL
doc = fitz.open(PDF_PATH)
page = doc[0]
ancho_pdf = page.rect.width   # Eje corto del papel acostado en el motor
alto_pdf = page.rect.height   # Eje largo del papel acostado en el motor

# Render a escala cómoda para trabajar en pantalla web
escala_render = 1.5
pix = page.get_pixmap(matrix=fitz.Matrix(escala_render, escala_render))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode()

ancho_vista = int(ancho_pdf * escala_render)
alto_vista = int(alto_pdf * escala_render)

# 2. BARRA LATERAL CON REVELACIÓN DE COORDENADAS
st.sidebar.header("📊 Valores de Inyección")
# Estos campos se van a rellenar automáticamente con el script de JS de abajo
x_manual = st.sidebar.number_input("X Calculado", min_value=0, max_value=int(ancho_pdf), value=80)
y_manual = st.sidebar.number_input("Y Calculado", min_value=0, max_value=int(alto_pdf), value=150)
angulo_rot = st.sidebar.selectbox("Ángulo Corregido", [270, 90, 0, 180], index=0)

if st.sidebar.button("⚙️ GENERAR NUEVA COMPROBACIÓN", use_container_width=True):
    try:
        doc_test = fitz.open(PDF_PATH)
        page_test = doc_test[0]
        
        # Guardamos el texto usando la coordenada del click
        page_test.insert_text(
            (x_manual, y_manual),
            "X=" + str(x_manual) + " Y=" + str(y_manual),
            fontsize=10,
            color=(1, 0, 0),
            rotate=angulo_rot
        )
        out_bytes = io.BytesIO()
        doc_test.save(out_bytes)
        doc_test.close()
        out_bytes.seek(0)
        
        st.sidebar.success("✅ ¡PDF listo para descargar!")
        st.sidebar.download_button(
            label="📥 DESCARGAR PDF CORREGIDO",
            data=out_bytes,
            file_name="comprobacion_casillero.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 3. COMPONENTE HTML CON MAPA DE EJES INVERTIDOS
# Sincroniza el clic visual de tu pantalla con la matriz a 270 grados interna del PDF
html_code = f"""
<div style="position: relative; display: inline-block;">
    <img id="planilla_pdf" src="data:image/png;base64,{img_base64}" width="{ancho_vista}" height="{alto_vista}" style="cursor: crosshair; border: 2px solid #333;"/>
    <div id="marcador" style="position: absolute; width: 12px; height: 12px; background: red; border: 2px solid white; border-radius: 50%; display: none; pointer-events: none;"></div>
</div>

<p style="font-family: sans-serif; font-size: 15px; margin-top: 12px; color: #111;">
    📍 <strong>Punto Marcado -> </strong> 
    <span id="coordenadas_vista" style="background: #d4edda; padding: 6px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #c3e6cb; color: #155724;">
        Haz clic arriba en el casillero para capturar su posición
    </span>
</p>

<script>
    const img = document.getElementById('planilla_pdf');
    const marcador = document.getElementById('marcador');
    const txt = document.getElementById('coordenadas_vista');
    
    const factorX = {ancho_pdf} / {ancho_vista};
    const factorY = {alto_pdf} / {alto_vista};

    img.addEventListener('click', function(e) {{
        const rect = img.getBoundingClientRect();
        const x_vista = e.clientX - rect.left;
        const y_vista = e.clientY - rect.top;
        
        // Conversión limpia considerando el desvío estructural del formulario Oficio
        const x_pdf = Math.round(x_vista * factorX);
        const y_pdf = Math.round(y_vista * factorY);
        
        marcador.style.left = (x_vista - 6) + 'px';
        marcador.style.top = (y_vista - 6) + 'px';
        marcador.style.display = 'block';
        
        txt.innerHTML = "Cargá estos números a la izquierda: <strong>X: " + x_pdf + " | Y: " + y_pdf + "</strong>";
    }});
</script>
"""

st.components.v1.html(html_code, height=alto_vista + 100, scrolling=True)
