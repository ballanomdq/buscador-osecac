import streamlit as st
import os
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Lluvia de Coordenadas", layout="centered")
st.title("🌧️ Lluvia de Números (Orientación Corregida)")
st.markdown("Este script mantiene el PDF quieto y gira automáticamente los números para que queden al derecho.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Obtenemos la rotación nativa que tiene el archivo (0, 90, 180 o 270)
    rot_original = page.rotation
    
    # Dimensiones reales de la hoja Legal sin alterar
    ancho = int(page.rect.width)
    alto = int(page.rect.height)
    
    fontsize = 6
    color = (1, 0, 0)  # Rojo
    
    contador = 1
    mapa_referencia = {}
    
    # REGLA DE GIRO: Forzamos el ángulo del texto para compensar el desvío del PDF.
    # Si los números salían de cabeza, el ángulo ideal de inserción es 90 o 270.
    # Probamos con 90 que es el inverso estándar para PDFs de cabeza en PyMuPDF.
    angulo_final_texto = 90 if rot_original in (90, 270) else 0
    
    # Barremos la matriz a lo largo y ancho de la hoja Legal
    for y in range(25, alto - 25, 20):
        for x in range(20, ancho - 20, 40):
            try:
                # Insertamos el texto girando SOLO el número en el aire
                page.insert_text(
                    (x, y), 
                    str(contador), 
                    fontsize=fontsize, 
                    color=color, 
                    rotate=angulo_final_texto
                )
                mapa_referencia[contador] = (x, y)
                contador += 1
            except Exception:
                pass
            
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
        with st.spinner("Mapeando grilla sobre hoja Legal..."):
            pdf_buffer, mapa = generar_lluvia_de_numeros()
        
        st.success("🎯 ¡Lluvia generada! Bajá el mapa visual aquí abajo.")
        st.session_state["mapa_coordenadas"] = mapa
        
        st.download_button(
            label="📥 DESCARGAR PDF MAPEADO",
            data=pdf_buffer,
            file_name="lluvia_al_derecho.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error en el servidor: {e}")
