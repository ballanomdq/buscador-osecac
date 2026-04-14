import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import numpy as np
import json

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

# ==================== FUNCIÓN DE LIMPIEZA NUCLEAR ====================
def limpiar_para_json(valor):
    """Convierte CUALQUIER valor a un tipo JSON serializable"""
    # None
    if valor is None:
        return None
    # NaN de pandas o numpy
    if pd.isna(valor):
        return None
    if isinstance(valor, float):
        if np.isnan(valor) or np.isinf(valor):
            return None
        # Si es float sin decimales, convertir a int
        if valor.is_integer():
            return int(valor)
        return valor
    # Timestamp
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.isoformat()
    # Numpy integers
    if isinstance(valor, np.integer):
        return int(valor)
    # Numpy floats
    if isinstance(valor, np.floating):
        if np.isnan(valor):
            return None
        return float(valor)
    # String vacío
    if isinstance(valor, str) and valor.strip() == '':
        return None
    # Cualquier otro tipo
    return valor

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
            # Leer Excel
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
                        # Limpieza nuclear de cada valor
                        if pd.isna(val):
                            valores.append(None)
                        else:
                            val_str = str(val).strip()
                            
                            # Columnas de números enteros
                            if col_tabla in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(int(num))
                                    else:
                                        valores.append(None)
                                except:
                                    valores.append(None)
                            
                            # Columnas de fechas
                            elif col_tabla in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl']:
                                if isinstance(val, (int, float)) and val > 30000:
                                    fecha = convertir_fecha_excel(val)
                                    valores.append(fecha)
                                else:
                                    valores.append(val_str if val_str else None)
                            
                            # Columnas de montos
                            elif col_tabla in ['deuda_presunta', 'detectado']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(f"${int(num):,}".replace(",", "."))
                                    else:
                                        valores.append(f"${num:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                except:
                                    valores.append(val_str if val_str else None)
                            
                            else:
                                valores.append(val_str if val_str else None)
                    
                    df_final[col_tabla] = valores
                else:
                    st.error(f"Columna '{col_excel}' no encontrada")
                    st.stop()
            
            # Agregar columnas extras
            df_final['leg'] = None
            df_final['vto'] = None
            df_final['mail_enviado'] = 'NO'
            df_final['acta'] = None
            df_final['fecha_carga'] = datetime.now().isoformat()
            df_final['estado_gestion'] = 'PENDIENTE'
            
            # LIMPIEZA NUCLEAR FINAL: convertir TODO a JSON serializable
            for col in df_final.columns:
                df_final[col] = df_final[col].apply(limpiar_para_json)
            
            st.success(f"✅ Archivo procesado: {len(df_final)} registros")
            
            with st.expander("Vista previa"):
                st.dataframe(df_final.head(10), use_container_width=True)
            
            if st.button("✅ Confirmar carga", type="primary"):
                with st.spinner("Cargando datos..."):
                    registros = df_final.to_dict(orient='records')
                    
                    # Verificar que no haya NaN en los registros
                    for reg in registros:
                        for k, v in reg.items():
                            if pd.isna(v):
                                reg[k] = None
                    
                    # Insertar en lotes
                    total = 0
                    for i in range(0, len(registros), 100):
                        lote = registros[i:i+100]
                        resultado = supabase.table("padron_deuda_presunta").insert(lote).execute()
                        total += len(resultado.data)
                    
                    st.success(f"✅ Carga completada: {total} registros insertados.")
                            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 2: EDITAR LEGAJOS Y VTOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    # Botones de acción
    col_accion1, col_accion2, col_accion3 = st.columns(3)
    
    with col_accion1:
        if st.button("🗑️ Eliminar ÚLTIMOS 100 registros"):
            with st.spinner("Eliminando..."):
                datos = supabase.table("padron_deuda_presunta").select("id").order("id", desc=True).limit(100).execute()
                if datos.data:
                    for reg in datos.data:
                        supabase.table("padron_deuda_presunta").delete().eq("id", reg['id']).execute()
                    st.success(f"✅ Se eliminaron {len(datos.data)} registros")
                    st.rerun()
    
    with col_accion2:
        if st.button("🗑️ Eliminar TODOS los registros"):
            st.session_state.confirmar_eliminar = True
    
    with col_accion3:
        if st.button("🔄 Recargar datos"):
            st.rerun()
    
    # Confirmación
    if st.session_state.get('confirmar_eliminar', False):
        st.warning("⚠️ ¿Estás seguro? Esta acción no se puede deshacer.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ SÍ, ELIMINAR TODO"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.success("✅ Todos los registros fueron eliminados")
                st.session_state.confirmar_eliminar = False
                st.rerun()
        with col_no:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_eliminar = False
                st.rerun()
    
    st.markdown("---")
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            total_registros = len(df_datos)
            st.write(f"**Total de registros en la base:** {total_registros}")
            
            # Selector de cantidad
            opciones = [100, 500, 1000, 5000, total_registros]
            mostrar = st.selectbox("Registros a mostrar:", opciones, index=min(3, len(opciones)-1))
            
            if mostrar == total_registros:
                df_mostrar = df_datos.copy()
            else:
                df_mostrar = df_datos.tail(mostrar).copy()
            
            if 'fecha_carga' in df_mostrar.columns:
                df_mostrar = df_mostrar.drop(columns=['fecha_carga'])
            
            df_mostrar = df_mostrar.rename(columns=TITULOS_MOSTRAR)
            
            st.info(f"📝 Mostrando {len(df_mostrar)} registros")
            
            # Editor
            edited_df = st.data_editor(
                df_mostrar,
                use_container_width=True,
                height=600,
                disabled=['ID', 'CUIT', 'RAZON SOCIAL', 'DEUDA PRESUNTA', 'CP', 'CALLE', 'NUMERO', 
                          'PISO', 'DPTO', 'FECHARELDEPENDENCIA', 'EMAIL', 'TEL_DOM_LEGAL', 'TEL_DOM_REAL',
                          'ULTIMA ACTA', 'DESDE', 'HASTA', 'DETECTADO', 'ESTADO', 'FECHA PAGO OBL',
                          'EMPL 10-2025', 'EMP 11-2025', 'EMPL 12-2025', 'ACTIVIDAD', 'SITUACION'],
                key="editor"
            )
            
            if st.button("💾 Guardar Cambios", type="primary"):
                with st.spinner("Guardando..."):
                    inverso = {v: k for k, v in TITULOS_MOSTRAR.items()}
                    modificados = 0
                    
                    for idx, row in edited_df.iterrows():
                        original = df_mostrar.loc[idx]
                        datos_update = {}
                        
                        for col_bonito in ['LEG', 'VTO', 'MAIL ENVIADO', 'ACTA', 'ESTADO GESTION']:
                            if col_bonito in edited_df.columns:
                                nuevo = row[col_bonito]
                                viejo = original.get(col_bonito)
                                
                                if pd.isna(nuevo) or nuevo == '':
                                    nuevo = None
                                if pd.isna(viejo) or viejo == '':
                                    viejo = None
                                
                                if nuevo != viejo:
                                    col_real = inverso.get(col_bonito, col_bonito.lower())
                                    datos_update[col_real] = limpiar_para_json(nuevo)
                        
                        if datos_update:
                            supabase.table("padron_deuda_presunta").update(datos_update).eq("id", row['ID']).execute()
                            modificados += 1
                    
                    st.success(f"✅ {modificados} registros actualizados")
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
                st.info(f"📧 {len(df_listos)} empresas listas para solicitar actas")
                st.dataframe(df_listos[['cuit', 'razon_social', 'leg', 'vto']], use_container_width=True)
                
                if st.button("📧 Enviar solicitud", type="primary"):
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
