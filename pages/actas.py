import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
import difflib
import hashlib
import time
import io

# ── Conexión ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(page_title="Fiscalización - OSECAC", layout="wide", initial_sidebar_state="collapsed")

# ── ESTILOS PROFESIONALES MEJORADOS ───────────────────────────────────────────
st.markdown("""
<style>
/* Reset y fuentes */
html, body, [class*="css"] { font-size: 13px !important; font-family: 'Inter', sans-serif; }

/* Header principal */
.app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 0.5rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid #334155;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.app-header h3 { color: #f1f5f9; margin: 0; font-size: 1.1rem; font-weight: 600; }
.app-header p { color: #94a3b8; margin: 0; font-size: 0.7rem; }

/* Botones principales */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

/* Botón GUARDAR CAMBIOS (Verde principal) */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Botones de gestión (Azul) */
.gestion-button button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
}
.gestion-button button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    transform: translateY(-1px);
}

/* Botones de informes (Ámbar) */
.informe-button button {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: white !important;
}
.informe-button button:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
    transform: translateY(-1px);
}

/* Botones de mantenimiento (Gris) */
.mantenimiento-button button {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
    color: white !important;
}
.mantenimiento-button button:hover {
    background: linear-gradient(135deg, #475569 0%, #334155 100%) !important;
}

/* Botón Volver */
.volver-button button {
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
}

/* KPI Cards mejoradas */
.kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 12px;
    padding: 0.6rem;
    text-align: center;
    border: 1px solid #334155;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    border-color: #3b82f6;
}
.kpi-card h1 { margin: 0; font-size: 1.8rem !important; font-weight: 700; }
.kpi-card p { margin: 0; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.5px; }

/* KPI específicos */
.kpi-total h1 { color: #3b82f6; }
.kpi-con-legajo h1 { color: #10b981; }
.kpi-sin-legajo h1 { color: #f59e0b; }

/* Inspector cards colapsables */
.inspector-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 8px;
    padding: 0.4rem;
    text-align: center;
    border: 1px solid #334155;
    transition: all 0.2s ease;
}
.inspector-card:hover {
    border-color: #10b981;
    transform: translateY(-1px);
}
.inspector-card h3 { margin: 0; font-size: 0.75rem; color: #10b981; font-weight: 600; }
.inspector-card h1 { margin: 0; font-size: 1.2rem; color: #f1f5f9; font-weight: 700; }
.inspector-card p { margin: 0; font-size: 0.55rem; color: #94a3b8; }

/* Filtros */
.filtro-titulo { 
    font-size: 0.65rem; 
    color: #94a3b8; 
    margin-bottom: 0.2rem; 
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* Tabla */
.stDataFrame {
    border-radius: 8px;
    border: 1px solid #334155;
}

/* Diálogo mejorado */
div[role="dialog"] {
    background: #f8fafc !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2), 0 10px 10px -5px rgba(0,0,0,0.1) !important;
}

div[role="dialog"] button[aria-label="Close"] {
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Separadores */
.custom-divider {
    margin: 0.8rem 0;
    border-top: 1px solid #334155;
}

/* Tooltips personalizados */
[data-tooltip] {
    position: relative;
    cursor: help;
}
[data-tooltip]:before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 8px;
    background: #1e293b;
    color: white;
    font-size: 11px;
    border-radius: 4px;
    white-space: nowrap;
    display: none;
    z-index: 1000;
}
[data-tooltip]:hover:before {
    display: block;
}
</style>
""", unsafe_allow_html=True)

