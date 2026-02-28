import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
# --- IMPORTACIONES PARA DRIVE ---
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
from PIL import Image
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w" 

# --- FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS ---
def editar_celda_google_sheets(sheet_url, fila_idx, columna_nombre, nuevo_valor):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)
        headers = worksheet.row_values(1)
        col_idx = headers.index(columna_nombre) + 1
        worksheet.update_cell(fila_idx + 2, col_idx, str(nuevo_valor))
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- FUNCIÓN PARA SUBIR A DRIVE CORREGIDA ---
def subir_a_drive(file_path, file_name):
    try:
        # Configurar correctamente los scopes
        scope = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        service = build('drive', 'v3', credentials=creds)
        
        # Verificar que la carpeta existe y tenemos acceso
        try:
            folder_check = service.files().get(fileId=FOLDER_ID, fields='id, name').execute()
            print(f"Carpeta encontrada: {folder_check.get('name')}")
        except Exception as e:
            st.error(f"Error al acceder a la carpeta: {e}")
            return None
        
        # Configurar metadata del archivo
        file_metadata = {
            'name': file_name,
            'parents': [FOLDER_ID]
        }
        
        # Crear el media upload
        media = MediaFileUpload(file_path, resumable=True, chunksize=1024*1024)
        
        # Subir el archivo
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Hacer el archivo público (opcional)
        try:
            service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except:
            pass  # Si no se puede hacer público, igual funciona con el link
        
        return file.get('webViewLink')
        
    except HttpError as e:
        error_details = str(e)
        if "403" in error_details:
            st.error("❌ Error de permisos: Asegúrate de haber compartido la carpeta con el correo de la cuenta de servicio")
            st.info("📧 Comparte la carpeta en Drive con: " + st.secrets["gcp"]["client_email"])
        else:
            st.error(f"Error al subir a Drive: {error_details}")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return None

# --- FUNCIÓN PARA VERIFICAR CONFIGURACIÓN DE DRIVE ---
def verificar_drive_config():
    try:
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        service = build('drive', 'v3', credentials=creds)
        
        # Intentar listar archivos en la carpeta
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        
        return True, "✅ Conexión a Drive OK"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00", "archivo_link": ""}]

# --- NUEVO: Estado para novedades vistas y clave de administración ---
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = {st.session_state.historial_novedades[0]["id"]}

if 'pass_novedades_valida' not in st.session_state:
    st.session_state.pass_novedades_valida = False

# --- INICIALIZAR ESTADOS DE SESIÓN PARA CLAVES Y CHECKBOXES ---
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False

# Estados exclusivos para checkboxes
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False

# Estado para controlar la expansión de novedades
if 'novedades_expandido' not in st.session_state:
    st.session_state.novedades_expandido = False

# --- CALLBACKS PARA CHECKBOXES EXCLUSIVOS ---
def toggle_faba():
    if st.session_state.faba_check:
        st.session_state.osecac_check = False
    else:
        st.session_state.osecac_check = True

def toggle_osecac():
    if st.session_state.osecac_check:
        st.session_state.faba_check = False
    else:
        st.session_state.faba_check = True

