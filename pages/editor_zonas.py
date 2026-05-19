# Botón para descargar el PDF original desde Google Drive
import requests

def descargar_pdf_desde_gdrive():
    # ID del archivo desde tu enlace de Google Drive
    file_id = "1KmGRQ8X1i3xvS8LYyaKDb5vUNarelQjf"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    response = requests.get(url)
    return response.content

# En la fila de botones, agregá:
with col_informe_mensual:  # o donde prefieras
    if st.button("📄 DESCARGAR PDF ORIGINAL", use_container_width=True):
        with st.spinner("Descargando PDF..."):
            pdf_data = descargar_pdf_desde_gdrive()
            st.download_button(
                label="✅ HACÉ CLIC PARA GUARDAR EL PDF",
                data=pdf_data,
                file_name="INFORME_MENSUAL_OSECAC.pdf",
                mime="application/pdf"
            )