# Header con título
st.markdown("""
<div class="app-header">
    <div>
        <h3>🎯 Fiscalización — Deuda Presunta</h3>
        <p>Sistema integral de gestión y seguimiento de empresas</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Botón Volver
col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver al inicio", key="btn_volver", help="Volver al portal principal"):
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

def traer_registros_con_legajo():
    registros, offset = [], 0
    while True:
        r = supabase.table("padron_deuda_presunta") \
            .select("*") \
            .not_.is_("leg", "null") \
            .range(offset, offset + 999).execute()
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
        r = supabase.table("padron_deuda_presunta") \
            .select("*") \
            .eq("leg", legajo) \
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

def generar_excel_para_mailing(df_seleccionado, fecha_vto_str):
    """Genera Excel con formato ordenado: CUIT, RAZON SOCIAL, LEGAJO, VTO ASIGNADO"""
    df_export = pd.DataFrame()
    df_export['CUIT'] = df_seleccionado['cuit'].astype(str)
    df_export['RAZON SOCIAL'] = df_seleccionado['razon_social'].astype(str)
    df_export['LEGAJO'] = df_seleccionado['leg'].astype(str)
    df_export['VTO ASIGNADO'] = fecha_vto_str
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Mailing', index=False)
        
        # Ajustar ancho de columnas
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
    columnas = ['id', 'cuit', 'razon_social', 'localidad', 'calle', 'numero', 
                'leg', 'vto', 'mail_enviado', 'acta', 'estado_gestion',
                'tel_dom_legal', 'tel_dom_real', 'email']
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
                columnas = ['id', 'cuit', 'razon_social', 'localidad', 'calle', 'numero', 
                            'vto', 'mail_enviado', 'acta', 'estado_gestion',
                            'tel_dom_legal', 'tel_dom_real', 'email']
                df_excel = df[[c for c in columnas if c in df.columns]]
                nombre_hoja = f"{ins['nombre'].split(',')[0][:20]} {ins['legajo']}"
                df_excel.to_excel(writer, sheet_name=nombre_hoja, index=False)
    return output.getvalue()

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Cargar Padrón",
    "✏️ Gestión de Legajos",
    "📧 Solicitar Actas",
    "📋 Subir Actas",
    "👥 Inspectores"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — Cargar Padrón
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### 📥 Cargar Padrón de Deuda Presunta")
    archivo = st.file_uploader("Seleccionar archivo Excel", type=["xls","xlsx"], key="upload_padron")

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
            c1.metric("📊 Total", len(registros))
            c2.metric("✨ Nuevos", len(nuevos))
            c3.metric("🔄 Duplicados", dupl)

            if nuevos:
                if st.button("✅ Confirmar carga", type="primary"):
                    with st.spinner("Insertando registros..."):
                        n = 0
                        for i in range(0, len(nuevos), 100):
                            res = supabase.table("padron_deuda_presunta").insert(nuevos[i:i+100]).execute()
                            n += len(res.data)
                    st.success(f"✅ {n} registros insertados correctamente.")
            else:
                st.warning("⚠️ No hay registros nuevos para insertar.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos (DISEÑO MEJORADO)
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### ✏️ Gestión de Legajos y Fechas de Vencimiento")

    total_general = supabase.table("padron_deuda_presunta").select("id", count="exact").execute().count
    con_legajo    = supabase.table("padron_deuda_presunta").select("id", count="exact").not_.is_("leg", "null").execute().count
    sin_legajo_total = total_general - con_legajo

    # KPI Cards mejoradas - más compactas
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f"""
        <div class="kpi-card kpi-total">
            <h1>{total_general:,}</h1>
            <p>📊 TOTAL REGISTROS</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="kpi-card kpi-con-legajo">
            <h1>{con_legajo:,}</h1>
            <p>✅ CON LEGAJO ASIGNADO</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown(f"""
        <div class="kpi-card kpi-sin-legajo">
            <h1>{sin_legajo_total:,}</h1>
            <p>⚠️ SIN LEGAJO ASIGNADO</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Sección colapsable de inspectores
    with st.expander("👥 Ver distribución por inspector", expanded=False):
        st.markdown("##### Asignación actual por inspector")
        inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
        if inspectores.data:
            # Mostrar en 3 filas según cantidad
            cols_per_row = 5
            for i in range(0, len(inspectores.data), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, ins in enumerate(inspectores.data[i:i+cols_per_row]):
                    count = supabase.table("padron_deuda_presunta").select("id", count="exact").eq("leg", ins['legajo']).execute().count
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="inspector-card">
                            <h3>{ins['nombre'].split(',')[0]}</h3>
                            <h1>{count}</h1>
                            <p>Legajo: {ins['legajo']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No hay inspectores cargados en el sistema")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Panel de botones organizado en 4 grupos
    st.markdown("##### 🎮 Panel de acciones")
    
    # Fila 1: Acción principal
    col_guardar, col_spacer = st.columns([1, 5])
    with col_guardar:
        guardar_click = st.button("💾 GUARDAR CAMBIOS", type="secondary", use_container_width=True, help="Guardar todos los cambios realizados en la tabla")
    
    # Fila 2: Gestión y Mantenimiento
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="gestion-button">', unsafe_allow_html=True)
        if st.button("🤖 Asignar Legajos", use_container_width=True, help="Asignar legajos automáticamente según dirección"):
            st.session_state.asignar_legajos = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="gestion-button">', unsafe_allow_html=True)
        if st.button("📧 Preparar Mails", use_container_width=True, help="Preparar mailing masivo"):
            st.session_state.preparar_mails = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="mantenimiento-button">', unsafe_allow_html=True)
        if st.button("🗑 Eliminar sel.", use_container_width=True, help="Eliminar registros seleccionados"):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="mantenimiento-button">', unsafe_allow_html=True)
        if st.button("🗑 Eliminar TODO", use_container_width=True, help="Eliminar TODOS los registros (requiere confirmación)"):
            st.session_state.confirmar_del_todo = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="mantenimiento-button">', unsafe_allow_html=True)
        if st.button("↺ Resetear filtros", use_container_width=True, help="Limpiar todos los filtros aplicados"):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fila 3: Informes
    col_inf1, col_inf2, col_inf3, col_inf4 = st.columns(4)
    with col_inf1:
        st.markdown('<div class="informe-button">', unsafe_allow_html=True)
        if st.button("📄 Inf. NO asignados", use_container_width=True, help="Generar informe de registros sin legajo"):
            st.session_state.generar_informe = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col_inf2:
        st.markdown('<div class="informe-button">', unsafe_allow_html=True)
        if st.button("📊 Inf. ASIGNADOS", use_container_width=True, help="Generar informe de todos los registros con legajo"):
            st.session_state.generar_informe_asignados = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col_inf3:
        st.markdown('<div class="informe-button">', unsafe_allow_html=True)
        if st.button("📊 Inf. POR INSPECTOR", use_container_width=True, help="Generar informe detallado por inspector"):
            st.session_state.generar_informe_por_inspector = True
        st.markdown('</div>', unsafe_allow_html=True)
    with col_inf4:
        st.markdown('<div class="mantenimiento-button">', unsafe_allow_html=True)
        if st.button("⟳ Recargar", use_container_width=True, help="Recargar la página"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ **ATENCIÓN:** Esta acción eliminará **TODOS** los registros de la base de datos. Esta operación es irreversible.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ Sí, eliminar todo", type="primary"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                st.rerun()
        with col_no:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    # ── DIÁLOGO FLOTANTE DE PREPARAR MAILS ───────────────────────────────────
    if st.session_state.get('preparar_mails'):
        @st.dialog("📧 PREPARAR MAILS")
        def mostrar_dialogo_preparar_mails():
            query = supabase.table("padron_deuda_presunta")\
                .select("*")\
                .not_.is_("leg", "null")\
                .eq("mail_enviado", "NO")\
                .is_("vto", "null")\
                .execute()
            
            df_candidatos = pd.DataFrame(query.data) if query.data else pd.DataFrame()
            
            if df_candidatos.empty:
                st.warning("No hay registros disponibles")
                if st.button("Finalizar"):
                    st.session_state.preparar_mails = False
                    st.rerun()
                return
            
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
                
                batch_size = 50
                for i in range(0, total_registros, batch_size):
                    batch = df_seleccionado.iloc[i:i+batch_size]
                    for _, row in batch.iterrows():
                        supabase.table("padron_deuda_presunta").update({
                            "vto": fecha_str,
                            "mail_enviado": "SI"
                        }).eq("id", row['id']).execute()
                    
                    progress_bar.progress(min((i + batch_size) / total_registros, 1.0))
                    time.sleep(0.05)
                
                progress_bar.progress(1.0)
                
                excel_data = generar_excel_para_mailing(df_seleccionado, fecha_mostrar)
                st.session_state.excel_descarga = excel_data
                st.session_state.nombre_excel = f"MAILING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                st.session_state.preparar_mails = False
                st.rerun()
            
            if st.button("✅ Finalizar", use_container_width=True):
                st.session_state.preparar_mails = False
                st.rerun()
        
        mostrar_dialogo_preparar_mails()

    # ── DESCARGA FUERA DEL MODAL ─────────────────────────────────────────────
    if st.session_state.get("excel_descarga"):
        st.success("🎉 ¡Mailing generado exitosamente! Descargue el archivo:")
        
        col_desc1, col_desc2, col_desc3 = st.columns([1, 2, 1])
        with col_desc2:
            st.download_button(
                label="📥 DESCARGAR EXCEL",
                data=st.session_state.excel_descarga,
                file_name=st.session_state.nombre_excel,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
            
            if st.button("✅ FINALIZAR", use_container_width=True):
                del st.session_state["excel_descarga"]
                del st.session_state["nombre_excel"]
                st.rerun()

    # ── GENERAR INFORMES ─────────────────────────────────────────────────────
    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe de no asignados..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(
                    label="📥 DESCARGAR TXT",
                    data=contenido_txt.encode('utf-8'),
                    file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                st.info(f"📊 {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo")
        st.session_state.generar_informe = False

    if st.session_state.get('generar_informe_asignados'):
        with st.spinner("Generando informe de asignados..."):
            registros_con_legajo = traer_registros_con_legajo()
            if registros_con_legajo:
                excel_data = generar_excel_asignados(registros_con_legajo)
                st.download_button(
                    label="📥 DESCARGAR EXCEL (TODOS)",
                    data=excel_data,
                    file_name=f"INFORME_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.info(f"📊 {len(registros_con_legajo)} registros con legajo")
            else:
                st.success("✅ No hay registros con legajo")
        st.session_state.generar_informe_asignados = False

    if st.session_state.get('generar_informe_por_inspector'):
        with st.spinner("Generando informe por inspector..."):
            excel_data = generar_excel_por_inspector()
            st.download_button(
                label="📥 DESCARGAR EXCEL (POR INSPECTOR)",
                data=excel_data,
                file_name=f"INFORME_POR_INSPECTOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ Informe generado - Una hoja por inspector")
        st.session_state.generar_informe_por_inspector = False

    # ── ASIGNACIÓN AUTOMÁTICA DE LEGAJOS ─────────────────────────────────────
    if st.session_state.get('asignar_legajos'):
        st.info("⏳ Asignando legajos automáticamente...")
        
        with st.spinner("Cargando configuración de inspectores..."):
            insp_loc   = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos  = cargar_sinonimos()
            lkp_loc    = construir_lookup_localidades(insp_loc)
            lkp_zonas  = construir_lookup_zonas(insp_zonas)
            lkp_sin    = construir_lookup_sinonimos(sinonimos)

        with st.spinner("Cargando registros sin legajo..."):
            registros = traer_registros_sin_legajo()

        if not registros:
            st.info("No hay registros sin legajo para asignar.")
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
                status_text.markdown(f"🔄 Procesando {int(percent * 100)}% - {reg.get('razon_social', 'Sin nombre')[:40]}...")
                
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

            with st.spinner("Guardando asignaciones..."):
                guardados = guardar_legajos_en_batch(asig)

            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {
                "asignados": guardados,
                "no_asignados": len(no_asig),
                "detalle": no_asig,
            }
            st.success(f"✅ {guardados} legajos asignados correctamente, {len(no_asig)} sin coincidencia.")
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
            st.download_button(
                label="📥 DESCARGAR INFORME DETALLADO",
                data=contenido_informe.encode('utf-8'),
                file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            with st.expander(f"📋 Ver detalles de {res['no_asignados']} registros no asignados"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    # ── FILTROS Y TABLA EDITABLE ────────────────────────────────────────────
    st.markdown("##### 🔍 Filtros de búsqueda")
    
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1:
        st.markdown('<p class="filtro-titulo">📌 CUIT</p>', unsafe_allow_html=True)
        filtro_cuit = st.text_input("CUIT", key="input_filtro_cuit", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with f2:
        st.markdown('<p class="filtro-titulo">🏢 Razón Social</p>', unsafe_allow_html=True)
        filtro_razon = st.text_input("Razón", key="input_filtro_razon", placeholder="Razón social", label_visibility="collapsed")
    with f3:
        st.markdown('<p class="filtro-titulo">📍 Localidad</p>', unsafe_allow_html=True)
        locs = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with f4:
        st.markdown('<p class="filtro-titulo">✉️ Mail enviado</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with f5:
        st.markdown('<p class="filtro-titulo">🆔 Legajo</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with f6:
        st.markdown('<p class="filtro-titulo">🏠 Calle</p>', unsafe_allow_html=True)
        filtro_calle_aprox = st.text_input("Calle", key="filtro_calle_aproximacion", placeholder="Ej: Yrigoyen", label_visibility="collapsed")

    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")

    datos = q.execute()

    if not datos.data:
        st.info("Sin datos para mostrar.")
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

        col_pag1, col_pag2, col_pag3 = st.columns([1, 3, 1])
        with col_pag1:
            if st.button("◀ Anterior", disabled=st.session_state.pagina_actual <= 1):
                st.session_state.pagina_actual -= 1
                st.rerun()
        with col_pag2:
            st.caption(f"Página {st.session_state.pagina_actual} de {pages} | Total: {total} registros")
        with col_pag3:
            if st.button("Siguiente ▶", disabled=st.session_state.pagina_actual >= pages):
                st.session_state.pagina_actual += 1
                st.rerun()

        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        for col in df_p.columns:
            df_p[col] = df_p[col].apply(lambda x: "" if pd.isna(x) else str(x))
        
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(lambda x: fmt_fecha(x) if x and x != "" else "")

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

        if st.checkbox("📌 Seleccionar todos los registros de esta página"):
            df_ed["🗑️"] = True

        edited = st.data_editor(
            df_ed, use_container_width=True, height=500,
            column_config={"🗑️": st.column_config.CheckboxColumn("Eliminar")},
            key=f"editor_{st.session_state.pagina_actual}",
        )

        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel
        if ids_sel:
            st.info(f"📌 {len(ids_sel)} registro(s) seleccionado(s) para eliminar")

        if guardar_click:
            mods = 0
            errores_fecha = 0
            with st.spinner("Guardando cambios..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd = {}
                    
                    nv = row.get('LEG')
                    if nv != orig.get('leg'):
                        if nv and str(nv).strip():
                            try:
                                upd['leg'] = int(float(str(nv)))
                            except:
                                upd['leg'] = None
                        else:
                            upd['leg'] = None
                    
                    nv = row.get('VTO')
                    if nv != orig.get('vto'):
                        if nv and str(nv).strip():
                            fecha_ok = norm_fecha(str(nv))
                            if fecha_ok:
                                upd['vto'] = fecha_ok
                            else:
                                errores_fecha += 1
                        else:
                            upd['vto'] = None
                    
                    nv = row.get('MAIL ENVIADO') or 'NO'
                    if nv not in ('SI', 'NO'):
                        nv = 'NO'
                    if nv != orig.get('mail_enviado'):
                        upd['mail_enviado'] = nv
                    
                    nv = row.get('ACTA')
                    if nv != orig.get('acta'):
                        upd['acta'] = nv if nv and str(nv).strip() else None
                    
                    nv = row.get('ESTADO GESTION') or 'PENDIENTE'
                    if nv != orig.get('estado_gestion'):
                        upd['estado_gestion'] = nv
                    
                    if upd:
                        supabase.table("padron_deuda_presunta").update(upd).eq("id", row['ID']).execute()
                        mods += 1

            if mods > 0:
                st.success(f"✅ {mods} registros actualizados correctamente.")
                if errores_fecha > 0:
                    st.warning(f"⚠️ {errores_fecha} fecha(s) no se pudieron guardar (formato incorrecto). Use DD/MM/YYYY.")
                st.rerun()
            elif errores_fecha > 0:
                st.warning(f"No se guardaron cambios. {errores_fecha} fecha(s) con formato incorrecto.")
            else:
                st.info("No se detectaron cambios para guardar.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Solicitar Actas
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.info("📧 **Solicitar Actas** — Módulo en construcción. Próximamente disponible.")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Subir Actas
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 📋 Subir Actas (CSV)")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 0.75rem 1rem; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.8rem;">El sistema busca coincidencias por <strong>CUIT + LEGAJO + FECHA VTO</strong>
        en registros con <strong>MAIL ENVIADO = SI</strong> y actualiza el estado a FINALIZADO.</p>
    </div>
    """, unsafe_allow_html=True)

    csv_file = st.file_uploader("Seleccionar archivo CSV", type=["csv"], key="upload_actas_csv")

    if csv_file:
        st.caption(f"Archivo seleccionado: **{csv_file.name}**")

        try:
            df_prev = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='utf-8-sig')
            with st.expander("📋 Vista previa (primeras 5 filas)"):
                st.dataframe(df_prev.head(5), use_container_width=True, height=200)
        except Exception:
            pass

        if st.button("📋 Procesar y actualizar actas", type="primary"):
            with st.spinner("Procesando archivo..."):
                try:
                    df4 = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='utf-8-sig')
                except Exception:
                    df4 = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='latin-1')

                df4.columns = [str(c).strip().upper() for c in df4.columns]

                col_cuit = col_leg = col_vto = col_acta = None
                for c in df4.columns:
                    cu = c.upper()
                    if 'CUIT' in cu and not col_cuit: col_cuit = c
                    if ('LEG' in cu or 'LEGAJO' in cu) and not col_leg: col_leg = c
                    if ('VTO' in cu or 'FECHA_VTO' in cu) and not col_vto: col_vto = c
                    if ('NRO_ACTA' in cu or cu == 'ACTA') and not col_acta: col_acta = c

                if not all([col_cuit, col_leg, col_vto]):
                    st.error(f"❌ Columnas no detectadas — CUIT: {col_cuit}, LEG: {col_leg}, VTO: {col_vto}")
                else:
                    st.caption(f"✅ Columnas detectadas: CUIT=`{col_cuit}` · LEG=`{col_leg}` · VTO=`{col_vto}`")
                    
                    actualizados = 0
                    no_encontrados = 0
                    bar = st.progress(0)

                    for i, row in df4.iterrows():
                        cuit = re.sub(r'[\.\-,\s]', '', str(row[col_cuit]).strip())
                        leg = str(row[col_leg]).strip() if row[col_leg] else None
                        vto = norm_fecha(row[col_vto])
                        acta = str(row[col_acta]) if col_acta and pd.notna(row.get(col_acta)) else "ACTUALIZADO"

                        if cuit and leg and vto:
                            try:
                                resultado = (supabase.table("padron_deuda_presunta")
                                           .select("id")
                                           .eq("cuit", cuit)
                                           .eq("leg", leg)
                                           .eq("vto", vto)
                                           .eq("mail_enviado", "SI")
                                           .execute())
                                
                                if resultado.data:
                                    for reg in resultado.data:
                                        supabase.table("padron_deuda_presunta") \
                                            .update({"acta": acta, "estado_gestion": "FINALIZADO"}) \
                                            .eq("id", reg['id']).execute()
                                    actualizados += len(resultado.data)
                                else:
                                    no_encontrados += 1
                            except Exception as e:
                                st.error(f"Error fila {i}: {e}")

                        bar.progress((i + 1) / len(df4))

                    bar.empty()
                    col_ok, col_no = st.columns(2)
                    col_ok.metric("✅ Actualizados", actualizados)
                    col_no.metric("❌ No encontrados", no_encontrados)

                    if actualizados > 0:
                        st.success(f"✅ {actualizados} actas actualizadas correctamente.")
                    if no_encontrados > 0:
                        st.warning(f"⚠️ {no_encontrados} filas sin coincidencia en la base de datos.")

# ══════════════════════════════════════════════════════════════════
# TAB 5 — INSPECTORES
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 👥 Gestión de Inspectores y Zonas")
    st.markdown("Acceda al panel completo de administración de inspectores, localidades y calles de Mar del Plata.")
    
    url_zonas = "https://buscador-osecac-6jztx7xjhgkvcaubfinn5y.streamlit.app/zonas"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid #3b82f6;">
            <h3 style="color: #3b82f6; margin: 0 0 0.3rem 0; font-size: 1rem;">🗺️ Zonas de Inspectores</h3>
            <p style="color: #94a3b8; margin-bottom: 0.5rem; font-size: 0.7rem;">Administre inspectores, asigne localidades y configure calles para Mar del Plata</p>
            <a href="{url_zonas}" target="_blank">
                <button style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; padding: 0.4rem 1.5rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 500;">
                    🔗 IR A INSPECTORES Y ZONAS
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption("💡 También puede acceder directamente desde el enlace: " + url_zonas)
