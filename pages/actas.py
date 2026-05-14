import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
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
    font-weight: 400 !important;
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    border-radius: 4px !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.4 !important;
}
div[data-testid="stButton"] > button:hover { background: #475569 !important; }
div[data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #1d4ed8 !important;
    color: #fff !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background: #1d4ed8 !important; }
.btn-danger div[data-testid="stButton"] > button {
    background: #7f1d1d !important;
    border-color: #991b1b !important;
    color: #fca5a5 !important;
}
.btn-success div[data-testid="stButton"] > button {
    background: #065f46 !important;
    border-color: #059669 !important;
    color: #a7f3d0 !important;
}
#MainMenu, footer, header { display: none !important; }
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div { font-size: 0.8rem !important; padding: 0.2rem 0.5rem !important; }
.msg { padding: 0.5rem 0.75rem; border-radius: 4px; font-size: 0.78rem;
       border-left: 3px solid; margin: 0.4rem 0; line-height: 1.5; }
.msg-info    { background: #1e293b; border-color: #3b82f6; color: #cbd5e1; }
.msg-success { background: #064e3b; border-color: #10b981; color: #6ee7b7; }
.msg-warning { background: #451a03; border-color: #f59e0b; color: #fcd34d; }
.stDataFrame { font-size: 0.78rem !important; }
.big-number {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 12px;
    padding: 0.5rem 1rem;
    text-align: center;
    border: 1px solid #3b82f6;
}
.big-number h1 { margin: 0; font-size: 2rem; color: #3b82f6; }
.big-number p { margin: 0; font-size: 0.7rem; color: #94a3b8; }
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

# ── Utilidades de limpieza ────────────────────────────────────────────────────
def limpiar_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return None if s.lower() in ('', 'nan', 'none', 'null', 'nat') else s

def limpiar_cuit(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    if 'E' in s.upper():
        try:
            return str(int(float(s)))
        except Exception:
            pass
    return re.sub(r'[\.\-,\s]', '', s)

def excel_serial_fecha(n):
    try:
        return (datetime(1899, 12, 30) + pd.Timedelta(days=int(n))).strftime("%Y-%m-%d")
    except Exception:
        return None

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
    if s.isdigit():
        return excel_serial_fecha(s)
    try:
        return pd.to_datetime(s, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def fmt_fecha(v):
    if not v:
        return None
    try:
        if pd.isna(v):
            return None
    except TypeError:
        pass
    try:
        if isinstance(v, (pd.Timestamp, datetime)):
            return v.strftime('%d/%m/%Y')
        s = str(v).strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', s):
            return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        return s
    except Exception:
        return str(v) if v else None

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

# ── Datos de inspectores para asignación automática ────────────────────────────
INSPECTORES_POR_LOCALIDAD = {
    "RODRIGUEZ MAXIMILIANO": {"legajo": "7713", "localidades": [
        "MAR DE AJO", "SAN BERNARDO", "COSTA AZUL", "LA LUCILA DEL MAR",
        "NUEVA ATLANTIS", "AGUAS VERDES", "GRAL. MADARIAGA", "SANTA CLARA DEL MAR",
        "MAR DE COBO", "BALNEARIO MAR CHIQUITA"
    ]},
    "POLINESSI JUAN JOSE": {"legajo": "9513", "localidades": [
        "VILLA GESELL", "MAR DE LAS PAMPAS", "MAR AZUL", "MIRAMAR",
        "CMTE. NICANOR OTAMENDI", "MECHONGUE", "SIERRA DE LOS PADRES", "ESTACION CAMET"
    ]},
    "LOPEZ MARTIN": {"legajo": "9983", "localidades": [
        "SANTA TERESITA", "MAR DEL TUYU", "COSTA DEL ESTE", "LAS TONINAS", "BATAN"
    ]},
    "CARBAYO VICTOR HUGO": {"legajo": "9220", "localidades": [
        "VIVORATA", "CNEL. VIDAL", "GRAL. PIRAN", "LAS ARMAS", "MAIPU",
        "LABARDEN", "GRAL. GUIDO", "DOLORES", "CASTELLI", "GRAL. CONESA"
    ]},
    "GARCIA JUAN PAULO": {"legajo": "7952", "localidades": [
        "PINAMAR", "CARILO", "OSTENDE", "VALERIA DEL MAR",
        "SAN CLEMENTE DEL TUYU", "GRAL. LAVALLE", "CHAPADMALAL"
    ]}
}

INSPECTORES_CALLES_MDQ = {
    "GARCIA JUAN PAULO": {"legajo": "7952", "calles": [
        ("COLON", "PAR", 2000, 2500), ("SAN JUAN", "PAR", 2100, 5400),
        ("PEHUAJO", "PAR", 2100, 5400), ("INDEPENDENCIA", "IMPAR", 2100, 3500),
        ("J.P. RAMOS", "IMPAR", 3500, 5400), ("MARIO BRAVO", "AMBOS", 2000, 2500),
        ("H. YRIGOYEN", "PAR", 1600, 2100), ("SAN LUIS", "IMPAR", 1600, 2100),
        ("COLON", "IMPAR", 1600, 1800), ("P.P. RAMOS", "AMBOS", 1600, 1800),
        ("ACHA", "PAR", 3500, 5400), ("J.B. JUSTO", "AMBOS", 0, 500),
        ("MARIO BRAVO", "AMBOS", 0, 500), ("TRABAJADORES", "AMBOS", 3500, 5400),
        ("RUTA 11", "AMBOS", 5400, 9000), ("CALLE 515", "AMBOS", 0, 3000),
        ("JORGE NEWBERY", "AMBOS", 5400, 9000), ("SALTA", "AMBOS", 2100, 5300),
        ("JUJUY", "AMBOS", 2100, 5300), ("ESPAÑA", "AMBOS", 2100, 5300),
        ("20 SEPTIEMBRE", "AMBOS", 2100, 5300), ("14 JULIO", "AMBOS", 2100, 5300),
        ("DORREGO", "AMBOS", 2100, 5300), ("GUIDO", "AMBOS", 2100, 5300),
        ("FUNES", "AMBOS", 2100, 5300), ("OLAZABAL", "AMBOS", 2100, 5300),
        ("ALMIRANTE BROWN", "AMBOS", 2100, 5300), ("FALUCHO", "AMBOS", 2100, 5300),
        ("GASCON", "AMBOS", 2100, 5300), ("ALBERTI", "AMBOS", 2100, 5300),
        ("MATHEU", "AMBOS", 2100, 5300), ("QUINTANA", "AMBOS", 2100, 5300),
        ("SAAVEDRA", "AMBOS", 2100, 5300), ("ROCA", "AMBOS", 2100, 5300),
        ("PEÑA", "AMBOS", 2100, 5300), ("PRIMERA JUNTA", "AMBOS", 2100, 5300),
        ("RODRIGUEZ PEÑA", "AMBOS", 2100, 5300), ("LAPRIDA", "AMBOS", 2100, 5300),
        ("AZCUENAGA", "AMBOS", 2100, 5300), ("LARREA", "AMBOS", 2100, 5300),
        ("VIEYTES", "AMBOS", 2100, 5300), ("PASO", "AMBOS", 2100, 5300),
        ("CASTELLI", "AMBOS", 2100, 5300), ("GARAY", "AMBOS", 2100, 5300),
        ("RAWSON", "AMBOS", 2100, 5300), ("MITRE", "AMBOS", 1600, 2000),
        ("SAN MARTIN", "AMBOS", 1600, 2000), ("RIVADAVIA", "AMBOS", 1600, 2000),
        ("BELGRANO", "AMBOS", 1600, 2000), ("MORENO", "AMBOS", 1600, 2000),
        ("BOLIVAR", "AMBOS", 1600, 2000), ("POSADAS", "AMBOS", 3600, 5300),
        ("RONDEAU", "AMBOS", 3600, 5300), ("BERMEJO", "AMBOS", 3600, 5300),
        ("FIGUEROA ALCORTA", "AMBOS", 3600, 5300), ("MARTINEZ DE HOZ", "AMBOS", 3600, 5300),
        ("SOLIS", "AMBOS", 3600, 5300), ("GABOTO", "AMBOS", 3600, 5300),
        ("ELCANO", "AMBOS", 3600, 5300), ("MAGALLANES", "AMBOS", 3600, 5300),
        ("12 DE OCTUBRE", "AMBOS", 3600, 5300), ("AYOLAS", "AMBOS", 3600, 5300),
        ("IRALA", "AMBOS", 3600, 5300), ("VERTIZ", "AMBOS", 3600, 5300),
        ("AZOPARDO", "AMBOS", 3600, 5300), ("BOUCHARD", "AMBOS", 3600, 5300),
        ("PIEDRABUENA", "AMBOS", 3600, 5300), ("RODRIGUEZ", "AMBOS", 3600, 5300),
        ("BESTO", "AMBOS", 3600, 5300), ("TRIPULANTES DEL FOURNIER", "AMBOS", 3600, 5300),
        ("ROSALES", "AMBOS", 3600, 5300), ("FORTUNATO DE LA PLAZA", "AMBOS", 3600, 5300),
        ("LEBENSOHN", "AMBOS", 3600, 5300), ("MALABIA", "AMBOS", 3600, 5300),
        ("ARANA Y GOIRI", "AMBOS", 3600, 5300), ("ORTIZ DE ZARATE", "AMBOS", 3600, 5300),
        ("GUANAHANI", "AMBOS", 3600, 5300), ("DON ARTURO", "AMBOS", 5500, 8900),
        ("MARGARITAS", "AMBOS", 5500, 8900), ("JAZMINES", "AMBOS", 5500, 8900),
        ("LOS ALERCES", "AMBOS", 5500, 8900), ("LOS SAUCES", "AMBOS", 5500, 8900)
    ]},
    "CARBAYO VICTOR HUGO": {"legajo": "9220", "calles": [
        ("COLON", "PAR", 2199, 3199), ("BUENOS AIRES", "IMPAR", 2201, 4499),
        ("SAN LUIS", "IMPAR", 2199, 3199), ("INDEPENDENCIA", "PAR", 2201, 4499),
        ("SALTA", "AMBOS", 2100, 5300), ("JUJUY", "AMBOS", 2100, 5300),
        ("ESPAÑA", "AMBOS", 2100, 5300), ("20 SEPTIEMBRE", "AMBOS", 2100, 5300),
        ("14 JULIO", "AMBOS", 2100, 5300), ("DORREGO", "AMBOS", 2100, 5300),
        ("GUIDO", "AMBOS", 2100, 5300), ("FUNES", "AMBOS", 2100, 5300),
        ("OLAZABAL", "AMBOS", 2100, 5300), ("ALMIRANTE BROWN", "AMBOS", 2100, 5300),
        ("FALUCHO", "AMBOS", 2100, 5300), ("GASCON", "AMBOS", 2100, 5300),
        ("ALBERTI", "AMBOS", 2100, 5300), ("MATHEU", "AMBOS", 2100, 5300),
        ("QUINTANA", "AMBOS", 2100, 5300), ("SAAVEDRA", "AMBOS", 2100, 5300),
        ("ROCA", "AMBOS", 2100, 5300), ("PEÑA", "AMBOS", 2100, 5300),
        ("PRIMERA JUNTA", "AMBOS", 2100, 5300), ("RODRIGUEZ PEÑA", "AMBOS", 2100, 5300),
        ("LAPRIDA", "AMBOS", 2100, 5300), ("AZCUENAGA", "AMBOS", 2100, 5300),
        ("LARREA", "AMBOS", 2100, 5300), ("VIEYTES", "AMBOS", 2100, 5300),
        ("PASO", "AMBOS", 2100, 5300), ("CASTELLI", "AMBOS", 2100, 5300),
        ("GARAY", "AMBOS", 2100, 5300), ("RAWSON", "AMBOS", 2100, 5300)
    ]},
    "RODRIGUEZ MAXIMILIANO": {"legajo": "7713", "calles": [
        ("CATAMARCA", "IMPAR", 500, 2100), ("COLON", "IMPAR", 3500, 3100),
        ("JARA", "PAR", 1, 9999), ("TEJEDOR CARLOS", "PAR", 1, 9999),
        ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("FELIX U. CAMET", "AMBOS", 1, 9999),
        ("MITRE", "AMBOS", 1600, 2000), ("SAN MARTIN", "AMBOS", 1600, 2000),
        ("RIVADAVIA", "AMBOS", 1600, 2000), ("BELGRANO", "AMBOS", 1600, 2000),
        ("MORENO", "AMBOS", 1600, 2000), ("BOLIVAR", "AMBOS", 1600, 2000)
    ]},
    "POLINESSI JUAN JOSE": {"legajo": "9513", "calles": [
        ("COLON", "IMPAR", 6301, 9999), ("CHAMPAGNAT", "IMPAR", 2199, 9999),
        ("CATAMARCA", "PAR", 2198, 3098), ("H. YRIGOYEN", "IMPAR", 2199, 9999),
        ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("FELIX U. CAMET", "AMBOS", 1, 9999),
        ("DON ARTURO", "AMBOS", 5500, 8900), ("MARGARITAS", "AMBOS", 5500, 8900),
        ("JAZMINES", "AMBOS", 5500, 8900), ("LOS ALERCES", "AMBOS", 5500, 8900),
        ("LOS SAUCES", "AMBOS", 5500, 8900)
    ]},
    "LOPEZ MARTIN": {"legajo": "9983", "calles": [
        ("COLON", "IMPAR", 1, 9999), ("SAN LUIS", "PAR", 1, 9999),
        ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("SANTA FE", "IMPAR", 1, 9999),
        ("POSADAS", "AMBOS", 3600, 5300), ("RONDEAU", "AMBOS", 3600, 5300),
        ("BERMEJO", "AMBOS", 3600, 5300), ("FIGUEROA ALCORTA", "AMBOS", 3600, 5300),
        ("MARTINEZ DE HOZ", "AMBOS", 3600, 5300), ("SOLIS", "AMBOS", 3600, 5300),
        ("GABOTO", "AMBOS", 3600, 5300), ("ELCANO", "AMBOS", 3600, 5300),
        ("MAGALLANES", "AMBOS", 3600, 5300), ("12 DE OCTUBRE", "AMBOS", 3600, 5300),
        ("AYOLAS", "AMBOS", 3600, 5300), ("IRALA", "AMBOS", 3600, 5300),
        ("VERTIZ", "AMBOS", 3600, 5300), ("AZOPARDO", "AMBOS", 3600, 5300),
        ("BOUCHARD", "AMBOS", 3600, 5300), ("PIEDRABUENA", "AMBOS", 3600, 5300),
        ("RODRIGUEZ", "AMBOS", 3600, 5300), ("BESTO", "AMBOS", 3600, 5300),
        ("TRIPULANTES DEL FOURNIER", "AMBOS", 3600, 5300), ("ROSALES", "AMBOS", 3600, 5300),
        ("FORTUNATO DE LA PLAZA", "AMBOS", 3600, 5300), ("LEBENSOHN", "AMBOS", 3600, 5300),
        ("MALABIA", "AMBOS", 3600, 5300), ("ARANA Y GOIRI", "AMBOS", 3600, 5300),
        ("ORTIZ DE ZARATE", "AMBOS", 3600, 5300), ("GUANAHANI", "AMBOS", 3600, 5300)
    ]}
}

def normalizar_calle(calle):
    calle = calle.upper().strip()
    for prefijo in ['AV ', 'AV.', 'AVENIDA ', 'CALLE ', 'C/']:
        if calle.startswith(prefijo):
            calle = calle[len(prefijo):]
    for sufijo in [' AV', ' AV.', ' AVENIDA']:
        if calle.endswith(sufijo):
            calle = calle[:-len(sufijo)]
    return calle.strip()

def asignar_legajo_por_direccion(localidad, calle, numero):
    if localidad.upper() != "MAR DEL PLATA":
        for inspector, data in INSPECTORES_POR_LOCALIDAD.items():
            for loc in data["localidades"]:
                if loc == localidad.upper():
                    return data["legajo"]
        return None
    
    if not calle or not numero:
        return None
    
    try:
        numero_limpio = int(re.sub(r'\D', '', str(numero)))
    except:
        return None
    
    lado = "PAR" if numero_limpio % 2 == 0 else "IMPAR"
    calle_norm = normalizar_calle(calle)
    
    for inspector, data in INSPECTORES_CALLES_MDQ.items():
        for calle_data in data["calles"]:
            calle_zona = normalizar_calle(calle_data[0])
            if calle_zona == calle_norm:
                lado_zona = calle_data[1]
                desde = calle_data[2]
                hasta = calle_data[3]
                if lado_zona == "AMBOS" or lado_zona == lado:
                    if desde <= numero_limpio <= hasta:
                        return data["legajo"]
    return None

# ── Datos cacheados ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_localidades(_sb):
    r = _sb.table("padron_deuda_presunta").select("localidad").execute()
    locs = sorted({x['localidad'] for x in r.data if x.get('localidad')})
    if 'MAR DEL PLATA' in locs:
        locs.remove('MAR DEL PLATA')
        locs = ['MAR DEL PLATA'] + locs
    return locs

@st.cache_data(ttl=60)
def get_pares_existentes(_sb):
    todos, offset = [], 0
    while True:
        batch = _sb.table("padron_deuda_presunta") \
                   .select("cuit, ultima_acta") \
                   .range(offset, offset + 999).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += 1000
        if len(batch.data) < 1000:
            break
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

# ── Mapeo columnas Excel ──────────────────────────────────────────────────────
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
TITULOS = {
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
}
COLS_DISABLED = [
    'ID','CUIT','RAZON SOCIAL','DEUDA PRESUNTA','CP','CALLE','NUMERO','PISO','DPTO',
    'FECHARELDEPENDENCIA','EMAIL','TEL_DOM_LEGAL','TEL_DOM_REAL','ULTIMA ACTA',
    'DESDE','HASTA','DETECTADO','ESTADO','FECHA PAGO OBL',
    'EMPL 10-2025','EMP 11-2025','EMPL 12-2025','ACTIVIDAD','SITUACION',
]

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
                v = excel_serial_fecha(v) if v.isdigit() else norm_fecha(v)
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

# ══════════════════════════════════════════════════════════════════
# TAB 1 — Cargar Padrón
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Cargar Padrón de Deuda Presunta")
    st.markdown("""<div class="msg msg-info">
    Seleccioná el Excel del padrón. El sistema filtra duplicados por <strong>CUIT + ULTIMA ACTA</strong>
    y solo inserta registros nuevos.
    </div>""", unsafe_allow_html=True)

    archivo = st.file_uploader("Archivo Excel", type=["xls","xlsx"], key="upload_padron")

    if archivo:
        st.caption(f"Archivo: **{archivo.name}**")
        try:
            registros = procesar_excel(archivo)
            hoy = date.today().isoformat()
            for r in registros:
                r.update({'leg':None,'vto':None,'mail_enviado':'NO','acta':None,
                           'fecha_carga':hoy,'estado_gestion':'PENDIENTE'})

            pares = get_pares_existentes(supabase)
            nuevos = [r for r in registros
                      if (str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) not in pares]
            dupl   = len(registros) - len(nuevos)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(registros))
            c2.metric("Nuevos", len(nuevos))
            c3.metric("Duplicados", dupl)

            if nuevos:
                with st.expander("Vista previa (10 primeros)"):
                    df_prev = pd.DataFrame(nuevos[:10])
                    for col in ['fechareldependencia','desde','hasta','fecha_pago_obl','vto','fecha_carga']:
                        if col in df_prev.columns:
                            df_prev[col] = df_prev[col].apply(fmt_fecha)
                    st.dataframe(df_prev, use_container_width=True, height=250)

                if st.button("✅ Confirmar carga", type="primary"):
                    with st.spinner("Insertando..."):
                        n = 0
                        for i in range(0, len(nuevos), 100):
                            res = supabase.table("padron_deuda_presunta").insert(nuevos[i:i+100]).execute()
                            n += len(res.data)
                    st.markdown(f'<div class="msg msg-success">✅ {n} registros insertados.</div>', unsafe_allow_html=True)
                    get_pares_existentes.clear()
                    get_localidades.clear()
            else:
                st.markdown('<div class="msg msg-warning">⚠️ No hay registros nuevos.</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos (con botón de asignación y filtros)
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Editar Legajos y F
