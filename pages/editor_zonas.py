import streamlit as st
import fitz
import io
import os
import base64

st.set_page_config(layout="wide", page_title="Verificar Coordenadas")
st.title("🔴 Verificación de Coordenadas - Puntos Rojos")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

# Las primeras 12 coordenadas de tu lista (las más importantes)
coordenadas = [
    {"nombre": "AREA FISCALIZACION", "x": 37, "y": 143},
    {"nombre": "INSPECTOR NOMBRE", "x": 521, "y": 165},
    {"nombre": "MES", "x": 144, "y": 459},
    {"nombre": "AÑO", "x": 302, "y": 459},
    {"nombre": "FOLIO", "x": 853, "y": 456},
    {"nombre": "EMPRESA 1 - RAZON SOCIAL", "x": 224, "y": 540},
    {"nombre": "EMPRESA 1 - CUIT", "x": 348, "y": 541},
    {"nombre": "EMPRESA 1 - ACTA", "x": 405, "y": 542},
    {"nombre": "EMPRESA 1 - VTO", "x": 422, "y": 541},
    {"nombre": "EMPRESA 1 - DESDE", "x": 525, "y": 542},
    {"nombre": "EMPRESA 1 - HASTA", "x": 559, "y": 542},
    {"nombre": "EMPRESA 1 - DEUDA", "x": 600, "y": 540},
]

if st.button("🔴 GENERAR PDF CON PUNTOS ROJOS", type="primary", use_container_width=True):
    # Abrir PDF
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    altura = page.rect.height
    
    # Dibujar círculos rojos en cada coordenada
    for i, coord in enumerate(coordenadas):
        x = coord["x"]
        y = altura - coord["y"]  # Convertir porque fitz usa Y desde abajo
        
        # Dibujar un círculo rojo
        page.draw_circle((x, y), 5, color=(1, 0, 0), fill=(1, 0, 0))
        
        # Escribir el número
        page.insert_text((x - 3, y - 3), str(i+1), fontsize=8, color=(1, 1, 1))
    
    # Guardar
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    st.success(f"✅ PDF generado con {len(coordenadas)} puntos rojos")
    
    # Descargar
    st.download_button(
        label="📥 DESCARGAR PDF CON PUNTOS",
        data=output,
        file_name="puntos_rojos.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Vista previa
    output.seek(0)
    base64_pdf = base64.b64encode(output.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📌 Instrucciones:")
st.markdown("1. Apretá el botón")
st.markdown("2. Descargá el PDF")
st.markdown("3. Buscá los **círculos rojos con números**")
st.markdown("4. Decime si cada número está en el casillero correcto")
