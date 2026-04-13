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
def verificar_tabla():
    try:
        supabase.table("padron_deuda_presunta").select("id").limit(1).execute()
        return True
    except Exception as e:
        if "relation" in str(e).lower() or "does not exist" in str(e).lower():
            st.markdown("""
            <div class="warning-box">
                <strong>TABLA NO EXISTE</strong><br>
                Ejecutá este SQL en Supabase:<br>
                <code>CREATE TABLE padron_deuda_presunta (id SERIAL PRIMARY KEY, cuit TEXT, ultima_acta TEXT, fecha_carga TIMESTAMP DEFAULT NOW());</code>
            </div>
            """, unsafe_allow_html=True)
            return False
        return True

if not verificar_tabla():
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

# Columnas a comparar para detectar cambios (excluyendo CUIT y ULTIMA ACTA)
COLUMNAS_COMPARACION = [
    'delegacion', 'localidad', 'razon_social', 'deuda_presunta', 'cp', 'calle',
    'numero', 'piso', 'dpto', 'fechareldependencia', 'email', 'tel_dom_legal',
    'tel_dom_real', 'desde', 'hasta', 'detectado', 'estado', 'fecha_pago_obl',
    'empl_10_2025', 'emp_11_2025', 'empl_12_2025', 'actividad', 'situacion'
]

