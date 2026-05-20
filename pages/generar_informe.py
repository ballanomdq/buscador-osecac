import streamlit as st
from pypdf import PdfReader, PdfWriter
from supabase import create_client
from datetime import datetime
import io
import time
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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h3>📄 Generar Informe Mensual de Inspección</h3>
    <p>Completa el formulario PDF con los datos de los registros listos</p>
</div>
""", unsafe_allow_html=True)

PDF_PATH = "ORIGINAL.pdf"

# ==================================================
# MAPEO DE FILAS (SOLO las 8 empresas, no 16)
# El PDF tiene filas intercaladas. Cada empresa ocupa 2 filas:
# Fila 1 (empresa 1): razón social + CUIT + acta + fechas
# Fila 2: CUIT repetido (en la columna de la izquierda)
# ==================================================

def nombre_campos_empresa(fila):
    """
    fila: 1 a 8 (número de empresa)
    Retorna los nombres de campo para esa empresa
    """
    # Números de fila reales en el PDF (están intercalados)
    # Empresa 1: filas 1 y 2
    # Empresa 2: filas 4 y 5? (según la numeración que me diste)
    # Usamos el patrón que identificó Claude pero limitado a 8 empresas
    
    # Mapeo de fila real según el PDF (esto lo ajustamos con tu feedback)
    fila_real = {
        1: 1,   # Empresa 1 usa fila 1
        2: 4,   # Empresa 2 usa fila 4 (porque hay una fila intermedia)
        3: 7,   # Empresa 3 usa fila 7
        4: 10,  # Empresa 4 usa fila 10
        5: 13,  # Empresa 5 usa fila 13
        6: 16,  # Empresa 6 usa fila 16
        7: 19,  # Empresa 7 usa fila 19
        8: 22,  # Empresa 8 usa fila 22
    }.get(fila, fila)
    
    # Segunda fila (donde va el CUIT repetido)
    fila_cuit2 = fila_real + 1
    
    return {
        "razon":      f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{fila_real}",
        "cuit1":      f"NRO DE  CUITRow{fila_real}",
        "cuit2":      f"NRO DE  CUITRow{fila_cuit2}",
        "acta":       f"NRORow{fila_real}",
        "vto_dia":    f"VTODIA{fila}",
        "vto_mes":    f"VTOMES{fila}",
        "vto_año":    f"VTOAÑO{fila}",
        "desde_mes":  f"PVMES{fila}",
        "desde_año":  f"PVAÑO{fila}",
        "hasta_mes":  f"PVMES{fila + 8}",
        "hasta_año":  f"PVAÑO{fila + 8}",
        "deuda":      f"DEUDA DETERMINADARow{fila_real}",
    }

def obtener_registros_listos(legajo=None):
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

def limpiar_campos_no_usados(writer):
    """Limpia los campos que no deben mostrar números de referencia"""
    # Lista de campos que tienen números impresos (los que hay que borrar)
    campos_a_limpiar = [
        "AREA DE FISCALIZACIONRow1",
        "APELLIDO Y NOMBRES INSPECTORRow1", 
        "MES Y AÑORow1",
        "FOLIORow1",
    ]
    
    # Para cada empresa (1 a 8), limpiar los campos de números
    for i in range(1, 9):
        campos_a_limpiar.extend([
            f"VTODIA{i}",
            f"VTOMES{i}", 
            f"VTOAÑO{i}",
            f"PVMES{i}",
            f"PVAÑO{i}",
            f"DEUDA DETERMINADARow{i}",
        ])
    
    datos_limpios = {campo: "" for campo in campos_a_limpiar}
    writer.update_page_form_field_values(writer.pages[0], datos_limpios, auto_regenerate=True)

def generar_pdf_informe(registros, inspector_nombre):
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    datos = {}

    # Cabecera
    datos["AREA DE FISCALIZACIONRow1"] = "MAR DEL PLATA"
    datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector_nombre

    if registros:
        fecha_cab = formatear_fecha(registros[0].get("vto"))
        if fecha_cab:
            datos["MES Y AÑORow1"] = fecha_cab.strftime("%m")
            datos["MES Y AÑO"] = fecha_cab.strftime("%Y")

    # Máximo 8 empresas
    for i, reg in enumerate(registros[:8]):
        fila = i + 1
        campos = nombre_campos_empresa(fila)

        razon = reg.get("razon_social", "")
        calle = reg.get("calle", "")
        numero = reg.get("numero", "")
        direccion = f"{calle} {numero}".strip()
        nombre_direccion = f"{razon} - {direccion}" if direccion else razon
        cuit = str(reg.get("cuit", ""))
        acta = str(reg.get("acta", ""))
        deuda = str(reg.get("deuda_presunta", ""))

        vto_obj = formatear_fecha(reg.get("vto"))
        desde_obj = formatear_fecha(reg.get("desde"))
        hasta_obj = formatear_fecha(reg.get("hasta"))

        datos[campos["razon"]] = nombre_direccion[:80]
        datos[campos["cuit1"]] = cuit
        datos[campos["cuit2"]] = cuit  # CUIT repetido en la fila siguiente
        datos[campos["acta"]] = acta
        datos[campos["deuda"]] = deuda

        if vto_obj:
            datos[campos["vto_dia"]] = vto_obj.strftime("%d")
            datos[campos["vto_mes"]] = vto_obj.strftime("%m")
            datos[campos["vto_año"]] = vto_obj.strftime("%Y")
        if desde_obj:
            datos[campos["desde_mes"]] = desde_obj.strftime("%m")
            datos[campos["desde_año"]] = desde_obj.strftime("%Y")
        if hasta_obj:
            datos[campos["hasta_mes"]] = hasta_obj.strftime("%m")
            datos[campos["hasta_año"]] = hasta_obj.strftime("%Y")

    # Escribir datos
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)
    
    # Limpiar números de referencia
    limpiar_campos_no_usados(writer)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# ── Interfaz ─────────────────────────────────────────────────────────────────
inspectores_res = supabase.table("inspectores").select("*").order("legajo").execute()
opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins for ins in inspectores_res.data}
opciones["TODOS"] = None

inspector_sel = st.selectbox("Inspector", options=list(opciones.keys()))

if st.button("📄 GENERAR INFORME", type="primary", use_container_width=True):
    inspector = opciones[inspector_sel]

    with st.spinner("Buscando registros listos..."):
        if inspector is None:
            registros = obtener_registros_listos()
            grupos = defaultdict(list)
            for reg in registros:
                grupos[reg.get("leg")].append(reg)
        else:
            registros = obtener_registros_listos(inspector["legajo"])
            grupos = {inspector["legajo"]: registros}

    if not registros:
        st.warning("⚠️ No hay registros listos para este inspector.")
    else:
        total = sum(len(r) for r in grupos.values())
        st.success(f"✅ {total} registro(s) encontrado(s)")

        with st.spinner("Generando PDFs..."):
            pdfs = []
            for leg, regs in grupos.items():
                nombre_insp = next((k for k, v in opciones.items() if v and v["legajo"] == leg), str(leg))
                nombre_limpio = nombre_insp.split(" (Legajo")[0]

                # MÁXIMO 8 EMPRESAS POR PÁGINA
                for idx in range(0, len(regs), 8):
                    batch = regs[idx:idx + 8]
                    num_pagina = idx // 8 + 1
                    total_paginas = (len(regs) + 7) // 8

                    pdf_buffer = generar_pdf_informe(batch, nombre_limpio)
                    pdfs.append({
                        "nombre": f"INFORME_{nombre_limpio}_pag{num_pagina}de{total_paginas}.pdf",
                        "buffer": pdf_buffer,
                    })

        st.info(f"📊 Se generaron {len(pdfs)} archivo(s)")
        st.markdown("### 📥 Descargar:")

        for pdf in pdfs:
            st.download_button(
                label=f"📄 {pdf['nombre']}",
                data=pdf["buffer"].getvalue(),
                file_name=pdf["nombre"],
                mime="application/pdf",
                use_container_width=True,
            )
