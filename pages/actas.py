import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import numpy as np
import re

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

# ==================== FUNCIONES DE CONVERSIÓN ====================
def fecha_para_mostrar(valor):
    """Convierte fecha a DD/MM/YYYY para mostrar"""
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%d/%m/%Y')
        if isinstance(valor, str):
            # Si ya es string en formato YYYY-MM-DD, convertirlo
            if re.match(r'\d{4}-\d{2}-\d{2}', valor):
                fecha = datetime.strptime(valor, '%Y-%m-%d')
                return fecha.strftime('%d/%m/%Y')
            return valor
        if isinstance(valor, (int, float)):
            fecha_base = datetime(1899, 12, 30)
            fecha = fecha_base + pd.Timedelta(days=float(valor))
            return fecha.strftime('%d/%m/%Y')
        return str(valor)
    except:
        return str(valor) if valor else None

def fecha_para_guardar(valor):
    """Convierte fecha a YYYY-MM-DD para guardar en Supabase"""
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%Y-%m-%d')
        if isinstance(valor, str):
            # Si viene en formato DD/MM/YYYY
            if re.match(r'\d{2}/\d{2}/\d{4}', valor):
                fecha = datetime.strptime(valor, '%d/%m/%Y')
                return fecha.strftime('%Y-%m-%d')
            # Si viene en formato YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', valor):
                return valor
        if isinstance(valor, (int, float)):
            fecha_base = datetime(1899, 12, 30)
            fecha = fecha_base + pd.Timedelta(days=float(valor))
            return fecha.strftime('%Y-%m-%d')
        return None
    except:
        return None

def limpiar_numero_entero(valor):
    """Convierte 1.0 a 1"""
    if valor is None or pd.isna(valor):
        return None
    try:
        num = float(valor)
        if num.is_integer():
            return int(num)
        return None
    except:
        return None

def convertir_fecha_excel_para_guardar(valor):
    """Convierte número de Excel a YYYY-MM-DD"""
    if valor is None or pd.isna(valor):
        return None
    try:
        if isinstance(valor, (int, float)) and valor > 30000:
            fecha_base = datetime(1899, 12, 30)
            fecha = fecha_base + pd.Timedelta(days=float(valor))
            return fecha.strftime('%Y-%m-%d')
        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor.strftime('%Y-%m-%d')
        if isinstance(valor, str):
            if re.match(r'\d{2}/\d{2}/\d{4}', valor):
                fecha = datetime.strptime(valor, '%d/%m/%Y')
                return fecha.strftime('%Y-%m-%d')
            return valor
        return None
    except:
        return None

