import streamlit as st
import os
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Relleno OSECAC", layout="centered")
st.title("Formulario OSECAC - Modo Producción")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

def rellenar_planilla_real(datos):
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    fontsize = 9
    color = (0, 0, 0) # Negro para impresión oficial
    
    # Entrega directa sobre los casilleros detectados
    for campo, (x, y, texto) in datos.items():
        # Insertar el texto respetando los 90 grados de la estructura del PDF original
        page.insert_text((x, y), str(texto), fontsize=fontsize, color=color, rotate=90)
        
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

if os.path.exists(PDF_PATH):
    # Diccionario de ejemplo simulando datos reales de inspección
    # Basado en la matriz real del documento Legal
    datos_a_llenar = {
        "inspector": (75, 150, "JUAN PEREZ"),
        "mes_anio": (75, 490, "05/2026"),
        "folio": (75, 555, "001"),
        
        # Fila 1 de la tabla
        "f1_razon": (155, 20, "EMPRESA TEST S.A."),
        "f1_cuit": (155, 170, "30-12345678-9"),
        "f1_acta": (155, 280, "45218"),
        "f1_vto": (155, 320, "15/06/2026"),
        "f1_emp": (155, 360, "14"),
        "f1_periodo": (155, 390, "04/2026"),
        "f1_deuda": (155, 445, "150500.00"),
    }
    
    if st.button("📥 GENERAR Y DESCARGAR PLANILLA OFICIAL", type="primary", use_container_width=True):
        pdf_listo = rellenar_planilla_real(datos_a_llenar)
        st.download_button(
            label="Descargar PDF Completado",
            data=pdf_listo,
            file_name="Planilla_Inspeccion_Completada.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.error("Falta el archivo 'PLANILLA INSPECTORES.pdf'")
