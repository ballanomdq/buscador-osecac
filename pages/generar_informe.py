import streamlit as st
import fitz  # PyMuPDF
from supabase import create_client
from datetime import datetime
import os
import time
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
st.markdown("""
<style>
.app-header { background: #1e293b; padding: 0.5rem 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
.app-header h3 { color: #fff; margin: 0; }
.app-header p { color: #94a3b8; margin: 0; font-size: 0.8rem; }
div[data-testid="stButton"] > button { border-radius: 8px !important; font-weight: 500 !important; }
div[data-testid="stButton"] > button[kind="primary"] { background-color: #10b981 !important; }
.stProgress > div > div > div > div { background-color: #10b981 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h3>📄 Generar Informe Mensual de Inspección</h3>
    <p>Completa el formulario PDF con los datos de los registros listos</p>
</div>
""", unsafe_allow_html=True)

# ── Configuración ────────────────────────────────────────────────────────────
PDF_PLANTILLA = "ORIGINAL.pdf"  # Archivo plantilla (NO SE MODIFICA)

# ==================================================
# COORDENADAS (número visible → coordenadas X, Y)
# ==================================================
COORDENADAS = {
    # Cabecera
    1: {"x": 145, "y": 303},
    2: {"x": 167, "y": 303},
    
    # Empresa 1
    5: {"x": 592, "y": 945},
    6: {"x": 144, "y": 759},
    7: {"x": 144, "y": 640},
    11: {"x": 592, "y": 950},
    381: {"x": 520, "y": 900},
    402: {"x": 540, "y": 890},
    403: {"x": 560, "y": 880},
    338: {"x": 144, "y": 485},
    335: {"x": 144, "y": 467},
    339: {"x": 144, "y": 449},
    355: {"x": 144, "y": 432},
    167: {"x": 144, "y": 362},
    
    # Empresa 2
    19: {"x": 188, "y": 974},
    20: {"x": 188, "y": 759},
    26: {"x": 211, "y": 974},
    13: {"x": 166, "y": 640},
    372: {"x": 520, "y": 929},
    400: {"x": 540, "y": 919},
    405: {"x": 560, "y": 909},
    337: {"x": 188, "y": 485},
    333: {"x": 188, "y": 467},
    341: {"x": 188, "y": 449},
    357: {"x": 188, "y": 432},
    156: {"x": 188, "y": 362},
    
    # Empresa 3
    34: {"x": 232, "y": 974},
    35: {"x": 232, "y": 759},
    42: {"x": 254, "y": 974},
    21: {"x": 188, "y": 640},
    374: {"x": 520, "y": 929},
    398: {"x": 540, "y": 919},
    407: {"x": 560, "y": 909},
    308: {"x": 232, "y": 485},
    331: {"x": 232, "y": 467},
    343: {"x": 232, "y": 449},
    359: {"x": 232, "y": 432},
    158: {"x": 232, "y": 362},
    
    # Empresa 4
    50: {"x": 592, "y": 944},
    51: {"x": 276, "y": 759},
    59: {"x": 254, "y": 359},
    28: {"x": 167, "y": 137},
    376: {"x": 520, "y": 899},
    396: {"x": 540, "y": 889},
    409: {"x": 560, "y": 879},
    310: {"x": 276, "y": 485},
    329: {"x": 276, "y": 467},
    345: {"x": 276, "y": 449},
    361: {"x": 276, "y": 432},
    160: {"x": 276, "y": 362},
    
    # Empresa 5
    67: {"x": 144, "y": 359},
    68: {"x": 166, "y": 359},
    76: {"x": 145, "y": 64},
    36: {"x": 166, "y": 482},
    380: {"x": 520, "y": 314},
    392: {"x": 540, "y": 304},
    413: {"x": 560, "y": 294},
    312: {"x": 320, "y": 485},
    327: {"x": 320, "y": 467},
    347: {"x": 320, "y": 449},
    363: {"x": 320, "y": 432},
    162: {"x": 320, "y": 362},
    
    # Empresa 6
    86: {"x": 277, "y": 133},
    87: {"x": 299, "y": 132},
    96: {"x": 299, "y": 96},
    44: {"x": 254, "y": 640},
    383: {"x": 520, "y": 88},
    390: {"x": 540, "y": 78},
    415: {"x": 560, "y": 68},
    314: {"x": 364, "y": 485},
    325: {"x": 363, "y": 467},
    349: {"x": 364, "y": 449},
    365: {"x": 364, "y": 432},
    172: {"x": 364, "y": 362},
    
    # Empresa 7
    106: {"x": 408, "y": 971},
    107: {"x": 408, "y": 759},
    116: {"x": 430, "y": 971},
    52: {"x": 276, "y": 640},
    385: {"x": 520, "y": 926},
    388: {"x": 540, "y": 916},
    417: {"x": 560, "y": 906},
    316: {"x": 408, "y": 485},
    323: {"x": 408, "y": 467},
    351: {"x": 408, "y": 449},
    367: {"x": 408, "y": 432},
    164: {"x": 408, "y": 362},
    
    # Empresa 8
    126: {"x": 452, "y": 971},
    127: {"x": 452, "y": 759},
    136: {"x": 474, "y": 971},
    61: {"x": 298, "y": 640},
    386: {"x": 520, "y": 926},
    385: {"x": 540, "y": 916},
    418: {"x": 560, "y": 906},
    318: {"x": 452, "y": 485},
    321: {"x": 452, "y": 467},
    353: {"x": 452, "y": 449},
    369: {"x": 452, "y": 432},
    173: {"x": 452, "y": 362},
}

