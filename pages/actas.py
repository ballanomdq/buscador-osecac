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
    .delete-button button { background-color: #dc2626 !important; }
    .delete-button button:hover { background-color: #b91c1c !important; }
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
def convertir_fecha_excel(valor):
    """Convierte número de Excel a fecha (44854 -> 28/02/2019)"""
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (int, float)):
            fecha_base = datetime(1899, 12, 30)
            fecha = fecha_base + pd.Timedelta(days=float(valor))
            return fecha.strftime('%d/%m/%Y')
        if isinstance(valor, str):
            return valor
        return None
    except:
        return str(valor) if valor else None

# ==================== MAPEO DE COLUMNAS ====================
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
    'fecha_pago_obl': 'FECHA PAGO OBL',
    'empl_10_2025': 'EMPL 10-2025',
    'emp_11_2025': 'EMP 11-2025',
    'empl_12_2025': 'EMPL 12-2025',
    'actividad': 'ACTIVIDAD',
    'situacion': 'SITUACION',
    'leg': 'LEG',
    'vto': 'VTO',
    'mail_enviado': 'MAIL ENVIADO',
    'acta': 'ACTA',
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
                df_raw = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                df_raw = pd.read_excel(uploaded_file, engine='openpyxl')
            
            df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
            
            df_final = pd.DataFrame()
            for col_excel, col_tabla in MAPEO_EXCEL_A_TABLA.items():
                if col_excel in df_raw.columns:
                    valores = []
                    for val in df_raw[col_excel]:
                        if pd.isna(val):
                            valores.append(None)
                        else:
                            val_str = str(val).strip()
                            
                            if col_tabla in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(int(num))
                                    else:
                                        valores.append(num)
                                except:
                                    valores.append(val_str)
                            
                            elif col_tabla in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl']:
                                if isinstance(val, (int, float)) and val > 30000:
                                    fecha = convertir_fecha_excel(val)
                                    valores.append(fecha)
                                else:
                                    valores.append(val_str)
                            
                            elif col_tabla in ['deuda_presunta', 'detectado']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(f"${int(num):,}".replace(",", "."))
                                    else:
                                        valores.append(f"${num:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                except:
                                    valores.append(val_str)
                            
                            else:
                                valores.append(val_str)
                    
                    df_final[col_tabla] = valores
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
                    total = 0
                    for i in range(0, len(registros), 100):
                        lote = registros[i:i+100]
                        resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                        total += len(resultado.data)
                    st.success(f"✅ Carga completada: {total} registros insertados.")
                            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 2: EDITAR LEGAJOS Y VTOS (CON ELIMINACIÓN) ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    # Botones de acción en la parte superior
    col_accion1, col_accion2, col_accion3 = st.columns(3)
    
    with col_accion1:
        if st.button("🗑️ Eliminar ÚLTIMOS 100 registros", help="Elimina los 100 registros más recientes"):
            with st.spinner("Eliminando..."):
                # Obtener los últimos 100 IDs
                datos = supabase.table("padron_deuda_presunta").select("id").order("id", desc=True).limit(100).execute()
                if datos.data:
                    ids_a_eliminar = [reg['id'] for reg in datos.data]
                    for id_reg in ids_a_eliminar:
                        supabase.table("padron_deuda_presunta").delete().eq("id", id_reg).execute()
                    st.success(f"✅ Se eliminaron {len(ids_a_eliminar)} registros")
                    st.rerun()
                else:
                    st.warning("No hay registros para eliminar")
    
    with col_accion2:
        if st.button("🗑️ Eliminar TODOS los registros", help="¡CUIDADO! Elimina toda la base"):
            st.session_state.confirmar_eliminar = True
    
    with col_accion3:
        if st.button("🔄 Recargar datos", help="Actualiza la vista"):
            st.rerun()
    
    # Confirmación de eliminación total
    if st.session_state.get('confirmar_eliminar', False):
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ ¡ATENCIÓN!</strong><br>
            Estás por eliminar TODOS los registros de la base de datos.<br>
            Esta acción no se puede deshacer.
        </div>
        """, unsafe_allow_html=True)
        
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("✅ SÍ, ELIMINAR TODO", key="confirmar_si"):
                with st.spinner("Eliminando todos los registros..."):
                    supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                    st.success("✅ Todos los registros fueron eliminados")
                    st.session_state.confirmar_eliminar = False
                    st.rerun()
        with col_confirm2:
            if st.button("❌ Cancelar", key="confirmar_no"):
                st.session_state.confirmar_eliminar = False
                st.rerun()
    
    st.markdown("---")
    
    # Mostrar datos
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            total_registros = len(df_datos)
            st.write(f"**Total de registros en la base:** {total_registros}")
            
            # Selector de cuántos registros mostrar
            opciones_mostrar = [100, 500, 1000, 5000, total_registros]
            mostrar_seleccion = st.selectbox(
                "¿Cuántos registros querés ver?",
                options=opciones_mostrar,
                index=min(3, len(opciones_mostrar)-1),
                format_func=lambda x: f"Últimos {x}" if x != total_registros else f"Todos ({x})"
            )
            
            # Obtener los últimos N registros (o todos)
            if mostrar_seleccion == total_registros:
                df_mostrar = df_datos.copy()
            else:
                df_mostrar = df_datos.tail(mostrar_seleccion).copy()
            
            # Eliminar columna fecha_carga de la vista
            if 'fecha_carga' in df_mostrar.columns:
                df_mostrar = df_mostrar.drop(columns=['fecha_carga'])
            
            # Renombrar columnas
            df_mostrar = df_mostrar.rename(columns=TITULOS_MOSTRAR)
            
            st.info(f"📝 Mostrando {len(df_mostrar)} registros. Editá las celdas y presioná 'Guardar Cambios'")
            
            # Checkbox para seleccionar filas a eliminar individualmente
            with st.expander("🗑️ Eliminar registros específicos"):
                st.warning("Seleccioná las filas que querés eliminar y presioná 'Eliminar seleccionados'")
                
                # Agregar columna de selección
                df_con_seleccion = df_mostrar.copy()
                df_con_seleccion.insert(0, "SELECCIONAR", False)
                
                df_seleccion = st.data_editor(
                    df_con_seleccion,
                    use_container_width=True,
                    column_config={"SELECCIONAR": st.column_config.CheckboxColumn("Eliminar", help="Marcar para eliminar")},
                    disabled=df_con_seleccion.columns[2:].tolist(),
                    key="selector_eliminar"
                )
                
                if st.button("🗑️ Eliminar seleccionados", type="primary"):
                    ids_a_eliminar = df_seleccion[df_seleccion["SELECCIONAR"]]["ID"].tolist()
                    if ids_a_eliminar:
                        with st.spinner(f"Eliminando {len(ids_a_eliminar)} registros..."):
                            for id_reg in ids_a_eliminar:
                                supabase.table("padron_deuda_presunta").delete().eq("id", id_reg).execute()
                            st.success(f"✅ Se eliminaron {len(ids_a_eliminar)} registros")
                            st.rerun()
                    else:
                        st.warning("No seleccionaste ningún registro")
            
            st.markdown("---")
            st.markdown("### Editor de datos")
            
            edited_df = st.data_editor(
                df_mostrar,
                use_container_width=True,
                height=600,
                disabled=['ID', 'CUIT', 'RAZON SOCIAL', 'DEUDA PRESUNTA', 'CP', 'CALLE', 'NUMERO', 
                          'PISO', 'DPTO', 'FECHARELDEPENDENCIA', 'EMAIL', 'TEL_DOM_LEGAL', 'TEL_DOM_REAL',
                          'ULTIMA ACTA', 'DESDE', 'HASTA', 'DETECTADO', 'ESTADO', 'FECHA PAGO OBL',
                          'EMPL 10-2025', 'EMP 11-2025', 'EMPL 12-2025', 'ACTIVIDAD', 'SITUACION'],
                key="editor_completo"
            )
            
            if st.button("💾 Guardar Cambios", type="primary"):
                with st.spinner("Guardando cambios..."):
                    modificados = 0
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
            st.info("No hay datos cargados. Cargue un padrón primero.")
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
