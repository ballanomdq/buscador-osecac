import streamlit as st
import fitz
import io
import os
from datetime import datetime

st.set_page_config(layout="centered", page_title="Prueba de Escritura en PDF")
st.title("✍️ Prueba de Escritura en PDF")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra '{PDF_PATH}'")
    st.stop()

# Botón para escribir "MAR DEL PLATA" en la coordenada X=138, Y=62
if st.button("📝 ESCRIBIR 'MAR DEL PLATA' EN X=138, Y=62", type="primary", use_container_width=True):
    # Abrir el PDF original
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Obtener dimensiones
    altura_pdf = page.rect.height
    
    # Escribir texto en la coordenada (convertir Y porque fitz usa Y desde abajo)
    x = 138
    y = altura_pdf - 62  # Convertir coordenada
    
    page.insert_text(
        (x, y),
        "MAR DEL PLATA",
        fontsize=10,
        color=(1, 0, 0),  # Rojo para que se vea bien
        rotate=0
    )
    
    # Guardar en memoria
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    # Descargar
    st.success("✅ PDF generado correctamente")
    st.download_button(
        label="📥 DESCARGAR PDF CON TEXTO",
        data=output,
        file_name=f"prueba_escritura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Mostrar vista previa
    st.markdown("### Vista previa:")
    base64_pdf = base64.b64encode(output.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Instrucciones:")
st.markdown("1. Apretá el botón")
st.markdown("2. Descargá el PDF")
st.markdown("3. Abrilo y buscá el texto **'MAR DEL PLATA'** en rojo")
st.markdown("4. Si aparece donde debe estar (debajo de AREA DE FISCALIZACION), el sistema funciona")
