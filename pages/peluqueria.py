import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2 import service_account
import time

# ==================== CONFIGURACIÓN DE PÁGINA ====================
st.set_page_config(
    page_title="Control de Bonos - Peluquería",
    page_icon="✂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header {
        display: none !important;
    }
    .stApp {
        background-color: #f0f2f6 !important;
    }
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(135deg, #1a3c6e, #2d5a8e);
        color: white;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        font-weight: 800;
    }
    .main-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    .card-apto {
        background: #d4edda;
        border: 3px solid #28a745;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .card-no-apto {
        background: #f8d7da;
        border: 3px solid #dc3545;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .card-apto h2 {
        color: #155724;
        margin: 0;
    }
    .card-no-apto h2 {
        color: #721c24;
        margin: 0;
    }
    .card-apto p, .card-no-apto p {
        margin: 8px 0 0 0;
        font-size: 1.1rem;
    }
    .fecha-destacada {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .boton-confirmar {
        background: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 12px !important;
        font-size: 1.2rem !important;
    }
    .boton-confirmar:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES DE GOOGLE SHEETS ====================
@st.cache_resource
def conectar_gsheets():
    """Conecta a Google Sheets usando las credenciales de st.secrets"""
    try:
        creds_info = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

def obtener_hoja_peluqueria():
    """
    Obtiene o crea la hoja de Peluquería.
    Si los encabezados faltan, los recrea automáticamente.
    """
    client = conectar_gsheets()
    if not client:
        return None
    
    try:
        # Usamos la hoja de PELUQUERIA SEC
        sheet_url = "https://docs.google.com/spreadsheets/d/19qa15tP4Hwgq-bzoo-5n6u8V_2FECll8YQT-PFw_ukc/edit?usp=sharing"
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        sh = client.open_by_key(sheet_id)
        
        # Buscar o crear la pestaña "Peluqueria"
        try:
            worksheet = sh.worksheet("Peluqueria")
        except gspread.WorksheetNotFound:
            worksheet = sh.add_worksheet(title="Peluqueria", rows=1000, cols=10)
            headers = ["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"]
            worksheet.append_row(headers)
            return worksheet
        
        # Verificar que los encabezados existan en la primera fila
        try:
            primera_fila = worksheet.row_values(1)
            # Si la primera fila está vacía o no tiene los títulos esperados
            if not primera_fila or primera_fila != ["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"]:
                # Recrear los encabezados
                worksheet.update('A1:D1', [["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"]])
        except:
            # Si hay error al leer la fila, asumimos que está vacía y ponemos los títulos
            worksheet.update('A1:D1', [["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"]])
        
        return worksheet
    except Exception as e:
        st.error(f"❌ Error al acceder a la hoja: {e}")
        return None

def cargar_datos(worksheet):
    """Carga todos los datos de la hoja como DataFrame"""
    try:
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return pd.DataFrame(columns=["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"])
        df = pd.DataFrame(data[1:], columns=data[0])
        if not df.empty:
            df["FECHA_ENTREGA"] = pd.to_datetime(df["FECHA_ENTREGA"], errors="coerce")
            df["FECHA_REGISTRO"] = pd.to_datetime(df["FECHA_REGISTRO"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame(columns=["DNI", "NOMBRE", "FECHA_ENTREGA", "FECHA_REGISTRO"])

def guardar_registro(worksheet, dni, nombre="AFILIADO"):
    """Guarda un nuevo registro con la fecha actual"""
    try:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila = [str(dni), nombre.upper(), ahora, ahora]
        worksheet.append_row(fila)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
        return False

def actualizar_registro(worksheet, fila_idx, dni, nombre, fecha_entrega):
    """Actualiza un registro existente"""
    try:
        worksheet.update_cell(fila_idx + 2, 1, str(dni))
        worksheet.update_cell(fila_idx + 2, 2, nombre.upper())
        worksheet.update_cell(fila_idx + 2, 3, fecha_entrega)
        worksheet.update_cell(fila_idx + 2, 4, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return True
    except Exception as e:
        st.error(f"❌ Error al actualizar: {e}")
        return False

def eliminar_registro(worksheet, fila_idx):
    """Elimina un registro"""
    try:
        worksheet.delete_rows(fila_idx + 2)
        return True
    except Exception as e:
        st.error(f"❌ Error al eliminar: {e}")
        return False

def limpiar_registros_antiguos(worksheet, df):
    """Elimina registros que ya pasaron los 15 días"""
    try:
        if df.empty:
            return 0
        
        ahora = datetime.now()
        filas_a_eliminar = []
        for idx, row in df.iterrows():
            if pd.notna(row["FECHA_ENTREGA"]):
                dias_pasados = (ahora - row["FECHA_ENTREGA"]).days
                if dias_pasados >= 15:
                    filas_a_eliminar.append(idx)
        
        for idx in sorted(filas_a_eliminar, reverse=True):
            worksheet.delete_rows(idx + 2)
        
        return len(filas_a_eliminar)
    except Exception as e:
        st.error(f"❌ Error al limpiar: {e}")
        return 0

# ==================== INICIALIZAR ESTADO DE SESIÓN ====================
if 'dni_consultado' not in st.session_state:
    st.session_state.dni_consultado = None
if 'registro_encontrado' not in st.session_state:
    st.session_state.registro_encontrado = None
if 'fecha_consulta' not in st.session_state:
    st.session_state.fecha_consulta = None
if 'boton_bloqueado' not in st.session_state:
    st.session_state.boton_bloqueado = False

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>✂️ CONTROL DE BONOS DE PELUQUERÍA</h1>
    <p>Sistema de control para afiliados - 15 días entre cada bono</p>
</div>
""", unsafe_allow_html=True)

# ==================== CONEXIÓN A GOOGLE SHEETS ====================
worksheet = obtener_hoja_peluqueria()

if not worksheet:
    st.error("❌ No se pudo conectar a la base de datos. Verificá las credenciales.")
    st.stop()

# ==================== LIMPIEZA AUTOMÁTICA ====================
df = cargar_datos(worksheet)
if not df.empty:
    eliminados = limpiar_registros_antiguos(worksheet, df)
    if eliminados > 0:
        st.success(f"🧹 Se eliminaron {eliminados} registros antiguos (más de 15 días).")
        df = cargar_datos(worksheet)

# ==================== SECCIÓN PRINCIPAL: CONSULTA POR DNI ====================
st.markdown("### 🔍 Consultar afiliado")

with st.form("form_consulta"):
    col1, col2 = st.columns([2, 1])
    with col1:
        dni_input = st.text_input("Ingresá el DNI del afiliado", placeholder="Ej: 25131361")
    with col2:
        consultar = st.form_submit_button("🔍 Consultar", use_container_width=True)

# ==================== LÓGICA DE CONSULTA ====================
if consultar and dni_input:
    dni_limpio = dni_input.strip()
    if not dni_limpio.isdigit():
        st.warning("⚠️ El DNI debe contener solo números.")
    else:
        df = cargar_datos(worksheet)
        if df.empty:
            st.session_state.registro_encontrado = None
            st.session_state.dni_consultado = dni_limpio
            st.session_state.fecha_consulta = None
            st.rerun()
        else:
            registro = df[df["DNI"].astype(str) == dni_limpio]
            if registro.empty:
                st.session_state.registro_encontrado = None
                st.session_state.dni_consultado = dni_limpio
                st.session_state.fecha_consulta = None
                st.rerun()
            else:
                fila = registro.iloc[0]
                st.session_state.registro_encontrado = fila
                st.session_state.dni_consultado = dni_limpio
                st.session_state.fecha_consulta = fila["FECHA_ENTREGA"]
                st.rerun()

# ==================== MOSTRAR RESULTADO DE CONSULTA ====================
if st.session_state.dni_consultado:
    dni_actual = st.session_state.dni_consultado
    registro = st.session_state.registro_encontrado
    fecha_actual = st.session_state.fecha_consulta
    
    if registro is None:
        st.markdown(f"""
        <div class="card-apto">
            <h2>✅ AFILIADO APTO PARA RETIRAR BONO</h2>
            <p><strong>DNI:</strong> {dni_actual}</p>
            <p>No tiene registros previos. Puede retirar el bono.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.boton_bloqueado:
            st.info("⏳ Procesando... por favor esperá.")
        else:
            if st.button("✅ CONFIRMAR ENTREGA DE BONO", use_container_width=True, key="btn_confirmar"):
                st.session_state.boton_bloqueado = True
                if guardar_registro(worksheet, dni_actual, "AFILIADO"):
                    st.success("✅ ¡Bono registrado exitosamente!")
                    time.sleep(1)
                    st.session_state.boton_bloqueado = False
                    st.session_state.dni_consultado = None
                    st.session_state.registro_encontrado = None
                    st.session_state.fecha_consulta = None
                    st.rerun()
                else:
                    st.error("❌ Error al guardar el registro.")
                    st.session_state.boton_bloqueado = False
    
    else:
        fecha_entrega = registro["FECHA_ENTREGA"]
        nombre = registro["NOMBRE"]
        ahora = datetime.now()
        dias_pasados = (ahora - fecha_entrega).days
        fecha_proxima = fecha_entrega + timedelta(days=15)
        
        if dias_pasados >= 15:
            st.markdown(f"""
            <div class="card-apto">
                <h2>✅ AFILIADO APTO PARA RETIRAR BONO</h2>
                <p><strong>DNI:</strong> {dni_actual}</p>
                <p><strong>Nombre:</strong> {nombre}</p>
                <p>✅ Ya pasaron <strong>{dias_pasados} días</strong> desde su último bono.</p>
                <p>📅 Última entrega: <span class="fecha-destacada">{fecha_entrega.strftime('%d/%m/%Y %H:%M')}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.boton_bloqueado:
                st.info("⏳ Procesando... por favor esperá.")
            else:
                if st.button("✅ CONFIRMAR NUEVA ENTREGA", use_container_width=True, key="btn_nueva"):
                    st.session_state.boton_bloqueado = True
                    fila_idx = df[df["DNI"].astype(str) == dni_actual].index[0]
                    nueva_fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if actualizar_registro(worksheet, fila_idx, dni_actual, nombre, nueva_fecha):
                        st.success("✅ ¡Nueva entrega registrada!")
                        time.sleep(1)
                        st.session_state.boton_bloqueado = False
                        st.session_state.dni_consultado = None
                        st.session_state.registro_encontrado = None
                        st.session_state.fecha_consulta = None
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar.")
                        st.session_state.boton_bloqueado = False
        
        else:
            dias_faltantes = 15 - dias_pasados
            st.markdown(f"""
            <div class="card-no-apto">
                <h2>⛔ AFILIADO NO APTO PARA RETIRAR BONO</h2>
                <p><strong>DNI:</strong> {dni_actual}</p>
                <p><strong>Nombre:</strong> {nombre}</p>
                <p>⏳ Deben pasar <strong>{dias_faltantes} días</strong> para poder retirar otro bono.</p>
                <p>📅 Última entrega: <span class="fecha-destacada">{fecha_entrega.strftime('%d/%m/%Y %H:%M')}</span></p>
                <p>📅 Podrá retirar nuevamente a partir del: <span class="fecha-destacada">{fecha_proxima.strftime('%d/%m/%Y')}</span></p>
            </div>
            """, unsafe_allow_html=True)

# ==================== PANEL DE ADMINISTRACIÓN (dentro de la página) ====================
with st.expander("🔧 PANEL DE ADMINISTRACIÓN - Editar/Eliminar Registros"):
    st.warning("⚠️ Esta sección es solo para personal autorizado.")
    
    df_admin = cargar_datos(worksheet)
    
    if df_admin.empty:
        st.info("📭 No hay registros en la base de datos.")
    else:
        st.write(f"📊 Total de registros activos: **{len(df_admin)}**")
        
        df_mostrar = df_admin.copy()
        df_mostrar["FECHA_ENTREGA"] = df_mostrar["FECHA_ENTREGA"].dt.strftime("%d/%m/%Y %H:%M")
        df_mostrar["FECHA_REGISTRO"] = df_mostrar["FECHA_REGISTRO"].dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(df_mostrar, use_container_width=True, height=300)
        
        st.markdown("---")
        st.subheader("✏️ Editar o Eliminar Registro")
        
        dni_lista = df_admin["DNI"].astype(str).tolist()
        dni_seleccionado = st.selectbox("Seleccionar DNI para editar/eliminar:", dni_lista)
        
        if dni_seleccionado:
            registro_editar = df_admin[df_admin["DNI"].astype(str) == dni_seleccionado].iloc[0]
            fila_idx = df_admin[df_admin["DNI"].astype(str) == dni_seleccionado].index[0]
            
            col1, col2 = st.columns(2)
            with col1:
                nuevo_dni = st.text_input("DNI", value=str(registro_editar["DNI"]))
                nuevo_nombre = st.text_input("Nombre", value=registro_editar["NOMBRE"])
            with col2:
                nueva_fecha = st.date_input(
                    "Fecha de entrega",
                    value=registro_editar["FECHA_ENTREGA"].date() if pd.notna(registro_editar["FECHA_ENTREGA"]) else datetime.now().date()
                )
                nueva_hora = st.time_input("Hora de entrega", value=datetime.now().time())
            
            fecha_completa = datetime.combine(nueva_fecha, nueva_hora).strftime("%Y-%m-%d %H:%M:%S")
            
            col_editar, col_eliminar = st.columns(2)
            with col_editar:
                if st.button("💾 GUARDAR CAMBIOS", use_container_width=True):
                    if actualizar_registro(worksheet, fila_idx, nuevo_dni, nuevo_nombre, fecha_completa):
                        st.success("✅ Registro actualizado correctamente.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar.")
            
            with col_eliminar:
                if st.button("🗑️ ELIMINAR REGISTRO", use_container_width=True):
                    if eliminar_registro(worksheet, fila_idx):
                        st.success("✅ Registro eliminado correctamente.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar.")

# ==================== ACCESO DIRECTO A GOOGLE SHEETS CON CLAVE ====================
with st.expander("🔐 ACCESO DIRECTO A GOOGLE SHEETS"):
    with st.form("form_clave"):
        clave = st.text_input("Ingresá la clave para acceder:", type="password")
        acceder = st.form_submit_button("🔓 ACCEDER")
        
        if acceder and clave == "1839":
            st.success("✅ Acceso concedido.")
            sheet_url = "https://docs.google.com/spreadsheets/d/19qa15tP4Hwgq-bzoo-5n6u8V_2FECll8YQT-PFw_ukc/edit?usp=sharing"
            st.link_button("📊 IR A GOOGLE SHEETS (PELUQUERÍA)", sheet_url, use_container_width=True)
            st.info("La pestaña 'Peluqueria' está en la parte inferior de la hoja.")
        elif acceder:
            st.error("❌ Clave incorrecta.")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("✂️ Sistema de Control de Bonos de Peluquería - OSECAC")
