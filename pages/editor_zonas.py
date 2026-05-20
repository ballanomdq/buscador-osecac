import streamlit as st
import os

st.set_page_config(page_title="Editor de Zonas - OSECAC", layout="wide")

st.markdown("# 🎨 Editor de Zonas")
st.markdown("Dibujá y guardá zonas geográficas para cada inspector")

st.markdown("---")

# Botón para descargar el PDF original (YA ESTÁ EN EL REPOSITORIO)
st.markdown("### 📄 Descargar formulario")

# La ruta exacta del archivo en tu repositorio
pdf_path = "EJEMPLO INFORME MENSUAL DE INSPECTORES 101150.pdf"

# Verificar si el archivo existe
if os.path.exists(pdf_path):
    if st.button("📥 DESCARGAR PDF ORIGINAL", use_container_width=True):
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        st.download_button(
            label="✅ GUARDAR PDF EN TU PC",
            data=pdf_data,
            file_name="INFORME_MENSUAL_OSECAC.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.error(f"❌ No se encuentra el archivo '{pdf_path}'")
    st.info("Asegurate de que el PDF esté en la misma carpeta que este script")

st.markdown("---")
st.markdown("### 🗺️ Aquí va el resto del editor de zonas")
st.info("Este es un esqueleto. Agregá acá el código de tu editor de zonas original")
