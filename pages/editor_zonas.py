import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="Planilla Inspectores", layout="wide")
st.title("🖊️ Planilla Inspectores - Por Coordenadas")

def rellenar_con_coordenadas(datos_coordenadas, input_pdf="PLANILLA INSPECTORES.pdf", output_pdf="COMPLETADA.pdf"):
    doc = fitz.open(input_pdf)
    page = doc[0]  # primera página

    for texto, (x, y) in datos_coordenadas.items():
        if texto.strip():  # solo si hay texto
            page.insert_text(
                point=(x, y),
                text=texto,
                fontsize=11,
                fontname="helv",
                color=(0, 0, 0)
            )
    
    doc.save(output_pdf)
    doc.close()
    return output_pdf

# ====================== EJEMPLO DE USO ======================
st.subheader("Datos del Inspector")
col1, col2 = st.columns(2)
with col1:
    inspector = st.text_input("Apellido y Nombres Inspector")
with col2:
    area = st.text_input("Área de Fiscalización", value="MAR DEL PLATA")

fecha = st.text_input("Lugar y Fecha / Mes y Año")

# Aquí irían más inputs según las coordenadas que tengas...

# Diccionario de ejemplo (tenés que completarlo con tus coordenadas reales)
datos = {
    inspector: (150, 120),      # ← cambialo con tus coordenadas reales
    area: (450, 120),
    fecha: (700, 80),
    # Agrega el resto...
}

if st.button("✅ Generar PDF", type="primary"):
    with st.spinner("Rellenando..."):
        try:
            archivo = rellenar_con_coordenadas(datos)
            with open(archivo, "rb") as f:
                st.download_button("⬇️ Descargar PDF", f, "PLANILLA_COMPLETADA.pdf", "application/pdf")
            st.success("Listo!")
        except Exception as e:
            st.error(f"Error: {e}")
