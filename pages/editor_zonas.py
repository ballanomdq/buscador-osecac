import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz

st.set_page_config(page_title="Numerador", layout="wide")
st.title("🔢 Numerador de Campos - Orden Exacto (como en tu PDF)")

def numerar_como_queres(input_pdf="PLANILLA INSPECTORES.pdf", output_pdf="PLANILLA_NUMEROS_CORRECTO.pdf"):
    doc = fitz.open(input_pdf)
    page = doc[0]
    
    campos = []
    for widget in page.widgets():
        if widget.field_name:
            rect = widget.rect
            center_x = (rect.x0 + rect.x1) / 2
            center_y = (rect.y0 + rect.y1) / 2
            campos.append((widget.field_name, center_x, center_y))

    # Orden personalizado según tu explicación y PDF
    # Primero los de arriba, luego la gran tabla fila por fila
    campos_ordenados = sorted(campos, key=lambda c: (-c[2], c[1]))  

    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    datos = {}
    for numero, (nombre, _, _) in enumerate(campos_ordenados, 1):
        datos[nombre] = str(numero)

    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)

    with open(output_pdf, "wb") as f:
        writer.write(f)
    
    doc.close()
    return output_pdf, len(datos)

# ====================== BOTÓN ======================
if st.button("🚀 GENERAR PDF CON NÚMEROS EN ORDEN CORRECTO", type="primary", use_container_width=True):
    with st.spinner("Generando numeración fila por fila..."):
        try:
            archivo, total = numerar_como_queres()
            st.success(f"✅ Listo! Numerados **{total} campos**")

            with open(archivo, "rb") as f:
                st.download_button(
                    "⬇️ DESCARGAR PDF CON NÚMEROS",
                    data=f,
                    file_name="PLANILLA_CON_NUMEROS_CORRECTO.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Error: {e}")

st.caption("Este código intenta seguir el orden que mostraste en tu PDF manual (1,2,3 arriba → luego fila por fila).")
