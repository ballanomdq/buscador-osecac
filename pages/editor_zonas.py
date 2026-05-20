import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Numerador de Campos", layout="wide")
st.title("🔢 Numerador de Campos - Planilla Inspectores")

def numerar_todos_los_campos(input_pdf="PLANILLA INSPECTORES.pdf", output_pdf="PLANILLA_CON_NUMEROS.pdf"):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    writer.append(reader)  # Copia el PDF completo
    writer.set_need_appearances_writer(True)

    fields = reader.get_fields()
    if not fields:
        st.error("No se encontraron campos en el PDF")
        return None

    datos = {}
    contador = 1
    
    st.info(f"Se encontraron **{len(fields)} campos** en total. Numerándolos...")

    for nombre_campo in fields.keys():
        datos[nombre_campo] = str(contador)
        contador += 1

    # Rellenar con los números
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    return output_pdf, datos

# ====================== BOTÓN ======================
if st.button("🚀 GENERAR PDF CON NÚMEROS EN TODOS LOS CAMPOS", type="primary", use_container_width=True):
    with st.spinner("Analizando y numerando todos los campos..."):
        resultado = numerar_todos_los_campos()
        
        if resultado:
            archivo, mapeo = resultado
            
            st.success(f"✅ Listo! Se numeraron **{len(mapeo)} campos**")
            
            with open(archivo, "rb") as f:
                st.download_button(
                    label="⬇️ DESCARGAR PDF CON NÚMEROS",
                    data=f,
                    file_name="PLANILLA_CON_NUMEROS.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Mostrar el mapeo
            with st.expander("Ver mapeo Número → Nombre del campo"):
                for num, (campo, valor) in enumerate(mapeo.items(), 1):
                    st.text(f"{num:3d}  →  {campo}")

st.caption("Apretá el botón y abrí el PDF generado. Ahí vas a ver claramente qué número cae en cada casillero.")
