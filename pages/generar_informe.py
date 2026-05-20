import streamlit as st
import fitz  # PyMuPDF
from supabase import create_client
from datetime import datetime
import os
import tempfile
import shutil
from collections import defaultdict

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(page_title="Generar Informe Mensual - OSECAC", layout="wide")

st.markdown("## 📄 Generar Informe Mensual de Inspección")

PDF_PLANTILLA = "ORIGINAL.pdf"

# SOLO LAS COORDENADAS QUE SABEMOS QUE FUNCIONAN (las que probaste)
COORDENADAS = {
    1: {"x": 145, "y": 303},   # MAR DEL PLATA
    2: {"x": 167, "y": 303},   # Inspector nombre
    5: {"x": 592, "y": 945},   # Empresa 1 - Razón Social
    6: {"x": 144, "y": 759},   # Empresa 1 - CUIT (2do lugar)
    7: {"x": 144, "y": 640},   # Empresa 1 - ACTA
    11: {"x": 592, "y": 950},  # Empresa 1 - CUIT (1er lugar)
}

def obtener_registros_listos(legajo=None):
    query = supabase.table("padron_deuda_presunta").select("*").eq("mail_enviado", "SI").not_.is_("leg", "null").not_.is_("acta", "null").not_.is_("vto", "null")
    if legajo:
        query = query.eq("leg", legajo)
    result = query.execute()
    return result.data if result.data else []

def generar_pdf_con_datos(registros, inspector_nombre, output_path):
    shutil.copy(PDF_PLANTILLA, output_path)
    doc = fitz.open(output_path)
    page = doc[0]
    altura = page.rect.height
    
    # Cabecera
    for num, texto in [(1, "MAR DEL PLATA"), (2, inspector_nombre)]:
        x = COORDENADAS[num]["x"]
        y = altura - COORDENADAS[num]["y"]
        page.insert_text((x, y), texto, fontsize=8, color=(0, 0, 0))
    
    # Escribir datos de empresas (solo campos que tenemos coordenadas)
    for i, reg in enumerate(registros[:8]):
        fila = i + 1
        razon_social = reg.get('razon_social', '')
        direccion = f"{reg.get('calle', '')} {reg.get('numero', '')}".strip()
        nombre_direccion = f"{razon_social} - {direccion}" if direccion else razon_social
        cuit = reg.get('cuit', '')
        acta = reg.get('acta', '')
        
        # Escribir en los números correspondientes (basado en la fila)
        # Para fila 1: números 5, 6, 7, 11
        # Para fila 2: habría que tener números 19, 20, 13, 26? (no tenemos coordenadas)
        # Por ahora solo funciona para la primera empresa
        
        if fila == 1:
            page.insert_text((COORDENADAS[5]["x"], altura - COORDENADAS[5]["y"]), nombre_direccion[:60], fontsize=7, color=(0,0,0))
            page.insert_text((COORDENADAS[11]["x"], altura - COORDENADAS[11]["y"]), cuit, fontsize=7, color=(0,0,0))
            page.insert_text((COORDENADAS[6]["x"], altura - COORDENADAS[6]["y"]), cuit, fontsize=7, color=(0,0,0))
            page.insert_text((COORDENADAS[7]["x"], altura - COORDENADAS[7]["y"]), acta, fontsize=7, color=(0,0,0))
    
    doc.save(output_path)
    doc.close()

# ── Interfaz ─────────────────────────────────────────────────────────────────
inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins for ins in inspectores.data}
inspector_sel = st.selectbox("Inspector", options=list(opciones.keys()))

if st.button("📄 GENERAR INFORME (PRUEBA)", type="primary"):
    inspector = opciones[inspector_sel]
    registros = obtener_registros_listos(inspector['legajo'])
    
    if not registros:
        st.warning("No hay registros listos")
    else:
        st.success(f"✅ {len(registros)} registros listos. Mostrando primera empresa.")
        
        temp_path = tempfile.mktemp(suffix=".pdf")
        generar_pdf_con_datos(registros[:1], inspector['nombre'].split(",")[0], temp_path)
        
        with open(temp_path, "rb") as f:
            st.download_button("📥 DESCARGAR PDF", data=f.read(), file_name="prueba.pdf", mime="application/pdf")
        os.unlink(temp_path)
