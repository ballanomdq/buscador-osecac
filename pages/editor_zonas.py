import streamlit as st
import requests

st.set_page_config(page_title="Editor de Zonas - OSECAC", layout="wide")

st.markdown("# 🎨 Editor de Zonas")
st.markdown("Dibujá y guardá zonas geográficas para cada inspector")

st.markdown("---")

# Botón para descargar el PDF original
st.markdown("### 📄 Descargar formulario")

if st.button("📥 DESCARGAR PDF ORIGINAL (INFORME MENSUAL)", use_container_width=True):
    try:
        file_id = "1KmGRQ8X1i3xvS8LYyaKDb5vUNarelQjf"
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            st.download_button(
                label="✅ GUARDAR PDF EN TU PC",
                data=response.content,
                file_name="INFORME_MENSUAL_OSECAC.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error(f"No se pudo descargar el PDF. Código: {response.status_code}")
    except Exception as e:
        st.error(f"Error al descargar: {e}")

st.markdown("---")
st.markdown("### 🗺️ Aquí va el resto del editor de zonas")
st.info("Este es un esqueleto. Agregá acá el código de tu editor de zonas original")
