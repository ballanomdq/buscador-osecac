import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib

# Configuración de página
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilo profesional
st.markdown("""
<style>
    .main-header {
        background-color: #1e293b;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    .success-box {
        background-color: #064e3b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #451a03;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    div[data-testid="stButton"] button {
        background-color: #3b82f6;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.4rem 1.2rem;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if 'carga_realizada' not in st.session_state:
    st.session_state.carga_realizada = False
if 'registros_insertados' not in st.session_state:
    st.session_state.registros_insertados = 0

# Header
st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-weight: 500;">Fiscalización - Deuda Presunta</h2>
    <p style="color: #94a3b8; margin: 0.3rem 0 0 0; font-size: 0.85rem;">Sistema de gestión y seguimiento</p>
</div>
""", unsafe_allow_html=True)

# Botón para volver al inicio
col_back, col_title = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver"):
        st.switch_page("main.py")

st.markdown("---")

# ==================== VERIFICAR TABLA ====================
@st.cache_data(ttl=60)
def verificar_tabla():
    """Verifica si la tabla existe en Supabase"""
    try:
        # Intentar hacer una consulta simple
        response = supabase.table("padron_deuda_presunta").select("id").limit(1).execute()
        return True, "Tabla encontrada"
    except Exception as e:
        error_msg = str(e)
        if "PGRST205" in error_msg or "does not exist" in error_msg:
            return False, "La tabla 'padron_deuda_presunta' no existe en Supabase"
        return False, error_msg

tabla_existe, mensaje = verificar_tabla()

