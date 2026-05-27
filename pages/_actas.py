import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
import difflib
import hashlib
import time
import io

# ── CONFIGURACIÓN INICIAL ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🔍"
)

# ── ESTILOS MODERNOS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.35rem; font-weight: 600; }
    .main-header p { color: #94a3b8; margin: 0; font-size: 0.78rem; }

    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 0.6rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
    }
    .kpi-card h1 { font-size: 2.4rem !important; font-weight: 700; margin: 0.1rem 0 0.3rem 0; line-height: 1; }
    .kpi-card p { font-size: 0.95rem !important; font-weight: 500; margin: 0; color: #334155; }
    .kpi-card .kpi-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }

    .kpi-total h1 { color: #3b82f6; }
    .kpi-con-legajo h1 { color: #10b981; }
    .kpi-sin-legajo h1 { color: #f59e0b; }
    .kpi-pendiente h1 { color: #ef4444; }
    .kpi-mail h1 { color: #f97316; }
    .kpi-finalizado h1 { color: #10b981; }

    .inspector-card {
        background: white;
        border-radius: 10px;
        padding: 0.8rem 0.4rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .inspector-card:hover { transform: translateY(-2px); border-color: #10b981; }
    .inspector-card h3 { font-size: 0.95rem !important; color: #10b981; margin: 0 0 0.3rem 0; font-weight: 600; }
    .inspector-card h1 { font-size: 1.65rem !important; font-weight: 700; color: #1e293b; margin: 0.1rem 0; }
    .inspector-card p { font-size: 0.85rem !important; color: #475569; margin: 0; }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton > button[kind="secondary"] { background: #10b981 !important; color: white !important; }
    .stButton > button[kind="secondary"]:hover { background: #059669 !important; }
    .stButton > button[kind="primary"] { background: #3b82f6 !important; color: white !important; }
    .stButton > button[kind="primary"]:hover { background: #2563eb !important; }

    /* Botón de eliminar cancelados - ROJO LLAMATIVO */
    .stButton > button[kind="danger"] {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3) !important;
    }
    .stButton > button[kind="danger"]:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4) !important;
    }

    .buscar-btn button { background: #3b82f6 !important; font-size: 0.9rem !important; padding: 0.4rem 1rem !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        background: #f1f5f9;
        padding: 0.4rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.4rem 1rem;
        transition: all 0.2s;
        color: #334155;
    }
    .stTabs [data-baseweb="tab"]:hover { background: #e2e8f0; }
    .stTabs [aria-selected="true"] { background: #3b82f6 !important; color: white !important; }

    .streamlit-expanderHeader {
        background: #f1f5f9 !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderHeader:hover { border-color: #3b82f6 !important; }

    .stDataEditor { border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0; }
    .filtro-titulo { font-size: 0.65rem; color: #64748b; margin-bottom: 0.2rem; letter-spacing: 0.3px; }
    hr { margin: 1rem 0; border-color: #e2e8f0; }

    div[role="dialog"] {
        background: white !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }
    div[role="dialog"] .stMarkdown p, div[role="dialog"] label { color: #1e293b !important; }
    div[role="dialog"] button[aria-label="Close"] { opacity: 0 !important; pointer-events: none !important; }

    .stDataFrame { background: white; }
    #MainMenu, footer, header { display: none !important; }
    
    .ficha-edicion {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
    }
    .ficha-titulo {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    .campo-label {
        font-size: 0.65rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 Fiscalización · Deuda Presunta</h1>
    <p>Sistema de Gestión y Seguimiento | OSECAC</p>
</div>
""", unsafe_allow_html=True)

# ── Conexión Supabase ───────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Utilidades ──────────────────────────────────────────────────────────────
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
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    if s.isdigit():
        try:
            fecha = datetime(1899, 12, 30) + pd.Timedelta(days=int(s))
            return fecha.strftime('%Y-%m-%d')
        except:
            pass
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
    (r'(?<![A-Z])H\.(\s*)', r'HIPOLITO '),
    (r'(?<![A-Z])J\.B\.(\s*)', r'JB '),
    (r'(?<![A-Z])JB\.(\s*)', r'JB '),
    (r'(?<![A-Z])GRAL\.(\s*)', r'GENERAL '),
    (r'(?<![A-Z])GRL\.(\s*)', r'GENERAL '),
    (r'(?<![A-Z])DR\.(\s*)', r'DOCTOR '),
    (r'(?<![A-Z])GOB\.(\s*)', r'GOBERNADOR '),
    (r'(?<![A-Z])PTE\.(\s*)', r'PRESIDENTE '),
    (r'(?<![A-Z])STA\.(\s*)', r'SANTA '),
    (r'(?<![A-Z])STO\.(\s*)', r'SANTO '),
    (r'([A-Z])\.([A-Z])', r'\1\2'),
    (r'([A-Z])\.', r'\1'),
    (r'\bYRIGOYEN\b', 'IRIGOYEN'),
    (r'\bSETIEMBRE\b', 'SEPTIEMBRE'),
    (r'\bSTIEMBRE\b', 'SEPTIEMBRE'),
    (r'\bAVENIDA\b', ''),
    (r'\bAV\b', ''),
    (r'\bCALLE\b', ''),
    (r'\bRUTA\b', ''),
    (r'\bPASAJE\b', ''),
    (r'\bBOULEVARD\b', ''),
    (r'\bBLEVARD\b', ''),
    (r'\bBLVD\b', ''),
    (r'C/', ''),
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

# ── Palabras ancla ───────────────────────────────────────────────────────────
def cargar_palabras_ancla():
    try:
        r = supabase.table("palabras_ancla").select("*").execute()
        return r.data if r.data else []
    except:
        return []

def construir_lookup_palabras_ancla(palabras_ancla):
    return palabras_ancla

def asignar_legajo(localidad, calle, numero, lookup_localidades, lookup_zonas, lookup_sinonimos, lookup_palabras_ancla):
    localidad_cmp = limpiar_para_comparar(localidad)
    if localidad_cmp not in ("MAR DEL PLATA", ""):
        return lookup_localidades.get(localidad_cmp)
    if localidad_cmp == "MAR DEL PLATA" and lookup_palabras_ancla:
        direccion_completa = f"{calle} {numero}".upper().strip()
        for ancla in lookup_palabras_ancla:
            palabra = ancla.get('palabra', '').upper().strip()
            legajo_ancla = ancla.get('legajo')
            if palabra and legajo_ancla and palabra in direccion_completa:
                return legajo_ancla
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
    except:
        return None
    lado_actual = "PAR" if num % 2 == 0 else "IMPAR"
    for zona in zonas:
        lado_db = str(zona['lado']).upper().strip()
        es_mismo_lado = (lado_db in ("AMBOS", "A") or (lado_actual == "PAR" and lado_db in ("PAR", "P")) or (lado_actual == "IMPAR" and lado_db in ("IMPAR", "I")))
        try:
            desde = int(zona['desde'])
            hasta = int(zona['hasta'])
        except:
            continue
        if es_mismo_lado and desde <= num <= hasta:
            return zona['legajo']
    return None

# ── Carga de datos ───────────────────────────────────────────────────────────
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
            'lado': zona['lado'],
            'desde': zona['altura_desde'],
            'hasta': zona['altura_hasta'],
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
        r = supabase.table("padron_deuda_presunta").select("id, localidad, calle, numero, razon_social, cuit, tel_dom_legal, tel_dom_real").is_("leg", "null").range(offset, offset + 999).execute()
        if not r.data:
            break
        registros.extend(r.data)
        offset += 1000
        if len(r.data) < 1000:
            break
    return registros

def traer_registros_con_legajo():
    registros, offset = [], 0
    while True:
        r = supabase.table("padron_deuda_presunta").select("*").not_.is_("leg", "null").range(offset, offset + 999).execute()
        if not r.data:
            break
        registros.extend(r.data)
        offset += 1000
        if len(r.data) < 1000:
            break
    return registros

def traer_registros_por_inspector(legajo):
    registros, offset = [], 0
    while True:
        r = supabase.table("padron_deuda_presunta").select("*").eq("leg", legajo).range(offset, offset + 999).execute()
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
        batch = supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").range(offset, offset + 999).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += 1000
        if len(batch.data) < 1000:
            break
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

# ── FUNCIÓN PARA ELIMINAR REGISTROS CANCELADOS ────────────────────────────────
def eliminar_registros_cancelados():
    """Obtiene los registros cancelados, descarga Excel y los elimina"""
    registros = supabase.table("padron_deuda_presunta").select("*").eq("deuda_cancelada", True).execute()
    if not registros.data:
        st.warning("⚠️ No hay registros con deuda cancelada para eliminar.")
        return None
    df_cancelados = pd.DataFrame(registros.data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_cancelados.to_excel(writer, sheet_name='Cancelados', index=False)
    excel_data = output.getvalue()
    ids_a_eliminar = [r['id'] for r in registros.data]
    supabase.table("padron_deuda_presunta").delete().in_("id", ids_a_eliminar).execute()
    return excel_data, len(ids_a_eliminar)

# ── UNA SOLA QUERY para todos los conteos del dashboard ─────────────────────
@st.cache_data(ttl=60)
def get_dashboard_stats():
    try:
        r = supabase.rpc("get_dashboard_stats").execute()
        return r.data if r.data else {}
    except Exception as e:
        return {}

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

def generar_excel_para_mailing(df_seleccionado, fecha_vto_str):
    df_export = pd.DataFrame()
    df_export['CUIT'] = df_seleccionado['cuit'].astype(str)
    df_export['RAZON SOCIAL'] = df_seleccionado['razon_social'].astype(str)
    df_export['LEGAJO'] = df_seleccionado['leg'].astype(str)
    df_export['VTO ASIGNADO'] = fecha_vto_str
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Mailing', index=False)
        worksheet = writer.sheets['Mailing']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    return output.getvalue()

def generar_excel_asignados(registros):
    df = pd.DataFrame(registros)
    columnas = ['id', 'cuit', 'razon_social', 'localidad', 'calle', 'numero', 'leg', 'vto', 'mail_enviado', 'acta', 'estado_gestion', 'tel_dom_legal', 'tel_dom_real', 'email']
    df_excel = df[[c for c in columnas if c in df.columns]]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel.to_excel(writer, sheet_name='Seleccionados', index=False)
    return output.getvalue()

def generar_excel_por_inspector():
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for ins in inspectores.data:
            registros = traer_registros_por_inspector(ins['legajo'])
            if registros:
                df = pd.DataFrame(registros)
                columnas = ['id', 'cuit', 'razon_social', 'localidad', 'calle', 'numero', 'vto', 'mail_enviado', 'acta', 'estado_gestion', 'tel_dom_legal', 'tel_dom_real', 'email']
                df_excel = df[[c for c in columnas if c in df.columns]]
                nombre_hoja = f"{ins['nombre'].split(',')[0][:20]} {ins['legajo']}"
                df_excel.to_excel(writer, sheet_name=nombre_hoja, index=False)
    return output.getvalue()

# ── Mapeo Excel ───────────────────────────────────────────────────────────────
COLS_EXCEL = [
    "DELEGACION","LOCALIDAD","CUIT","RAZON SOCIAL","DEUDA PRESUNTA","CP","CALLE","NUMERO","PISO","DPTO","FECHARELDEPENDENCIA","EMAIL","TEL_DOM_LEGAL","TEL_DOM_REAL","ULTIMA ACTA","DESDE","HASTA","DETECTADO","ESTADO","FECHA_PAGO_OBL","EMPL 10-2025","EMP 11-2025","EMPL 12-2025","ACTIVIDAD","SITUACION",
]
MAPA = {
    "DELEGACION":"delegacion","LOCALIDAD":"localidad","CUIT":"cuit","RAZON SOCIAL":"razon_social","DEUDA PRESUNTA":"deuda_presunta","CP":"cp","CALLE":"calle","NUMERO":"numero","PISO":"piso","DPTO":"dpto","FECHARELDEPENDENCIA":"fechareldependencia","EMAIL":"email","TEL_DOM_LEGAL":"tel_dom_legal","TEL_DOM_REAL":"tel_dom_real","ULTIMA ACTA":"ultima_acta","DESDE":"desde","HASTA":"hasta","DETECTADO":"detectado","ESTADO":"estado","FECHA_PAGO_OBL":"fecha_pago_obl","EMPL 10-2025":"empl_10_2025","EMP 11-2025":"emp_11_2025","EMPL 12-2025":"empl_12_2025","ACTIVIDAD":"actividad","SITUACION":"situacion",
}
COLS_FECHA = {"fechareldependencia","desde","hasta","fecha_pago_obl"}
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
                except:
                    pass
            if col == "ultima_acta" and not v:
                v = "*"
            r[col] = v
        out.append(r)
    return out

# ══════════════════════════════════════════════════════════════════
# TABS (6 pestañas)
# ══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📤 Cargar Padrón",
    "✏️ Gestionar Registros",
    "📋 Subir Actas",
    "✏️ Editar Registro",
    "📧 Generar Informe",
    "👥 Inspectores"
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
                r.update({'leg':None,'vto':None,'mail_enviado':'NO','acta':None, 'fecha_carga':hoy,'estado_gestion':'PENDIENTE', 'deuda_cancelada':False})
            pares = get_pares_existentes()
            nuevos = [r for r in registros if (str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) not in pares]
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
                    get_dashboard_stats.clear()
            else:
                st.warning("⚠️ No hay registros nuevos.")
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Gestionar Registros (con filtro de estado)
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Gestionar Legajos y Fechas de Vencimiento")

    stats = get_dashboard_stats()

    total_general       = stats.get('total', 0) or 0
    con_legajo          = stats.get('con_legajo', 0) or 0
    sin_legajo_total    = total_general - con_legajo
    pendientes_sin_mail = stats.get('sin_mail', 0) or 0
    pendientes_con_mail = stats.get('con_mail', 0) or 0
    finalizados         = stats.get('finalizados', 0) or 0
    por_inspector       = stats.get('por_inspector') or {}

    with st.expander("📊 CONTEO DE REGISTROS", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="kpi-card kpi-total"><div class="kpi-icon">📊</div><h1>{total_general:,}</h1><p>TOTAL REGISTROS</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="kpi-card kpi-con-legajo"><div class="kpi-icon">✅</div><h1>{con_legajo:,}</h1><p>CON LEGAJO</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="kpi-card kpi-sin-legajo"><div class="kpi-icon">⚠️</div><h1>{sin_legajo_total:,}</h1><p>SIN LEGAJO</p></div>""", unsafe_allow_html=True)

    with st.expander("🔄 ESTADO DE REGISTROS", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="kpi-card kpi-pendiente"><div class="kpi-icon">📧</div><h1>{pendientes_sin_mail:,}</h1><p>PENDIENTES (sin mail)</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="kpi-card kpi-mail"><div class="kpi-icon">📨</div><h1>{pendientes_con_mail:,}</h1><p>MAIL ENVIADO</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="kpi-card kpi-finalizado"><div class="kpi-icon">🏁</div><h1>{finalizados:,}</h1><p>FINALIZADOS</p></div>""", unsafe_allow_html=True)

    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        with st.expander("👥 EMPRESAS POR INSPECTOR", expanded=False):
            cols = st.columns(len(inspectores.data))
            for idx, ins in enumerate(inspectores.data):
                count = por_inspector.get(str(ins['legajo']), 0)
                nombre_corto = ins['nombre'].split(',')[0]
                with cols[idx]:
                    st.markdown(f"""<div class="inspector-card"><h3>{nombre_corto}</h3><h1>{count}</h1><p>Legajo: {ins['legajo']}</p></div>""", unsafe_allow_html=True)

    st.divider()

    col_guardar, col_elim_sel, col_elim_todo, col_asignar, col_preparar_mails, col_inf_no, col_inf_si, col_inf_insp, col_reset, col_recargar = st.columns(10)
    
    with col_guardar:
        guardar_click = st.button("💾 GUARDAR CAMBIOS", type="secondary", use_container_width=True)
    with col_elim_sel:
        if st.button("🗑 Eliminar sel.", use_container_width=True):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                get_dashboard_stats.clear()
                st.rerun()
    with col_elim_todo:
        if st.button("🗑 Eliminar TODO", use_container_width=True):
            st.session_state.confirmar_del_todo = True
    with col_asignar:
        if st.button("🤖 Asignar Legajos", use_container_width=True):
            st.session_state.asignar_legajos = True
    with col_preparar_mails:
        if st.button("📧 PREPARAR MAILS", use_container_width=True):
            st.session_state.preparar_mails = True
    with col_inf_no:
        if st.button("📄 Inf. NO asig.", use_container_width=True):
            st.session_state.generar_informe = True
    with col_inf_si:
        if st.button("📊 Inf. ASIGNADOS", use_container_width=True):
            st.session_state.generar_informe_asignados = True
    with col_inf_insp:
        if st.button("📊 Inf. POR INSPECTOR", use_container_width=True):
            st.session_state.generar_informe_por_inspector = True
    with col_reset:
        if st.button("↺ Resetear filtros", use_container_width=True):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad', 'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual','filtro_estado']:
                st.session_state.pop(k, None)
            st.rerun()
    with col_recargar:
        if st.button("⟳ Recargar", use_container_width=True):
            st.session_state.ultima_recarga = datetime.now()
            st.session_state.pop('pagina_actual', None)
            get_dashboard_stats.clear()
            st.rerun()

    st.markdown("---")
    col_elim_cancel1, col_elim_cancel2, col_elim_cancel3 = st.columns([1, 2, 1])
    with col_elim_cancel2:
        if st.button("🗑️ EMPAQUETAR Y ELIMINAR REGISTROS CON DEUDA CANCELADA", type="primary", use_container_width=True):
            resultado = eliminar_registros_cancelados()
            if resultado:
                excel_data, cantidad = resultado
                st.success(f"✅ {cantidad} registros eliminados. Descargando backup...")
                st.download_button(
                    label="📥 DESCARGAR BACKUP (Excel)",
                    data=excel_data,
                    file_name=f"BACKUP_DEUDA_CANCELADA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                get_dashboard_stats.clear()
                time.sleep(1)
                st.rerun()

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, eliminar todo"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                get_dashboard_stats.clear()
                st.rerun()
        with col_no:
            if st.button("Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    # ── DIÁLOGO PREPARAR MAILS (resumido) ───────────────────────────────────
    if st.session_state.get('preparar_mails'):
        @st.dialog("📧 PREPARAR MAILS")
        def mostrar_dialogo_preparar_mails():
            st.markdown("### Seleccioná el método de carga")
            opcion = st.radio("Método:", ["📊 POR LOTES (por localidad, orden, etc.)", "🎯 POR CUIT (carga individual)"], index=0, horizontal=True)
            
            if opcion == "📊 POR LOTES (por localidad, orden, etc.)":
                st.markdown("---")
                st.info("Cargando todos los registros candidatos...")
                todos_los_registros = []
                offset = 0
                batch_size = 1000
                while True:
                    query = supabase.table("padron_deuda_presunta").select("*").not_.is_("leg", "null").eq("mail_enviado", "NO").is_("vto", "null").range(offset, offset + batch_size - 1).execute()
                    if not query.data:
                        break
                    todos_los_registros.extend(query.data)
                    offset += batch_size
                    if len(query.data) < batch_size:
                        break
                df_candidatos = pd.DataFrame(todos_los_registros) if todos_los_registros else pd.DataFrame()
                if df_candidatos.empty:
                    st.warning("No hay registros disponibles")
                    if st.button("Finalizar"):
                        st.session_state.preparar_mails = False
                        st.rerun()
                    return
                st.success(f"✅ Total de registros candidatos: {len(df_candidatos)}")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    localidades = ["TODAS"] + sorted(df_candidatos['localidad'].unique().tolist())
                    localidad_filtro = st.selectbox("Localidad", localidades, key="dialog_localidad")
                    usar_todos = st.checkbox("Seleccionar TODOS", value=True, key="dialog_usar_todos")
                    cantidad_personalizada = None
                    if not usar_todos:
                        cantidad_personalizada = st.number_input("Cantidad", min_value=1, max_value=len(df_candidatos), value=100, step=1, key="dialog_cantidad")
                with col_f2:
                    nueva_fecha_vto = st.date_input("Fecha VTO", value=date.today(), key="dialog_fecha")
                    ordenar_deuda = st.checkbox("Ordenar por DEUDA (mayor a menor)", value=True, key="dialog_deuda")
                    ordenar_hasta = st.checkbox("Ordenar por HASTA (más antiguo)", value=False, key="dialog_hasta")
                df_filtrado = df_candidatos.copy()
                if localidad_filtro != "TODAS":
                    df_filtrado = df_filtrado[df_filtrado['localidad'] == localidad_filtro]
                if ordenar_deuda or ordenar_hasta:
                    def parse_deuda(val):
                        if val is None:
                            return 0
                        try:
                            if isinstance(val, str):
                                val = val.replace('$', '').replace('.', '').replace(',', '.').strip()
                            return float(val)
                        except:
                            return 0
                    def parse_hasta(val):
                        if val is None:
                            return datetime.max
                        try:
                            if isinstance(val, str):
                                if '/' in val:
                                    return datetime.strptime(val, '%d/%m/%Y')
                                if '-' in val:
                                    return datetime.strptime(val, '%Y-%m-%d')
                            return val
                        except:
                            return datetime.max
                    if ordenar_deuda:
                        df_filtrado['_deuda_num'] = df_filtrado['deuda_presunta'].apply(parse_deuda)
                        df_filtrado = df_filtrado.sort_values('_deuda_num', ascending=False)
                    if ordenar_hasta:
                        df_filtrado['_hasta_date'] = df_filtrado['hasta'].apply(parse_hasta)
                        df_filtrado = df_filtrado.sort_values('_hasta_date', ascending=True)
                    df_filtrado = df_filtrado.drop(columns=[c for c in ['_deuda_num', '_hasta_date'] if c in df_filtrado.columns])
                if usar_todos:
                    df_seleccionado = df_filtrado.copy()
                else:
                    df_seleccionado = df_filtrado.head(int(cantidad_personalizada))
                if st.button("✅ PROCESAR Y DESCARGAR", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    fecha_str = nueva_fecha_vto.strftime('%Y-%m-%d')
                    fecha_mostrar = nueva_fecha_vto.strftime('%d/%m/%Y')
                    total_registros = len(df_seleccionado)
                    batch_size_update = 50
                    for i in range(0, total_registros, batch_size_update):
                        batch = df_seleccionado.iloc[i:i+batch_size_update]
                        for _, row in batch.iterrows():
                            supabase.table("padron_deuda_presunta").update({"vto": fecha_str, "mail_enviado": "SI"}).eq("id", row['id']).execute()
                        progress_bar.progress(min((i + batch_size_update) / total_registros, 1.0))
                        time.sleep(0.05)
                    progress_bar.progress(1.0)
                    excel_data = generar_excel_para_mailing(df_seleccionado, fecha_mostrar)
                    st.session_state.excel_descarga = excel_data
                    st.session_state.nombre_excel = f"MAILING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.session_state.preparar_mails = False
                    get_dashboard_stats.clear()
                    st.rerun()
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.preparar_mails = False
                    st.rerun()
            else:
                st.markdown("---")
                st.markdown("### Ingresar CUITs manualmente")
                st.caption("Pegá los CUITs separados por coma, espacio o salto de línea")
                cuit_input = st.text_area("CUITs", placeholder="Ej: 30-12345678-9, 33-98765432-1, 27-11111111-2", height=150)
                nueva_fecha_vto_cuit = st.date_input("Fecha VTO a asignar", value=date.today(), key="dialog_fecha_cuit")
                if st.button("✅ PROCESAR CUITs", type="primary", use_container_width=True):
                    if not cuit_input.strip():
                        st.warning("Ingresá al menos un CUIT")
                        return
                    cuit_limpios = re.findall(r'\d{2,11}', cuit_input)
                    if not cuit_limpios:
                        st.warning("No se encontraron CUITs válidos")
                        return
                    cuit_unicos = list(set(cuit_limpios))
                    st.info(f"📊 Se encontraron {len(cuit_unicos)} CUIT(s) únicos")
                    registros_encontrados = []
                    no_encontrados = []
                    for cuit in cuit_unicos:
                        resultado = supabase.table("padron_deuda_presunta").select("*").eq("cuit", cuit).not_.is_("leg", "null").eq("mail_enviado", "NO").is_("vto", "null").execute()
                        if resultado.data:
                            registros_encontrados.extend(resultado.data)
                        else:
                            no_encontrados.append(cuit)
                    if not registros_encontrados:
                        st.warning("No se encontraron registros listos para los CUITs ingresados")
                        return
                    st.success(f"✅ {len(registros_encontrados)} registro(s) encontrado(s)")
                    if no_encontrados:
                        st.warning(f"⚠️ CUITs no encontrados o no disponibles: {', '.join(no_encontrados[:5])}")
                    progress_bar = st.progress(0)
                    fecha_str = nueva_fecha_vto_cuit.strftime('%Y-%m-%d')
                    fecha_mostrar = nueva_fecha_vto_cuit.strftime('%d/%m/%Y')
                    total_registros = len(registros_encontrados)
                    for i, reg in enumerate(registros_encontrados):
                        supabase.table("padron_deuda_presunta").update({"vto": fecha_str, "mail_enviado": "SI"}).eq("id", reg['id']).execute()
                        progress_bar.progress((i + 1) / total_registros)
                        time.sleep(0.02)
                    progress_bar.progress(1.0)
                    df_resultado = pd.DataFrame(registros_encontrados)
                    excel_data = generar_excel_para_mailing(df_resultado, fecha_mostrar)
                    st.session_state.excel_descarga = excel_data
                    st.session_state.nombre_excel = f"MAILING_CUIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.session_state.preparar_mails = False
                    get_dashboard_stats.clear()
                    st.rerun()
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.preparar_mails = False
                    st.rerun()
        
        mostrar_dialogo_preparar_mails()

    if st.session_state.get("excel_descarga"):
        st.success("🎉 ¡Mailing generado exitosamente! Descargue el archivo:")
        col_desc1, col_desc2, col_desc3 = st.columns([1, 2, 1])
        with col_desc2:
            st.download_button(label="📥 DESCARGAR EXCEL", data=st.session_state.excel_descarga, file_name=st.session_state.nombre_excel, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
            if st.button("✅ FINALIZAR", use_container_width=True):
                del st.session_state["excel_descarga"]
                del st.session_state["nombre_excel"]
                st.rerun()

    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(label="📥 DESCARGAR TXT", data=contenido_txt.encode('utf-8'), file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")
                st.info(f"📊 {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo")
        st.session_state.generar_informe = False

    if st.session_state.get('generar_informe_asignados'):
        with st.spinner("Generando informe..."):
            registros_con_legajo = traer_registros_con_legajo()
            if registros_con_legajo:
                excel_data = generar_excel_asignados(registros_con_legajo)
                st.download_button(label="📥 DESCARGAR EXCEL (TODOS)", data=excel_data, file_name=f"INFORME_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.info(f"📊 {len(registros_con_legajo)} registros con legajo")
            else:
                st.success("✅ No hay registros con legajo")
        st.session_state.generar_informe_asignados = False

    if st.session_state.get('generar_informe_por_inspector'):
        with st.spinner("Generando informe por inspector..."):
            excel_data = generar_excel_por_inspector()
            st.download_button(label="📥 DESCARGAR EXCEL (POR INSPECTOR)", data=excel_data, file_name=f"INFORME_POR_INSPECTOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.success("✅ Informe generado - Una hoja por inspector")
        st.session_state.generar_informe_por_inspector = False

    if st.session_state.get('asignar_legajos'):
        st.info("⏳ Asignando legajos...")
        with st.spinner("Cargando configuración..."):
            insp_loc = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos = cargar_sinonimos()
            palabras_ancla = cargar_palabras_ancla()
            lkp_loc = construir_lookup_localidades(insp_loc)
            lkp_zonas = construir_lookup_zonas(insp_zonas)
            lkp_sin = construir_lookup_sinonimos(sinonimos)
            lkp_palabras = construir_lookup_palabras_ancla(palabras_ancla)
        with st.spinner("Cargando registros..."):
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
                status_text.markdown(f"🔄 {int(percent * 100)}% - {reg.get('razon_social', 'Sin nombre')[:40]}...")
                legajo = asignar_legajo(reg.get('localidad', '') or '', reg.get('calle', '') or '', reg.get('numero', '') or '', lkp_loc, lkp_zonas, lkp_sin, lkp_palabras)
                if legajo:
                    asig.append({'id': reg['id'], 'legajo': legajo})
                else:
                    no_asig.append({'id': reg['id'], 'localidad': reg.get('localidad', ''), 'calle': reg.get('calle', ''), 'numero': reg.get('numero', ''), 'razon_social': reg.get('razon_social', ''), 'cuit': reg.get('cuit', ''), 'tel_dom_legal': reg.get('tel_dom_legal', ''), 'tel_dom_real': reg.get('tel_dom_real', '')})
                time.sleep(0.01)
            progress_bar.empty()
            status_text.empty()
            with st.spinner("Guardando..."):
                guardados = guardar_legajos_en_batch(asig)
            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {"asignados": guardados, "no_asignados": len(no_asig), "detalle": no_asig}
            get_dashboard_stats.clear()
            st.success(f"✅ {guardados} legajos asignados, {len(no_asig)} sin coincidencia.")
            st.rerun()

    if st.session_state.get('ultima_asignacion'):
        res = st.session_state.ultima_asignacion
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.success(f"✅ {res['asignados']} legajos asignados")
        with col_res2:
            st.warning(f"⚠️ {res['no_asignados']} sin coincidencia")
        if res['no_asignados'] > 0:
            contenido_informe = generar_informe_txt(res['detalle'])
            st.download_button(label="📥 DESCARGAR INFORME", data=contenido_informe.encode('utf-8'), file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")
            with st.expander(f"📋 Ver {res['no_asignados']} registros"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    # ── FILTROS Y TABLA EDITABLE ──
    st.markdown("### 🔎 Filtros de búsqueda")
    
    if 'ultima_recarga' not in st.session_state:
        st.session_state.ultima_recarga = datetime.now()
    
    if 'filtro_estado' not in st.session_state:
        st.session_state.filtro_estado = "AMBOS"
    
    col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns(6)
    with col_f1:
        st.markdown('<p class="filtro-titulo">📍 LOCALIDAD</p>', unsafe_allow_html=True)
        locs = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with col_f2:
        st.markdown('<p class="filtro-titulo">✉️ MAIL</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with col_f3:
        st.markdown('<p class="filtro-titulo">🆔 LEGAJO</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with col_f4:
        st.markdown('<p class="filtro-titulo">🔢 CUIT</p>', unsafe_allow_html=True)
        filtro_cuit_temp = st.text_input("CUIT", key="filtro_cuit_temp", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with col_f5:
        st.markdown('<p class="filtro-titulo">🏢 RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon_temp = st.text_input("Razón Social", key="filtro_razon_temp", placeholder="Razón social", label_visibility="collapsed")
    with col_f6:
        st.markdown('<p class="filtro-titulo">📌 ESTADO GESTIÓN</p>', unsafe_allow_html=True)
        filtro_estado_temp = st.selectbox("Estado Gestión", ["AMBOS", "PENDIENTE", "FINALIZADO"], key="filtro_estado_temp", label_visibility="collapsed")
    
    col_f7, col_f8 = st.columns([3, 1])
    with col_f7:
        st.markdown('<p class="filtro-titulo">🏠 CALLE</p>', unsafe_allow_html=True)
        filtro_calle_temp = st.text_input("Calle", key="filtro_calle_temp", placeholder="Ej: Yrigoyen", label_visibility="collapsed")
    with col_f8:
        st.markdown('<div class="buscar-btn" style="margin-top: 18px;">', unsafe_allow_html=True)
        buscar_click = st.button("🔍 BUSCAR", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if 'filtro_cuit' not in st.session_state:
        st.session_state.filtro_cuit = ""
    if 'filtro_razon' not in st.session_state:
        st.session_state.filtro_razon = ""
    if 'filtro_calle' not in st.session_state:
        st.session_state.filtro_calle = ""
    
    if buscar_click:
        st.session_state.filtro_cuit = filtro_cuit_temp
        st.session_state.filtro_razon = filtro_razon_temp
        st.session_state.filtro_calle = filtro_calle_temp
        st.session_state.filtro_estado = filtro_estado_temp
        st.session_state.pagina_actual = 1
        st.rerun()
    
    filtro_cuit = st.session_state.filtro_cuit
    filtro_razon = st.session_state.filtro_razon
    filtro_calle_aprox = st.session_state.filtro_calle
    filtro_estado = st.session_state.filtro_estado
    
    if filtro_cuit or filtro_razon or filtro_calle_aprox or filtro_estado != "AMBOS":
        st.caption(f"🔍 Búsqueda activa - CUIT: {filtro_cuit or 'todo'} | Razón Social: {filtro_razon or 'todo'} | Calle: {filtro_calle_aprox or 'todo'} | Estado: {filtro_estado}")

    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")
    if filtro_leg == "CON LEGAJO":
        q = q.not_.is_("leg", "null")
    elif filtro_leg == "SIN LEGAJO":
        q = q.is_("leg", "null")
    if filtro_estado != "AMBOS":
        q = q.eq("estado_gestion", filtro_estado)
    
    with st.spinner("Consultando base de datos..."):
        datos = q.execute()
    
    df = pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    
    if not df.empty and filtro_cuit:
        df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if not df.empty and filtro_razon:
        df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    if not df.empty and filtro_calle_aprox:
        filtro_norm = normalizar_calle(filtro_calle_aprox)
        if filtro_norm:
            df['calle_norm'] = df['calle'].apply(lambda x: normalizar_calle(str(x)) if x else "")
            df['similitud'] = df['calle_norm'].apply(lambda x: difflib.SequenceMatcher(None, filtro_norm, x).ratio() if x else 0)
            df = df[df['similitud'] > 0.4].sort_values('similitud', ascending=False)
            df = df.drop(columns=['calle_norm', 'similitud'])

    total_en_tabla = len(df)
    RPP = 200
    pages = max(1, (total_en_tabla + RPP - 1) // RPP)

    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 1
    st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

    col_pag1, col_pag2, col_pag3 = st.columns([1, 3, 1])
    with col_pag1:
        if st.button("◀ Anterior", disabled=st.session_state.pagina_actual <= 1):
            st.session_state.pagina_actual -= 1
            st.rerun()
    with col_pag2:
        st.caption(f"Página {st.session_state.pagina_actual} de {pages} | Total en tabla: {total_en_tabla} registros")
    with col_pag3:
        if st.button("Siguiente ▶", disabled=st.session_state.pagina_actual >= pages):
            st.session_state.pagina_actual += 1
            st.rerun()

    if df.empty:
        st.info("No hay registros que coincidan con los filtros seleccionados.")
    else:
        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()
        for col in df_p.columns:
            df_p[col] = df_p[col].apply(lambda x: "" if pd.isna(x) else str(x))
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(lambda x: fmt_fecha(x) if x and x != "" else "")
        df_orig = df_p.copy()
        df_ed = df_p.rename(columns={
            'id':'ID', 'delegacion':'DELEGACION', 'localidad':'LOCALIDAD', 'cuit':'CUIT',
            'razon_social':'RAZON SOCIAL', 'deuda_presunta':'DEUDA PRESUNTA', 'cp':'CP',
            'calle':'CALLE', 'numero':'NUMERO', 'piso':'PISO', 'dpto':'DPTO',
            'fechareldependencia':'FECHARELDEPENDENCIA', 'email':'EMAIL',
            'tel_dom_legal':'TEL_DOM_LEGAL', 'tel_dom_real':'TEL_DOM_REAL',
            'ultima_acta':'ULTIMA ACTA', 'desde':'DESDE', 'hasta':'HASTA',
            'detectado':'DETECTADO', 'estado':'ESTADO', 'fecha_pago_obl':'FECHA PAGO OBL',
            'empl_10_2025':'EMPL 10-2025', 'emp_11_2025':'EMP 11-2025', 'empl_12_2025':'EMPL 12-2025',
            'actividad':'ACTIVIDAD', 'situacion':'SITUACION',
            'leg':'LEG', 'vto':'VTO', 'mail_enviado':'MAIL ENVIADO',
            'acta':'ACTA', 'estado_gestion':'ESTADO GESTION', 'deuda_cancelada':'CANCELAR',
        })
        df_ed.insert(0, "🗑️", False)
        if st.checkbox("Seleccionar todos los de esta página"):
            df_ed["🗑️"] = True
        editor_key = f"editor_{st.session_state.pagina_actual}_{st.session_state.ultima_recarga.timestamp()}"
        edited = st.data_editor(df_ed, use_container_width=True, height=500, column_config={"🗑️": st.column_config.CheckboxColumn("Eliminar"), "CANCELAR": st.column_config.CheckboxColumn("Cancelar Deuda")}, key=editor_key)
        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel
        if ids_sel:
            st.info(f"📌 {len(ids_sel)} registro(s) seleccionado(s) para eliminar")
        if guardar_click:
            mods = 0
            errores_fecha = 0
            with st.spinner("Guardando cambios en Supabase..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd = {}
                    
                    id_valor = row.get('ID')
                    if pd.isna(id_valor) or id_valor is None or str(id_valor).strip() == '':
                        continue
                    
                    for col_edit, col_orig in [
                        ('LEG', 'leg'), ('VTO', 'vto'), ('MAIL ENVIADO', 'mail_enviado'),
                        ('ACTA', 'acta'), ('ESTADO GESTION', 'estado_gestion'),
                        ('LOCALIDAD', 'localidad'), ('RAZON SOCIAL', 'razon_social'),
                        ('CUIT', 'cuit'), ('CALLE', 'calle'), ('NUMERO', 'numero'),
                        ('DEUDA PRESUNTA', 'deuda_presunta'), ('DESDE', 'desde'), ('HASTA', 'hasta'),
                        ('CANCELAR', 'deuda_cancelada')
                    ]:
                        nv = row.get(col_edit)
                        if nv is None or (isinstance(nv, float) and pd.isna(nv)) or (isinstance(nv, str) and nv.strip() == ''):
                            nv = None
                        elif isinstance(nv, str):
                            nv = nv.strip()
                        
                        if nv != orig.get(col_orig):
                            if col_orig == 'vto' and nv:
                                fecha_ok = norm_fecha(str(nv))
                                if fecha_ok:
                                    upd[col_orig] = fecha_ok
                                else:
                                    errores_fecha += 1
                            elif col_orig == 'leg' and nv:
                                try:
                                    upd[col_orig] = int(float(str(nv)))
                                except:
                                    upd[col_orig] = None
                            else:
                                upd[col_orig] = nv
                    
                    if upd:
                        try:
                            supabase.table("padron_deuda_presunta").update(upd).eq("id", int(id_valor)).execute()
                            mods += 1
                        except Exception as e:
                            st.error(f"Error actualizando registro ID {id_valor}: {e}")
            if mods > 0:
                st.success(f"✅ ¡{mods} registros actualizados correctamente!")
                if errores_fecha > 0:
                    st.warning(f"⚠️ {errores_fecha} fecha(s) no se pudieron guardar (formato incorrecto). Usá DD/MM/YYYY.")
                get_dashboard_stats.clear()
                st.session_state.ultima_recarga = datetime.now()
                st.rerun()
            elif errores_fecha > 0:
                st.warning(f"No se guardaron cambios. {errores_fecha} fecha(s) con formato incorrecto.")
            else:
                st.info("No se detectaron cambios para guardar.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Subir Actas (con períodos DESDE y HASTA)
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 📋 Subir Actas (CSV)")
    st.markdown("""
    <div style="background: #f1f5f9; padding: 0.5rem 1rem; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
    El sistema busca coincidencias por <strong>CUIT + LEGAJO + FECHA VTO</strong>
    en registros con <strong>MAIL ENVIADO = SI</strong> y actualiza:
    <ul>
        <li>ACTA y ESTADO GESTIÓN a FINALIZADO</li>
        <li>DEUDA PRESUNTA (si la columna existe)</li>
        <li>PERÍODO DESDE y PERÍODO HASTA (si las columnas existen, formato AAAA/MM → se completa con día 1)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    csv_file = st.file_uploader("Archivo CSV", type=["csv"], key="upload_actas_csv")

    if csv_file:
        st.caption(f"Archivo: **{csv_file.name}**")
        
        def esta_amontonado(df):
            if len(df.columns) == 1:
                primera_fila = str(df.iloc[0, 0]) if len(df) > 0 else ""
                if ',' in primera_fila or ';' in primera_fila:
                    return True
            return False
        
        def separar_csv_amontonado(df_original):
            columna_unica = df_original.columns[0]
            primera_fila = str(df_original.iloc[0, 0]) if len(df_original) > 0 else ""
            separador = ',' if ',' in primera_fila else ';'
            datos_separados = df_original[columna_unica].str.split(separador, expand=True)
            primera_fila_dividida = primera_fila.split(separador)
            if len(primera_fila_dividida) > 1 and all(p.strip().upper() in ['CUIT', 'LEG', 'VTO', 'ACTA', 'NRO ACTA', 'FECHA VTO', 'DEUDA_TOTAL', 'DEUDA', 'MONTO', 'PERIODO_DESDE', 'PERIODO_HASTA'] for p in primera_fila_dividida[:4]):
                nuevos_encabezados = [p.strip().upper() for p in primera_fila_dividida]
                datos_separados.columns = nuevos_encabezados
                datos_separados = datos_separados.iloc[1:].reset_index(drop=True)
            else:
                datos_separados.columns = [f"COL_{i+1}" for i in range(len(datos_separados.columns))]
            return datos_separados
        
        # Función para parsear fecha "AAAA/MM" a "YYYY-MM-01"
        def parsear_periodo(valor):
            if not valor or pd.isna(valor):
                return None
            try:
                s = str(valor).strip()
                match = re.match(r'(\d{4})[/](\d{1,2})', s)
                if match:
                    anio = int(match.group(1))
                    mes = int(match.group(2))
                    if 1 <= mes <= 12:
                        return datetime(anio, mes, 1).strftime('%Y-%m-%d')
                return None
            except:
                return None
        
        try:
            df_raw = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=None, engine='python', dtype=str, encoding='utf-8-sig', nrows=5)
            with st.expander("📄 Vista previa del archivo original"):
                st.dataframe(df_raw.head(5), use_container_width=True, height=150)
            if esta_amontonado(df_raw):
                st.info("🔧 El archivo parece estar 'amontonado' (datos en una sola columna). Acomodando automáticamente...")
                df_procesado = separar_csv_amontonado(df_raw)
                with st.expander("📄 Vista previa DESPUÉS de acomodar"):
                    st.dataframe(df_procesado.head(5), use_container_width=True, height=150)
            else:
                st.success("✅ El archivo ya está en formato correcto.")
                df_procesado = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=None, engine='python', dtype=str, encoding='utf-8-sig')
            
            st.caption(f"Columnas detectadas: {', '.join(df_procesado.columns.tolist())}")
            col_cuit = col_leg = col_vto = col_acta = col_deuda = col_desde = col_hasta = None
            for c in df_procesado.columns:
                cu = c.upper()
                if 'CUIT' in cu and not col_cuit: col_cuit = c
                if ('LEG' in cu or 'LEGAJO' in cu) and not col_leg: col_leg = c
                if ('VTO' in cu or 'FECHA_VTO' in cu) and not col_vto: col_vto = c
                if ('NRO_ACTA' in cu or cu == 'ACTA') and not col_acta: col_acta = c
                if ('DEUDA' in cu or 'MONTO' in cu) and not col_deuda: col_deuda = c
                if 'PERIODO_DESDE' in cu and not col_desde: col_desde = c
                if 'PERIODO_HASTA' in cu and not col_hasta: col_hasta = c
            
            if not all([col_cuit, col_leg, col_vto]):
                st.warning(f"⚠️ No se detectaron todas las columnas necesarias. Buscamos: CUIT, LEG, VTO")
                st.info(f"Columnas encontradas: CUIT={col_cuit}, LEG={col_leg}, VTO={col_vto}, ACTA={col_acta}, DEUDA={col_deuda}, DESDE={col_desde}, HASTA={col_hasta}")
            else:
                st.success(f"✅ Columnas detectadas: CUIT=`{col_cuit}` · LEG=`{col_leg}` · VTO=`{col_vto}`" +
                          (f" · DEUDA=`{col_deuda}`" if col_deuda else "") +
                          (f" · PERIODO_DESDE=`{col_desde}`" if col_desde else "") +
                          (f" · PERIODO_HASTA=`{col_hasta}`" if col_hasta else ""))
                if esta_amontonado(df_raw):
                    df_completo = df_procesado
                else:
                    df_completo = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=None, engine='python', dtype=str, encoding='utf-8-sig')
                if st.button("📋 Procesar y actualizar actas", type="primary"):
                    with st.spinner("Procesando..."):
                        actualizados = 0
                        no_encontrados = 0
                        bar = st.progress(0)
                        errores = []
                        for i, row in df_completo.iterrows():
                            try:
                                cuit_raw = str(row[col_cuit]) if pd.notna(row[col_cuit]) else ""
                                cuit = re.sub(r'[\.\-,\s]', '', cuit_raw).strip()
                                leg_raw = str(row[col_leg]) if pd.notna(row[col_leg]) else ""
                                leg = re.sub(r'\D', '', leg_raw).strip() if leg_raw else None
                                vto_raw = str(row[col_vto]) if pd.notna(row[col_vto]) else ""
                                vto = norm_fecha(vto_raw)
                                acta = str(row[col_acta]) if col_acta and pd.notna(row.get(col_acta)) else "ACTUALIZADO"
                                deuda_nueva = None
                                if col_deuda and pd.notna(row.get(col_deuda)):
                                    deuda_raw = str(row[col_deuda]).replace(',', '.').strip()
                                    try:
                                        deuda_valor = float(deuda_raw)
                                        deuda_nueva = fmt_moneda(deuda_valor)
                                    except:
                                        deuda_nueva = deuda_raw
                                
                                desde_nuevo = None
                                if col_desde and pd.notna(row.get(col_desde)):
                                    desde_nuevo = parsear_periodo(row[col_desde])
                                hasta_nuevo = None
                                if col_hasta and pd.notna(row.get(col_hasta)):
                                    hasta_nuevo = parsear_periodo(row[col_hasta])
                                
                                if cuit and leg and vto:
                                    resultado = supabase.table("padron_deuda_presunta").select("id").eq("cuit", cuit).eq("leg", leg).eq("vto", vto).eq("mail_enviado", "SI").execute()
                                    if resultado.data:
                                        for reg in resultado.data:
                                            update_data = {"acta": acta, "estado_gestion": "FINALIZADO"}
                                            if deuda_nueva:
                                                update_data["deuda_presunta"] = deuda_nueva
                                            if desde_nuevo:
                                                update_data["desde"] = desde_nuevo
                                            if hasta_nuevo:
                                                update_data["hasta"] = hasta_nuevo
                                            supabase.table("padron_deuda_presunta").update(update_data).eq("id", reg['id']).execute()
                                            actualizados += 1
                                    else:
                                        no_encontrados += 1
                                else:
                                    no_encontrados += 1
                            except Exception as e:
                                errores.append(f"Fila {i+1}: {str(e)}")
                            bar.progress((i + 1) / len(df_completo))
                        bar.empty()
                        col_ok, col_no = st.columns(2)
                        col_ok.metric("✅ Actualizados", actualizados)
                        col_no.metric("❌ No encontrados", no_encontrados)
                        if errores:
                            with st.expander(f"⚠️ {len(errores)} error(es) durante el procesamiento"):
                                for err in errores[:10]:
                                    st.caption(err)
                        if actualizados > 0:
                            st.success(f"✅ {actualizados} actas actualizadas correctamente.")
                            get_dashboard_stats.clear()
                        if no_encontrados > 0:
                            st.warning(f"⚠️ {no_encontrados} filas sin coincidencia en la base de datos.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
            st.info("Asegurate de que el archivo sea un CSV válido.")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Editar Registro (TODOS LOS CAMPOS - COMPACTO)
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### ✏️ Editar Registro Individual")
    st.markdown("Buscá un registro por CUIT, Razón Social o Calle, editá sus campos y guardá los cambios.")
    
    if 'registros_busqueda' not in st.session_state:
        st.session_state.registros_busqueda = []
    if 'indice_actual' not in st.session_state:
        st.session_state.indice_actual = 0
    if 'registro_editado' not in st.session_state:
        st.session_state.registro_editado = None
    if 'ultima_busqueda' not in st.session_state:
        st.session_state.ultima_busqueda = datetime.now().timestamp()
    
    col_busqueda1, col_busqueda2, col_busqueda3 = st.columns([2, 2, 1])
    with col_busqueda1:
        tipo_busqueda = st.selectbox("Buscar por:", ["CUIT", "RAZÓN SOCIAL", "CALLE"], key="tipo_busqueda_tab4")
    with col_busqueda2:
        termino_busqueda = st.text_input("Término a buscar:", placeholder="Ej: 30-12345678-9 o nombre de empresa o calle", key="termino_busqueda_tab4")
    with col_busqueda3:
        st.markdown("---")
        if st.button("🔍 BUSCAR REGISTROS", type="primary", use_container_width=True, key="btn_buscar_tab4"):
            if termino_busqueda.strip():
                with st.spinner("Buscando..."):
                    query = supabase.table("padron_deuda_presunta").select("*")
                    if tipo_busqueda == "CUIT":
                        cuit_limpio = re.sub(r'[\.\-,\s]', '', termino_busqueda).strip()
                        query = query.eq("cuit", cuit_limpio)
                    elif tipo_busqueda == "RAZÓN SOCIAL":
                        query = query.ilike("razon_social", f"%{termino_busqueda}%")
                    else:
                        query = query.ilike("calle", f"%{termino_busqueda}%")
                    resultado = query.execute()
                    st.session_state.registros_busqueda = resultado.data if resultado.data else []
                    st.session_state.indice_actual = 0
                    st.session_state.registro_editado = None
                    st.session_state.ultima_busqueda = datetime.now().timestamp()
                    st.rerun()
    
    if st.session_state.registros_busqueda:
        total_resultados = len(st.session_state.registros_busqueda)
        st.info(f"📊 Se encontraron {total_resultados} registro(s)")
        if total_resultados > 1:
            col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 3, 1])
            with col_nav1:
                if st.button("◀◀ Primero", key="nav_primero", disabled=st.session_state.indice_actual == 0):
                    st.session_state.indice_actual = 0
                    st.session_state.registro_editado = None
                    st.rerun()
            with col_nav2:
                if st.button("◀ Anterior", key="nav_anterior", disabled=st.session_state.indice_actual == 0):
                    st.session_state.indice_actual -= 1
                    st.session_state.registro_editado = None
                    st.rerun()
            with col_nav4:
                if st.button("Siguiente ▶", key="nav_siguiente", disabled=st.session_state.indice_actual >= total_resultados - 1):
                    st.session_state.indice_actual += 1
                    st.session_state.registro_editado = None
                    st.rerun()
            with col_nav3:
                st.caption(f"Registro {st.session_state.indice_actual + 1} de {total_resultados}")
        
        registro_actual = st.session_state.registros_busqueda[st.session_state.indice_actual]
        if st.session_state.registro_editado is None:
            st.session_state.registro_editado = registro_actual.copy()
        
        registro_id = registro_actual.get('id', 0)
        key_suffix = f"{registro_id}_{st.session_state.ultima_busqueda}"
        
        st.markdown('<div class="ficha-edicion">', unsafe_allow_html=True)
        st.markdown('<div class="ficha-titulo">📋 Datos del Registro</div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown('<p class="campo-label">CUIT</p>', unsafe_allow_html=True)
            nuevo_cuit = st.text_input("CUIT", value=st.session_state.registro_editado.get('cuit', ''), key=f"cuit_{key_suffix}")
            
            st.markdown('<p class="campo-label">RAZÓN SOCIAL</p>', unsafe_allow_html=True)
            nueva_razon = st.text_input("Razón Social", value=st.session_state.registro_editado.get('razon_social', ''), key=f"razon_{key_suffix}")
            
            st.markdown('<p class="campo-label">CALLE</p>', unsafe_allow_html=True)
            nueva_calle = st.text_input("Calle", value=st.session_state.registro_editado.get('calle', ''), key=f"calle_{key_suffix}")
            
            st.markdown('<p class="campo-label">NÚMERO</p>', unsafe_allow_html=True)
            nuevo_numero = st.text_input("Número", value=st.session_state.registro_editado.get('numero', ''), key=f"numero_{key_suffix}")
            
            st.markdown('<p class="campo-label">LOCALIDAD</p>', unsafe_allow_html=True)
            locs = get_localidades()
            localidad_actual = st.session_state.registro_editado.get('localidad', 'MAR DEL PLATA')
            localidad_index = locs.index(localidad_actual) if localidad_actual in locs else 0
            nueva_localidad = st.selectbox("Localidad", locs, index=localidad_index, key=f"localidad_{key_suffix}")
            
            st.markdown('<p class="campo-label">CP</p>', unsafe_allow_html=True)
            nuevo_cp = st.text_input("CP", value=st.session_state.registro_editado.get('cp', ''), key=f"cp_{key_suffix}")
        
        with col_b:
            st.markdown('<p class="campo-label">LEGAJO</p>', unsafe_allow_html=True)
            inspectores_list = supabase.table("inspectores").select("*").order("legajo").execute()
            inspectores_opts = {ins['nombre']: ins['legajo'] for ins in inspectores_list.data}
            inspectores_opts["SIN LEGAJO"] = ""
            legajo_actual = st.session_state.registro_editado.get('leg', '')
            inspector_actual_nombre = next((k for k, v in inspectores_opts.items() if str(v) == str(legajo_actual)), "SIN LEGAJO")
            inspector_index = list(inspectores_opts.keys()).index(inspector_actual_nombre) if inspector_actual_nombre in inspectores_opts else 0
            inspector_seleccionado = st.selectbox("Inspector", options=list(inspectores_opts.keys()), index=inspector_index, key=f"inspector_{key_suffix}")
            nuevo_legajo = inspectores_opts[inspector_seleccionado] if inspector_seleccionado != "SIN LEGAJO" else None
            
            st.markdown('<p class="campo-label">FECHA VTO</p>', unsafe_allow_html=True)
            vto_actual = st.session_state.registro_editado.get('vto', '')
            vto_fecha = norm_fecha(vto_actual) if vto_actual else None
            vto_default = datetime.strptime(vto_fecha, '%Y-%m-%d') if vto_fecha else date.today()
            nuevo_vto = st.date_input("Fecha VTO", value=vto_default, key=f"vto_{key_suffix}")
            
            st.markdown('<p class="campo-label">ACTA</p>', unsafe_allow_html=True)
            nueva_acta = st.text_input("Acta", value=st.session_state.registro_editado.get('acta', ''), key=f"acta_{key_suffix}")
            
            st.markdown('<p class="campo-label">DEUDA PRESUNTA</p>', unsafe_allow_html=True)
            nueva_deuda = st.text_input("Deuda", value=st.session_state.registro_editado.get('deuda_presunta', ''), key=f"deuda_{key_suffix}")
            
            st.markdown('<p class="campo-label">ESTADO GESTIÓN</p>', unsafe_allow_html=True)
            estados = ["PENDIENTE", "EN PROCESO", "COMPLETADO", "RECHAZADO", "FINALIZADO", "ACTA_SOLICITADA", "ACTA_SUBIDA"]
            estado_actual = st.session_state.registro_editado.get('estado_gestion', 'PENDIENTE')
            estado_index = estados.index(estado_actual) if estado_actual in estados else 0
            nuevo_estado = st.selectbox("Estado", estados, index=estado_index, key=f"estado_{key_suffix}")
        
        with col_c:
            st.markdown('<p class="campo-label">EMAIL</p>', unsafe_allow_html=True)
            nuevo_email = st.text_input("Email", value=st.session_state.registro_editado.get('email', ''), key=f"email_{key_suffix}")
            
            st.markdown('<p class="campo-label">TELÉFONO LEGAL</p>', unsafe_allow_html=True)
            nuevo_tel_legal = st.text_input("Teléfono Legal", value=st.session_state.registro_editado.get('tel_dom_legal', ''), key=f"tel_legal_{key_suffix}")
            
            st.markdown('<p class="campo-label">TELÉFONO REAL</p>', unsafe_allow_html=True)
            nuevo_tel_real = st.text_input("Teléfono Real", value=st.session_state.registro_editado.get('tel_dom_real', ''), key=f"tel_real_{key_suffix}")
            
            st.markdown('<p class="campo-label">PERÍODO DESDE</p>', unsafe_allow_html=True)
            desde_actual = st.session_state.registro_editado.get('desde', '')
            desde_fecha = norm_fecha(desde_actual) if desde_actual else None
            desde_default = datetime.strptime(desde_fecha, '%Y-%m-%d') if desde_fecha else date.today()
            nuevo_desde = st.date_input("Desde", value=desde_default, key=f"desde_{key_suffix}")
            
            st.markdown('<p class="campo-label">PERÍODO HASTA</p>', unsafe_allow_html=True)
            hasta_actual = st.session_state.registro_editado.get('hasta', '')
            hasta_fecha = norm_fecha(hasta_actual) if hasta_actual else None
            hasta_default = datetime.strptime(hasta_fecha, '%Y-%m-%d') if hasta_fecha else date.today()
            nuevo_hasta = st.date_input("Hasta", value=hasta_default, key=f"hasta_{key_suffix}")
        
        col_guardar_reg, col_cancelar_reg = st.columns(2)
        with col_guardar_reg:
            st.markdown('<p class="campo-label">DEUDA CANCELADA</p>', unsafe_allow_html=True)
            cancelada_actual = st.session_state.registro_editado.get('deuda_cancelada', False)
            nueva_cancelada = st.checkbox("Marcar como deuda cancelada", value=cancelada_actual, key=f"cancelada_{key_suffix}")
            
            if st.button("💾 GUARDAR CAMBIOS", type="secondary", use_container_width=True, key=f"guardar_{key_suffix}"):
                update_data = {
                    "cuit": nuevo_cuit,
                    "razon_social": nueva_razon,
                    "calle": nueva_calle,
                    "numero": nuevo_numero,
                    "localidad": nueva_localidad,
                    "cp": nuevo_cp,
                    "leg": nuevo_legajo,
                    "vto": nuevo_vto.strftime('%Y-%m-%d'),
                    "acta": nueva_acta if nueva_acta.strip() else None,
                    "deuda_presunta": nueva_deuda,
                    "estado_gestion": nuevo_estado,
                    "email": nuevo_email,
                    "tel_dom_legal": nuevo_tel_legal,
                    "tel_dom_real": nuevo_tel_real,
                    "desde": nuevo_desde.strftime('%Y-%m-%d'),
                    "hasta": nuevo_hasta.strftime('%Y-%m-%d'),
                    "deuda_cancelada": nueva_cancelada,
                }
                with st.spinner("Guardando cambios..."):
                    try:
                        supabase.table("padron_deuda_presunta").update(update_data).eq("id", registro_actual['id']).execute()
                        st.success("✅ Carga correcta")
                        st.session_state.registro_editado.update(update_data)
                        st.session_state.registros_busqueda[st.session_state.indice_actual] = st.session_state.registro_editado.copy()
                        get_dashboard_stats.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
        
        with col_cancelar_reg:
            if st.button("❌ Cancelar", use_container_width=True, key=f"cancelar_{key_suffix}"):
                st.session_state.registro_editado = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"ID del registro: {registro_actual.get('id', 'N/A')}")
    
    elif termino_busqueda.strip() and st.session_state.registros_busqueda == []:
        st.warning("No se encontraron registros con ese término de búsqueda.")

# ══════════════════════════════════════════════════════════════════
# TAB 5 — Generar Informe
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="color: #3b82f6; margin: 0 0 0.3rem 0; font-size: 1rem;">📄 Generar Informe Mensual</h3>
        <p style="color: #64748b; margin-bottom: 0.5rem; font-size: 0.7rem;">Completá el formulario PDF con los datos de los registros listos</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.page_link("pages/generar_informe.py", label="🔗 IR A GENERAR INFORME", icon="📄", use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 6 — INSPECTORES
# ══════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="color: #10b981; margin: 0 0 0.3rem 0; font-size: 1rem;">🗺️ Zonas de Inspectores</h3>
        <p style="color: #64748b; margin-bottom: 0.5rem; font-size: 0.7rem;">Administre inspectores, localidades y calles de Mar del Plata</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.page_link("pages/zonas.py", label="🔗 IR A INSPECTORES Y ZONAS", icon="👥", use_container_width=True)