# --- FUNCIÓN PARA ABRIR NOVEDADES ---
def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS MODERNO DEFINITIVO ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] details[open] summary { border: 2px solid #ff4b4b !important; box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; color: #ffffff !important; }
.ficha-novedad { border-left: 6px solid #ff4b4b; }
.stLinkButton a { background-color: rgba(30, 41, 59, 0.8) !important; color: #ffffff !important; border: 1px solid rgba(56,189,248,0.5) !important; border-radius: 10px !important; }
.stLinkButton a:hover { background-color: #38bdf8 !important; color: #000000 !important; }
div[data-baseweb="input"] { background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
input { color: #000000 !important; font-weight: bold !important; }
.block-container { max-width: 1100px !important; padding-top: 2rem !important; }

/* ESTILOS PARA HEADER CON LOGO */
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 10px 0;
}
.logo-titulo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}
.logo-img {
    height: 70px;
    width: auto;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.titulo-principal {
    font-weight: 800;
    font-size: 2rem;
    color: #ffffff;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.botones-container {
    display: flex;
    gap: 12px;
    align-items: center;
}
.boton-novedad {
    background: linear-gradient(145deg, #ff4b4b, #ff0000);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 12px 25px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    animation: parpadeo 1.2s infinite;
    box-shadow: 0 0 20px rgba(255, 75, 75, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.3);
    transition: all 0.3s;
    letter-spacing: 1px;
}
.boton-novedad:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 75, 75, 1);
}
@keyframes parpadeo {
    0% { opacity: 1; background: #ff4b4b; }
    50% { opacity: 0.9; background: #ff0000; box-shadow: 0 0 30px rgba(255, 0, 0, 1); transform: scale(1.02); }
    100% { opacity: 1; background: #ff4b4b; }
}
.boton-lapiz-admin {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    color: white;
    border: 2px solid #38bdf8;
    border-radius: 30px;
    padding: 10px 20px;
    cursor: pointer;
    font-size: 1.3rem;
    font-weight: bold;
    transition: all 0.3s;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
}
.boton-lapiz-admin:hover {
    background: #38bdf8;
    color: black;
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(56, 189, 248, 0.8);
}

/* ESTILOS PARA NOVEDADES EXPANDIDAS */
div[data-testid="stExpander"][aria-expanded="true"] {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 20px;
    margin: 20px 0;
    border: 2px solid #ff4b4b;
    box-shadow: 0 0 30px rgba(255, 75, 75, 0.3);
}
div[data-testid="stExpander"] summary {
    font-size: 1.3rem !important;
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
}
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/edit",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/edit",
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/edit",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=1119565576",
}

df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])
df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])

# ================= HEADER CON LOGO =================
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<div class="logo-titulo-container">', unsafe_allow_html=True)

# Mostrar logo
try:
    if os.path.exists('logo.jpg'):
        logo = Image.open('logo.jpg')
        st.image(logo, width=70)
    else:
        st.markdown('<div style="width:70px; height:70px; background: linear-gradient(145deg, #1e293b, #0f172a); border-radius:12px; border:2px solid #38bdf8; display: flex; align-items: center; justify-content: center; font-size: 24px;">📋</div>', unsafe_allow_html=True)
except:
    st.markdown('<div style="width:70px; height:70px; background: linear-gradient(145deg, #1e293b, #0f172a); border-radius:12px; border:2px solid #38bdf8; display: flex; align-items: center; justify-content: center; font-size: 24px;">📋</div>', unsafe_allow_html=True)

# Título
st.markdown('<h1 class="titulo-principal">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Botones a la derecha
st.markdown('<div class="botones-container">', unsafe_allow_html=True)

# Verificar si hay novedades no vistas
ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
hay_novedades_nuevas = ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas

# Botón de novedad (solo si hay novedades nuevas)
if hay_novedades_nuevas:
    st.button("🔴 NOVEDAD NUEVA", key="btn_novedad_header", on_click=abrir_novedades)

# Lápiz de administración
popover_novedades = st.popover("✏️ ADMIN")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# ================= POPOVER DE ADMINISTRACIÓN DE NOVEDADES =================
with popover_novedades:
    st.markdown("### 🔐 Clave Administración")
    
    # Verificar configuración de Drive (solo para debug)
    drive_ok, drive_msg = verificar_drive_config()
    if not drive_ok:
        st.warning("⚠️ " + drive_msg)
        st.info("📧 Comparte la carpeta con: " + st.secrets["gcp"]["client_email"])
    
    if not st.session_state.pass_novedades_valida:
        with st.form("form_novedades_admin"):
            cl_admin = st.text_input("Ingrese Clave:", type="password")
            if st.form_submit_button("✅ OK"):
                if cl_admin == "*":
                    st.session_state.pass_novedades_valida = True
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta")
    else:
        st.success("✅ Acceso concedido")
        st.markdown("---")
        st.write("### 📝 Administrar Novedades")
        
        # Opciones de administración
        accion = st.radio("Seleccionar acción:", ["➕ Agregar nueva", "✏️ Editar existente", "🗑️ Eliminar"])
        
        if accion == "➕ Agregar nueva":
            with st.form("nueva_novedad_form"):
                m = st.text_area("📄 Nuevo comunicado:", placeholder="Escriba el mensaje de la novedad...")
                uploaded_file = st.file_uploader("📎 Adjuntar archivo (PDF, Imagen):", type=["pdf", "png", "jpg", "jpeg"])
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("📢 PUBLICAR")
                with col2:
                    cancel = st.form_submit_button("❌ CANCELAR")
                
                if submit:
                    if not m.strip():
                        st.error("❌ El mensaje no puede estar vacío")
                    else:
                        drive_link = ""
                        if uploaded_file is not None:
                            with st.spinner("Subiendo archivo a Drive..."):
                                # Guardar temporalmente
                                temp_path = f"temp_{uploaded_file.name}"
                                with open(temp_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                # Subir a Drive
                                drive_link = subir_a_drive(temp_path, uploaded_file.name)
                                
                                # Borrar temporal
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                            
                            if not drive_link:
                                st.warning("⚠️ No se pudo subir el archivo, pero la novedad se publicará sin él")
                        
                        nueva_novedad = {
                            "id": str(time.time()), 
                            "mensaje": m, 
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "archivo_link": drive_link
                        }
                        st.session_state.historial_novedades.insert(0, nueva_novedad)
                        st.session_state.novedades_vistas = set()  # Resetear vistas
                        st.success("✅ ¡Publicado exitosamente!")
                        time.sleep(1)
                        st.rerun()
        
        elif accion == "✏️ Editar existente":
            if st.session_state.historial_novedades:
                opciones = [f"{n['fecha']} - {n['mensaje'][:50]}..." for n in st.session_state.historial_novedades]
                idx_editar = st.selectbox("Seleccionar novedad a editar:", range(len(opciones)), format_func=lambda x: opciones[x])
                
                novedad = st.session_state.historial_novedades[idx_editar]
                with st.form("editar_novedad_form"):
                    nuevo_mensaje = st.text_area("Editar mensaje:", value=novedad['mensaje'])
                    if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                        st.session_state.historial_novedades[idx_editar]['mensaje'] = nuevo_mensaje
                        st.success("✅ ¡Actualizado!")
                        time.sleep(1)
                        st.rerun()
        
        elif accion == "🗑️ Eliminar":
            if st.session_state.historial_novedades:
                opciones = [f"{n['fecha']} - {n['mensaje'][:50]}..." for n in st.session_state.historial_novedades]
                idx_eliminar = st.selectbox("Seleccionar novedad a eliminar:", range(len(opciones)), format_func=lambda x: opciones[x])
                
                if st.button("🗑️ CONFIRMAR ELIMINACIÓN", type="primary"):
                    st.session_state.historial_novedades.pop(idx_eliminar)
                    st.success("✅ ¡Eliminado!")
                    time.sleep(1)
                    st.rerun()

# ================== APLICACIÓN ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    
    with c1:
        pop_f = st.popover("✏️")
        pop_f.markdown("### 🔑 Clave FABA")
        if not st.session_state.pass_f_valida:
            with pop_f.form("form_faba"):
                cl_f_in = st.text_input("Ingrese Clave:", type="password")
                if st.form_submit_button("✅ OK"):
                    if cl_f_in == "*":
                        st.session_state.pass_f_valida = True
                        st.rerun()
                    else: st.error("❌ Clave incorrecta")
        else: pop_f.success("✅ FABA Habilitado")

    with c2:
        st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
        
    with c3:
        pop_o = st.popover("✏️")
        pop_o.markdown("### 🔑 Clave OSECAC")
        if not st.session_state.pass_o_valida:
            with pop_o.form("form_osecac"):
                cl_o_in = st.text_input("Ingrese Clave:", type="password")
                if st.form_submit_button("✅ OK"):
                    if cl_o_in == "*":
                        st.session_state.pass_o_valida = True
                        st.rerun()
                    else: st.error("❌ Clave incorrecta")
        else: pop_o.success("✅ OSECAC Habilitado")
            
    with c4:
        st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)

    # Lógica de selección
    sel_faba = st.session_state.faba_check
    sel_osecac = st.session_state.osecac_check
    
    opcion = "OSECAC" if sel_osecac else "FABA"
    
    # Determinar si la edición está habilitada
    edicion_habilitada = False
    if sel_osecac and st.session_state.pass_o_valida:
        edicion_habilitada = True
        df_u = df_osecac_busq
        url_u = URLs["osecac"]
    elif sel_faba and st.session_state.pass_f_valida:
        edicion_habilitada = True
        df_u = df_faba
        url_u = URLs["faba"]
    else:
        df_u = df_osecac_busq if sel_osecac else df_faba
        url_u = URLs["osecac"] if sel_osecac else URLs["faba"]

    # BÚSQUEDA
    term = st.text_input(f"🔍 Escriba término de búsqueda en {opcion}...", key="busqueda_input")
    btn_buscar = st.button("Buscar")
    
    if btn_buscar:
        if term:
            mask = df_u.apply(lambda row: all(p in str(row).lower() for p in term.lower().split()), axis=1)
            results = df_u[mask]
            
            if results.empty:
                st.warning("No se encontraron resultados.")
            else:
                for i, row in results.iterrows():
                    st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
                    
                    # --- SECCIÓN DE EDICIÓN ---
                    if edicion_habilitada: 
                        with st.expander(f"📝 Editar fila {i}"):
                            c_edit = st.selectbox("Columna:", row.index, key=f"sel_{i}")
                            v_edit = st.text_input("Nuevo valor:", value=row[c_edit], key=f"val_{i}")
                            if st.button("Guardar Cambios", key=f"btn_{i}"):
                                if editar_celda_google_sheets(url_u, i, c_edit, v_edit):
                                    st.success("✅ ¡Sincronizado!"); st.cache_data.clear(); st.rerun()
        else:
            st.info("Escriba algo en el buscador.")

    # --- ADVERTENCIA ---
    if not edicion_habilitada:
        st.info("💡 Para editar, ingrese la clave correspondiente en el lápiz ✏️")

# 2. PEDIDOS
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 3. PÁGINAS ÚTILES", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with cols[1]:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
        st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# 4. GESTIONES / DATOS
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha ficha-practica">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        re = df_especialistas[df_especialistas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in re.iterrows():
            st.markdown(f'<div class="ficha ficha-especialista">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 6. AGENDAS / MAILS
with st.expander("📞 6. AGENDAS / MAILS", expanded=False):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# 7. NOVEDADES (EXPANDIDO EN GRANDE)
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    st.markdown("## 📢 Últimos Comunicados")
    st.markdown("---")
    
    # Mostrar novedades
    for n in st.session_state.historial_novedades:
        # Marcar como vista
        if n["id"] not in st.session_state.novedades_vistas:
            st.session_state.novedades_vistas.add(n["id"])
        
        # Mostrar la novedad en grande
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e293b, #0f172a); 
                    border-left: 8px solid #ff4b4b;
                    border-radius: 16px;
                    padding: 25px;
                    margin: 20px 0;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px;">📅 {n["fecha"]}</div>
            <div style="color: white; font-size: 1.2rem; line-height: 1.6; white-space: pre-wrap;">{n["mensaje"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if n.get("archivo_link"):
            st.markdown(f'<a href="{n["archivo_link"]}" target="_blank" style="display: inline-block; background: #38bdf8; color: black; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold; margin-top: 10px;">📂 Ver archivo adjunto</a>', unsafe_allow_html=True)
    
    # Botón para cerrar
    if st.button("❌ Cerrar Novedades"):
        st.session_state.novedades_expandido = False
        st.rerun()
