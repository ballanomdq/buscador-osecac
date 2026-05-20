import streamlit as st
from pypdf import PdfReader, PdfWriter
from supabase import create_client
from datetime import datetime
import io
import os
import time

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
div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #10b981 !important;
}
.stProgress > div > div > div > div {
    background-color: #10b981 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h3>📄 Generar Informe Mensual de Inspección</h3>
    <p>Completa el formulario PDF con los datos de los registros listos</p>
</div>
""", unsafe_allow_html=True)

# ── Configuración ────────────────────────────────────────────────────────────
PDF_PATH = "ORIGINAL.pdf"  # El PDF plantilla con números

# Mapeo de números de campo (según el PDF numerado) → nombre del campo
# Este mapeo se completa con los nombres reales al leer el PDF
CAMPOS_POR_NUMERO = {}

# ── Funciones ────────────────────────────────────────────────────────────────
def obtener_nombres_campos():
    """Lee el PDF y obtiene los nombres de los campos en orden"""
    if not os.path.exists(PDF_PATH):
        st.error(f"No se encuentra '{PDF_PATH}'")
        return None
    reader = PdfReader(PDF_PATH)
    fields = reader.get_fields()
    if fields:
        return list(fields.keys())
    return None

def obtener_registros_listos(legajo=None):
    """Obtiene registros que cumplen: leg NOT NULL, mail_enviado='SI', acta NOT NULL, vto NOT NULL"""
    query = supabase.table("padron_deuda_presunta").select("*").eq("mail_enviado", "SI").not_.is_("leg", "null").not_.is_("acta", "null").not_.is_("vto", "null")
    if legajo:
        query = query.eq("leg", legajo)
    result = query.execute()
    return result.data if result.data else []

def formatear_fecha(fecha_str):
    """Convierte YYYY-MM-DD a objeto datetime"""
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        return None

def generar_pdf_informe(registros, inspector_nombre, num_pagina, nombres_campos):
    """Genera un PDF con los datos de hasta 8 registros"""
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)
    
    datos = {}
    
    # === CABECERA ===
    datos[nombres_campos[0]] = "MAR DEL PLATA"      # Campo 1
    datos[nombres_campos[1]] = inspector_nombre     # Campo 2
    
    # Tomar fecha VTO del primer registro
    if registros:
        fecha_obj = formatear_fecha(registros[0].get('vto'))
        if fecha_obj:
            datos[nombres_campos[152]] = fecha_obj.strftime('%Y')   # Campo 153: año
            datos[nombres_campos[153]] = fecha_obj.strftime('%m')   # Campo 154: mes
    
    # === EMPRESAS (hasta 8) ===
    # Mapeo según instrucciones del usuario
    # Índices: (razon_social, cuit1, cuit2, acta, vto_dia, vto_mes, vto_año, desde_mes, desde_año, hasta_mes, hasta_año, deuda)
    mapeo_filas = [
        # Empresa 1: números de campo (0-indexado, restamos 1)
        {"razon": 4, "cuit1": 10, "cuit2": 5, "acta": 6, "vto_dia": 380, "vto_mes": 401, "vto_año": 402,
         "desde_mes": 337, "desde_año": 334, "hasta_mes": 338, "hasta_año": 354, "deuda": 166},
        # Empresa 2
        {"razon": 18, "cuit1": 25, "cuit2": 19, "acta": 12, "vto_dia": 371, "vto_mes": 399, "vto_año": 404,
         "desde_mes": 336, "desde_año": 332, "hasta_mes": 340, "hasta_año": 356, "deuda": 155},
        # Empresa 3
        {"razon": 33, "cuit1": 41, "cuit2": 34, "acta": 20, "vto_dia": 373, "vto_mes": 397, "vto_año": 406,
         "desde_mes": 307, "desde_año": 330, "hasta_mes": 342, "hasta_año": 358, "deuda": 157},
        # Empresa 4
        {"razon": 49, "cuit1": 58, "cuit2": 50, "acta": 27, "vto_dia": 375, "vto_mes": 395, "vto_año": 408,
         "desde_mes": 309, "desde_año": 328, "hasta_mes": 344, "hasta_año": 360, "deuda": 159},
        # Empresa 5
        {"razon": 66, "cuit1": 75, "cuit2": 67, "acta": 35, "vto_dia": 379, "vto_mes": 391, "vto_año": 412,
         "desde_mes": 311, "desde_año": 326, "hasta_mes": 346, "hasta_año": 362, "deuda": 161},
        # Empresa 6
        {"razon": 85, "cuit1": 95, "cuit2": 86, "acta": 43, "vto_dia": 382, "vto_mes": 389, "vto_año": 414,
         "desde_mes": 313, "desde_año": 324, "hasta_mes": 348, "hasta_año": 364, "deuda": 171},
        # Empresa 7
        {"razon": 105, "cuit1": 115, "cuit2": 106, "acta": 51, "vto_dia": 384, "vto_mes": 387, "vto_año": 416,
         "desde_mes": 315, "desde_año": 322, "hasta_mes": 350, "hasta_año": 366, "deuda": 163},
        # Empresa 8
        {"razon": 125, "cuit1": 135, "cuit2": 126, "acta": 60, "vto_dia": 386, "vto_mes": 385, "vto_año": 418,
         "desde_mes": 317, "desde_año": 320, "hasta_mes": 352, "hasta_año": 368, "deuda": 172},
    ]
    
    for i, reg in enumerate(registros[:8]):
        if i >= len(mapeo_filas):
            break
        m = mapeo_filas[i]
        
        razon_social = reg.get('razon_social', '')
        direccion = f"{reg.get('calle', '')} {reg.get('numero', '')}".strip()
        nombre_direccion = f"{razon_social} - {direccion}" if direccion else razon_social
        
        cuit = reg.get('cuit', '')
        acta = reg.get('acta', '')
        deuda = reg.get('deuda_presunta', '')
        
        # Fecha VTO
        fecha_obj = formatear_fecha(reg.get('vto'))
        if fecha_obj:
            vto_dia = fecha_obj.strftime('%d')
            vto_mes = fecha_obj.strftime('%m')
            vto_año = fecha_obj.strftime('%Y')
        else:
            vto_dia = vto_mes = vto_año = ''
        
        # Fechas DESDE y HASTA
        desde_obj = formatear_fecha(reg.get('desde'))
        hasta_obj = formatear_fecha(reg.get('hasta'))
        
        desde_mes = desde_obj.strftime('%m') if desde_obj else ''
        desde_año = desde_obj.strftime('%Y') if desde_obj else ''
        hasta_mes = hasta_obj.strftime('%m') if hasta_obj else ''
        hasta_año = hasta_obj.strftime('%Y') if hasta_obj else ''
        
        # Asignar a los campos
        datos[nombres_campos[m["razon"]]] = nombre_direccion[:80]
        datos[nombres_campos[m["cuit1"]]] = cuit
        datos[nombres_campos[m["cuit2"]]] = cuit
        datos[nombres_campos[m["acta"]]] = acta
        datos[nombres_campos[m["vto_dia"]]] = vto_dia
        datos[nombres_campos[m["vto_mes"]]] = vto_mes
        datos[nombres_campos[m["vto_año"]]] = vto_año
        datos[nombres_campos[m["desde_mes"]]] = desde_mes
        datos[nombres_campos[m["desde_año"]]] = desde_año
        datos[nombres_campos[m["hasta_mes"]]] = hasta_mes
        datos[nombres_campos[m["hasta_año"]]] = hasta_año
        datos[nombres_campos[m["deuda"]]] = deuda
    
    # Actualizar campos
    writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# ── Cargar nombres de campos al inicio ───────────────────────────────────────
nombres_campos = obtener_nombres_campos()
if not nombres_campos:
    st.error("❌ No se pudo leer el PDF. Verificá que 'ORIGINAL.pdf' esté en la carpeta.")
    st.stop()

st.success(f"✅ PDF cargado correctamente. {len(nombres_campos)} campos disponibles.")

# ── Obtener inspectores ──────────────────────────────────────────────────────
inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
opciones_inspectores = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
opciones_inspectores["TODOS"] = 0

# ── Ventana flotante ─────────────────────────────────────────────────────────
if st.button("📋 GENERAR INFORME MENSUAL", type="primary", use_container_width=True):
    @st.dialog("📄 GENERAR INFORME MENSUAL", width="large")
    def dialog_generar_informe():
        st.markdown("Seleccioná el inspector y confirmá la generación")
        
        inspector_seleccionado = st.selectbox("Inspector", options=list(opciones_inspectores.keys()), key="dialog_inspector")
        legajo_seleccionado = opciones_inspectores[inspector_seleccionado]
        
        # Obtener registros listos
        with st.spinner("Buscando registros listos..."):
            if legajo_seleccionado == 0:
                registros = obtener_registros_listos()
                # Agrupar por inspector
                from collections import defaultdict
                grupos = defaultdict(list)
                for reg in registros:
                    grupos[reg.get('leg')].append(reg)
                total_registros = len(registros)
                st.info(f"📊 Total registros listos: {total_registros}")
                if total_registros == 0:
                    st.warning("No hay registros listos en ningún inspector")
                    if st.button("Cerrar"):
                        st.rerun()
                    return
            else:
                registros = obtener_registros_listos(legajo_seleccionado)
                if not registros:
                    st.warning(f"El inspector {inspector_seleccionado} no tiene registros listos")
                    if st.button("Cerrar"):
                        st.rerun()
                    return
                st.info(f"📊 {inspector_seleccionado}: {len(registros)} registro(s) listo(s)")
                grupos = {legajo_seleccionado: registros}
        
        # Mostrar resumen
        st.markdown("---")
        st.markdown("### 📋 Resumen a generar:")
        for leg, regs in grupos.items():
            nombre_insp = next((k for k, v in opciones_inspectores.items() if v == leg), str(leg))
            paginas = (len(regs) + 7) // 8
            st.caption(f"• {nombre_insp}: {len(regs)} empresa(s) → {paginas} página(s)")
        
        col_ok, col_cancel = st.columns(2)
        with col_ok:
            if st.button("✅ CONFIRMAR Y GENERAR", type="primary", use_container_width=True):
                with st.spinner("Generando informes..."):
                    pdfs_generados = []
                    total_grupos = len(grupos)
                    progreso = st.progress(0)
                    
                    for idx, (leg, regs) in enumerate(grupos.items()):
                        nombre_insp = next((k for k, v in opciones_inspectores.items() if v == leg), str(leg))
                        nombre_limpio = nombre_insp.split(" (Legajo")[0]
                        
                        # Dividir en grupos de 8
                        for i in range(0, len(regs), 8):
                            batch = regs[i:i+8]
                            num_pagina = i // 8 + 1
                            
                            pdf_buffer = generar_pdf_informe(batch, nombre_limpio, num_pagina, nombres_campos)
                            pdfs_generados.append({
                                'inspector': nombre_limpio,
                                'pagina': num_pagina,
                                'total_paginas': (len(regs) + 7) // 8,
                                'buffer': pdf_buffer
                            })
                        
                        progreso.progress((idx + 1) / total_grupos)
                        time.sleep(0.1)
                    
                    progreso.progress(1.0)
                    st.session_state.pdfs_generados = pdfs_generados
                    st.session_state.dialog_abierto = False
                    st.rerun()
        
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True):
                st.rerun()
    
    dialog_generar_informe()

# ── Mostrar PDFs generados ────────────────────────────────────────────────────
if st.session_state.get('pdfs_generados'):
    st.success("✅ Informes generados correctamente")
    
    # Resumen
    total_empresas = 0
    for pdf in st.session_state.pdfs_generados:
        total_empresas += 8  # Aproximado
    st.info(f"📊 Se generaron {len(st.session_state.pdfs_generados)} archivo(s)")
    
    # Botones de descarga
    st.markdown("### 📥 Descargar archivos:")
    for pdf in st.session_state.pdfs_generados:
        nombre_archivo = f"INFORME_{pdf['inspector']}_pag{pdf['pagina']}_de_{pdf['total_paginas']}.pdf"
        st.download_button(
            label=f"📄 {pdf['inspector']} - Página {pdf['pagina']} de {pdf['total_paginas']}",
            data=pdf['buffer'].getvalue(),
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True
        )
    
    if st.button("🗑️ Limpiar", use_container_width=True):
        del st.session_state["pdfs_generados"]
        st.rerun()
