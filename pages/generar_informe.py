import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔍 Extracción de Coordenadas de Números")

PDF_PATH = "ORIGINAL.pdf"

# LISTA COMPLETA DE NÚMEROS QUE NECESITAS
# (ordenada como me la diste en tu mensaje enorme)
NUMEROS_A_BUSCAR = [
    # Cabecera
    1, 2,
    # Empresa 1
    5, 6, 7, 11, 381, 402, 403, 338, 335, 339, 355, 167,
    # Empresa 2
    19, 20, 26, 13, 372, 400, 405, 337, 333, 341, 357, 156,
    # Empresa 3
    34, 35, 42, 21, 374, 398, 407, 308, 331, 343, 359, 158,
    # Empresa 4
    50, 51, 59, 28, 376, 396, 409, 310, 329, 345, 361, 160,
    # Empresa 5
    67, 68, 76, 36, 380, 392, 413, 312, 327, 347, 363, 162,
    # Empresa 6
    86, 87, 96, 44, 383, 390, 415, 314, 325, 349, 365, 172,
    # Empresa 7
    106, 107, 116, 52, 385, 388, 417, 316, 323, 351, 367, 164,
    # Empresa 8
    126, 127, 136, 61, 386, 385, 418, 318, 321, 353, 369, 173,
]

def buscar_numero(pdf_path, numero):
    """Busca un número en el PDF y devuelve sus coordenadas"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Buscar el texto exacto
    instancias = page.search_for(str(numero))
    
    if instancias:
        rect = instancias[0]
        x = (rect.x0 + rect.x1) / 2
        y = (rect.y0 + rect.y1) / 2
        doc.close()
        return x, y
    else:
        doc.close()
        return None

if st.button("🔍 EXTRAER COORDENADAS DE TODOS LOS NÚMEROS", type="primary", use_container_width=True):
    resultados = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, numero in enumerate(NUMEROS_A_BUSCAR):
        status_text.text(f"Buscando número {numero}... ({i+1}/{len(NUMEROS_A_BUSCAR)})")
        coords = buscar_numero(PDF_PATH, numero)
        if coords:
            resultados.append({
                "Número": numero,
                "X": round(coords[0]),
                "Y": round(coords[1])
            })
            status_text.text(f"✅ Número {numero} → X={round(coords[0])}, Y={round(coords[1])}")
        else:
            resultados.append({
                "Número": numero,
                "X": "NO ENCONTRADO",
                "Y": "NO ENCONTRADO"
            })
            status_text.text(f"❌ Número {numero} NO encontrado")
        
        progress_bar.progress((i + 1) / len(NUMEROS_A_BUSCAR))
    
    progress_bar.empty()
    status_text.empty()
    
    # Mostrar resultados
    df = pd.DataFrame(resultados)
    st.success(f"✅ Procesados {len(resultados)} números")
    st.dataframe(df, use_container_width=True)
    
    # Descargar como CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 DESCARGAR COORDENADAS (CSV)",
        data=csv,
        file_name="coordenadas_completas.csv",
        mime="text/csv"
    )
    
    # Mostrar en formato código
    st.markdown("### 📋 Formato para copiar:")
    st.code("COORDENADAS = {")
    for r in resultados:
        if r["X"] != "NO ENCONTRADO":
            st.code(f"    {r['Número']}: {{'x': {r['X']}, 'y': {r['Y']}}},")
    st.code("}")