if not tabla_existe:
    st.markdown(f"""
    <div class="warning-box">
        <strong>ERROR DE CONFIGURACIÓN</strong><br>
        {mensaje}<br><br>
        <strong>Solución:</strong> Ejecutá el siguiente SQL en el editor de Supabase:<br>
        <code style="background:#000; padding:0.5rem; display:block; white-space:pre-wrap;">
CREATE TABLE padron_deuda_presunta (
    id SERIAL PRIMARY KEY,
    cuit TEXT,
    razon_social TEXT,
    ultima_acta TEXT,
    fecha_carga TIMESTAMP DEFAULT NOW()
);
        </code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==================== MAPEO DE COLUMNAS ====================
COLUMNAS_EXCEL_A_INTERNO = {
    'DELEGACION': 'delegacion',
    'LOCALIDAD': 'localidad',
    'CUIT': 'cuit',
    'RAZON SOCIAL': 'razon_social',
    'DEUDA PRESUNTA': 'deuda_presunta',
    'CP': 'cp',
    'CALLE': 'calle',
    'NUMERO': 'numero',
    'PISO': 'piso',
    'DPTO': 'dpto',
    'FECHARELDEPENDENCIA': 'fechareldependencia',
    'EMAIL': 'email',
    'TEL_DOM_LEGAL': 'tel_dom_legal',
    'TEL_DOM_REAL': 'tel_dom_real',
    'ULTIMA ACTA': 'ultima_acta',
    'DESDE': 'desde',
    'HASTA': 'hasta',
    'DETECTADO': 'detectado',
    'ESTADO': 'estado',
    'FECHA_PAGO_OBL': 'fecha_pago_obl',
    'EMPL 10-2025': 'empl_10_2025',
    'EMP 11-2025': 'emp_11_2025',
    'EMPL 12-2025': 'empl_12_2025',
    'ACTIVIDAD': 'actividad',
    'SITUACION': 'situacion'
}

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Legajos", "📧 Solicitar Actas"])

# ==================== TAB 1: CARGAR PADRÓN ====================
with tab1:
    st.markdown("### Cargar Padrón de Deuda Presunta")
    
    uploaded_file = st.file_uploader(
        "Seleccionar archivo (Padrón Deuda Presunta)",
        type=["xls", "xlsx"],
        key="upload_padron"
    )
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Archivo", uploaded_file.name[:35] + "..." if len(uploaded_file.name) > 35 else uploaded_file.name)
        with col2:
            st.metric("Tamaño", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Formato", "XLS" if uploaded_file.name.endswith('.xls') else "XLSX")
        
        try:
            # Leer archivo
            if uploaded_file.name.endswith('.xls'):
                df_raw = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                df_raw = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Limpiar nombres de columnas
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            # Mapear a nombres internos
            df_ordenado = pd.DataFrame()
            columnas_faltantes = []
            
            for nombre_excel, nombre_interno in COLUMNAS_EXCEL_A_INTERNO.items():
                if nombre_excel in df_raw.columns:
                    df_ordenado[nombre_interno] = df_raw[nombre_excel]
                else:
                    columnas_faltantes.append(nombre_excel)
            
            if columnas_faltantes:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>COLUMNAS NO ENCONTRADAS</strong><br>
                    No se encontraron: {', '.join(columnas_faltantes[:5])}<br>
                    <small>Verifique que el archivo tenga el formato correcto.</small>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
            
            # Limpiar datos
            df_ordenado = df_ordenado.replace({pd.NA: None, float('nan'): None})
            
            if df_ordenado.empty:
                st.markdown("""
                <div class="warning-box">
                    <strong>ARCHIVO VACÍO</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Agregar columnas nuevas
                df_ordenado['legajo_inspector'] = None
                df_ordenado['fecha_vencimiento'] = None
                df_ordenado['nro_acta'] = None
                df_ordenado['fecha_carga'] = datetime.now().isoformat()
                df_ordenado['estado_gestion'] = 'PENDIENTE'
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>Resumen del archivo</strong><br>
                    Registros detectados: {len(df_ordenado):,}
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Ver vista previa"):
                    st.dataframe(df_ordenado.head(10), use_container_width=True)
                
                if st.button("Confirmar carga", type="primary", key="btn_cargar_padron"):
                    with st.spinner("Verificando y procesando..."):
                        registros = df_ordenado.to_dict(orient='records')
                        
                        # Obtener registros existentes (solo CUIT y ultima_acta para comparar)
                        try:
                            existentes = supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").execute()
                        except Exception as e:
                            st.markdown(f"""
                            <div class="warning-box">
                                <strong>ERROR AL CONSULTAR BASE DE DATOS</strong><br>
                                {str(e)[:200]}
                            </div>
                            """, unsafe_allow_html=True)
                            st.stop()
                        
                        # Crear set de pares (cuit, ultima_acta) existentes
                        existentes_set = set()
                        for reg in existentes.data:
                            cuit = reg.get('cuit', '')
                            acta = reg.get('ultima_acta', '')
                            if cuit:
                                existentes_set.add((cuit, acta if acta else ''))
                        
                        # Filtrar nuevos registros
                        nuevos = []
                        duplicados = 0
                        
                        for reg in registros:
                            cuit = reg.get('cuit', '')
                            acta = reg.get('ultima_acta', '')
                            
                            if (cuit, acta if acta else '') not in existentes_set:
                                nuevos.append(reg)
                            else:
                                duplicados += 1
                        
                        if nuevos:
                            try:
                                # Insertar todos los nuevos
                                resultado = supabase.table("padron_deuda_presunta").insert(nuevos).execute()
                                
                                st.session_state.registros_insertados = len(resultado.data)
                                st.session_state.carga_realizada = True
                                
                                st.markdown(f"""
                                <div class="success-box">
                                    <strong>CARGA COMPLETADA</strong><br>
                                    Se insertaron {len(resultado.data):,} registros nuevos.<br>
                                    {f'({duplicados} duplicados omitidos)' if duplicados > 0 else ''}
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.markdown(f"""
                                <div class="warning-box">
                                    <strong>ERROR AL INSERTAR</strong><br>
                                    {str(e)[:300]}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="warning-box">
                                <strong>SIN REGISTROS NUEVOS</strong><br>
                                Todos los registros ya existen en la base de datos.
                            </div>
                            """, unsafe_allow_html=True)
                            
        except Exception as e:
            st.markdown(f"""
            <div class="warning-box">
                <strong>ERROR AL LEER EL ARCHIVO</strong><br>
                {str(e)[:300]}
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 2: EDITAR LEGAJOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    st.info("Funcionalidad disponible después de cargar datos")
    
    try:
        # Intentar cargar datos existentes
        datos = supabase.table("padron_deuda_presunta").select("id, cuit, razon_social, legajo_inspector, fecha_vencimiento, estado_gestion").limit(10).execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            st.dataframe(df_datos, use_container_width=True)
        else:
            st.info("No hay datos cargados todavía")
    except Exception as e:
        st.info("Cargue un padrón primero")

# ==================== TAB 3: SOLICITAR ACTAS ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    st.info("Funcionalidad disponible después de cargar y editar legajos")
