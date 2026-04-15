import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import math
import numpy as np
import re
import locale
import io

# Intentar configurar locale para formato argentino
try:
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'spanish')
    except:
        pass

# ==================== CONEXIÓN CACHEADA A SUPABASE ====================
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# Configuración de página
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo mejorado
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; color: #ffffff; }
    .warning-box { background-color: #451a03; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 1rem 0; color: #ffffff; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; color: #ffffff; }
    .info-box strong, .info-box p, .info-box li { color: #ffffff !important; }
    div[data-testid="stButton"] button { background-color: #3b82f6; color: white; font-weight: 500; border: none; padding: 0.4rem 1.2rem; }
    div[data-testid="stButton"] button:hover { background-color: #2563eb; }
    .delete-btn button { background-color: #dc2626 !important; }
    .delete-btn button:hover { background-color: #b91c1c !important; }
    .reset-btn button { background-color: #64748b !important; }
    .reset-btn button:hover { background-color: #475569 !important; }
    .stDataFrame { background-color: #0f172a; }
    .stSelectbox label, .stTextInput label { color: #ffffff !important; }
    .stMetric label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-weight: 500;">Fiscalización - Deuda Presunta</h2>
    <p style="color: #94a3b8; margin: 0.3rem 0 0 0; font-size: 0.85rem;">Sistema de gestión y seguimiento</p>
</div>
""", unsafe_allow_html=True)

# Botón volver
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver"):
        st.switch_page("main.py")

st.markdown("---")

# ==================== FUNCIONES DE LIMPIEZA ====================
def formatear_numero_argentino(valor):
    if valor is None or pd.isna(valor):
        return None
    try:
        num = float(valor)
        if num.is_integer():
            return f"${int(num):,}".replace(",", ".")
        else:
            entero = int(num)
            decimal = int(round((num - entero) * 100))
            entero_formateado = f"{entero:,}".replace(",", ".")
            return f"${entero_formateado},{decimal:02d}"
    except:
        return str(valor) if valor else None

def limpiar_valor(val):
    if val is None:
        return None
    if pd.isna(val):
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        if val == int(val):
            return str(int(val))
        return str(val)
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        if math.isnan(float(val)) or math.isinf(float(val)):
            return None
        v = float(val)
        return str(int(v)) if v == int(v) else str(v)
    if isinstance(val, np.bool_):
        return bool(val)
    if val is pd.NaT:
        return None
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, str):
        val = val.strip()
        if val.lower() in ("nan", "none", "nat", ""):
            return None
        return val
    return str(val)

def excel_serial_a_fecha(n):
    try:
        n = int(n)
        fecha_base = datetime(1899, 12, 30)
        fecha = fecha_base + pd.Timedelta(days=n)
        return fecha.strftime("%Y-%m-%d")
    except Exception:
        return str(n)

def fecha_para_mostrar(valor):
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    try:
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%d/%m/%Y')
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
            # Formato ISO con T
            if re.match(r'\d{4}-\d{2}-\d{2}T', valor):
                return datetime.strptime(valor[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
            # Formato ISO con espacio
            if re.match(r'\d{4}-\d{2}-\d{2} ', valor):
                return datetime.strptime(valor[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
            # Formato ISO puro
            if re.match(r'^\d{4}-\d{2}-\d{2}$', valor):
                return datetime.strptime(valor, '%Y-%m-%d').strftime('%d/%m/%Y')
            # Ya está en DD/MM/YYYY
            if re.match(r'^\d{2}/\d{2}/\d{4}$', valor):
                return valor
            # DD/MM/YYYY con barras
            if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', valor):
                partes = valor.split('/')
                if len(partes) == 3:
                    return f"{int(partes[0]):02d}/{int(partes[1]):02d}/{partes[2]}"
            return valor
        return str(valor)
    except:
        return str(valor) if valor else None

def normalizar_fecha_para_supabase(fecha_str):
    """Convierte CUALQUIER formato de fecha a YYYY-MM-DD para Supabase"""
    if fecha_str is None or pd.isna(fecha_str):
        return None
    fecha_str = str(fecha_str).strip()
    if not fecha_str:
        return None
    
    # Ya está en formato ISO
    if re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
        return fecha_str
    
    # Formato DD/MM/YYYY o D/M/YYYY
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', fecha_str):
        partes = fecha_str.split('/')
        if len(partes) == 3:
            dia = int(partes[0])
            mes = int(partes[1])
            año = int(partes[2])
            if año > 1900 and 1 <= mes <= 12 and 1 <= dia <= 31:
                return f"{año:04d}-{mes:02d}-{dia:02d}"
    
    # Formato DD-MM-YYYY
    if re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', fecha_str):
        partes = fecha_str.split('-')
        if len(partes) == 3:
            dia = int(partes[0])
            mes = int(partes[1])
            año = int(partes[2])
            if año > 1900 and 1 <= mes <= 12 and 1 <= dia <= 31:
                return f"{año:04d}-{mes:02d}-{dia:02d}"
    
    # Formato DD.MM.YYYY
    if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', fecha_str):
        partes = fecha_str.split('.')
        if len(partes) == 3:
            dia = int(partes[0])
            mes = int(partes[1])
            año = int(partes[2])
            if año > 1900 and 1 <= mes <= 12 and 1 <= dia <= 31:
                return f"{año:04d}-{mes:02d}-{dia:02d}"
    
    # Formato YYYY-MM-DD ya está
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', fecha_str):
        partes = fecha_str.split('-')
        if len(partes) == 3:
            return f"{partes[0]}-{int(partes[1]):02d}-{int(partes[2]):02d}"
    
    # Número de Excel
    if fecha_str.isdigit():
        return excel_serial_a_fecha(int(fecha_str))
    
    return None

def fecha_para_guardar(valor):
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%Y-%m-%d')
        if isinstance(valor, str):
            return normalizar_fecha_para_supabase(valor)
        return None
    except:
        return None

def limpiar_numero_entero(valor):
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, str) and valor.isdigit():
            return int(valor)
        num = float(valor)
        if num.is_integer():
            return int(num)
        return None
    except:
        return None

def limpiar_cuit_csv(valor):
    if valor is None or pd.isna(valor):
        return None
    try:
        valor_str = str(valor).strip()
        if 'E' in valor_str.upper():
            num = float(valor_str)
            return str(int(num))
        # Limpiar puntos y guiones del CUIT
        valor_str = re.sub(r'[\.\-]', '', valor_str)
        if valor_str.isdigit():
            return valor_str
        return valor_str
    except:
        return str(valor)

def detectar_columna_csv(df, posibles_nombres):
    for col in df.columns:
        col_upper = col.upper().strip()
        for posible in posibles_nombres:
            if posible.upper() in col_upper or col_upper in posible.upper():
                return col
    return None

# ==================== FUNCIONES CON CACHÉ ====================
@st.cache_data(ttl=300)
def obtener_localidades(_supabase):
    todas = _supabase.table("padron_deuda_presunta").select("localidad").execute()
    localidades = sorted(set([l['localidad'] for l in todas.data if l.get('localidad')]))
    if 'MAR DEL PLATA' in localidades:
        localidades.remove('MAR DEL PLATA')
        localidades = ['MAR DEL PLATA'] + localidades
    return localidades

@st.cache_data(ttl=60)
def obtener_pares_existentes(_supabase):
    todos = []
    offset = 0
    batch_size = 1000
    while True:
        batch = _supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").range(offset, offset + batch_size - 1).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += batch_size
        if len(batch.data) < batch_size:
            break
    batch_none = _supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").is_("ultima_acta", "null").execute()
    for reg in batch_none.data:
        cuit = str(reg.get('cuit') or '')
        if cuit:
            todos.append({'cuit': cuit, 'ultima_acta': '*'})
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

@st.cache_data(ttl=60)
def contar_registros(_supabase, localidad, filtro_mail):
    query = _supabase.table("padron_deuda_presunta").select("*", count="exact", head=True)
    if localidad != "TODAS":
        query = query.eq("localidad", localidad)
    if filtro_mail == "SI":
        query = query.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        query = query.eq("mail_enviado", "NO")
    return query.execute().count

# ==================== MAPEO DE COLUMNAS ====================
COLUMNAS_EXCEL = [
    "DELEGACION", "LOCALIDAD", "CUIT", "RAZON SOCIAL", "DEUDA PRESUNTA",
    "CP", "CALLE", "NUMERO", "PISO", "DPTO", "FECHARELDEPENDENCIA",
    "EMAIL", "TEL_DOM_LEGAL", "TEL_DOM_REAL", "ULTIMA ACTA", "DESDE",
    "HASTA", "DETECTADO", "ESTADO", "FECHA_PAGO_OBL", "EMPL 10-2025",
    "EMP 11-2025", "EMPL 12-2025", "ACTIVIDAD", "SITUACION"
]

MAPA_COLUMNAS = {
    "DELEGACION": "delegacion", "LOCALIDAD": "localidad", "CUIT": "cuit",
    "RAZON SOCIAL": "razon_social", "DEUDA PRESUNTA": "deuda_presunta",
    "CP": "cp", "CALLE": "calle", "NUMERO": "numero", "PISO": "piso",
    "DPTO": "dpto", "FECHARELDEPENDENCIA": "fechareldependencia",
    "EMAIL": "email", "TEL_DOM_LEGAL": "tel_dom_legal", "TEL_DOM_REAL": "tel_dom_real",
    "ULTIMA ACTA": "ultima_acta", "DESDE": "desde", "HASTA": "hasta",
    "DETECTADO": "detectado", "ESTADO": "estado", "FECHA_PAGO_OBL": "fecha_pago_obl",
    "EMPL 10-2025": "empl_10_2025", "EMP 11-2025": "emp_11_2025", "EMPL 12-2025": "empl_12_2025",
    "ACTIVIDAD": "actividad", "SITUACION": "situacion"
}

COLUMNAS_MONEDA = {"deuda_presunta", "detectado"}
COLUMNAS_FECHA = {"fechareldependencia", "desde", "hasta", "fecha_pago_obl"}

TITULOS_MOSTRAR = {
    'id': 'ID', 'delegacion': 'DELEGACION', 'localidad': 'LOCALIDAD',
    'cuit': 'CUIT', 'razon_social': 'RAZON SOCIAL', 'deuda_presunta': 'DEUDA PRESUNTA',
    'cp': 'CP', 'calle': 'CALLE', 'numero': 'NUMERO', 'piso': 'PISO', 'dpto': 'DPTO',
    'fechareldependencia': 'FECHARELDEPENDENCIA', 'email': 'EMAIL',
    'tel_dom_legal': 'TEL_DOM_LEGAL', 'tel_dom_real': 'TEL_DOM_REAL',
    'ultima_acta': 'ULTIMA ACTA', 'desde': 'DESDE', 'hasta': 'HASTA',
    'detectado': 'DETECTADO', 'estado': 'ESTADO', 'fecha_pago_obl': 'FECHA PAGO OBL',
    'empl_10_2025': 'EMPL 10-2025', 'emp_11_2025': 'EMP 11-2025', 'empl_12_2025': 'EMPL 12-2025',
    'actividad': 'ACTIVIDAD', 'situacion': 'SITUACION',
    'leg': 'LEG', 'vto': 'VTO', 'mail_enviado': 'MAIL ENVIADO', 'acta': 'ACTA', 'estado_gestion': 'ESTADO GESTION'
}

# ==================== FUNCIÓN PROCESAR EXCEL ====================
def procesar_excel(archivo):
    if archivo.name.endswith('.xls'):
        df = pd.read_excel(archivo, engine='xlrd', dtype=str)
    else:
        df = pd.read_excel(archivo, engine='openpyxl', dtype=str)
    
    df.columns = [str(col).strip().upper() for col in df.columns]
    faltantes = [c for c in COLUMNAS_EXCEL if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    
    df = df[COLUMNAS_EXCEL].rename(columns=MAPA_COLUMNAS)
    registros_limpios = []
    
    for _, fila in df.iterrows():
        registro = {}
        for col_db in MAPA_COLUMNAS.values():
            val = fila.get(col_db)
            val = limpiar_valor(val)
            if isinstance(val, str):
                val = val.strip()
                if val.lower() in ("nan", "none", "nat", ""):
                    val = None
                elif val.endswith(".0") and val[:-2].lstrip("-").isdigit():
                    val = val[:-2]
                elif col_db in COLUMNAS_FECHA and val and val.isdigit():
                    val = excel_serial_a_fecha(int(val))
            if col_db in COLUMNAS_MONEDA and val and isinstance(val, (int, float, str)):
                try:
                    num_val = float(val) if isinstance(val, str) else val
                    val = formatear_numero_argentino(num_val)
                except:
                    pass
            if col_db == "ultima_acta" and not val:
                val = "*"
            registro[col_db] = val
        registros_limpios.append(registro)
    return registros_limpios

# ==================== FUNCIÓN PROCESAR CSV ACTAS ====================
def procesar_csv_actas_inteligente(archivo):
    try:
        contenido = archivo.getvalue().decode('latin-1')
        df = pd.read_csv(io.StringIO(contenido), sep=None, engine='python')
        df.columns = [str(col).strip() for col in df.columns]
        
        col_cuit = detectar_columna_csv(df, ['CUIT', 'CUIL', 'CUIT EMPRESA', 'NRO CUIT'])
        col_legajo = detectar_columna_csv(df, ['LEGAJO', 'LEG', 'NRO LEGAJO', 'INSPECTOR LEGAJO'])
        col_vto = detectar_columna_csv(df, ['VTO', 'FECHA_VTO', 'FECHA VTO', 'VENCIMIENTO', 'FECHA VENCIMIENTO'])
        col_nro_acta = detectar_columna_csv(df, ['NRO_ACTA', 'ACTA', 'NUMERO ACTA', 'NRO ACTA', 'ANO_ACTA'])
        
        if not col_cuit and len(df.columns) > 1:
            col_cuit = df.columns[1]
        if not col_legajo and len(df.columns) > 5:
            col_legajo = df.columns[5]
        if not col_vto and len(df.columns) > 13:
            col_vto = df.columns[13]
        
        if not col_cuit or not col_legajo or not col_vto or not col_nro_acta:
            return []
        
        resultados = []
        for _, row in df.iterrows():
            cuit = limpiar_cuit_csv(row[col_cuit])
            legajo = str(row[col_legajo]).strip() if pd.notna(row[col_legajo]) else None
            vto_raw = str(row[col_vto]).strip() if pd.notna(row[col_vto]) else None
            nro_acta = str(row[col_nro_acta]).strip() if pd.notna(row[col_nro_acta]) else None
            
            if cuit and legajo and vto_raw and nro_acta:
                vto_limpio = normalizar_fecha_para_supabase(vto_raw)
                resultados.append({
                    'cuit': cuit,
                    'leg': legajo,
                    'vto': vto_limpio,
                    'nro_acta': nro_acta
                })
        return resultados
    except Exception as e:
        return []

# ==================== INICIALIZAR SESSION STATE ====================
if 'filtro_cuit' not in st.session_state:
    st.session_state.filtro_cuit = ""
if 'filtro_razon' not in st.session_state:
    st.session_state.filtro_razon = ""
if 'localidad_seleccionada' not in st.session_state:
    st.session_state.localidad_seleccionada = "TODAS"
if 'filtro_mail' not in st.session_state:
    st.session_state.filtro_mail = "AMBOS"
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 1

# ==================== PESTAÑAS ====================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Legajos y Vtos", "📧 Solicitar Actas", "📋 Subir Actas"])

# ==================== TAB 1 ====================
with tab1:
    st.markdown("### Cargar Padrón de Deuda Presunta")
    st.markdown("""
    <div class="info-box">
        📌 <strong>Instrucciones:</strong><br>
        1. Seleccioná el archivo Excel del padrón de deuda presunta.<br>
        2. El sistema detectará automáticamente los duplicados por CUIT + ULTIMA ACTA.<br>
        3. Solo se cargarán los registros nuevos.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Seleccionar archivo Excel", type=["xls", "xlsx"], key="upload_padron")
    
    if uploaded_file is not None:
        st.info(f"Archivo: {uploaded_file.name}")
        try:
            registros = procesar_excel(uploaded_file)
            total_registros = len(registros)
            
            for reg in registros:
                reg['leg'] = None
                reg['vto'] = None
                reg['mail_enviado'] = 'NO'
                reg['acta'] = None
                reg['fecha_carga'] = date.today().isoformat()
                reg['estado_gestion'] = 'PENDIENTE'
            
            existentes_set = obtener_pares_existentes(supabase)
            nuevos_registros = []
            duplicados = 0
            
            for reg in registros:
                cuit = str(reg.get('cuit') or '')
                acta = str(reg.get('ultima_acta') or '*')
                if (cuit, acta) not in existentes_set:
                    nuevos_registros.append(reg)
                else:
                    duplicados += 1
            
            nuevos_count = len(nuevos_registros)
            st.markdown(f"""
            <div class="info-box">
                <strong>📊 Resumen del archivo</strong><br>
                Total de registros: {total_registros}<br>
                Registros NUEVOS: {nuevos_count}<br>
                Registros DUPLICADOS: {duplicados}
            </div>
            """, unsafe_allow_html=True)
            
            if nuevos_registros:
                with st.expander("Vista previa"):
                    df_preview = pd.DataFrame(nuevos_registros[:10])
                    for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
                        if col in df_preview.columns:
                            df_preview[col] = df_preview[col].apply(fecha_para_mostrar)
                    st.dataframe(df_preview, use_container_width=True)
            
            if nuevos_registros and st.button("✅ Confirmar carga", type="primary"):
                with st.spinner("Cargando datos..."):
                    total_insertados = 0
                    for i in range(0, len(nuevos_registros), 100):
                        lote = nuevos_registros[i:i+100]
                        resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                        total_insertados += len(resultado.data)
                    st.success(f"✅ Carga completada: {total_insertados} registros insertados")
                    obtener_pares_existentes.clear()
                    obtener_localidades.clear()
                    contar_registros.clear()
            elif not nuevos_registros:
                st.warning(f"⚠️ No hay registros nuevos para cargar.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 2 ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    # Botones de acción
    col_accion1, col_accion2, col_accion3, col_accion4 = st.columns(4)
    
    with col_accion1:
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Eliminar seleccionados", key="btn_eliminar_seleccionados"):
            if st.session_state.get('ids_a_eliminar', []):
                supabase.table("padron_deuda_presunta").delete().in_("id", st.session_state.ids_a_eliminar).execute()
                st.success(f"✅ Se eliminaron {len(st.session_state.ids_a_eliminar)} registros")
                st.session_state.ids_a_eliminar = []
                st.rerun()
            else:
                st.warning("No hay registros seleccionados")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_accion2:
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Eliminar TODO", key="btn_eliminar_todo"):
            st.session_state.confirmar_eliminar_todo = True
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_accion3:
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("🔄 Resetear filtros", key="btn_reset_filtros"):
            st.session_state.filtro_cuit = ""
            st.session_state.filtro_razon = ""
            st.session_state.localidad_seleccionada = "TODAS"
            st.session_state.filtro_mail = "AMBOS"
            st.session_state.pagina_actual = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_accion4:
        if st.button("🔄 Recargar", key="btn_recargar"):
            st.rerun()
    
    if st.session_state.get('confirmar_eliminar_todo', False):
        st.warning("⚠️ ¿Estás SEGURO? Esta acción eliminará TODOS los registros.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ SÍ, ELIMINAR TODO"):
                with st.spinner("Eliminando..."):
                    supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                    st.success("✅ Todos los registros fueron eliminados")
                    st.session_state.confirmar_eliminar_todo = False
                    st.session_state.ids_a_eliminar = []
                    st.rerun()
        with col_no:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_eliminar_todo = False
                st.rerun()
    
    st.markdown("---")
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns([1, 1, 1, 1])
    
    with col_filtro1:
        filtro_cuit = st.text_input("🔍 Filtrar por CUIT", value=st.session_state.filtro_cuit, key="input_filtro_cuit", placeholder="Ej: 30707685243")
        st.session_state.filtro_cuit = filtro_cuit
    
    with col_filtro2:
        filtro_razon = st.text_input("🔍 Filtrar por RAZON SOCIAL", value=st.session_state.filtro_razon, key="input_filtro_razon", placeholder="Ej: OMEGASUR")
        st.session_state.filtro_razon = filtro_razon
    
    with col_filtro3:
        localidades_unicas = obtener_localidades(supabase)
        if localidades_unicas:
            localidad_seleccionada = st.selectbox("📌 LOCALIDAD:", options=["TODAS"] + localidades_unicas, index=0, key="filtro_localidad")
            st.session_state.localidad_seleccionada = localidad_seleccionada
        else:
            localidad_seleccionada = "TODAS"
    
    with col_filtro4:
        filtro_mail = st.selectbox("📧 MAIL ENVIADO:", options=["AMBOS", "NO", "SI"], index=0, key="filtro_mail")
        st.session_state.filtro_mail = filtro_mail
    
    # Obtener datos filtrados
    query = supabase.table("padron_deuda_presunta").select("*")
    
    if st.session_state.localidad_seleccionada != "TODAS" and localidades_unicas:
        query = query.eq("localidad", st.session_state.localidad_seleccionada)
    
    if st.session_state.filtro_mail == "SI":
        query = query.eq("mail_enviado", "SI")
    elif st.session_state.filtro_mail == "NO":
        query = query.eq("mail_enviado", "NO")
    
    datos_completos = query.execute()
    
    if datos_completos.data:
        df_completo = pd.DataFrame(datos_completos.data)
        
        # Aplicar filtros de texto
        if st.session_state.filtro_cuit:
            df_completo = df_completo[df_completo['cuit'].astype(str).str.contains(st.session_state.filtro_cuit, na=False, case=False)]
        if st.session_state.filtro_razon:
            df_completo = df_completo[df_completo['razon_social'].astype(str).str.contains(st.session_state.filtro_razon, na=False, case=False)]
        
        total_filtrado = len(df_completo)
        st.write(f"**Total de registros con filtros:** {total_filtrado}")
        
        if total_filtrado > 0:
            registros_por_pagina = 300
            paginas_totales = (total_filtrado + registros_por_pagina - 1) // registros_por_pagina
            
            # Asegurar que página_actual esté dentro del rango
            if st.session_state.pagina_actual < 1:
                st.session_state.pagina_actual = 1
            if st.session_state.pagina_actual > paginas_totales:
                st.session_state.pagina_actual = paginas_totales
            
            # Navegación
            st.markdown("### 📄 Navegación")
            col_ant, col_num, col_sig = st.columns([1, 2, 1])
            
            with col_ant:
                if st.button("◀ Anterior", key="btn_anterior"):
                    if st.session_state.pagina_actual > 1:
                        st.session_state.pagina_actual -= 1
                        st.rerun()
            
            with col_num:
                pagina_actual = st.selectbox(
                    "Página",
                    options=list(range(1, paginas_totales + 1)),
                    index=st.session_state.pagina_actual - 1,
                    key="pagina_select",
                    label_visibility="collapsed",
                    on_change=lambda: st.session_state.update(pagina_actual=st.session_state.pagina_select)
                )
                st.session_state.pagina_actual = pagina_actual
            
            with col_sig:
                if st.button("Siguiente ▶", key="btn_siguiente"):
                    if st.session_state.pagina_actual < paginas_totales:
                        st.session_state.pagina_actual += 1
                        st.rerun()
            
            offset = (st.session_state.pagina_actual - 1) * registros_por_pagina
            df_mostrar = df_completo.iloc[offset:offset + registros_por_pagina].copy()
            
            desde = offset + 1
            hasta = min(offset + registros_por_pagina, total_filtrado)
            st.info(f"📝 Mostrando {desde} a {hasta} de {total_filtrado}")
            
            # Limpiar datos para mostrar
            for col in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                if col in df_mostrar.columns:
                    df_mostrar[col] = df_mostrar[col].apply(limpiar_numero_entero)
            
            for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
                if col in df_mostrar.columns:
                    df_mostrar[col] = df_mostrar[col].apply(fecha_para_mostrar)
            
            df_original = df_mostrar.copy()
            
            # Preparar para editar
            df_editable = df_mostrar.copy()
            if 'fecha_carga' in df_editable.columns:
                df_editable = df_editable.drop(columns=['fecha_carga'])
            df_editable = df_editable.rename(columns=TITULOS_MOSTRAR)
            
            st.markdown("#### Seleccionar registros")
            col_check_all, _ = st.columns([1, 4])
            with col_check_all:
                seleccionar_todos = st.checkbox("✅ SELECCIONAR TODOS (página actual)", key="seleccionar_todos")
            
            df_editable.insert(0, "🗑️", False)
            if seleccionar_todos:
                df_editable["🗑️"] = True
            
            edited_df = st.data_editor(
                df_editable, use_container_width=True, height=600,
                column_config={"🗑️": st.column_config.CheckboxColumn("Eliminar", help="Marcar para eliminar")},
                disabled=['ID', 'CUIT', 'RAZON SOCIAL', 'DEUDA PRESUNTA', 'CP', 'CALLE', 'NUMERO', 
                          'PISO', 'DPTO', 'FECHARELDEPENDENCIA', 'EMAIL', 'TEL_DOM_LEGAL', 'TEL_DOM_REAL',
                          'ULTIMA ACTA', 'DESDE', 'HASTA', 'DETECTADO', 'ESTADO', 'FECHA PAGO OBL',
                          'EMPL 10-2025', 'EMP 11-2025', 'EMPL 12-2025', 'ACTIVIDAD', 'SITUACION'],
                key=f"editor_{st.session_state.pagina_actual}"
            )
            
            ids_seleccionados = edited_df[edited_df["🗑️"]]["ID"].tolist()
            st.session_state.ids_a_eliminar = ids_seleccionados
            if ids_seleccionados:
                st.caption(f"📌 {len(ids_seleccionados)} registro(s) seleccionado(s) para eliminar")
            
            st.markdown("---")
            st.markdown("#### Editar campos (LEG, VTO, ACTA, etc.)")
            
            if st.button("💾 Guardar Cambios", type="primary"):
                with st.spinner("Guardando..."):
                    inverso = {v: k for k, v in TITULOS_MOSTRAR.items()}
                    modificados = 0
                    for idx, row in edited_df.iterrows():
                        original_row = df_original.loc[idx] if idx in df_original.index else None
                        if original_row is None:
                            continue
                        datos_update = {}
                        
                        nuevo_leg = row.get('LEG')
                        viejo_leg = original_row.get('leg')
                        if pd.isna(nuevo_leg) or nuevo_leg == '':
                            nuevo_leg = None
                        if pd.isna(viejo_leg) or viejo_leg == '':
                            viejo_leg = None
                        if nuevo_leg != viejo_leg:
                            datos_update['leg'] = nuevo_leg
                        
                        nuevo_vto = row.get('VTO')
                        viejo_vto = original_row.get('vto')
                        if pd.isna(nuevo_vto) or nuevo_vto == '':
                            nuevo_vto = None
                        else:
                            nuevo_vto = normalizar_fecha_para_supabase(nuevo_vto)
                        if pd.isna(viejo_vto) or viejo_vto == '':
                            viejo_vto = None
                        else:
                            viejo_vto = normalizar_fecha_para_supabase(viejo_vto)
                        if nuevo_vto != viejo_vto:
                            datos_update['vto'] = nuevo_vto
                        
                        nuevo_mail = row.get('MAIL ENVIADO')
                        viejo_mail = original_row.get('mail_enviado')
                        if pd.isna(nuevo_mail) or nuevo_mail == '':
                            nuevo_mail = 'NO'
                        if nuevo_mail != viejo_mail:
                            datos_update['mail_enviado'] = nuevo_mail
                        
                        nuevo_acta = row.get('ACTA')
                        viejo_acta = original_row.get('acta')
                        if pd.isna(nuevo_acta) or nuevo_acta == '':
                            nuevo_acta = None
                        if nuevo_acta != viejo_acta:
                            datos_update['acta'] = nuevo_acta
                        
                        nuevo_estado = row.get('ESTADO GESTION')
                        viejo_estado = original_row.get('estado_gestion')
                        if pd.isna(nuevo_estado) or nuevo_estado == '':
                            nuevo_estado = 'PENDIENTE'
                        if nuevo_estado != viejo_estado:
                            datos_update['estado_gestion'] = nuevo_estado
                        
                        if datos_update:
                            supabase.table("padron_deuda_presunta").update(datos_update).eq("id", row['ID']).execute()
                            modificados += 1
                    if modificados > 0:
                        st.success(f"✅ {modificados} registros actualizados")
                        st.rerun()
                    else:
                        st.info("No se detectaron cambios")
    else:
        st.info("No hay datos cargados")

# ==================== TAB 3 ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    st.markdown("""
    <div class="info-box">
        📌 <strong>Instrucciones:</strong><br>
        1. Esta pestaña muestra las empresas que ya tienen LEGAJO y VENCIMIENTO asignados.<br>
        2. Al enviar la solicitud, se actualizará el estado.
    </div>
    """, unsafe_allow_html=True)
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("id, cuit, razon_social, leg, vto, mail_enviado, estado_gestion").eq("mail_enviado", "NO").not_.is_("leg", "null").not_.is_("vto", "null").execute()
        if datos.data:
            df_listos = pd.DataFrame(datos.data)
            if len(df_listos) > 0:
                st.info(f"📧 {len(df_listos)} empresas listas para solicitar actas")
                df_mostrar = df_listos[['cuit', 'razon_social', 'leg', 'vto']].copy()
                if 'vto' in df_mostrar.columns:
                    df_mostrar['vto'] = df_mostrar['vto'].apply(fecha_para_mostrar)
                st.dataframe(df_mostrar, use_container_width=True)
                if st.button("📧 Enviar solicitud", type="primary"):
                    for _, row in df_listos.iterrows():
                        supabase.table("padron_deuda_presunta").update({"mail_enviado": "SI", "estado_gestion": "ACTA_SOLICITADA"}).eq("id", row['id']).execute()
                    st.success(f"Solicitud registrada para {len(df_listos)} empresas")
                    contar_registros.clear()
            else:
                st.info("No hay registros listos")
        else:
            st.info("No hay datos cargados")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==================== TAB 4 ====================
with tab4:
    st.markdown("### Subir Archivo de Actas (CSV)")
    st.markdown("""
    <div class="info-box">
        📌 <strong>Instrucciones:</strong><br>
        1. Subí el archivo CSV que te envía Central.<br>
        2. El sistema detectará automáticamente las columnas.<br>
        3. Buscará coincidencias por <strong>CUIT + LEGAJO + FECHA VENCIMIENTO</strong>.<br>
        4. Solo actualizará registros con <strong>MAIL ENVIADO = SI</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_csv = st.file_uploader("Seleccionar archivo CSV", type=["csv"], key="upload_actas")
    
    if uploaded_csv is not None:
        st.info(f"Archivo: {uploaded_csv.name}")
        try:
            contenido = uploaded_csv.getvalue().decode('latin-1')
            df_preview = pd.read_csv(io.StringIO(contenido), sep=None, engine='python')
            st.write("**Vista previa del archivo CSV:**")
            st.dataframe(df_preview.head(10), use_container_width=True)
            
            if st.button("📋 Procesar y actualizar actas", type="primary"):
                with st.spinner("Procesando archivo..."):
                    datos_csv = procesar_csv_actas_inteligente(uploaded_csv)
                    if not datos_csv:
                        st.warning("No se pudieron extraer datos del archivo.")
                    else:
                        st.write(f"**Registros en CSV:** {len(datos_csv)}")
                        actualizados = 0
                        no_encontrados = 0
                        progress_bar = st.progress(0)
                        for i, item in enumerate(datos_csv):
                            try:
                                # Buscar coincidencia por CUIT + LEG + VTO
                                resultado = supabase.table("padron_deuda_presunta").select("id").eq("cuit", item['cuit']).eq("leg", item['leg']).eq("vto", item['vto']).eq("mail_enviado", "SI").execute()
                                if resultado.data:
                                    for registro in resultado.data:
                                        supabase.table("padron_deuda_presunta").update({"acta": item['nro_acta'], "estado_gestion": "FINALIZADO"}).eq("id", registro['id']).execute()
                                        actualizados += 1
                                else:
                                    no_encontrados += 1
                            except Exception as e:
                                st.warning(f"Error: {str(e)}")
                            progress_bar.progress((i + 1) / len(datos_csv))
                        st.success(f"✅ {actualizados} actualizados, {no_encontrados} no encontrados")
                        contar_registros.clear()
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
