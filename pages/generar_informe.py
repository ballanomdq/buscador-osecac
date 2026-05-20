import streamlit as st
from pypdf import PdfReader, PdfWriter
from supabase import create_client
from datetime import datetime, date
import io
import zipfile
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
    background: #1e293b; padding: 0.5rem 1rem; border-radius: 10px;
    margin-bottom: 1rem; border-left: 4px solid #3b82f6;
}
.app-header h3 { color: #fff; margin: 0; }
.app-header p  { color: #94a3b8; margin: 0; font-size: 0.8rem; }
div[data-testid="stButton"] > button { border-radius: 8px !important; font-weight: 500 !important; }
div[data-testid="stButton"] > button[kind="primary"] { background-color: #10b981 !important; }
.actas-button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.4rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}
.actas-button:hover {
    background: #2563eb;
}
</style>
""", unsafe_allow_html=True)

# Header con botón de acceso a Actas
col_header, col_btn = st.columns([4, 1])
with col_header:
    st.markdown("""
    <div class="app-header">
        <h3>📄 Generar Informe Mensual de Inspección</h3>
        <p>Completa el formulario PDF con los datos de los registros listos</p>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("""
    <a href="https://buscador-osecac-6jztx7xjhgkvcaubfinn5y.streamlit.app/actas" target="_blank" style="text-decoration: none;">
        <div style="background: #3b82f6; padding: 0.5rem 0.8rem; border-radius: 8px; text-align: center; margin-top: 0.3rem;">
            <span style="color: white; font-weight: 500;">📋 IR A ACTAS</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

PDF_PATH = "ORIGINAL.pdf"

# ════════════════════════════════════════════════════════════════════════════
# MAPEO DE LAS 8 EMPRESAS
# Fila principal (impar):  todos los datos
# Fila intermedia (par):   el CUIT va en el campo RAZON SOCIAL (columna izquierda)
# ════════════════════════════════════════════════════════════════════════════

MAPEO_EMPRESAS = [
    {   # Empresa 1
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow1",
        "cuit_ppal":   "NRO DE  CUITRow1",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow2",
        "acta":        "NRORow1",
        "vto_dia":     "VTODIA1",   "vto_mes":   "VTOMES1",   "vto_año":   "VTOAÑO1",
        "desde_mes":   "PVMES1",    "desde_año": "PVAÑO1",
        "hasta_mes":   "PVMES17",   "hasta_año": "PVAÑO17",
        "deuda":       "DEUDA DETERMINADARow1",
    },
    {   # Empresa 2
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow3",
        "cuit_ppal":   "NRO DE  CUITRow3",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow4",
        "acta":        "NRORow3",
        "vto_dia":     "VTODIA3",   "vto_mes":   "VTOMES3",   "vto_año":   "VTOAÑO3",
        "desde_mes":   "PVMES3",    "desde_año": "PVAÑO3",
        "hasta_mes":   "PVMES19",   "hasta_año": "PVAÑO19",
        "deuda":       "DEUDA DETERMINADARow3",
    },
    {   # Empresa 3
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow5",
        "cuit_ppal":   "NRO DE  CUITRow5",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow6",
        "acta":        "NRORow5",
        "vto_dia":     "VTODIA5",   "vto_mes":   "VTOMES5",   "vto_año":   "VTOAÑO5",
        "desde_mes":   "PVMES5",    "desde_año": "PVAÑO5",
        "hasta_mes":   "PVMES21",   "hasta_año": "PVAÑO21",
        "deuda":       "DEUDA DETERMINADARow5",
    },
    {   # Empresa 4
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow7",
        "cuit_ppal":   "NRO DE  CUITRow7",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow8",
        "acta":        "NRORow7",
        "vto_dia":     "VTODIA7",   "vto_mes":   "VTOMES7",   "vto_año":   "VTOAÑO7",
        "desde_mes":   "PVMES7",    "desde_año": "PVAÑO7",
        "hasta_mes":   "PVMES23",   "hasta_año": "PVAÑO23",
        "deuda":       "DEUDA DETERMINADARow7",
    },
    {   # Empresa 5
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow9",
        "cuit_ppal":   "NRO DE  CUITRow9",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow10",
        "acta":        "NRORow9",
        "vto_dia":     "VTODIA9",   "vto_mes":   "VTOMES9",   "vto_año":   "VTOAÑO9",
        "desde_mes":   "PVMES9",    "desde_año": "PVAÑO9",
        "hasta_mes":   "PVMES25",   "hasta_año": "PVAÑO25",
        "deuda":       "DEUDA DETERMINADARow9",
    },
    {   # Empresa 6
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow11",
        "cuit_ppal":   "NRO DE  CUITRow11",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow12",
        "acta":        "NRORow11",
        "vto_dia":     "VTODIA11",  "vto_mes":   "VTOMES11",  "vto_año":   "VTOAÑO11",
        "desde_mes":   "PVMES11",   "desde_año": "PVAÑO11",
        "hasta_mes":   "PVMES27",   "hasta_año": "PVAÑO27",
        "deuda":       "DEUDA DETERMINADARow11",
    },
    {   # Empresa 7
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow13",
        "cuit_ppal":   "NRO DE  CUITRow13",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow14",
        "acta":        "NRORow13",
        "vto_dia":     "VTODIA13",  "vto_mes":   "VTOMES13",  "vto_año":   "VTOAÑO13",
        "desde_mes":   "PVMES13",   "desde_año": "PVAÑO13",
        "hasta_mes":   "PVMES29",   "hasta_año": "PVAÑO29",
        "deuda":       "DEUDA DETERMINADARow13",
    },
    {   # Empresa 8
        "razon":       "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow15",
        "cuit_ppal":   "NRO DE  CUITRow15",
        "cuit_inter":  "EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow16",
        "acta":        "NRORow15",
        "vto_dia":     "VTODIA15",  "vto_mes":   "VTOMES15",  "vto_año":   "VTOAÑO15",
        "desde_mes":   "PVMES15",   "desde_año": "PVAÑO15",
        "hasta_mes":   "PVMES31",   "hasta_año": "PVAÑO31",
        "deuda":       "DEUDA DETERMINADARow15",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def año_corto(fecha_obj):
    """Últimos 2 dígitos del año — para casilleros chicos"""
    return fecha_obj.strftime("%y") if fecha_obj else ""

def año_completo(fecha_obj):
    """4 dígitos del año — solo para la cabecera"""
    return fecha_obj.strftime("%Y") if fecha_obj else ""

@st.cache_data
def obtener_todos_los_campos():
    reader = PdfReader(PDF_PATH)
    fields = reader.get_fields()
    return list(fields.keys()) if fields else []

def obtener_registros_listos(legajo=None):
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
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except Exception:
        return None

def empaquetar_zip(pdfs):
    """Empaqueta todos los PDFs en un único ZIP en memoria"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdf in pdfs:
            zf.writestr(pdf["nombre"], pdf["buffer"].getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# ── Generación del PDF ────────────────────────────────────────────────────────

def generar_pdf_informe(registros_batch, inspector_nombre, todos_los_campos):
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)

    # PASO 1 — limpiar todos los campos (elimina números de referencia)
    datos = {campo: "" for campo in todos_los_campos}

    # PASO 2 — cabecera
    datos["AREA DE FISCALIZACIONRow1"]        = "MAR DEL PLATA"
    datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector_nombre

    if registros_batch:
        fecha_cab = formatear_fecha(registros_batch[0].get("vto"))
        if fecha_cab:
            # "MES Y AÑO"     = casillero de la IZQUIERDA → mes          ej: 01
            # "MES Y AÑORow1" = casillero de la DERECHA   → año completo ej: 1976
            datos["MES Y AÑO"]     = fecha_cab.strftime("%m")  # mes  → 01
            datos["MES Y AÑORow1"] = año_completo(fecha_cab)   # año  → 1976

    # PASO 3 — empresas
    for i, reg in enumerate(registros_batch):
        m = MAPEO_EMPRESAS[i]

        # Solo la razón social — sin dirección
        razon_social = str(reg.get("razon_social", ""))

        cuit  = str(reg.get("cuit", ""))
        acta  = str(reg.get("acta", ""))
        deuda = str(reg.get("deuda_presunta", ""))

        vto_obj   = formatear_fecha(reg.get("vto"))
        desde_obj = formatear_fecha(reg.get("desde"))
        hasta_obj = formatear_fecha(reg.get("hasta"))

        # Fila principal
        datos[m["razon"]]     = razon_social[:80]
        datos[m["cuit_ppal"]] = cuit
        datos[m["acta"]]      = acta
        datos[m["deuda"]]     = deuda

        # Fecha VTO — año en 2 dígitos (casillero chico)
        if vto_obj:
            datos[m["vto_dia"]] = vto_obj.strftime("%d")
            datos[m["vto_mes"]] = vto_obj.strftime("%m")
            datos[m["vto_año"]] = año_corto(vto_obj)

        # Período DESDE — año en 2 dígitos
        if desde_obj:
            datos[m["desde_mes"]] = desde_obj.strftime("%m")
            datos[m["desde_año"]] = año_corto(desde_obj)

        # Período HASTA — año en 2 dígitos
        if hasta_obj:
            datos[m["hasta_mes"]] = hasta_obj.strftime("%m")
            datos[m["hasta_año"]] = año_corto(hasta_obj)

        # Fila intermedia — solo CUIT en columna izquierda
        datos[m["cuit_inter"]] = cuit

    # PASO 4 — escribir
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# ── Interfaz ──────────────────────────────────────────────────────────────────

todos_los_campos = obtener_todos_los_campos()
if not todos_los_campos:
    st.error("❌ No se pudo leer 'ORIGINAL.pdf'. Verificá que esté en la carpeta del proyecto.")
    st.stop()

inspectores_res = supabase.table("inspectores").select("*").order("legajo").execute()
opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins for ins in inspectores_res.data}
opciones["TODOS"] = None

inspector_sel = st.selectbox("Inspector", options=list(opciones.keys()))

if st.button("📄 GENERAR INFORME", type="primary", use_container_width=True):
    inspector = opciones[inspector_sel]

    with st.spinner("Buscando registros..."):
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
                total_pags    = (len(regs) + 7) // 8

                for idx in range(0, len(regs), 8):
                    batch      = regs[idx : idx + 8]
                    num_pag    = idx // 8 + 1
                    pdf_buffer = generar_pdf_informe(batch, nombre_limpio, todos_los_campos)
                    pdfs.append({
                        "nombre": f"INFORME_{nombre_limpio}_pag{num_pag}de{total_pags}.pdf",
                        "buffer": pdf_buffer,
                    })

        st.info(f"📊 Se generaron {len(pdfs)} archivo(s)")

        if len(pdfs) == 1:
            # Un solo PDF → descarga directa
            st.download_button(
                label=f"📥 Descargar {pdfs[0]['nombre']}",
                data=pdfs[0]["buffer"].getvalue(),
                file_name=pdfs[0]["nombre"],
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            # Varios PDFs → un solo ZIP
            nombre_zip = f"INFORMES_{date.today().strftime('%Y%m%d')}.zip"
            zip_buffer = empaquetar_zip(pdfs)
            st.markdown("### 📥 Descargar todos los informes:")
            st.download_button(
                label=f"📦 Descargar ZIP con {len(pdfs)} informes ({nombre_zip})",
                data=zip_buffer.getvalue(),
                file_name=nombre_zip,
                mime="application/zip",
                use_container_width=True,
            )
            st.caption("Archivos incluidos: " + ", ".join(p["nombre"] for p in pdfs))
