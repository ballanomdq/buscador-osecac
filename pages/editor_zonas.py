# Botón para descargar el PDF original
import requests

st.markdown("---")
st.markdown("### 📄 Descargar formulario")

if st.button("📥 DESCARGAR PDF ORIGINAL (INFORME MENSUAL)", use_container_width=True):
    try:
        file_id = "1KmGRQ8X1i3xvS8LYyaKDb5vUNarelQjf"
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            st.download_button(
                label="✅ GUARDAR PDF",
                data=response.content,
                file_name="INFORME_MENSUAL_OSECAC.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error("No se pudo descargar el PDF")
    except Exception as e:
        st.error(f"Error: {e}")
