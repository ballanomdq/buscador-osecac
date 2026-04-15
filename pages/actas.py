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
    """Crea una única conexión a Supabase (reutilizada en toda la sesión)"""
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

# Estilo
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; }
    .warning-box { background-color: #451a03; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 1rem 0; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; }
    div[data-testid="stButton"] button { background-color: #3b82f6; color: white; font-weight: 500; border: none; padding: 0.4rem 1.2rem; }
    div[data-testid="stButton"] button:hover { background-color: #2563eb; }
    .delete-btn button { background-color: #dc2626 !important; }
    .delete-btn button:hover { background-color: #b91c1c !important; }
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
    """Convierte un número a formato argentino: $1.234,56"""
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
    """Convierte cualquier valor no serializable a JSON en None o string limpio."""
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
    """Convierte número serial de Excel a string YYYY-MM-DD (sin hora)."""
    try:
        n = int(n)
        fecha_base = datetime(1899, 12, 30)
        fecha = fecha_base + pd.Timedelta(days=n)
        return fecha.strftime("%Y-%m-%d")
    except Exception:
        return str(n)

def fecha_para_mostrar(valor):
    """Convierte fecha a DD/MM/YYYY para mostrar (sin hora)."""
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
            if re.match(r'\d{4}-\d{2}-\d{2}T', valor):
                return datetime.strptime(valor[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
            if re.match(r'\d{4}-\d{2}-\d{2} ', valor):
                return datetime.strptime(valor[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
            if re.match(r'^\d{4}-\d{2}-\d{2}$', valor):
                return datetime.strptime(valor, '%Y-%m-%d').strftime('%d/%m/%Y')
            if re.match(r'^\d{2}/\d{2}/\d{4}$', valor):
                return valor
            return valor
        return str(valor)
    except:
        return str(valor) if valor else None

def fecha_para_guardar(valor):
    """Convierte fecha a YYYY-MM-DD para guardar en Supabase (sin hora)."""
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%Y-%m-%d')
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
            if re.match(r'\d{2}/\d{2}/\d{4}', valor):
                fecha = datetime.strptime(valor, '%d/%m/%Y')
                return fecha.strftime('%Y-%m-%d')
            if re.match(r'\d{4}-\d{2}-\d{2}', valor):
                return valor[:10]
        return None
    except:
        return None

def limpiar_numero_entero(valor):
    """Convierte 1.0 a 1"""
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
    """Limpia el CUIT que viene en formato científico (3,0717E+10)"""
    if valor is None or pd.isna(valor):
        return None
    try:
        valor_str = str(valor).strip()
        if 'E' in valor_str.upper():
            num = float(valor_str)
            return str(int(num))
        if valor_str.isdigit():
            return valor_str
        return valor_str
    except:
        return str(valor)

# ==================== FUNCIONES CON CACHÉ PARA RENDIMIENTO ====================
@st.cache_data(ttl=300)
def obtener_localidades(_supabase):
    """Obtiene localidades únicas (cacheado por 5 minutos)"""
    todas = _supabase.table("padron_deuda_presunta").select("localidad").execute()
    localidades = sorted(set([l['localidad'] for l in todas.data if l.get('localidad')]))
    if 'MAR DEL PLATA' in localidades:
        localidades.remove('MAR DEL PLATA')
        localidades = ['MAR DEL PLATA'] + localidades
    return localidades

@st.cache_data(ttl=60)
def obtener_pares_existentes(_supabase):
    """Trae solo los pares (cuit, ultima_acta) de la tabla (cacheado 1 minuto)"""
    todos = []
    offset = 0
    batch_size = 1000
    while True:
        batch = _supabase.table("padron_deuda_presunta")\
            .select("cuit, ultima_acta")\
            .range(offset, offset + batch_size - 1)\
            .execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += batch_size
        if len(batch.data) < batch_size:
            break
    batch_none = _supabase.table("padron_deuda_presunta")\
        .select("cuit, ultima_acta")\
        .is_("ultima_acta", "null")\
        .execute()
    for reg in batch_none.data:
        cuit = str(reg.get('cuit') or '')
        if cuit:
            todos.append({'cuit': cuit, 'ultima_acta': '*'})
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

@st.cache_data(ttl=60)
def contar_registros(_supabase, localidad, filtro_mail):
    """Cuenta registros con filtros (cacheado 1 minuto)"""
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
    "DELEGACION": "delegacion",
    "LOCALIDAD": "localidad",
    "CUIT": "cuit",
    "RAZON SOCIAL": "razon_social",
    "DEUDA PRESUNTA": "deuda_presunta",
    "CP": "cp",
    "CALLE": "calle",
    "NUMERO": "numero",
    "PISO": "piso",
    "DPTO": "dpto",
    "FECHARELDEPENDENCIA": "fechareldependencia",
    "EMAIL": "email",
    "TEL_DOM_LEGAL": "tel_dom_legal",
    "TEL_DOM_REAL": "tel_dom_real",
    "ULTIMA ACTA": "ultima_acta",
    "DESDE": "desde",
    "HASTA": "hasta",
    "DETECTADO": "detectado",
    "ESTADO": "estado",
    "FECHA_PAGO_OBL": "fecha_pago_obl",
    "EMPL 10-2025": "empl_10_2025",
    "EMP 11-2025": "emp_11_2025",
    "EMPL 12-2025": "empl_12_2025",
    "ACTIVIDAD": "actividad",
    "SITUACION": "situacion"
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

# ==================== FUNCIÓN PARA PROCESAR EXCEL ====================
def procesar_excel(archivo):
    """Lee el Excel y devuelve una lista de dicts listos para Supabase."""
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

# ==================== FUNCIÓN PARA PROCESAR CSV DE ACTAS ====================
def procesar_csv_actas(archivo):
    """Lee el CSV de actas y devuelve una lista de dicts con los datos relevantes"""
    try:
        contenido = archivo.getvalue().decode('latin-1')
        df = pd.read_csv(io.StringIO(contenido), sep=None, engine='python')
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Buscar columnas necesarias
        col_cuit = None
        col_legajo = None
        col_vto = None
        col_nro_acta = None
        
        for col in df.columns:
            if 'CUIT' in col:
                col_cuit = col
            if 'LEGAJO' in col or col == 'LEG':
                col_legajo = col
            if 'VTO' in col or 'FECHA_VTO' in col:
                col_vto = col
            if 'NRO_ACTA' in col or col == 'ACTA':
                col_nro_acta = col
        
        if not col_cuit or not col_legajo or not col_vto or not col_nro_acta:
            st.error(f"No se encontraron columnas: CUIT={col_cuit}, LEGAJO={col_legajo}, VTO={col_vto}, NRO_ACTA={col_nro_acta}")
            return []
        
        resultados = []
        for _, row in df.iterrows():
            cuit = limpiar_cuit_csv(row[col_cuit])
            legajo = str(row[col_legajo]).strip() if pd.notna(row[col_legajo]) else None
            vto = str(row[col_vto]).strip() if pd.notna(row[col_vto]) else None
            nro_acta = str(row[col_nro_acta]).strip() if pd.notna(row[col_nro_acta]) else None
            
            if cuit and legajo and vto and nro_acta:
                if '/' in vto:
                    partes = vto.split('/')
                    if len(partes) == 3:
                        vto_limpio = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    else:
                        vto_limpio = vto
                else:
                    vto_limpio = vto
                
                resultados.append({
                    'cuit': cuit,
                    'leg': legajo,
                    'vto': vto_limpio,
                    'nro_acta': nro_acta
                })
        return resultados
    except Exception as e:
        st.error(f"Error al leer el archivo CSV: {str(e)}")
        return []

# ==================== PESTAÑAS ====================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Legajos y Vtos", "📧 Solicitar Actas", "📋 Subir Actas"])

# ==================== TAB 1: CARGAR PADRÓN ====================
with tab1:
    st.markdown("### Cargar Padrón de Deuda Presunta")
    
    uploaded_file = st.file_uploader(
        "Seleccionar archivo Excel",
        type=["xls", "xlsx"],
        key="upload_padron"
    )
    
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
                Total de registros en el archivo: {total_registros}<br>
                Registros NUEVOS (se cargarán): {nuevos_count}<br>
                Registros DUPLICADOS (se omitirán): {duplicados}<br>
                <small>* Los registros sin número de ULTIMA ACTA se identifican con '*'</small>
            </div>
            """, unsafe_allow_html=True)
            
            if nuevos_registros:
                with st.expander("Vista previa (primeros 10 registros nuevos)"):
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
                    
                    st.success(f"✅ Carga completada: {total_insertados} registros nuevos insertados. Duplicados omitidos: {duplicados}")
                    obtener_pares_existentes.clear()
                    obtener_localidades.clear()
                    contar_registros.clear()
            elif not nuevos_registros:
                st.warning(f"⚠️ No hay registros nuevos para cargar.")
                            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 2: EDITAR LEGAJOS Y VTOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    col_accion1, col_accion2, col_accion3 = st.columns(3)
    
    with col_accion1:
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Eliminar seleccionados", key="btn_eliminar_seleccionados"):
            if st.session_state.get('ids_a_eliminar', []):
                supabase.table("padron_deuda_presunta").delete().in_("id", st.session_state.ids_a_eliminar).execute()
                st.success(f"✅ Se eliminaron {len(st.session_state.ids_a_eliminar)} registros")
                st.session_state.ids_a_eliminar = []
                obtener_localidades.clear()
                contar_registros.clear()
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
        if st.button("🔄 Recargar", key="btn_recargar"):
            st.rerun()
    
    if st.session_state.get('confirmar_eliminar_todo', False):
        st.warning("⚠️ ¿Estás SEGURO? Esta acción eliminará TODOS los registros. No se puede deshacer.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ SÍ, ELIMINAR TODO"):
                with st.spinner("Eliminando todos los registros..."):
                    supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                    st.success("✅ Todos los registros fueron eliminados")
                    st.session_state.confirmar_eliminar_todo = False
                    st.session_state.ids_a_eliminar = []
                    obtener_localidades.clear()
                    contar_registros.clear()
                    obtener_pares_existentes.clear()
                    st.rerun()
        with col_no:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_eliminar_todo = False
                st.rerun()
    
    st.markdown("---")
    
    localidades_unicas = obtener_localidades(supabase)
    
    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 1, 1])
    
    with col_filtro1:
        if localidades_unicas:
            localidad_seleccionada = st.selectbox(
                "📌 LOCALIDAD:",
                options=["TODAS"] + localidades_unicas,
                index=0,
                key="filtro_localidad"
            )
        else:
            localidad_seleccionada = "TODAS"
            st.selectbox("📌 LOCALIDAD:", options=["TODAS"], index=0, key="filtro_localidad", disabled=True)
    
    with col_filtro2:
        filtro_mail = st.selectbox(
            "📧 MAIL ENVIADO:",
            options=["AMBOS", "NO", "SI"],
            index=0,
            key="filtro_mail"
        )
    
    total = contar_registros(supabase, localidad_seleccionada, filtro_mail)
    
    with col_filtro3:
        st.metric("Total registros", total)
    
    if total > 0:
        registros_por_pagina = 300
        paginas_totales = (total + registros_por_pagina - 1) // registros_por_pagina
        
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        if 'ultimo_filtro' not in st.session_state:
            st.session_state.ultimo_filtro = (localidad_seleccionada, filtro_mail)
        
        if st.session_state.ultimo_filtro != (localidad_seleccionada, filtro_mail):
            st.session_state.pagina_actual = 1
            st.session_state.ultimo_filtro = (localidad_seleccionada, filtro_mail)
            st.rerun()
        
        col_ant, col_num, col_sig = st.columns([1, 2, 1])
        
        with col_ant:
            if st.button("◀ Anterior", disabled=(st.session_state.pagina_actual <= 1)):
                st.session_state.pagina_actual = max(1, st.session_state.pagina_actual - 1)
                st.rerun()
        
        with col_num:
            pagina_actual = st.selectbox(
                "Página",
                options=list(range(1, paginas_totales + 1)),
                index=st.session_state.pagina_actual - 1,
                key="pagina_select",
                label_visibility="collapsed"
            )
            st.session_state.pagina_actual = pagina_actual
        
        with col_sig:
            if st.button("Siguiente ▶", disabled=(st.session_state.pagina_actual >= paginas_totales)):
                st.session_state.pagina_actual = min(paginas_totales, st.session_state.pagina_actual + 1)
                st.rerun()
        
        offset = (st.session_state.pagina_actual - 1) * registros_por_pagina
        
        query_datos = supabase.table("padron_deuda_presunta").select("*")
        
        if localidad_seleccionada != "TODAS" and localidades_unicas:
            query_datos = query_datos.eq("localidad", localidad_seleccionada)
        
        if filtro_mail == "SI":
            query_datos = query_datos.eq("mail_enviado", "SI")
        elif filtro_mail == "NO":
            query_datos = query_datos.eq("mail_enviado", "NO")
        
        datos = query_datos.range(offset, offset + registros_por_pagina - 1).execute()
        
        if datos.data:
            desde = offset + 1
            hasta = min(offset + registros_por_pagina, total)
            st.info(f"📝 Mostrando {desde} a {hasta} de {total}")
            
            df_datos = pd.DataFrame(datos.data)
            
            for col in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                if col in df_datos.columns:
                    df_datos[col] = df_datos[col].apply(limpiar_numero_entero)
            
            for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
                if col in df_datos.columns:
                    df_datos[col] = df_datos[col].apply(fecha_para_mostrar)
            
            df_original = df_datos.copy()
            
            df_mostrar = df_datos.copy()
            if 'fecha_carga' in df_mostrar.columns:
                df_mostrar = df_mostrar.drop(columns=['fecha_carga'])
            
            df_mostrar = df_mostrar.rename(columns=TITULOS_MOSTRAR)
            
            st.markdown("#### Seleccionar registros")
            col_check_all, _ = st.columns([1, 4])
            with col_check_all:
                seleccionar_todos = st.checkbox("✅ SELECCIONAR TODOS (página actual)", key="seleccionar_todos")
            
            df_mostrar.insert(0, "🗑️", False)
            
            if seleccionar_todos:
                df_mostrar["🗑️"] = True
            
            edited_df = st.data_editor(
                df_mostrar,
                use_container_width=True,
                height=600,
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
                            nuevo_vto = fecha_para_guardar(nuevo_vto)
                        if pd.isna(viejo_vto) or viejo_vto == '':
                            viejo_vto = None
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
                            datos_update['estado_gestion'] =
