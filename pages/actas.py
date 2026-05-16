import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
import difflib
import hashlib
import time

# ── Conexión ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(page_title="Fiscalización - OSECAC", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
html, body, [class*="css"] { font-size: 13px !important; }
.app-header { padding: 0.6rem 1rem; background: #1e293b; border-left: 3px solid #3b82f6;
              border-radius: 6px; margin-bottom: 0.8rem; }
.app-header h3 { color: #fff; margin: 0; font-size: 1rem; font-weight: 500; }
.app-header p  { color: #94a3b8; margin: 0; font-size: 0.75rem; }
div[data-testid="stButton"] > button {
    padding: 0.25rem 0.75rem !important;
    font-size: 0.78rem !important;
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    border-radius: 4px !important;
}
div[data-testid="stButton"] > button:hover { background: #475569 !important; }
div[data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #1d4ed8 !important;
}
#MainMenu, footer, header { display: none !important; }
.big-number {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 12px;
    padding: 0.5rem 1rem;
    text-align: center;
    border: 1px solid #3b82f6;
}
.big-number h1 { margin: 0; font-size: 2.2rem !important; color: #3b82f6; }
.big-number p { margin: 0; font-size: 0.8rem !important; color: #94a3b8; }
.filtro-titulo { font-size: 0.7rem; color: #94a3b8; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <h3>Fiscalización — Deuda Presunta</h3>
  <p>Sistema de gestión y seguimiento</p>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver"):
        st.switch_page("main.py")

# ── Utilidades generales ──────────────────────────────────────────────────────
def limpiar_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return None if s.lower() in ('', 'nan', 'none', 'null', 'nat') else s

def norm_fecha(v):
    if not v:
        return None
    s = limpiar_str(v)
    if not s:
        return None
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def fmt_fecha(v):
    if not v:
        return ""
    try:
        if isinstance(v, (pd.Timestamp, datetime)):
            return v.strftime('%d/%m/%Y')
        s = str(v).strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', s):
            return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        return s
    except Exception:
        return str(v) if v else ""

def fmt_moneda(v):
    if not v or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        n = float(v)
        if n.is_integer():
            return "${:,.0f}".format(n).replace(",", ".")
        e, d = int(n), int(round((n - int(n)) * 100))
        return "${},{:02d}".format("{:,}".format(e).replace(",", "."), d)
    except Exception:
        return str(v)

def limpiar_entero(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        n = float(v)
        return int(n) if n == int(n) else None
    except Exception:
        return None

def limpiar_para_comparar(texto):
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', str(texto).upper()).strip()

def generar_key_segura(texto):
    return hashlib.md5(texto.encode()).hexdigest()

# ── Normalización de calles ───────────────────────────────────────────────────
REEMPLAZOS_CALLE = [
    (r'(?<![A-Z])H\.(\s*)',      r'HIPOLITO '),
    (r'(?<![A-Z])J\.B\.(\s*)',   r'JB '),
    (r'(?<![A-Z])JB\.(\s*)',     r'JB '),
    (r'(?<![A-Z])GRAL\.(\s*)',   r'GENERAL '),
    (r'(?<![A-Z])GRL\.(\s*)',    r'GENERAL '),
    (r'(?<![A-Z])DR\.(\s*)',     r'DOCTOR '),
    (r'(?<![A-Z])GOB\.(\s*)',    r'GOBERNADOR '),
    (r'(?<![A-Z])PTE\.(\s*)',    r'PRESIDENTE '),
    (r'(?<![A-Z])STA\.(\s*)',    r'SANTA '),
    (r'(?<![A-Z])STO\.(\s*)',    r'SANTO '),
    (r'([A-Z])\.([A-Z])',        r'\1\2'),
    (r'([A-Z])\.',               r'\1'),
    (r'\bYRIGOYEN\b',            'IRIGOYEN'),
    (r'\bSETIEMBRE\b',           'SEPTIEMBRE'),
    (r'\bSTIEMBRE\b',            'SEPTIEMBRE'),
    (r'\bAVENIDA\b',             ''),
    (r'\bAV\b',                  ''),
    (r'\bCALLE\b',               ''),
    (r'\bRUTA\b',                ''),
    (r'\bPASAJE\b',              ''),
    (r'\bBOULEVARD\b',           ''),
    (r'\bBLEVARD\b',             ''),
    (r'\bBLVD\b',                ''),
    (r'C/',                      ''),
]

def normalizar_calle(calle: str) -> str:
    if not calle:
        return ""
    calle = str(calle).upper().strip()
    m_par = re.search(r'\(([^)]+)\)', calle)
    if m_par:
        contenido_par = m_par.group(1).strip()
        exterior = re.sub(r'\(.*?\)', '', calle).strip()
        exterior_limpio = re.sub(r'\b(AV\.?|AVENIDA|CALLE|BLVD\.?|BOULEVARD|PASAJE|RUTA|RP|C/)\b', '', exterior, flags=re.IGNORECASE).strip()
        exterior_limpio = re.sub(r'\s+', ' ', exterior_limpio).strip()
        if re.match(r'^\d*$', exterior_limpio):
            calle = contenido_par
        else:
            calle = exterior.strip()
    for patron, reemplazo in REEMPLAZOS_CALLE:
        calle = re.sub(patron, reemplazo, calle)
    calle = re.sub(r'[^A-ZÁÉÍÓÚÜÑ0-9 ]', '', calle)
    return re.sub(r'\s+', ' ', calle).strip()

# ── Asignación de legajo ──────────────────────────────────────────────────────
def asignar_legajo(localidad, calle, numero, lookup_localidades, lookup_zonas, lookup_sinonimos):
    localidad_cmp = limpiar_para_comparar(localidad)
    if localidad_cmp not in ("MAR DEL PLATA", ""):
        return lookup_localidades.get(localidad_cmp)
    
    calle_norm = normalizar_calle(calle)
    if not calle_norm:
        return None
    
    calle_buscar = calle_norm
    zonas = lookup_zonas.get(calle_buscar, [])
    
    if not zonas and calle_buscar in lookup_sinonimos:
        calle_oficial = lookup_sinonimos[calle_buscar]
        zonas = lookup_zonas.get(calle_oficial, [])
    
    if not zonas:
        return None
    
    try:
        num = int(re.sub(r'\D', '', str(numero)))
    except Exception:
        return None
    
    lado_actual = "PAR" if num % 2 == 0 else "IMPAR"
    
    for zona in zonas:
        lado_db = str(zona['lado']).upper().strip()
        es_mismo_lado = (
            lado_db in ("AMBOS", "A")
            or (lado_actual == "PAR"   and lado_db in ("PAR",   "P"))
            or (lado_actual == "IMPAR" and lado_db in ("IMPAR", "I"))
        )
        try:
            desde = int(zona['desde'])
            hasta = int(zona['hasta'])
        except (TypeError, ValueError):
            continue
        if es_mismo_lado and desde <= num <= hasta:
            return zona['legajo']
    
    return None

# ── Carga de datos ────────────────────────────────────────────────────────────
def cargar_inspectores_localidad():
    r = supabase.table("inspectores_localidad").select("*").execute()
    return r.data if r.data else []

def cargar_zonas_inspectores():
    r = supabase.table("zonas_inspectores").select("*").execute()
    return r.data if r.data else []

def cargar_sinonimos():
    try:
        r = supabase.table("sinonimos_calles").select("*").execute()
        return r.data if r.data else []
    except:
        return []

def construir_lookup_localidades(inspectores_localidad):
    lookup = {}
    for item in inspectores_localidad:
        clave = limpiar_para_comparar(item['localidad'])
        if clave:
            lookup[clave] = item['legajo']
    return lookup

def construir_lookup_zonas(zonas_inspectores):
    lookup = {}
    for zona in zonas_inspectores:
        clave = normalizar_calle(zona.get('calle', ''))
        if not clave:
            continue
        lookup.setdefault(clave, []).append({
            'legajo': zona['legajo'],
            'lado':   zona['lado'],
            'desde':  zona['altura_desde'],
            'hasta':  zona['altura_hasta'],
        })
    return lookup

def construir_lookup_sinonimos(sinonimos):
    lookup = {}
    for sin in sinonimos:
        sinonimo_norm = normalizar_calle(sin.get('sinonimo', ''))
        if sinonimo_norm:
            lookup[sinonimo_norm] = normalizar_calle(sin.get('calle_oficial', ''))
    return lookup

def traer_registros_sin_legajo():
    registros, offset = [], 0
    while True:
        r = supabase.table("padron_deuda_presunta") \
            .select("id, localidad, calle, numero, razon_social, cuit, tel_dom_legal, tel_dom_real") \
            .is_("leg", "null") \
            .range(offset, offset + 999).execute()
        if not r.data:
            break
        registros.extend(r.data)
        offset += 1000
        if len(r.data) < 1000:
            break
    return registros

def guardar_legajos_en_batch(asignaciones, batch_size=100):
    if not asignaciones:
        return 0
    por_legajo = {}
    for a in asignaciones:
        por_legajo.setdefault(a['legajo'], []).append(a['id'])
    total = 0
    for legajo, ids in por_legajo.items():
        for i in range(0, len(ids), batch_size):
            chunk = ids[i:i + batch_size]
            supabase.table("padron_deuda_presunta").update({"leg": legajo}).in_("id", chunk).execute()
            total += len(chunk)
    return total

def get_localidades():
    r = supabase.table("padron_deuda_presunta").select("localidad").execute()
    locs = sorted({x['localidad'] for x in r.data if x.get('localidad')})
    if 'MAR DEL PLATA' in locs:
        locs.remove('MAR DEL PLATA')
        locs = ['MAR DEL PLATA'] + locs
    return locs

def get_pares_existentes():
    todos, offset = [], 0
    while True:
        batch = supabase.table("padron_deuda_presunta") \
                   .select("cuit, ultima_acta") \
                   .range(offset, offset + 999).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += 1000
        if len(batch.data) < 1000:
            break
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

def generar_informe_txt(registros_sin_legajo):
    contenido = []
    contenido.append("=" * 80)
    contenido.append("                    INFORME DE REGISTROS SIN LEGAJO ASIGNADO")
    contenido.append(f"                        Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    contenido.append(f"                        Total de registros: {len(registros_sin_legajo)}")
    contenido.append("=" * 80)
    contenido.append("")
    
    for i in range(0, len(registros_sin_legajo), 2):
        reg_izq = registros_sin_legajo[i]
        contenido.append("┌" + "─" * 78 + "┐")
        contenido.append(f"│ REGISTRO N° {i+1:<70}│")
        contenido.append("├" + "─" * 78 + "┤")
        contenido.append(f"│ LOCALIDAD:     {str(reg_izq.get('localidad', 'N/D')):<61}│")
        contenido.append(f"│ CUIT:          {str(reg_izq.get('cuit', 'N/D')):<61}│")
        contenido.append(f"│ RAZON SOCIAL:  {str(reg_izq.get('razon_social', 'N/D')):<61}│")
        contenido.append(f"│ CALLE:         {str(reg_izq.get('calle', 'N/D'))} {str(reg_izq.get('numero', '')):<61}│")
        contenido.append(f"│ TELEFONO LEGAL:{str(reg_izq.get('tel_dom_legal', 'N/D')):<61}│")
        contenido.append(f"│ TELEFONO REAL: {str(reg_izq.get('tel_dom_real', 'N/D')):<61}│")
        
        if i + 1 < len(registros_sin_legajo):
            reg_der = registros_sin_legajo[i + 1]
            contenido.append("├" + "─" * 78 + "┤")
            contenido.append(f"│ REGISTRO N° {i+2:<70}│")
            contenido.append("├" + "─" * 78 + "┤")
            contenido.append(f"│ LOCALIDAD:     {str(reg_der.get('localidad', 'N/D')):<61}│")
            contenido.append(f"│ CUIT:          {str(reg_der.get('cuit', 'N/D')):<61}│")
            contenido.append(f"│ RAZON SOCIAL:  {str(reg_der.get('razon_social', 'N/D')):<61}│")
            contenido.append(f"│ CALLE:         {str(reg_der.get('calle', 'N/D'))} {str(reg_der.get('numero', '')):<61}│")
            contenido.append(f"│ TELEFONO LEGAL:{str(reg_der.get('tel_dom_legal', 'N/D')):<61}│")
            contenido.append(f"│ TELEFONO REAL: {str(reg_der.get('tel_dom_real', 'N/D')):<61}│")
            contenido.append("└" + "─" * 78 + "┘")
        else:
            contenido.append("└" + "─" * 78 + "┘")
        contenido.append("")
    
    contenido.append("=" * 80)
    contenido.append("                        FIN DEL INFORME")
    contenido.append("=" * 80)
    
    return "\n".join(contenido)

# ── Mapeo Excel ───────────────────────────────────────────────────────────────
COLS_EXCEL = [
    "DELEGACION","LOCALIDAD","CUIT","RAZON SOCIAL","DEUDA PRESUNTA",
    "CP","CALLE","NUMERO","PISO","DPTO","FECHARELDEPENDENCIA",
    "EMAIL","TEL_DOM_LEGAL","TEL_DOM_REAL","ULTIMA ACTA","DESDE",
    "HASTA","DETECTADO","ESTADO","FECHA_PAGO_OBL",
    "EMPL 10-2025","EMP 11-2025","EMPL 12-2025","ACTIVIDAD","SITUACION",
]
MAPA = {
    "DELEGACION":"delegacion","LOCALIDAD":"localidad","CUIT":"cuit",
    "RAZON SOCIAL":"razon_social","DEUDA PRESUNTA":"deuda_presunta",
    "CP":"cp","CALLE":"calle","NUMERO":"numero","PISO":"piso","DPTO":"dpto",
    "FECHARELDEPENDENCIA":"fechareldependencia","EMAIL":"email",
    "TEL_DOM_LEGAL":"tel_dom_legal","TEL_DOM_REAL":"tel_dom_real",
    "ULTIMA ACTA":"ultima_acta","DESDE":"desde","HASTA":"hasta",
    "DETECTADO":"detectado","ESTADO":"estado","FECHA_PAGO_OBL":"fecha_pago_obl",
    "EMPL 10-2025":"empl_10_2025","EMP 11-2025":"emp_11_2025","EMPL 12-2025":"empl_12_2025",
    "ACTIVIDAD":"actividad","SITUACION":"situacion",
}
COLS_FECHA  = {"fechareldependencia","desde","hasta","fecha_pago_obl"}
COLS_MONEDA = {"deuda_presunta","detectado"}

def procesar_excel(archivo):
    engine = 'xlrd' if archivo.name.endswith('.xls') else 'openpyxl'
    df = pd.read_excel(archivo, engine=engine, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    faltantes = [c for c in COLS_EXCEL if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    df = df[COLS_EXCEL].rename(columns=MAPA)
    out = []
    for _, fila in df.iterrows():
        r = {}
        for col in MAPA.values():
            v = fila.get(col)
            v = None if pd.isna(v) else limpiar_str(v)
            if col in COLS_FECHA and v:
                v = norm_fecha(v)
            if col in COLS_MONEDA and v:
                try:
                    v = fmt_moneda(float(v))
                except Exception:
                    pass
            if col == "ultima_acta" and not v:
                v = "*"
            r[col] = v
        out.append(r)
    return out

# ── Pestañas ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Cargar Padrón",
    "✏️ Editar Legajos y Vtos",
    "📧 Solicitar Actas",
    "📋 Subir Actas",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — Cargar Padrón
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Cargar Padrón de Deuda Presunta")
    archivo = st.file_uploader("Archivo Excel", type=["xls","xlsx"], key="upload_padron")

    if archivo:
        st.caption(f"Archivo: **{archivo.name}**")
        try:
            registros = procesar_excel(archivo)
            hoy = date.today().isoformat()
            for r in registros:
                r.update({'leg':None,'vto':None,'mail_enviado':'NO','acta':None,
                           'fecha_carga':hoy,'estado_gestion':'PENDIENTE'})

            pares = get_pares_existentes()
            nuevos = [r for r in registros
                      if (str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) not in pares]
            dupl = len(registros) - len(nuevos)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(registros))
            c2.metric("Nuevos", len(nuevos))
            c3.metric("Duplicados", dupl)

            if nuevos:
                if st.button("✅ Confirmar carga", type="primary"):
                    with st.spinner("Insertando..."):
                        n = 0
                        for i in range(0, len(nuevos), 100):
                            res = supabase.table("padron_deuda_presunta").insert(nuevos[i:i+100]).execute()
                            n += len(res.data)
                    st.success(f"✅ {n} registros insertados.")
            else:
                st.warning("⚠️ No hay registros nuevos.")
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos (VERSIÓN CON TABLA TOTALMENTE EDITABLE)
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Editar Legajos y Fechas de Vencimiento")

    total_general = supabase.table("padron_deuda_presunta").select("id", count="exact").execute().count
    con_legajo    = supabase.table("padron_deuda_presunta").select("id", count="exact").not_.is_("leg", "null").execute().count
    sin_legajo_total = total_general - con_legajo

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f'<div class="big-number"><h1>{total_general}</h1><p>TOTAL</p></div>', unsafe_allow_html=True)
    with col_t2:
        st.markdown(f'<div class="big-number"><h1>{con_legajo}</h1><p>CON LEGAJO</p></div>', unsafe_allow_html=True)
    with col_t3:
        st.markdown(f'<div class="big-number"><h1>{sin_legajo_total}</h1><p>SIN LEGAJO</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("🗑 Eliminar seleccionados"):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                st.rerun()
    with col2:
        if st.button("🗑 Eliminar TODO"):
            st.session_state.confirmar_del_todo = True
    with col3:
        if st.button("🤖 Asignar Legajos"):
            st.session_state.asignar_legajos = True
    with col4:
        if st.button("🔍 Buscar calles sin asociar"):
            st.session_state.buscar_sinonimos = True
    with col5:
        if st.button("📄 INFORME NO ASIGNADOS"):
            st.session_state.generar_informe = True
    with col6:
        if st.button("↺ Resetear filtros"):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
    with col7:
        if st.button("⟳ Recargar"):
            st.rerun()

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, eliminar todo"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                st.rerun()
        with col_no:
            if st.button("Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    # ── Generar informe TXT ─────────────────────────────────────────────────
    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe de no asignados..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(
                    label="📥 DESCARGAR INFORME (TXT)",
                    data=contenido_txt.encode('utf-8'),
                    file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_informe"
                )
                st.info(f"📊 Se encontraron {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo para exportar")
        st.session_state.generar_informe = False

    # ── Asignación automática de legajos ─────────────────────────────────
    if st.session_state.get('asignar_legajos'):
        st.info("⏳ INICIANDO ASIGNACIÓN DE LEGAJOS... Esto puede tomar unos minutos.")
        
        with st.spinner("Cargando tablas de inspectores..."):
            insp_loc   = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos  = cargar_sinonimos()
            lkp_loc    = construir_lookup_localidades(insp_loc)
            lkp_zonas  = construir_lookup_zonas(insp_zonas)
            lkp_sin    = construir_lookup_sinonimos(sinonimos)

        with st.spinner("Cargando registros sin legajo..."):
            registros = traer_registros_sin_legajo()

        if not registros:
            st.info("No hay registros sin legajo.")
            st.session_state.asignar_legajos = False
        else:
            total = len(registros)
            progress_bar = st.progress(0)
            status_text = st.empty()
            asig = []
            no_asig = []

            for i, reg in enumerate(registros):
                percent = (i + 1) / total
                progress_bar.progress(percent)
                status_text.markdown(f"🔄 Progreso: {int(percent * 100)}% - {reg.get('razon_social', 'Sin nombre')[:40]}...")
                
                legajo = asignar_legajo(
                    reg.get('localidad', '') or '',
                    reg.get('calle', '') or '',
                    reg.get('numero', '') or '',
                    lkp_loc, lkp_zonas, lkp_sin
                )
                
                if legajo:
                    asig.append({'id': reg['id'], 'legajo': legajo})
                else:
                    no_asig.append({
                        'id': reg['id'],
                        'localidad': reg.get('localidad', ''),
                        'calle': reg.get('calle', ''),
                        'numero': reg.get('numero', ''),
                        'razon_social': reg.get('razon_social', ''),
                        'cuit': reg.get('cuit', ''),
                        'tel_dom_legal': reg.get('tel_dom_legal', ''),
                        'tel_dom_real': reg.get('tel_dom_real', ''),
                    })
                
                time.sleep(0.01)

            progress_bar.empty()
            status_text.empty()

            with st.spinner("Guardando legajos..."):
                guardados = guardar_legajos_en_batch(asig)

            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {
                "asignados": guardados,
                "no_asignados": len(no_asig),
                "detalle": no_asig,
            }
            st.success(f"✅ ASIGNACIÓN COMPLETADA: {guardados} legajos asignados, {len(no_asig)} sin coincidencia.")
            st.rerun()

    # ── Buscar calles sin asociar ──────────────────────────────────────────
    if st.session_state.get('buscar_sinonimos'):
        with st.spinner("Analizando calles de Mar del Plata..."):
            calles_oficiales = supabase.table("zonas_inspectores").select("calle").execute()
            calles_oficiales_set = set([normalizar_calle(c['calle']) for c in calles_oficiales.data]) if calles_oficiales.data else set()
            
            sinonimos_existentes = supabase.table("sinonimos_calles").select("sinonimo").execute()
            sinonimos_set = set([normalizar_calle(s['sinonimo']) for s in sinonimos_existentes.data]) if sinonimos_existentes.data else set()
            
            registros_mdq = supabase.table("padron_deuda_presunta")\
                .select("calle")\
                .eq("localidad", "MAR DEL PLATA")\
                .execute()
            
            calles_en_padron = set()
            for r in registros_mdq.data:
                calle_norm = normalizar_calle(r.get('calle', ''))
                if calle_norm:
                    calles_en_padron.add(calle_norm)
            
            calles_sin_asociar = []
            for calle in calles_en_padron:
                if calle not in calles_oficiales_set and calle not in sinonimos_set:
                    calles_sin_asociar.append(calle)
            
            if not calles_sin_asociar:
                st.success("✅ Todas las calles de Mar del Plata están correctamente asociadas")
                st.session_state.buscar_sinonimos = False
            else:
                st.warning(f"🔍 Se encontraron {len(calles_sin_asociar)} calles únicas sin asociar")
                
                for calle_problema in sorted(calles_sin_asociar):
                    key_segura = generar_key_segura(calle_problema)
                    
                    with st.container():
                        st.markdown(f"**Calle en el padrón:** `{calle_problema}`")
                        
                        coincidencias = []
                        for oficial in calles_oficiales_set:
                            ratio = difflib.SequenceMatcher(None, calle_problema, oficial).ratio()
                            if ratio > 0.6:
                                coincidencias.append((oficial, ratio))
                        
                        coincidencias.sort(key=lambda x: x[1], reverse=True)
                        
                        if coincidencias:
                            st.markdown("**Posibles coincidencias:**")
                            cols = st.columns(min(len(coincidencias) + 1, 4))
                            for i, (oficial, ratio) in enumerate(coincidencias[:3]):
                                porcentaje = int(ratio * 100)
                                if cols[i].button(f"✅ Asociar a '{oficial}' ({porcentaje}%)", key=f"asoc_{key_segura}_{i}"):
                                    try:
                                        supabase.table("sinonimos_calles").insert({
                                            "calle_oficial": oficial,
                                            "sinonimo": calle_problema,
                                            "creado_por": "auto_detectado"
                                        }).execute()
                                        st.success(f"Sinónimo guardado: {calle_problema} → {oficial}")
                                        st.rerun()
                                    except Exception as e:
                                        if "duplicate" in str(e).lower():
                                            st.warning("Este sinónimo ya existe")
                                        else:
                                            st.error(f"Error: {e}")
                            
                            idx_manual = min(len(coincidencias), 3)
                            if cols[idx_manual].button("✏️ Asociar manualmente", key=f"manual_{key_segura}"):
                                st.session_state[f"manual_{key_segura}"] = calle_problema
                        else:
                            st.info("No se encontraron coincidencias automáticas")
                            if st.button("✏️ Asociar manualmente", key=f"manual2_{key_segura}"):
                                st.session_state[f"manual_{key_segura}"] = calle_problema
                        
                        if st.session_state.get(f"manual_{key_segura}"):
                            with st.form(key=f"form_manual_{key_segura}"):
                                oficial_manual = st.selectbox("Seleccionar calle oficial", options=sorted(calles_oficiales_set))
                                if st.form_submit_button("Guardar asociación"):
                                    try:
                                        supabase.table("sinonimos_calles").insert({
                                            "calle_oficial": oficial_manual,
                                            "sinonimo": calle_problema,
                                            "creado_por": "usuario"
                                        }).execute()
                                        st.success(f"Sinónimo guardado manualmente")
                                        del st.session_state[f"manual_{key_segura}"]
                                        st.rerun()
                                    except Exception as e:
                                        if "duplicate" in str(e).lower():
                                            st.warning("Este sinónimo ya existe")
                                        else:
                                            st.error(f"Error: {e}")
                            
                            if st.button("Cancelar", key=f"cancel_{key_segura}"):
                                del st.session_state[f"manual_{key_segura}"]
                                st.rerun()
                        
                        st.markdown("---")
                
                if st.button("Cerrar búsqueda", key="cerrar_busqueda"):
                    st.session_state.buscar_sinonimos = False
                    st.rerun()

    if st.session_state.get('ultima_asignacion'):
        res = st.session_state.ultima_asignacion
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.success(f"✅ {res['asignados']} legajos asignados")
        with col_res2:
            st.warning(f"⚠️ {res['no_asignados']} registros sin coincidencia")
        
        if res['no_asignados'] > 0:
            contenido_informe = generar_informe_txt(res['detalle'])
            st.download_button(
                label="📥 DESCARGAR INFORME DE NO ASIGNADOS",
                data=contenido_informe.encode('utf-8'),
                file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_no_asignados"
            )
            
            with st.expander(f"📋 Ver detalle de {res['no_asignados']} registros sin legajo"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    st.markdown("---")

    # ── Filtros ───────────────────────────────────────────────────────────
    st.markdown("### 📋 Filtros de búsqueda")
    
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1:
        st.markdown('<p class="filtro-titulo">CUIT</p>', unsafe_allow_html=True)
        filtro_cuit = st.text_input("CUIT", key="input_filtro_cuit", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with f2:
        st.markdown('<p class="filtro-titulo">RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon = st.text_input("Razón", key="input_filtro_razon", placeholder="Razón social", label_visibility="collapsed")
    with f3:
        st.markdown('<p class="filtro-titulo">LOCALIDAD</p>', unsafe_allow_html=True)
        locs = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with f4:
        st.markdown('<p class="filtro-titulo">MAIL ENVIADO</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with f5:
        st.markdown('<p class="filtro-titulo">LEGAJO</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with f6:
        st.markdown('<p class="filtro-titulo">CALLE (APROXIMACIÓN)</p>', unsafe_allow_html=True)
        filtro_calle_aprox = st.text_input("Calle", key="filtro_calle_aproximacion", placeholder="Ej: Yrigoyen, Colon...", label_visibility="collapsed")

    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")

    datos = q.execute()

    if not datos.data:
        st.info("Sin datos.")
    else:
        df = pd.DataFrame(datos.data)
        if filtro_cuit:
            df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
        if filtro_razon:
            df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
        if filtro_leg == "CON LEGAJO":
            df = df[df['leg'].notna()]
        elif filtro_leg == "SIN LEGAJO":
            df = df[df['leg'].isna()]
        
        if filtro_calle_aprox:
            filtro_norm = normalizar_calle(filtro_calle_aprox)
            if filtro_norm:
                df['calle_norm'] = df['calle'].apply(lambda x: normalizar_calle(str(x)) if x else "")
                df['similitud'] = df['calle_norm'].apply(lambda x: difflib.SequenceMatcher(None, filtro_norm, x).ratio() if x else 0)
                df = df[df['similitud'] > 0.4].sort_values('similitud', ascending=False)
                df = df.drop(columns=['calle_norm', 'similitud'])

        total = len(df)
        RPP = 300
        pages = max(1, (total + RPP - 1) // RPP)

        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

        pa, pn, ps = st.columns([1, 3, 1])
        with pa:
            if st.button("◀ ANTERIOR") and st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
                st.rerun()
        with pn:
            st.caption(f"📄 Página {st.session_state.pagina_actual} / {pages} | {total} registros totales")
        with ps:
            if st.button("SIGUIENTE ▶") and st.session_state.pagina_actual < pages:
                st.session_state.pagina_actual += 1
                st.rerun()

        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        # ==================== CLAVE: CONVERTIR TODO A STRING ====================
        # Esto evita TODOS los errores de tipos en el data_editor
        for col in df_p.columns:
            df_p[col] = df_p[col].apply(lambda x: "" if pd.isna(x) else str(x))
        
        # Formatear fechas para mostrar bonito (solo visual)
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(lambda x: fmt_fecha(x) if x and x != "" else "")
        # =======================================================================

        # Renombrar columnas para la tabla
        df_orig = df_p.copy()
        df_ed = df_p.rename(columns={
            'id':'ID','delegacion':'DELEGACION','localidad':'LOCALIDAD','cuit':'CUIT',
            'razon_social':'RAZON SOCIAL','deuda_presunta':'DEUDA PRESUNTA','cp':'CP',
            'calle':'CALLE','numero':'NUMERO','piso':'PISO','dpto':'DPTO',
            'fechareldependencia':'FECHARELDEPENDENCIA','email':'EMAIL',
            'tel_dom_legal':'TEL_DOM_LEGAL','tel_dom_real':'TEL_DOM_REAL',
            'ultima_acta':'ULTIMA ACTA','desde':'DESDE','hasta':'HASTA',
            'detectado':'DETECTADO','estado':'ESTADO','fecha_pago_obl':'FECHA PAGO OBL',
            'empl_10_2025':'EMPL 10-2025','emp_11_2025':'EMP 11-2025','empl_12_2025':'EMPL 12-2025',
            'actividad':'ACTIVIDAD','situacion':'SITUACION',
            'leg':'LEG','vto':'VTO','mail_enviado':'MAIL ENVIADO',
            'acta':'ACTA','estado_gestion':'ESTADO GESTION',
        })
        df_ed.insert(0, "🗑️", False)

        if st.checkbox("Seleccionar todos (página actual)"):
            df_ed["🗑️"] = True

        # TABLA COMPLETAMENTE EDITABLE (todas las columnas)
        edited = st.data_editor(
            df_ed, use_container_width=True, height=550,
            column_config={"🗑️": st.column_config.CheckboxColumn("Elim.")},
            key=f"editor_{st.session_state.pagina_actual}",
        )

        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel

        # ==================== GUARDAR CAMBIOS CON CONVERSIÓN DE TIPOS ====================
        if st.button("💾 GUARDAR CAMBIOS", type="primary"):
            mods = 0
            with st.spinner("Guardando cambios..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd = {}
                    
                    # Mapeo de columnas editables a campos de la base de datos
                    mapeo = {
                        'LEG': 'leg',
                        'VTO': 'vto',
                        'MAIL ENVIADO': 'mail_enviado',
                        'ACTA': 'acta',
                        'ESTADO GESTION': 'estado_gestion',
                        'LOCALIDAD': 'localidad',
                        'CUIT': 'cuit',
                        'RAZON SOCIAL': 'razon_social',
                        'CALLE': 'calle',
                        'NUMERO': 'numero',
                        'PISO': 'piso',
                        'DPTO': 'dpto',
                        'TEL_DOM_LEGAL': 'tel_dom_legal',
                        'TEL_DOM_REAL': 'tel_dom_real',
                        'EMAIL': 'email',
                        'ULTIMA ACTA': 'ultima_acta',
                        'DEUDA PRESUNTA': 'deuda_presunta',
                        'DETECTADO': 'detectado',
                    }
                    
                    for col_mostrada, campo_db in mapeo.items():
                        if col_mostrada in row.index and col_mostrada in orig.index:
                            valor_nuevo = row.get(col_mostrada)
                            valor_original = orig.get(col_mostrada)
                            
                            # Normalizar (string vacío = None)
                            if valor_nuevo == "" or valor_nuevo is None:
                                valor_nuevo = None
                            if valor_original == "" or valor_original is None:
                                valor_original = None
                            
                            # Si cambió, procesar según el tipo de campo
                            if valor_nuevo != valor_original:
                                # Para fechas
                                if campo_db in ['vto', 'fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl']:
                                    if valor_nuevo:
                                        valor_nuevo = norm_fecha(str(valor_nuevo))
                                    else:
                                        valor_nuevo = None
                                # Para números (legajo, numero)
                                elif campo_db in ['leg', 'numero']:
                                    if valor_nuevo and str(valor_nuevo).strip():
                                        try:
                                            valor_nuevo = int(float(str(valor_nuevo)))
                                        except:
                                            valor_nuevo = None
                                    else:
                                        valor_nuevo = None
                                # Para mail enviado (SI/NO)
                                elif campo_db == 'mail_enviado':
                                    valor_nuevo = 'SI' if str(valor_nuevo).upper() == 'SI' else 'NO'
                                # Para el resto, texto plano
                                else:
                                    valor_nuevo = limpiar_str(str(valor_nuevo)) if valor_nuevo else None
                                
                                upd[campo_db] = valor_nuevo
                    
                    if upd:
                        supabase.table("padron_deuda_presunta").update(upd).eq("id", row['ID']).execute()
                        mods += 1

            if mods:
                st.success(f"✅ {mods} registros actualizados.")
                st.rerun()
        # ===================================================================================

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Solicitar Actas
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.info("📧 Solicitar Actas — En construcción")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Subir Actas
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.info("📋 Subir Actas — En construcción")
