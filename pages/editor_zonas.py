import streamlit as st
import json
from pypdf import PdfReader, PdfWriter
from datetime import datetime
import io
import os

st.set_page_config(layout="centered", page_title="Completar Formulario OSECAC")
st.title("📝 Completar Informe Mensual de Inspector")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"No se encuentra '{PDF_PATH}'")
    st.stop()

# Datos de prueba (después conectás con tu base de datos)
datos_prueba = {
    "AREA DE FISCALIZACIONRow1": "MAR DEL PLATA",
    "APELLIDO Y NOMBRES INSPECTORRow1": "LOPEZ, Martin",
    "MES Y AÑORow1": "10 2024",
    "FOLIORow1": "1",
    "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow1": "EMPRESA EJEMPLO SA - CALLE 123",
    "NRO DE  CUITRow1": "30-12345678-9",
    "NRORow1": "ACTA-001",
    "VTODIA1": "15",
    "VTOMES1": "10",
    "VTOAÑO1": "2024",
    "PVDIA1": "01",
    "PVMES1": "01",
    "PVAÑO1": "2024",
    "DEUDA DETERMINADARow1": "$ 10.000",
}

def completar_formulario(datos):
    """Rellena el PDF con los datos proporcionados"""
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    
    # Obtener los campos del formulario
    for page in reader.pages:
        writer.add_page(page)
    
    # Actualizar los campos
    writer.update_page_form_field_values(
        writer.pages[0],
        datos,
        auto_regenerate=True
    )
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# Mostrar campos disponibles
st.subheader("📋 Campos disponibles en el formulario")
with open("campos_disponibles.json", "r", encoding="utf-8") as f:
    campos = json.load(f)

st.info(f"Total de campos: {len(campos)}")

# Opción para ver campos
with st.expander("Ver lista de campos"):
    for i, nombre in enumerate(sorted(campos.keys())):
        st.caption(f"{i+1}. {nombre}")

st.markdown("---")

if st.button("📄 GENERAR PDF DE PRUEBA", type="primary"):
    with st.spinner("Generando formulario..."):
        pdf_buffer = completar_formulario(datos_prueba)
        
        st.success("✅ Formulario generado correctamente")
        st.download_button(
            label="📥 DESCARGAR PDF COMPLETADO",
            data=pdf_buffer,
            file_name=f"informe_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Vista previa
        pdf_buffer.seek(0)
        import base64
        base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🔗 Próximo paso:")
st.markdown("Conectá estos campos con los datos de tu base de datos (`padron_deuda_presunta`) para cada inspector.")