def obtener_registros_listos(legajo=None):
    """Obtiene registros que cumplen las condiciones"""
    query = supabase.table("padron_deuda_presunta").select("*").eq("mail_enviado", "SI").not_.is_("leg", "null").not_.is_("acta", "null").not_.is_("vto", "null")
    if legajo:
        query = query.eq("leg", legajo)
    result = query.execute()
    return result.data if result.data else []

def formatear_fecha(fecha_str):
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        return None

def generar_pdf_con_datos(registros, inspector_nombre, output_path):
    """Genera un PDF con los datos (sin modificar la plantilla original)"""
    # Copiar la plantilla a un archivo temporal
    shutil.copy(PDF_PLANTILLA, output_path)
    
    doc = fitz.open(output_path)
    page = doc[0]
    altura = page.rect.height
    
    # Escribir cabecera
    for num, texto in [(1, "MAR DEL PLATA"), (2, inspector_nombre)]:
        if num in COORDENADAS:
            x = COORDENADAS[num]["x"]
            y = altura - COORDENADAS[num]["y"]
            page.insert_text((x, y), texto, fontsize=8, color=(0, 0, 0))
    
    # Mapeo de números por fila
    nums = {
        "razon_social": {1: 5, 2: 19, 3: 34, 4: 50, 5: 67, 6: 86, 7: 106, 8: 126},
        "cuit1": {1: 11, 2: 26, 3: 42, 4: 59, 5: 76, 6: 96, 7: 116, 8: 136},
        "cuit2": {1: 6, 2: 20, 3: 35, 4: 51, 5: 68, 6: 87, 7: 107, 8: 127},
        "acta": {1: 7, 2: 13, 3: 21, 4: 28, 5: 36, 6: 44, 7: 52, 8: 61},
        "vto_dia": {1: 381, 2: 372, 3: 374, 4: 376, 5: 380, 6: 383, 7: 385, 8: 386},
        "vto_mes": {1: 402, 2: 400, 3: 398, 4: 396, 5: 392, 6: 390, 7: 388, 8: 385},
        "vto_año": {1: 403, 2: 405, 3: 407, 4: 409, 5: 413, 6: 415, 7: 417, 8: 418},
        "desde_mes": {1: 338, 2: 337, 3: 308, 4: 310, 5: 312, 6: 314, 7: 316, 8: 318},
        "desde_año": {1: 335, 2: 333, 3: 331, 4: 329, 5: 327, 6: 325, 7: 323, 8: 321},
        "hasta_mes": {1: 339, 2: 341, 3: 343, 4: 345, 5: 347, 6: 349, 7: 351, 8: 353},
        "hasta_año": {1: 355, 2: 357, 3: 359, 4: 361, 5: 363, 6: 365, 7: 367, 8: 369},
        "deuda": {1: 167, 2: 156, 3: 158, 4: 160, 5: 162, 6: 172, 7: 164, 8: 173},
    }
    
    for i, reg in enumerate(registros[:8]):
        fila = i + 1
        
        razon_social = reg.get('razon_social', '')
        direccion = f"{reg.get('calle', '')} {reg.get('numero', '')}".strip()
        nombre_direccion = f"{razon_social} - {direccion}" if direccion else razon_social
        
        cuit = reg.get('cuit', '')
        acta = reg.get('acta', '')
        deuda = reg.get('deuda_presunta', '')
        
        fecha_obj = formatear_fecha(reg.get('vto'))
        if fecha_obj:
            vto_dia = fecha_obj.strftime('%d')
            vto_mes = fecha_obj.strftime('%m')
            vto_año = fecha_obj.strftime('%Y')
        else:
            vto_dia = vto_mes = vto_año = ''
        
        desde_obj = formatear_fecha(reg.get('desde'))
        hasta_obj = formatear_fecha(reg.get('hasta'))
        
        desde_mes = desde_obj.strftime('%m') if desde_obj else ''
        desde_año = desde_obj.strftime('%Y') if desde_obj else ''
        hasta_mes = hasta_obj.strftime('%m') if hasta_obj else ''
        hasta_año = hasta_obj.strftime('%Y') if hasta_obj else ''
        
        # Escribir cada campo en su coordenada
        campos = [
            (nums["razon_social"][fila], nombre_direccion[:60]),
            (nums["cuit1"][fila], cuit),
            (nums["cuit2"][fila], cuit),
            (nums["acta"][fila], acta),
            (nums["vto_dia"][fila], vto_dia),
            (nums["vto_mes"][fila], vto_mes),
            (nums["vto_año"][fila], vto_año),
            (nums["desde_mes"][fila], desde_mes),
            (nums["desde_año"][fila], desde_año),
            (nums["hasta_mes"][fila], hasta_mes),
            (nums["hasta_año"][fila], hasta_año),
            (nums["deuda"][fila], deuda),
        ]
        
        for num, texto in campos:
            if num in COORDENADAS:
                x = COORDENADAS[num]["x"]
                y = altura - COORDENADAS[num]["y"]
                page.insert_text((x, y), str(texto), fontsize=8, color=(0, 0, 0))
    
    doc.save(output_path)
    doc.close()

