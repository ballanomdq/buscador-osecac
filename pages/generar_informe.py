import streamlit as st
import fitz  # PyMuPDF
from supabase import create_client
from datetime import datetime
import io
import os

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(layout="centered")
st.title("📄 Generar Informe - Búsqueda Automática de Números")

PDF_PATH = "ORIGINAL.pdf"

def buscar_numero_en_pdf(pdf_path, numero_buscar):
    """Busca un número en el PDF y devuelve sus coordenadas (x, y)"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Buscar el texto exacto del número
    texto_buscar = str(numero_buscar)
    instancias = page.search_for(texto_buscar)
    
    if instancias:
        rect = instancias[0]  # Primera ocurrencia
        # Devuelve el centro del rectángulo
        x = (rect.x0 + rect.x1) / 2
        y = (rect.y0 + rect.y1) / 2
        doc.close()
        return x, y
    else:
        doc.close()
        return None

# Mapeo de qué número corresponde a qué dato
# (Esto es lo que vos ya me explicaste)
mapeo_datos = {
    1: {"tipo": "fijo", "valor": "MAR DEL PLATA"},
    2: {"tipo": "inspector", "campo": "nombre"},
    5: {"tipo": "empresa", "campo": "razon_social", "fila": 1},
    6: {"tipo": "empresa", "campo": "cuit", "fila": 1},
    7: {"tipo": "empresa", "campo": "acta", "fila": 1},
    11: {"tipo": "empresa", "campo": "cuit", "fila": 1},
    381: {"tipo": "empresa", "campo": "vto_dia", "fila": 1},
    402: {"tipo": "empresa", "campo": "vto_mes", "fila": 1},
    403: {"tipo": "empresa", "campo": "vto_año", "fila": 1},
    338: {"tipo": "empresa", "campo": "desde_mes", "fila": 1},
    335: {"tipo": "empresa", "campo": "desde_año", "fila": 1},
    339: {"tipo": "empresa", "campo": "hasta_mes", "fila": 1},
    355: {"tipo": "empresa", "campo": "hasta_año", "fila": 1},
    167: {"tipo": "empresa", "campo": "deuda", "fila": 1},
}

if st.button("🔍 PROBAR BÚSQUEDA DE NÚMEROS", type="primary"):
    st.write("### Buscando números en el PDF...")
    
    for num in list(mapeo_datos.keys())[:5]:  # Probamos los primeros 5
        coords = buscar_numero_en_pdf(PDF_PATH, num)
        if coords:
            st.success(f"Número {num} encontrado en X={coords[0]:.0f}, Y={coords[1]:.0f}")
        else:
            st.error(f"Número {num} NO encontrado")
