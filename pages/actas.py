import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import math

# Configuración de página
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase (proyecto fiscalización)
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

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

# ==================== MAPEO EXCEL -> TABLA ====================
MAPEO_EXCEL_A_TABLA = {
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

# ==================== FUNCIÓN LIMPIAR VALORES ====================
def limpiar_valor(valor):
    if valor is None:
        return None
    if pd.isna(valor) or (isinstance(valor, float) and math.isnan(valor)):
        return None
    if isinstance(valor, float) and math.isinf(valor):
        return None
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.isoformat() if hasattr(valor, 'isoformat') else str(valor)
    if isinstance(valor, (int, float)):
        return valor
    if isinstance(valor, str):
        return valor.strip() if valor.strip() else None
    return str(valor) if valor else None

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["📊 Cargar Padrón", "✏️ Editar Legajos y Vtos", "📧 Solicitar Actas"])

# ==================== TAB 1: CARGAR PADRÓN ====================
with tab1:
    st.markdown("### Cargar Padrón de Deuda Presunta")
    
    uploaded_file = st.file_uploader(
        "Seleccionar archivo Excel",
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
            
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            # Crear DataFrame con las columnas mapeadas
            df_final = pd.DataFrame()
            for col_excel, col_tabla in MAPEO_EXCEL_A_TABLA.items():
                if col_excel in df_raw.columns:
                    df_final[col_tabla] = df_raw[col_excel].apply(limpiar_valor)
                else:
                    st.error(f"Columna '{col_excel}' no encontrada en el archivo")
                    st.stop()
            
            if df_final.empty:
                st.warning("Archivo vacío")
            else:
                # Agregar columnas que no vienen del Excel
                df_final['leg'] = None
                df_final['vto'] = None
                df_final['mail_enviado'] = 'NO'
                df_final['acta'] = None
                df_final['fecha_carga'] = datetime.now().isoformat()
                df_final['estado_gestion'] = 'PENDIENTE'
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>Resumen del archivo</strong><br>
                    Registros detectados: {len(df_final):,}
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Ver vista previa"):
                    st.dataframe(df_final.head(10), use_container_width=True)
                
                if st.button("Confirmar carga", type="primary"):
                    with st.spinner("Procesando..."):
                        registros = df_final.to_dict(orient='records')
                        
                        # Verificar duplicados por CUIT + ULTIMA_ACTA
                        existentes = supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").execute()
                        existentes_set = set()
                        for reg in existentes.data:
                            cuit = reg.get('cuit', '')
                            acta = reg.get('ultima_acta', '')
                            if cuit:
                                existentes_set.add((str(cuit), str(acta) if acta else ''))
                        
                        nuevos = []
                        duplicados = 0
                        for reg in registros:
                            cuit = str(reg.get('cuit', ''))
                            acta = str(reg.get('ultima_acta', ''))
                            if (cuit, acta) not in existentes_set:
                                nuevos.append(reg)
                            else:
                                duplicados += 1
                        
                        if nuevos:
                            # Insertar en lotes de 50
                            total_insertados = 0
                            for i in range(0, len(nuevos), 50):
                                lote = nuevos[i:i+50]
                                resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                                total_insertados += len(resultado.data)
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>CARGA COMPLETADA</strong><br>
                                Se insertaron {total_insertados:,} registros nuevos.<br>
                                {f'({duplicados} duplicados omitidos)' if duplicados > 0 else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("Sin registros nuevos. Todos ya existen.")
                            
        except Exception as e:
            st.error(f"Error: {str(e)[:300]}")

# ==================== TAB 2: EDITAR LEGAJOS Y VTOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            st.write(f"**Total de registros:** {len(df_datos)}")
            
            # Columnas a mostrar en el editor
            columnas_editor = ['id', 'cuit', 'razon_social', 'leg', 'vto', 'mail_enviado', 'acta', 'estado_gestion']
            columnas_existentes = [col for col in columnas_editor if col in df_datos.columns]
            df_editable = df_datos[columnas_existentes].copy()
            
            edited_df = st.data_editor(
                df_editable,
                use_container_width=True,
                column_config={
                    "leg": st.column_config.TextColumn("LEG", help="Número de legajo del inspector"),
                    "vto": st.column_config.DateColumn("VTO", format="DD/MM/YYYY", help="Fecha de vencimiento"),
                    "mail_enviado": st.column_config.SelectColumn("MAIL ENVIADO", options=["NO", "SI"]),
                    "acta": st.column_config.TextColumn("ACTA", help="Número de acta"),
                    "estado_gestion": st.column_config.SelectColumn("Estado", options=["PENDIENTE", "ACTA_SOLICITADA", "ACTA_RECIBIDA", "CERRADO"]),
                },
                disabled=['id', 'cuit', 'razon_social'],
                key="editor_completo"
            )
            
            if st.button("Guardar Cambios", type="primary"):
                with st.spinner("Guardando..."):
                    for _, row in edited_df.iterrows():
                        datos_update = {}
                        if 'leg' in edited_df.columns:
                            datos_update['leg'] = row['leg'] if pd.notna(row['leg']) else None
                        if 'vto' in edited_df.columns:
                            datos_update['vto'] = row['vto'] if pd.notna(row['vto']) else None
                        if 'mail_enviado' in edited_df.columns:
                            datos_update['mail_enviado'] = row['mail_enviado']
                        if 'acta' in edited_df.columns:
                            datos_update['acta'] = row['acta'] if pd.notna(row['acta']) else None
                        if 'estado_gestion' in edited_df.columns:
                            datos_update['estado_gestion'] = row['estado_gestion']
                        
                        if datos_update:
                            supabase.table("padron_deuda_presunta").update(datos_update).eq("id", row['id']).execute()
                    
                    st.success("Cambios guardados correctamente")
                    st.rerun()
        else:
            st.info("No hay datos cargados. Cargue un padrón primero.")
    except Exception as e:
        st.error(f"Error: {str(e)[:200]}")

# ==================== TAB 3: SOLICITAR ACTAS ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    st.info("Funcionalidad en desarrollo. Próximamente.")
