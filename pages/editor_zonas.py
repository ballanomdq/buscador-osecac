import streamlit as st
import os
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Lluvia de Coordenadas", layout="centered")
st.title("🌧️ Lluvia de Números de Control")
st.markdown("Este script llena el PDF de números secuenciales cada 15 puntos para mapear el formulario real.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Conseguimos el tamaño real del PDF que está abriendo PyMuPDF
    ancho = int(page.rect.width)
    alto = int(page.rect.height)
    
    fontsize = 6  # Chiquito para que entren muchos y sea preciso
    color = (1, 0, 0)  # Rojo furioso
    
    contador = 1
    mapa_referencia = {}
    
    # Pasamos un rastrillo de números cada 40 puntos en X y cada 20 en Y
    for y in range(40, alto - 40, 20):
        for x in range(20, ancho - 20, 40):
            # Dibujamos el número de control en la coordenada exacta
            page.insert_text((x, y), str(contador), fontsize=fontsize, color=color)
            # Guardamos qué coordenada real representa ese número
            mapa_referencia[contador] = (x, y)
            contador += 1
            
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    return output, mapa_referencia

if not os.path.exists(PDF_PATH):
    st.error(f"❌ Falta el archivo '{PDF_PATH}'")
    st.stop()

if st.button("🚀 LANZAR LLUVIA DE NÚMEROS", type="primary", use_container_width=True):
    try:
        pdf_buffer, mapa = generar_lluvia_de_numeros()
        st.success("🎯 ¡Lluvia generada! Bajá el archivo abajo.")
        
        # Guardamos el mapa en la sesión por si lo necesitás después
        st.session_state["mapa_coordenadas"] = mapa
        
        st.download_button(
            label="📥 DESCARGAR PDF MAPEADO",
            data=pdf_buffer,
            file_name="lluvia_coordenadas_osecac.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error: {e}")