def limpiar_para_json(valor):
    """Convierte CUALQUIER valor a JSON serializable"""
    if valor is None:
        return None
    if pd.isna(valor):
        return None
    if isinstance(valor, float):
        if np.isnan(valor) or np.isinf(valor):
            return None
        if valor.is_integer():
            return int(valor)
        return valor
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.strftime('%Y-%m-%d')
    if isinstance(valor, np.integer):
        return int(valor)
    if isinstance(valor, np.floating):
        if np.isnan(valor):
            return None
        return float(valor)
    if isinstance(valor, str) and valor.strip() == '':
        return None
    return valor

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
                            # Columnas de números enteros (EMPL)
                            if col_tabla in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(int(num))
                                    else:
                                        valores.append(None)
                                except:
                                    valores.append(None)
                            
                            # Columnas de fechas - guardar en formato ISO
                            elif col_tabla in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl']:
                                fecha_iso = convertir_fecha_excel_para_guardar(val)
                                valores.append(fecha_iso)
                            
                            # Columnas de montos
                            elif col_tabla in ['deuda_presunta', 'detectado']:
                                try:
                                    num = float(val)
                                    if num.is_integer():
                                        valores.append(f"${int(num):,}".replace(",", "."))
                                    else:
                                        valores.append(f"${num:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                                except:
                                    valores.append(str(val) if str(val).strip() else None)
                            
                            else:
                                valores.append(str(val).strip() if str(val).strip() else None)
                    
                    df_final[col_tabla] = valores
                else:
                    st.error(f"Columna '{col_excel}' no encontrada")
                    st.stop()
            
            # Agregar columnas extras
            df_final['leg'] = None
            df_final['vto'] = None
            df_final['mail_enviado'] = 'NO'
            df_final['acta'] = None
            df_final['fecha_carga'] = datetime.now().strftime('%Y-%m-%d')
            df_final['estado_gestion'] = 'PENDIENTE'
            
            # Limpieza final
            for col in df_final.columns:
                df_final[col] = df_final[col].apply(limpiar_para_json)
            
            st.success(f"✅ Archivo procesado: {len(df_final)} registros")
            
            # Vista previa con fechas formateadas para mostrar
            df_preview = df_final.copy()
            for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
                if col in df_preview.columns:
                    df_preview[col] = df_preview[col].apply(fecha_para_mostrar)
            
            with st.expander("Vista previa"):
                st.dataframe(df_preview.head(10), use_container_width=True)
            
            if st.button("✅ Confirmar carga", type="primary"):
                with st.spinner("Cargando datos..."):
                    registros = df_final.to_dict(orient='records')
                    
                    for reg in registros:
                        for k, v in reg.items():
                            if pd.isna(v):
                                reg[k] = None
                    
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
            
            # Limpiar números enteros en EMPL
            for col in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
                if col in df_datos.columns:
                    df_datos[col] = df_datos[col].apply(limpiar_numero_entero)
            
            # Convertir fechas a formato de visualización (DD/MM/YYYY)
            for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto']:
                if col in df_datos.columns:
                    df_datos[col] = df_datos[col].apply(fecha_para_mostrar)
            
            # Mostrar TODOS los registros
            st.info(f"📝 Mostrando TODOS los {total_registros} registros")
            
            df_mostrar = df_datos.copy()
            if 'fecha_carga' in df_mostrar.columns:
                df_mostrar = df_mostrar.drop(columns=['fecha_carga'])
            
            df_mostrar = df_mostrar.rename(columns=TITULOS_MOSTRAR)
            
            edited_df = st.data_editor(
                df_mostrar,
                use_container_width=True,
                height=700,
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
                        
                        # LEG
                        nuevo_leg = row.get('LEG')
                        viejo_leg = original.get('LEG')
                        if pd.isna(nuevo_leg) or nuevo_leg == '':
                            nuevo_leg = None
                        if pd.isna(viejo_leg) or viejo_leg == '':
                            viejo_leg = None
                        if nuevo_leg != viejo_leg:
                            datos_update['leg'] = nuevo_leg
                        
                        # VTO - convertir a formato ISO para guardar
                        nuevo_vto = row.get('VTO')
                        viejo_vto = original.get('VTO')
                        if pd.isna(nuevo_vto) or nuevo_vto == '':
                            nuevo_vto = None
                        else:
                            nuevo_vto = fecha_para_guardar(nuevo_vto)
                        if pd.isna(viejo_vto) or viejo_vto == '':
                            viejo_vto = None
                        if nuevo_vto != viejo_vto:
                            datos_update['vto'] = nuevo_vto
                        
                        # MAIL ENVIADO
                        nuevo_mail = row.get('MAIL ENVIADO')
                        viejo_mail = original.get('MAIL ENVIADO')
                        if pd.isna(nuevo_mail) or nuevo_mail == '':
                            nuevo_mail = 'NO'
                        if nuevo_mail != viejo_mail:
                            datos_update['mail_enviado'] = nuevo_mail
                        
                        # ACTA
                        nuevo_acta = row.get('ACTA')
                        viejo_acta = original.get('ACTA')
                        if pd.isna(nuevo_acta) or nuevo_acta == '':
                            nuevo_acta = None
                        if nuevo_acta != viejo_acta:
                            datos_update['acta'] = nuevo_acta
                        
                        # ESTADO GESTION
                        nuevo_estado = row.get('ESTADO GESTION')
                        viejo_estado = original.get('ESTADO GESTION')
                        if pd.isna(nuevo_estado) or nuevo_estado == '':
                            nuevo_estado = 'PENDIENTE'
                        if nuevo_estado != viejo_estado:
                            datos_update['estado_gestion'] = nuevo_estado
                        
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
                # Mostrar fechas en formato DD/MM/YYYY
                df_mostrar = df_listos[['cuit', 'razon_social', 'leg', 'vto']].copy()
                if 'vto' in df_mostrar.columns:
                    df_mostrar['vto'] = df_mostrar['vto'].apply(fecha_para_mostrar)
                st.dataframe(df_mostrar, use_container_width=True)
                
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
