import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF (para obtener posiciones)

st.set_page_config(page_title="Numerador Inteligente", layout="wide")
st.title("🔢 Numerador de Campos - Orden Horizontal (fila por fila)")

def numerar_campos_horizontal(input_pdf="PLANILLA INSPECTORES.pdf", output_pdf="PLANILLA_CON_NUMEROS.pdf"):
    # Usamos PyMuPDF para obtener posiciones reales
    doc = fitz.open(input_pdf)
    page = doc[0]
    
    # Obtener todos los widgets (campos)
    widgets = []
    for widget in page.widgets():
        if widget.field_name:
            # Guardamos nombre + centro del campo (para ordenar)
            rect = widget.rect
            center_x = (rect.x0 + rect.x1) / 2
            center_y = (rect.y0 + rect.y1) / 2
            widgets.append((widget.field_name, center_x, center_y))
    
    # Ordenar: primero por Y (de arriba hacia abajo), luego por X (izquierda a derecha)
    widgets.sort(key=lambda w: (w[2], w[1]))   # ← Esto es lo clave

    # Ahora rellenamos con pypdf
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    datos = {}
    contador = 1

    st.write(f"Se encontraron **{len(widgets)} campos**")

    for nombre, _, _ in widgets:
        datos[nombre] = str(contador)
        contador += 1

    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)

    with open(output_pdf, "wb") as f:
        writer.write(f)
    
    doc.close()
    return output_pdf, datos

# ====================== BOTÓN ======================
if st.button("🚀 GENERAR PDF CON NÚMEROS EN ORDEN HORIZONTAL", type="primary", use_container_width=True):
    with st.spinner("Ordenando campos de izquierda a derecha y fila por fila..."):
        try:
            archivo, mapeo = numerar_campos_horizontal()
            
            st.success(f"✅ ¡Listo! Se numeraron **{len(mapeo)} campos** en orden horizontal")
            
            with open(archivo, "rb") as f:
                st.download_button(
                    label="⬇️ DESCARGAR PDF CON NÚMEROS (Orden fila por fila)",
                    data=f,
                    file_name="PLANILLA_CON_NUMEROS_HORIZONTAL.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with st.expander("Ver lista de campos numerados"):
                for num, campo in enumerate(mapeo.keys(), 1):
                    st.text(f"{num:3d} → {campo}")
                    
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Asegúrate de tener pymupdf instalado en requirements.txt")

st.caption("Este código ordena los campos visualmente de izquierda a derecha, fila por fila.")
