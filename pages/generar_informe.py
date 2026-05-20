import streamlit as st
from supabase import create_client
from datetime import datetime
import io
import os
import tempfile
import shutil
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black

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

# SOLO LAS COORDENADAS QUE FUNCIONARON
COORDENADAS = {
    1: {"x": 145, "y": 303},
    2: {"x": 167, "y": 303},
    5: {"x": 592, "y": 945},
    6: {"x": 144, "y": 759},
    7: {"x": 144, "y": 640},
    11: {"x": 592, "y": 950},
}

def obtener_registros_listos(legajo=None):
    query = supabase.table("padron_deuda_presunta").select("*").eq("mail_enviado", "SI").not_.is_("leg", "null").not_.is_("acta", "null").not_.is_("vto", "null")
    if legajo:
        query = query.eq("leg", legajo)
    result = query.execute()
    return result.data if result.data else []

def generar_pdf_con_datos(registros, inspector_nombre, output_path):
    """Genera un PDF escribiendo sobre la plantilla usando reportlab"""
    # Copiar plantilla
    shutil.copy(PDF_PLANTILLA, output_path)
    
    # Crear un PDF overlay con los textos
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))
    can.setFont("Helvetica", 8)
    
    # Escribir cabecera
    can.drawString(COORDENADAS[1]["x"], COORDENADAS[1]["y"], "MAR DEL PLATA")
    can.drawString(COORDENADAS[2]["x"], COORDENADAS[2]["y"], inspector_nombre)
    
    for i, reg in enumerate(registros[:8]):
        fila = i + 1
        if fila == 1:
            razon_social = reg.get('razon_social', '')
            direccion = f"{reg.get('calle', '')} {reg.get('numero', '')}".strip()
            nombre_direccion = f"{razon_social} - {direccion}" if direccion else razon_social
            cuit = reg.get('cuit', '')
            acta = reg.get('acta', '')
            
            can.drawString(COORDENADAS[5]["x"], COORDENADAS[5]["y"], nombre_direccion[:50])
            can.drawString(COORDENADAS[11]["x"], COORDENADAS[11]["y"], cuit)
            can.drawString(COORDENADAS[6]["x"], COORDENADAS[6]["y"], cuit)
            can.drawString(COORDENADAS[7]["x"], COORDENADAS[7]["y"], acta)
    
    can.save()
    packet.seek(0)
    
    # Fusionar el overlay con la plantilla
    from PyPDF2 import PdfReader, PdfWriter
    plantilla = PdfReader(output_path)
    overlay = PdfReader(packet)
    
    writer = PdfWriter()
    for i, page in enumerate(plantilla.pages):
        if i == 0:
            page.merge_page(overlay.pages[0])
        writer.add_page(page)
    
    with open(output_path, "wb") as f:
        writer.write(f)

# ── Interfaz ─────────────────────────────────────────────────────────────────
inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins for ins in inspectores.data}
inspector_sel = st.selectbox("Inspector", options=list(opciones.keys()))

if st.button("📄 GENERAR INFORME", type="primary"):
    inspector = opciones[inspector_sel]
    registros = obtener_registros_listos(inspector['legajo'])
    
    if not registros:
        st.warning("No hay registros listos")
    else:
        st.success(f"✅ {len(registros)} registros listos")
        
        temp_path = tempfile.mktemp(suffix=".pdf")
        generar_pdf_con_datos(registros[:8], inspector['nombre'].split(",")[0], temp_path)
        
        with open(temp_path, "rb") as f:
            st.download_button("📥 DESCARGAR PDF", data=f.read(), file_name="informe.pdf", mime="application/pdf")
        
        os.unlink(temp_path)
