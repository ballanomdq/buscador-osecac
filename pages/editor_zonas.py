import streamlit as st
import os
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Lluvia de Coordenadas", layout="centered")
st.title("🌧️ Lluvia de Números (Orientación Original)")
st.markdown("Este script mantiene el PDF quieto y gira los números para que coincidan con la lectura del formulario.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Dejamos la página quieta con su rotación nativa
    rot_original = page.rotation
    
    # Usamos las dimensiones nativas del PDF sin alterar nada
    ancho = int(page.rect.width)
    alto = int(page.rect.height)
    
    fontsize = 6
    color = (1, 0, 0)  # Rojo
    
    contador = 1
    mapa_referencia = {}
    
    # Barremos la matriz nativa del archivo
    for y in range(20, alto - 20, 20):
        for x in range(20, ancho - 20, 40):
            
            # MAGIA AQUÍ: Dejamos la hoja quieta, pero rotamos el TEXTO 
            # para que compense los 90 grados del PDF y lo leas horizontal.
            # Si se ve al revés, se cambia a 90 o 270 según corresponda.
            angulo_texto = (360 - rot_original) % 360 if rot_original != 0 else 0
            
            page.insert_text(
                (x, y), 
                str(contador), 
                fontsize=fontsize, 
                color=color, 
                rotate=angulo_texto
            )
            
            mapa_referencia[contador] = (x, y)
            contador += 1
            
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    return output, mapa_referencia

if not os.path.exists(PDF_PATH):
    st.error(f"❌ Falta el archivo '{PDF_PATH}' en la carpeta raíz.")
    st.stop()

if st.button("🚀 LANZAR LLUVIA DE NÚMEROS", type="primary", use_container_width=True):
    try:
        with st.spinner("Generando lluvia con texto rotado..."):
            pdf_buffer, mapa = generar_lluvia_de_numeros()
        
        st.success("🎯 ¡Lluvia generada correctamente!")
        st.session_state["mapa_coordenadas"] = mapa
        
        st.download_button(
            label="📥 DESCARGAR PDF MAPEADO",
            data=pdf_buffer,
            file_name="lluvia_perfecta_osecac.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error al procesar: {e}")
