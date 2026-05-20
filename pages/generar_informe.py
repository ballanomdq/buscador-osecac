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
.app-header {
    background: #1e293b;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid #3b82f6;
}
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

# ── Mapeo de campos por nombre real del PDF ──────────────────────────────────
# El PDF tiene campos con nombres como VTODIA1, VTOMES1, VTOAÑO1, PVMES1, etc.
# Cada fila (1 a 16) corresponde a una empresa en el informe.

def nombre_campos_fila(fila):
    """Devuelve el diccionario de nombres de campo para una fila dada (1-16)"""
    return {
        "razon":      f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{fila}",
        "cuit":       f"NRO DE  CUITRow{fila}",
        "acta":       f"NRORow{fila}",
        "vto_dia":    f"VTODIA{fila}",
        "vto_mes":    f"VTOMES{fila}",
        "vto_año":    f"VTOAÑO{fila}",
        "desde_mes":  f"PVMES{fila}",           # periodo desde - mes
        "desde_año":  f"PVAÑO{fila}",           # periodo desde - año
        "hasta_mes":  f"PVMES{fila + 16}",      # periodo hasta - mes
        "hasta_año":  f"PVAÑO{fila + 16}",      # periodo hasta - año
        "deuda":      f"DEUDA DETERMINADARow{fila}",
    }

# ── Funciones ────────────────────────────────────────────────────────────────

def obtener_registros_listos(legajo=None):
    """Registros con mail_enviado=SI, leg/acta/vto no nulos"""
    query = (
        supabase.table("padron_deuda_presunta")
        .select("*")
        .eq("mail_enviado", "SI")
        .not_.is_("leg", "null")
        .not_.is_("acta", "null")
        .not_.is_("vto", "null")
    )
    if legajo:
        query = query.eq("leg", legajo)
    result = query.execute()
    return result.data if result.data else []

def formatear_fecha(fecha_str):
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except Exception:
        return None

def generar_pdf_informe(registros, inspector_nombre):
    """
    Genera un PDF completando los campos del formulario ORIGINAL.pdf.
    Acepta hasta 16 registros por página.
    Devuelve un BytesIO listo para descargar.
    """
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    datos = {}

    # ── Cabecera ──────────────────────────────────────────────────────────────
    datos["AREA DE FISCALIZACIONRow1"] = "MAR DEL PLATA"
    datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector_nombre

    # Mes y año de cabecera: tomamos del primer registro
    if registros:
        fecha_cab = formatear_fecha(registros[0].get("vto"))
        if fecha_cab:
            datos["MES Y AÑORow1"] = fecha_cab.strftime("%m")   # mes
            datos["MES Y AÑO"]     = fecha_cab.strftime("%Y")   # año

    # ── Filas de empresas (hasta 16) ─────────────────────────────────────────
    for i, reg in enumerate(registros[:16]):
        fila = i + 1
        campos = nombre_campos_fila(fila)

        # Razón social + dirección
        razon = reg.get("razon_social", "")
        calle = reg.get("calle", "")
        numero = reg.get("numero", "")
        direccion = f"{calle} {numero}".strip()
        nombre_direccion = f"{razon} - {direccion}" if direccion else razon

        # Fechas
        vto_obj   = formatear_fecha(reg.get("vto"))
        desde_obj = formatear_fecha(reg.get("desde"))
        hasta_obj = formatear_fecha(reg.get("hasta"))

        datos[campos["razon"]]     = nombre_direccion[:80]
        datos[campos["cuit"]]      = str(reg.get("cuit", ""))
        datos[campos["acta"]]      = str(reg.get("acta", ""))
        datos[campos["deuda"]]     = str(reg.get("deuda_presunta", ""))

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

    # ── Escribir en el PDF ────────────────────────────────────────────────────
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)

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
                nombre_insp = next(
                    (k for k, v in opciones.items() if v and v["legajo"] == leg),
                    str(leg)
                )
                nombre_limpio = nombre_insp.split(" (Legajo")[0]

                # Cada PDF tiene hasta 16 empresas
                for idx in range(0, len(regs), 16):
                    batch = regs[idx:idx + 16]
                    num_pagina = idx // 16 + 1
                    total_paginas = (len(regs) + 15) // 16

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