def generar_hash_registro(registro, columnas):
    """Genera un hash único del registro para comparar"""
    valores = []
    for col in columnas:
        val = registro.get(col, '')
        if pd.isna(val):
            val = ''
        valores.append(str(val))
    texto = '|'.join(valores)
    return hashlib.md5(texto.encode()).hexdigest()

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
            for nombre_excel, nombre_interno in COLUMNAS_EXCEL_A_INTERNO.items():
                if nombre_excel in df_raw.columns:
                    df_ordenado[nombre_interno] = df_raw[nombre_excel]
                else:
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>COLUMNA NO ENCONTRADA</strong><br>
                        No se pudo encontrar: {nombre_excel}
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
                    with st.spinner("Verificando duplicados y procesando..."):
                        registros = df_ordenado.to_dict(orient='records')
                        
                        # Obtener todos los registros existentes
                        existentes = supabase.table("padron_deuda_presunta").select("*").execute()
                        
                        # Crear diccionario de existentes por CUIT
                        existentes_por_cuit = {}
                        for reg in existentes.data:
                            cuit = reg.get('cuit', '')
                            if cuit:
                                if cuit not in existentes_por_cuit:
                                    existentes_por_cuit[cuit] = []
                                existentes_por_cuit[cuit].append(reg)
                        
                        nuevos_registros = []
                        duplicados = 0
                        actualizados = 0
                        
                        for nuevo in registros:
                            cuit_nuevo = nuevo.get('cuit', '')
                            acta_nueva = nuevo.get('ultima_acta', '')
                            
                            # Generar hash del nuevo registro
                            hash_nuevo = generar_hash_registro(nuevo, COLUMNAS_COMPARACION)
                            
                            es_duplicado = False
                            
                            if cuit_nuevo in existentes_por_cuit:
                                for existente in existentes_por_cuit[cuit_nuevo]:
                                    acta_existente = existente.get('ultima_acta', '')
                                    
                                    # Caso 1: Ambas tienen acta y son iguales -> DUPLICADO
                                    if acta_nueva and acta_existente and acta_nueva == acta_existente:
                                        es_duplicado = True
                                        break
                                    
                                    # Caso 2: Ambas NO tienen acta (None o vacío)
                                    elif not acta_nueva and not acta_existente:
                                        hash_existente = generar_hash_registro(existente, COLUMNAS_COMPARACION)
                                        if hash_nuevo == hash_existente:
                                            es_duplicado = True
                                            break
                            
                            if es_duplicado:
                                duplicados += 1
                            else:
                                nuevos_registros.append(nuevo)
                        
                        if nuevos_registros:
                            # Insertar en lotes de 500
                            lote_size = 500
                            total_insertados = 0
                            
                            for i in range(0, len(nuevos_registros), lote_size):
                                lote = nuevos_registros[i:i+lote_size]
                                try:
                                    resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                                    total_insertados += len(resultado.data)
                                except Exception as e:
                                    st.markdown(f"""
                                    <div class="warning-box">
                                        <strong>ERROR EN LOTE {i//lote_size + 1}</strong><br>
                                        {str(e)[:200]}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.session_state.registros_insertados = total_insertados
                            st.session_state.carga_realizada = True
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>CARGA COMPLETADA</strong><br>
                                Se insertaron {total_insertados:,} registros nuevos.<br>
                                {f'({duplicados} registros duplicados omitidos)' if duplicados > 0 else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="warning-box">
                                <strong>SIN REGISTROS NUEVOS</strong><br>
                                Todos los registros del archivo ya existen en la base de datos.
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
    
    try:
        # Obtener lista de actas disponibles
        datos_totales = supabase.table("padron_deuda_presunta").select("ultima_acta, fecha_carga").order("fecha_carga", desc=True).execute()
        
        actas_unicas = []
        if datos_totales.data:
            for reg in datos_totales.data:
                acta = reg.get('ultima_acta')
                if acta and acta not in actas_unicas:
                    actas_unicas.append(acta)
            # Agregar opción para "SIN ACTA"
            actas_unicas.insert(0, "(SIN NÚMERO DE ACTA)")
        
        if actas_unicas:
            acta_seleccionada = st.selectbox("Seleccionar período", actas_unicas, key="select_acta")
            
            if st.button("👥 Administrar Inspectores", key="btn_admin_inspectores"):
                try:
                    st.switch_page("pages/inspectores.py")
                except:
                    st.warning("Página de inspectores no encontrada")
            
            # Cargar datos según selección
            if acta_seleccionada == "(SIN NÚMERO DE ACTA)":
                datos = supabase.table("padron_deuda_presunta").select("*").is_("ultima_acta", "null").execute()
            else:
                datos = supabase.table("padron_deuda_presunta").select("*").eq("ultima_acta", acta_seleccionada).execute()
            
            if datos.data:
                df_datos = pd.DataFrame(datos.data)
                
                columnas_mostrar = ['id', 'cuit', 'razon_social', 'calle', 'numero', 'legajo_inspector', 'fecha_vencimiento', 'nro_acta', 'estado_gestion']
                df_editable = df_datos[[col for col in columnas_mostrar if col in df_datos.columns]].copy()
                
                st.info(f"Mostrando {len(df_editable)} registros")
                
                edited_df = st.data_editor(
                    df_editable,
                    use_container_width=True,
                    column_config={
                        "legajo_inspector": st.column_config.TextColumn("Legajo Inspector"),
                        "fecha_vencimiento": st.column_config.DateColumn("Fecha Vencimiento", format="DD/MM/YYYY"),
                        "estado_gestion": st.column_config.SelectColumn("Estado", options=["PENDIENTE", "ACTA_SOLICITADA", "ACTA_RECIBIDA", "CERRADO"]),
                    },
                    disabled=['id', 'cuit', 'razon_social', 'calle', 'numero', 'nro_acta'],
                    key="editor_legajos"
                )
                
                if st.button("Guardar Cambios", type="primary", key="btn_guardar_legajos"):
                    with st.spinner("Guardando cambios..."):
                        for _, row in edited_df.iterrows():
                            supabase.table("padron_deuda_presunta").update({
                                "legajo_inspector": row['legajo_inspector'] if pd.notna(row['legajo_inspector']) else None,
                                "fecha_vencimiento": row['fecha_vencimiento'] if pd.notna(row['fecha_vencimiento']) else None,
                                "estado_gestion": row['estado_gestion']
                            }).eq("id", row['id']).execute()
                        
                        st.markdown("""
                        <div class="success-box">
                            <strong>CAMBIOS GUARDADOS</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
            else:
                st.info("No hay datos para la selección actual")
        else:
            st.info("No hay períodos cargados. Cargue un padrón primero.")
    except Exception as e:
        st.markdown(f"""
        <div class="warning-box">
            <strong>ERROR AL CARGAR DATOS</strong><br>
            {str(e)[:200]}
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 3: SOLICITAR ACTAS ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    
    try:
        datos_totales = supabase.table("padron_deuda_presunta").select("ultima_acta").execute()
        
        actas_unicas = []
        if datos_totales.data:
            for reg in datos_totales.data:
                acta = reg.get('ultima_acta')
                if acta and acta not in actas_unicas:
                    actas_unicas.append(acta)
        
        if actas_unicas:
            acta_solicitud = st.selectbox("Seleccionar período", actas_unicas, key="select_acta_solicitud")
            
            datos = supabase.table("padron_deuda_presunta").select("*").eq("ultima_acta", acta_solicitud).execute()
            
            if datos.data:
                df_solicitud = pd.DataFrame(datos.data)
                
                df_completos = df_solicitud[
                    df_solicitud['legajo_inspector'].notna() & 
                    df_solicitud['fecha_vencimiento'].notna()
                ]
                
                if len(df_completos) > 0:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Registros listos para solicitar actas</strong><br>
                        {len(df_completos)} empresas tienen legajo y vencimiento asignados.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    df_envio = df_completos[['cuit', 'legajo_inspector', 'fecha_vencimiento', 'razon_social']].copy()
                    st.dataframe(df_envio, use_container_width=True)
                    
                    email_destino = st.text_input("Email de destino", value="central@osecac.org.ar")
                    
                    if st.button("Registrar Solicitud", type="primary", key="btn_enviar_email"):
                        for _, row in df_completos.iterrows():
                            supabase.table("padron_deuda_presunta").update({
                                "estado_gestion": "ACTA_SOLICITADA"
                            }).eq("id", row['id']).execute()
                        
                        st.markdown("""
                        <div class="success-box">
                            <strong>SOLICITUD REGISTRADA</strong><br>
                            Se actualizó el estado de los registros a "ACTA_SOLICITADA".
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No hay registros con legajo y fecha de vencimiento completos.")
            else:
                st.info(f"No hay datos para el acta seleccionada")
        else:
            st.info("No hay períodos cargados.")
    except Exception as e:
        st.markdown(f"""
        <div class="warning-box">
            <strong>ERROR</strong><br>
            {str(e)[:200]}
        </div>
        """, unsafe_allow_html=True)