# ── Obtener inspectores ──────────────────────────────────────────────────────
inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
opciones_inspectores = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins for ins in inspectores.data}
opciones_inspectores["TODOS"] = None

# ── Interfaz ─────────────────────────────────────────────────────────────────
st.markdown("### Seleccionar Inspector")
inspector_sel = st.selectbox("Inspector", options=list(opciones_inspectores.keys()))

if st.button("📄 GENERAR INFORME", type="primary", use_container_width=True):
    inspector = opciones_inspectores[inspector_sel]
    
    with st.spinner("Buscando registros listos..."):
        if inspector is None:
            registros = obtener_registros_listos()
            grupos = defaultdict(list)
            for reg in registros:
                grupos[reg.get('leg')].append(reg)
        else:
            registros = obtener_registros_listos(inspector['legajo'])
            grupos = {inspector['legajo']: registros}
    
    if not registros:
        st.warning("No hay registros listos para este inspector")
    else:
        total_registros = sum(len(regs) for regs in grupos.values())
        st.success(f"✅ Se encontraron {total_registros} registros listos")
        
        total_paginas = 0
        for regs in grupos.values():
            total_paginas += (len(regs) + 7) // 8
        
        st.info(f"📊 Se generarán {total_paginas} página(s)")
        
        with st.spinner("Generando PDFs..."):
            pdfs_generados = []
            
            for leg, regs in grupos.items():
                nombre_insp = next((k for k, v in opciones_inspectores.items() if v and v['legajo'] == leg), "Desconocido")
                nombre_limpio = nombre_insp.split(" (Legajo")[0]
                
                for pagina_idx in range(0, len(regs), 8):
                    batch = regs[pagina_idx:pagina_idx+8]
                    num_pagina = pagina_idx // 8 + 1
                    
                    temp_path = tempfile.mktemp(suffix=".pdf")
                    generar_pdf_con_datos(batch, nombre_limpio, temp_path)
                    
                    with open(temp_path, "rb") as f:
                        pdfs_generados.append({
                            "nombre": f"INFORME_{nombre_limpio}_pag{num_pagina}.pdf",
                            "data": f.read()
                        })
                    
                    os.unlink(temp_path)
            
            st.success(f"✅ Se generaron {len(pdfs_generados)} PDF(s)")
            
            for pdf in pdfs_generados:
                st.download_button(
                    label=f"📥 {pdf['nombre']}",
                    data=pdf['data'],
                    file_name=pdf['nombre'],
                    mime="application/pdf",
                    use_container_width=True
                )
