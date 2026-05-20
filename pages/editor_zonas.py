import streamlit as st
import os
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Lluvia de Coordenadas", layout="centered")
st.title("🌧️ Lluvia de Números (Corregida)")
st.markdown("Este script endereza el PDF rotado y lo llena de números para mapear los casilleros.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # 1. SOLUCIÓN DEFINITIVA PARA LA PÁGINA EN BLANCO:
    # Si el PDF está rotado de costado, lo enderezamos a 0 grados físicamente.
    if page.rotation != 0:
        page.set_rotation(0)
    
    # Ahora las dimensiones son reales y fijas (842x595 o 595x842)
    ancho = int(page.rect.width)
    alto = int(page.rect.height)
    
    fontsize = 6
    color = (1, 0, 0)  # Rojo
    
    contador = 1
    mapa_referencia = {}
    
    # Barremos con total seguridad de que la hoja está derecha
    for y in range(30, alto - 30, 20):
        for x in range(20, ancho - 20, 40):
            try:
                # Insertamos el texto de forma estándar (sin el parámetro rotate que bugeaba)
                page.insert_text((x, y), str(contador), fontsize=fontsize, color=color)
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

# Volvemos a levantar el botón
if st.button("🚀 LANZAR LLUVIA DE NÚMEROS", type="primary", use_container_width=True):
    try:
        with st.spinner("Procesando matriz de la planilla..."):
            pdf_buffer, mapa = generar_lluvia_de_numeros()
        
        st.success("🎯 ¡Logrado! Ya podés descargar tu mapa visual.")
        st.session_state["mapa_coordenadas"] = mapa
        
        st.download_button(
            label="📥 DESCARGAR PDF MAPEADO",
            data=pdf_buffer,
            file_name="lluvia_derecha_osecac.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Hubo un problema al dibujar: {e}")
