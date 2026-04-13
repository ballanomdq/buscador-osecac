import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

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

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Legajos", "📧 Solicitar Actas"])

# ==================== TAB 1: CARGAR PADRÓN ====================
with tab1:
    st.markdown("### Cargar Padrón de Deuda Presunta")
    
    # Columnas esperadas en el orden correcto
    COLUMNAS_ORDEN = [
        'DELEGACION', 'LOCALIDAD', 'CUIT', 'RAZON SOCIAL', 'DEUDA PRESUNTA',
        'CP', 'CALLE', 'NUMERO', 'PISO', 'DPTO', 'FECHARELDEPENDENCIA',
        'EMAIL', 'TEL_DOM_LEGAL', 'TEL_DOM_REAL', 'ULTIMA ACTA', 'DESDE',
        'HASTA', 'DETECTADO', 'ESTADO', 'FECHA_PAGO_OBL', 'EMPL 10-2025',
        'EMP 11-2025', 'EMPL 12-2025', 'ACTIVIDAD', 'SITUACION'
    ]
    
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
            
            # Limpiar nombres de columnas (mayúsculas y sin espacios extras)
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            # Buscar las columnas necesarias (flexible, no importa el orden)
            mapeo_columnas = {}
            for col_esperada in COLUMNAS_ORDEN:
                col_upper = col_esperada.upper()
                if col_upper in df_raw.columns:
                    mapeo_columnas[col_esperada] = col_upper
                else:
                    # Buscar coincidencia parcial
                    encontrada = None
                    for col_real in df_raw.columns:
                        if col_esperada.upper() in col_real or col_real in col_esperada.upper():
                            encontrada = col_real
                            break
                    if encontrada:
                        mapeo_columnas[col_esperada] = encontrada
                    else:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>COLUMNA NO ENCONTRADA</strong><br>
                            No se pudo encontrar la columna: {col_esperada}<br>
                            Columnas disponibles: {', '.join(df_raw.columns[:10])}...
                        </div>
                        """, unsafe_allow_html=True)
                        st.stop()
            
            # Reordenar el DataFrame según el orden esperado
            df_ordenado = pd.DataFrame()
            for col_esperada in COLUMNAS_ORDEN:
                col_real = mapeo_columnas[col_esperada]
                df_ordenado[col_esperada] = df_raw[col_real]
            
            # Limpiar datos
            df_ordenado = df_ordenado.replace({pd.NA: None, float('nan'): None})
            
            # Validar que se pudo leer correctamente
            if df_ordenado.empty or len(df_ordenado) == 0:
                st.markdown("""
                <div class="warning-box">
                    <strong>ARCHIVO VACÍO</strong><br>
                    El archivo no contiene datos para procesar.
                </div>
                """, unsafe_allow_html=True)
            else:
                # Verificar que la columna CUIT y ULTIMA ACTA existan
                if 'CUIT' not in df_ordenado.columns or 'ULTIMA ACTA' not in df_ordenado.columns:
                    st.markdown("""
                    <div class="warning-box">
                        <strong>ESTRUCTURA INCORRECTA</strong><br>
                        El archivo no contiene las columnas 'CUIT' o 'ULTIMA ACTA'.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Agregar columnas nuevas
                    df_ordenado['legajo_inspector'] = None
                    df_ordenado['fecha_vencimiento'] = None
                    df_ordenado['nro_acta'] = None
                    df_ordenado['fecha_carga'] = datetime.now().isoformat()
                    df_ordenado['estado_gestion'] = 'PENDIENTE'
                    
                    # Mostrar resumen
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Resumen del archivo</strong><br>
                        Registros detectados: {len(df_ordenado):,}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("Ver vista previa (primeras 10 filas)"):
                        st.dataframe(df_ordenado.head(10), use_container_width=True)
                    
                    if st.button("Confirmar carga", type="primary", key="btn_cargar_padron"):
                        with st.spinner("Verificando duplicados y procesando..."):
                            registros = df_ordenado.to_dict(orient='records')
                            
                            # Obtener todos los pares (CUIT, ULTIMA ACTA) existentes en la BD
                            existentes = supabase.table("padron_deuda_presunta").select("CUIT, ULTIMA ACTA").execute()
                            existentes_set = set()
                            for reg in existentes.data:
                                cuit_val = reg.get('CUIT')
                                acta_val = reg.get('ULTIMA ACTA')
                                if cuit_val and acta_val:
                                    existentes_set.add((str(cuit_val).strip(), str(acta_val).strip()))
                            
                            # Filtrar registros nuevos (los que NO tienen el mismo CUIT + misma ULTIMA ACTA)
                            nuevos_registros = []
                            duplicados = 0
                            
                            for reg in registros:
                                cuit_reg = str(reg.get('CUIT', '')).strip()
                                acta_reg = str(reg.get('ULTIMA ACTA', '')).strip()
                                
                                clave = (cuit_reg, acta_reg)
                                if clave not in existentes_set:
                                    nuevos_registros.append(reg)
                                else:
                                    duplicados += 1
                            
                            if nuevos_registros:
                                # Insertar en lotes de 500
                                lote_size = 500
                                total_insertados = 0
                                
                                for i in range(0, len(nuevos_registros), lote_size):
                                    lote = nuevos_registros[i:i+lote_size]
                                    resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                                    total_insertados += len(resultado.data)
                                
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
                                    Todos los registros del archivo ya existen en la base de datos<br>
                                    (mismo CUIT y mismo número de ULTIMA ACTA).
                                </div>
                                """, unsafe_allow_html=True)
                            
        except Exception as e:
            st.markdown(f"""
            <div class="warning-box">
                <strong>ERROR AL LEER EL ARCHIVO</strong><br>
                {str(e)}<br><br>
                <strong>Posibles soluciones:</strong><br>
                - Verificar que el archivo no esté abierto en otro programa<br>
                - Guardar el archivo como .xlsx (formato más reciente)<br>
                - Verificar que las columnas tengan los nombres esperados
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 2: EDITAR LEGAJOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    # Obtener lista de períodos disponibles (usando ULTIMA ACTA como identificador)
    datos_totales = supabase.table("padron_deuda_presunta").select("ULTIMA ACTA, fecha_carga").order("fecha_carga", desc=True).execute()
    
    actas_unicas = []
    if datos_totales.data:
        for reg in datos_totales.data:
            if reg.get('ULTIMA ACTA') and reg.get('ULTIMA ACTA') not in actas_unicas:
                actas_unicas.append(reg.get('ULTIMA ACTA'))
    
    if actas_unicas:
        acta_seleccionada = st.selectbox("Seleccionar período (por ULTIMA ACTA)", actas_unicas, key="select_acta")
        
        # Botón para editar inspectores
        if st.button("👥 Administrar Inspectores", key="btn_admin_inspectores"):
            st.switch_page("pages/inspectores.py")
        
        # Cargar datos del acta seleccionada
        datos = supabase.table("padron_deuda_presunta").select("*").eq("ULTIMA ACTA", acta_seleccionada).execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            
            # Seleccionar columnas a mostrar
            columnas_mostrar = ['id', 'CUIT', 'RAZON SOCIAL', 'CALLE', 'NUMERO', 'legajo_inspector', 'fecha_vencimiento', 'nro_acta', 'estado_gestion']
            df_editable = df_datos[[col for col in columnas_mostrar if col in df_datos.columns]].copy()
            
            st.info(f"Mostrando {len(df_editable)} registros del acta {acta_seleccionada}")
            
            # Editor de datos
            edited_df = st.data_editor(
                df_editable,
                use_container_width=True,
                column_config={
                    "legajo_inspector": st.column_config.TextColumn("Legajo Inspector", help="Número de legajo del inspector asignado"),
                    "fecha_vencimiento": st.column_config.DateColumn("Fecha Vencimiento", format="DD/MM/YYYY"),
                    "estado_gestion": st.column_config.SelectColumn("Estado", options=["PENDIENTE", "ACTA_SOLICITADA", "ACTA_RECIBIDA", "CERRADO"]),
                },
                disabled=['id', 'CUIT', 'RAZON SOCIAL', 'CALLE', 'NUMERO', 'nro_acta'],
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
                        <strong>CAMBIOS GUARDADOS</strong><br>
                        Los datos fueron actualizados correctamente.
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
        else:
            st.info(f"No hay datos para el acta {acta_seleccionada}")
    else:
        st.info("No hay períodos cargados. Cargue un padrón primero.")

# ==================== TAB 3: SOLICITAR ACTAS ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    
    if actas_unicas:
        acta_solicitud = st.selectbox("Seleccionar período (por ULTIMA ACTA)", actas_unicas, key="select_acta_solicitud")
        
        # Cargar registros con legajo y vencimiento completos
        datos = supabase.table("padron_deuda_presunta").select("*").eq("ULTIMA ACTA", acta_solicitud).execute()
        
        if datos.data:
            df_solicitud = pd.DataFrame(datos.data)
            
            # Filtrar los que tienen legajo y vencimiento
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
                
                # Mostrar los registros a enviar
                df_envio = df_completos[['CUIT', 'legajo_inspector', 'fecha_vencimiento', 'RAZON SOCIAL']].copy()
                st.dataframe(df_envio, use_container_width=True)
                
                # Campo para email destinatario
                email_destino = st.text_input(
                    "Email de destino (Central)",
                    value="central@osecac.org.ar",
                    help="Los datos se enviarán a esta dirección"
                )
                
                if st.button("Enviar Solicitud por Email", type="primary", key="btn_enviar_email"):
                    with st.spinner("Preparando solicitud..."):
                        # Construir cuerpo del email
                        cuerpo = f"Solicitud de Actas - Acta N° {acta_solicitud}\n\n"
                        cuerpo += "Se solicitan actas para las siguientes empresas:\n\n"
                        cuerpo += "CUIT | Legajo Inspector | Fecha Vencimiento | Razón Social\n"
                        cuerpo += "-" * 80 + "\n"
                        
                        for _, row in df_completos.iterrows():
                            cuerpo += f"{row['CUIT']} | {row['legajo_inspector']} | {row['fecha_vencimiento']} | {row['RAZON SOCIAL']}\n"
                        
                        cuerpo += f"\nTotal de solicitudes: {len(df_completos)}\n"
                        cuerpo += f"Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        
                        # Mostrar preview
                        st.text_area("Preview del email", cuerpo, height=300)
                        
                        # Actualizar estado en la base
                        for _, row in df_completos.iterrows():
                            supabase.table("padron_deuda_presunta").update({
                                "estado_gestion": "ACTA_SOLICITADA"
                            }).eq("id", row['id']).execute()
                        
                        st.markdown("""
                        <div class="success-box">
                            <strong>SOLICITUD REGISTRADA</strong><br>
                            Se actualizó el estado de los registros a "ACTA_SOLICITADA".<br>
                            <strong>Nota:</strong> La configuración de envío de email SMTP debe ser completada en los secrets.
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No hay registros con legajo y fecha de vencimiento completos para este período.")
        else:
            st.info(f"No hay datos para el acta {acta_solicitud}")
    else:
        st.info("No hay períodos cargados.")
