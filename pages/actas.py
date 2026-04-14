import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Fiscalización - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

# Estilo
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; }
    .warning-box { background-color: #451a03; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 1rem 0; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; }
    div[data-testid="stButton"] button { background-color: #3b82f6; color: white; font-weight: 500; border: none; padding: 0.4rem 1.2rem; }
    div[data-testid="stButton"] button:hover { background-color: #2563eb; }
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

# MAPEO DE COLUMNAS
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

# Títulos bonitos para mostrar
TITULOS_MOSTRAR = {
    'id': 'ID',
    'delegacion': 'DELEGACION',
    'localidad': 'LOCALIDAD',
    'cuit': 'CUIT',
    'razon_social': 'RAZON SOCIAL',
    'deuda_presunta': 'DEUDA PRESUNTA',
    'cp': 'CP',
    'calle': 'CALLE',
    'numero': 'NUMERO',
    'piso': 'PISO',
    'dpto': 'DPTO',
    'fechareldependencia': 'FECHARELDEPENDENCIA',
    'email': 'EMAIL',
    'tel_dom_legal': 'TEL_DOM_LEGAL',
    'tel_dom_real': 'TEL_DOM_REAL',
    'ultima_acta': 'ULTIMA ACTA',
    'desde': 'DESDE',
    'hasta': 'HASTA',
    'detectado': 'DETECTADO',
    'estado': 'ESTADO',
    'fecha_pago_obl': 'FECHA_PAGO_OBL',
    'empl_10_2025': 'EMPL 10-2025',
    'emp_11_2025': 'EMP 11-2025',
    'empl_12_2025': 'EMPL 12-2025',
    'actividad': 'ACTIVIDAD',
    'situacion': 'SITUACION',
    'leg': 'LEG',
    'vto': 'VTO',
    'mail_enviado': 'MAIL ENVIADO',
    'acta': 'ACTA',
    'fecha_carga': 'FECHA CARGA',
    'estado_gestion': 'ESTADO GESTION'
}

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
        st.info(f"Archivo: {uploaded_file.name}")
        
        try:
            if uploaded_file.name.endswith('.xls'):
                df_raw = pd.read_excel(uploaded_file, engine='xlrd', dtype=str)
            else:
                df_raw = pd.read_excel(uploaded_file, engine='openpyxl', dtype=str)
            
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            df_raw = df_raw.replace({np.nan: None, 'nan': None, 'NaN': None, '': None})
            
            df_final = pd.DataFrame()
            for col_excel, col_tabla in MAPEO_EXCEL_A_TABLA.items():
                if col_excel in df_raw.columns:
                    df_final[col_tabla] = df_raw[col_excel]
                else:
                    st.error(f"Columna '{col_excel}' no encontrada")
                    st.stop()
            
            df_final['leg'] = None
            df_final['vto'] = None
            df_final['mail_enviado'] = 'NO'
            df_final['acta'] = None
            df_final['fecha_carga'] = datetime.now().isoformat()
            df_final['estado_gestion'] = 'PENDIENTE'
            
            st.success(f"✅ Archivo procesado: {len(df_final)} registros")
            
            with st.expander("Vista previa"):
                st.dataframe(df_final.head(10), use_container_width=True)
            
            if st.button("✅ Confirmar carga", type="primary"):
                with st.spinner("Cargando datos..."):
                    registros = df_final.to_dict(orient='records')
                    
                    existentes = supabase.table("padron_deuda_presunta").select("cuit, ultima_acta").execute()
                    existentes_set = set()
                    for reg in existentes.data:
                        cuit = str(reg.get('cuit') or '')
                        acta = str(reg.get('ultima_acta') or '')
                        existentes_set.add((cuit, acta))
                    
                    nuevos = []
                    duplicados = 0
                    for reg in registros:
                        cuit = str(reg.get('cuit') or '')
                        acta = str(reg.get('ultima_acta') or '')
                        if (cuit, acta) not in existentes_set:
                            nuevos.append(reg)
                        else:
                            duplicados += 1
                    
                    if nuevos:
                        total = 0
                        for i in range(0, len(nuevos), 100):
                            lote = nuevos[i:i+100]
                            resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                            total += len(resultado.data)
                        
                        st.success(f"✅ Carga completada: {total} registros insertados. Duplicados omitidos: {duplicados}")
                    else:
                        st.warning("Sin registros nuevos")
                            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 2: EDITAR LEGAJOS Y VTOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            total_registros = len(df_datos)
            st.write(f"**Total de registros en la base:** {total_registros}")
            
            # Selector de cantidad
            mostrar = st.radio(
                "¿Cuántos registros querés ver?",
                options=[100, 500, 1000, total_registros],
                horizontal=True,
                index=0
            )
            
            df_mostrar = df_datos.head(mostrar).copy()
            
            # Renombrar columnas para mostrar títulos bonitos
            df_mostrar = df_mostrar.rename(columns=TITULOS_MOSTRAR)
            
            st.info(f"📝 Mostrando {len(df_mostrar)} registros. Editá las celdas y presioná 'Guardar Cambios'")
            
            edited_df = st.data_editor(
                df_mostrar,
                use_container_width=True,
                height=500,
                disabled=['ID', 'CUIT', 'RAZON SOCIAL'],  # Estas no se pueden editar
                key="editor_completo"
            )
            
            if st.button("💾 Guardar Cambios", type="primary"):
                with st.spinner("Guardando cambios..."):
                    modificados = 0
                    # Mapeo inverso para guardar
                    inverso = {v: k for k, v in TITULOS_MOSTRAR.items()}
                    
                    for idx, row in edited_df.iterrows():
                        original = df_mostrar.loc[idx]
                        datos_update = {}
                        
                        for col_bonito in ['LEG', 'VTO', 'MAIL ENVIADO', 'ACTA', 'ESTADO GESTION']:
                            if col_bonito in edited_df.columns:
                                nuevo_valor = row[col_bonito]
                                viejo_valor = original.get(col_bonito)
                                
                                if pd.isna(nuevo_valor) or nuevo_valor == '':
                                    nuevo_valor = None
                                if pd.isna(viejo_valor) or viejo_valor == '':
                                    viejo_valor = None
                                
                                if nuevo_valor != viejo_valor:
                                    col_real = inverso.get(col_bonito, col_bonito.lower())
                                    datos_update[col_real] = nuevo_valor
                        
                        if datos_update:
                            supabase.table("padron_deuda_presunta").update(datos_update).eq("id", row['ID']).execute()
                            modificados += 1
                    
                    st.success(f"✅ {modificados} registros actualizados correctamente")
                    st.rerun()
        else:
            st.info("No hay datos cargados")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==================== TAB 3: SOLICITAR ACTAS ====================
with tab3:
    st.markdown("### Solicitar Actas a Central")
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            
            df_listos = df_datos[
                (df_datos['leg'].notna()) & 
                (df_datos['vto'].notna()) &
                (df_datos['mail_enviado'] != 'SI')
            ]
            
            if len(df_listos) > 0:
                st.markdown(f"""
                <div class="info-box">
                    <strong>Registros listos:</strong> {len(df_listos)} empresas
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(df_listos[['cuit', 'razon_social', 'leg', 'vto']], use_container_width=True)
                
                if st.button("Enviar solicitud", type="primary"):
                    for _, row in df_listos.iterrows():
                        supabase.table("padron_deuda_presunta").update({
                            "mail_enviado": "SI",
                            "estado_gestion": "ACTA_SOLICITADA"
                        }).eq("id", row['id']).execute()
                    
                    st.success(f"Solicitud registrada para {len(df_listos)} empresas")
            else:
                st.info("No hay registros listos")
        else:
            st.info("No hay datos cargados")
    except Exception as e:
        st.error(f"Error: {str(e)}")
