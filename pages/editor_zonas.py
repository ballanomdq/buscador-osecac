import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF - para posiciones

st.set_page_config(page_title="Numerador Exacto", layout="wide")
st.title("🔢 Numerador de Campos - Orden Exacto como vos querés")

def numerar_en_orden_visual(input_pdf="PLANILLA INSPECTORES.pdf", output_pdf="PLANILLA_NUMEROS_EXACTO.pdf"):
    # 1. Obtener posiciones con PyMuPDF
    doc = fitz.open(input_pdf)
    page = doc[0]
    
    campos_con_posicion = []
    for widget in page.widgets():
        if widget.field_name:
            rect = widget.rect
            center_x = (rect.x0 + rect.x1) / 2
            center_y = (rect.y0 + rect.y1) / 2
            campos_con_posicion.append((widget.field_name, center_x, center_y))

    # 2. Ordenar: Arriba hacia abajo (Y descendente), y dentro de la misma altura de izquierda a derecha
    campos_ordenados = sorted(campos_con_posicion, key=lambda c: (-c[2], c[1]))

    # 3. Rellenar con números
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    datos = {}
    for numero, (nombre_campo, _, _) in enumerate(campos_ordenados, 1):
        datos[nombre_campo] = str(numero)

    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)

    with open(output_pdf, "wb") as f:
        writer.write(f)
    
    doc.close()
    return output_pdf, datos

# ====================== BOTÓN ======================
if st.button("🚀 GENERAR PDF CON NÚMEROS EN ORDEN REAL (fila por fila)", 
             type="primary", use_container_width=True):
    
    with st.spinner("Ordenando campos exactamente como pediste..."):
        try:
            archivo, mapeo = numerar_en_orden_visual()
            
            st.success(f"✅ Generado correctamente con **{len(mapeo)} campos** numerados")
            
            with open(archivo, "rb") as f:
                st.download_button(
                    label="⬇️ DESCARGAR PDF CON NÚMEROS (Orden correcto)",
                    data=f,
                    file_name="PLANILLA_CON_NUMEROS_CORRECTO.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with st.expander("📋 Ver lista completa de campos numerados"):
                for num, nombre in enumerate(mapeo.keys(), 1):
                    st.text(f"{num:3d} → {nombre}")
                    
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Agregá 'pymupdf' en tu requirements.txt")

st.caption("Este código ordena de arriba-izquierda hacia abajo-derecha, tal como explicaste.")
