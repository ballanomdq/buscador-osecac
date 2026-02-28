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
import os

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
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
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

# --- FUNCIÓN PARA SUBIR A DRIVE ---
def subir_a_drive(file_path, file_name):
    try:
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': file_name,
            'parents': [FOLDER_ID]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error al subir a Drive: {e}")
        return None

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00", "archivo_link": ""}]

# --- INICIALIZAR ESTADOS DE SESIÓN PARA CLAVES Y CHECKBOXES ---
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'pass_novedades_valida' not in st.session_state: st.session_state.pass_novedades_valida = False

# Estados exclusivos para checkboxes
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False

# Estado para novedades vistas
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = set()

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
.header-master { text-align: center; margin-bottom: 20px; }
.titulo-mini { font-weight: 800; font-size: 1.6rem; color: #ffffff !important; }

/* Estilos para el header con notificaciones */
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.header-left {
    flex: 1;
}
.header-right {
    display: flex;
    gap: 10px;
    align-items: center;
}
.notificacion-btn {
    background-color: #ff4b4b;
    color: white;
    border: none;
    border-radius: 50px;
    padding: 8px 20px;
    font-weight: bold;
    cursor: pointer;
    animation: parpadeo 1.5s infinite;
    box-shadow: 0 0 10px rgba(255, 75, 75, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
}
@keyframes parpadeo {
    0% { opacity: 1; background-color: #ff4b4b; }
    50% { opacity: 0.7; background-color: #ff0000; box-shadow: 0 0 20px rgba(255, 0, 0, 0.8); }
    100% { opacity: 1; background-color: #ff4b4b; }
}
.lapiz-btn {
    background-color: rgba(30, 41, 59, 0.8);
    color: white;
    border: 2px solid #38bdf8;
    border-radius: 10px;
    padding: 5px 15px;
    cursor: pointer;
    font-size: 1.2rem;
    transition: all 0.3s;
}
.lapiz-btn:hover {
    background-color: #38bdf8;
    color: black;
}
.popover-clave {
    background-color: #1e293b;
    border: 2px solid #38bdf8;
    border-radius: 10px;
    padding: 15px;
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

# ================= HEADER CON NOVEDADES Y LÁPIZ =================
# Verificar si hay novedades no vistas
ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
hay_novedad_no_vista = ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas

# Header personalizado con botón de novedades y lápiz
st.markdown("""
<div class="header-container">
    <div class="header-left">
        <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
    </div>
    <div class="header-right">
""", unsafe_allow_html=True)

# Columna para el botón de novedades (solo si hay novedad no vista)
if hay_novedad_no_vista:
    if st.button("🔴 NOVEDAD NUEVA", key="btn_novedad_header", help="¡Hay una nueva novedad disponible!"):
        st.session_state.mostrar_novedades = True
else:
    st.markdown('<div style="width: 0;"></div>', unsafe_allow_html=True)

# Columna para el lápiz de administración
col_lapiz = st.columns([0.1])[0]
with col_lapiz:
    pop_admin = st.popover("✏️")
    with pop_admin:
        st.markdown('<div class="popover-clave">', unsafe_allow_html=True)
        st.markdown("### Clave Administrador")
        if not st.session_state.pass_novedades_valida:
            with st.form("form_novedades"):
                cl_admin_in = st.text_input("Ingrese Clave:", type="password")
                if st.form_submit_button("OK"):
                    if cl_admin_in == "*":
                        st.session_state.pass_novedades_valida = True
                        st.rerun()
                    else:
                        st.error("Clave incorrecta")
        else:
            st.success("✅ Administrador Habilitado")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
st.markdown("---")

# ================== APLICACIÓN ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    
    with c1:
        pop_f = st.popover("✏️")
        pop_f.markdown("### Clave FABA")
        if not st.session_state.pass_f_valida:
            with pop_f.form("form_faba"):
                cl_f_in = st.text_input("Ingrese Clave:", type="password")
                if st.form_submit_button("OK"):
                    if cl_f_in == "*":
                        st.session_state.pass_f_valida = True
                        st.rerun()
                    else: st.error("Clave incorrecta")
        else: pop_f.success("✅ FABA Habilitado")

    with c2:
        st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
        
    with c3:
        pop_o = st.popover("✏️")
        pop_o.markdown("### Clave OSECAC")
        if not st.session_state.pass_o_valida:
            with pop_o.form("form_osecac"):
                cl_o_in = st.text_input("Ingrese Clave:", type="password")
                if st.form_submit_button("OK"):
                    if cl_o_in == "*":
                        st.session_state.pass_o_valida = True
                        st.rerun()
                    else: st.error("Clave incorrecta")
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
                                    st.success("¡Sincronizado!"); st.cache_data.clear(); st.rerun()
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

# 7. NOVEDADES
with st.expander("📢 7. NOVEDADES", expanded=True):
    st.write("### Últimos comunicados")
    
    # Mostrar novedades
    for n in st.session_state.historial_novedades:
        # Marcar como vista si el usuario ve esta novedad
        if n["id"] not in st.session_state.novedades_vistas:
            st.session_state.novedades_vistas.add(n["id"])
            
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
        if n.get("archivo_link"):
            st.markdown(f'<a href="{n["archivo_link"]}" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: none;">📂 Ver archivo en Drive</a>', unsafe_allow_html=True)
    
    # --- PANEL ADMINISTRADOR (solo visible si la clave es válida) ---
    if st.session_state.pass_novedades_valida:
        st.markdown("---")
        st.write("### ✍️ Publicar Nueva Novedad")
        with st.form("n_form", clear_on_submit=True):
            m = st.text_area("Nuevo comunicado:")
            uploaded_file = st.file_uploader("Adjuntar archivo (PDF, Imagen):", type=["pdf", "png", "jpg", "jpeg"])
            
            if st.form_submit_button("PUBLICAR"):
                drive_link = ""
                if uploaded_file is not None:
                    # Guardar temporalmente
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Subir a Drive
                    drive_link = subir_a_drive(temp_path, uploaded_file.name)
                    
                    # Borrar temporal
                    os.remove(temp_path)
                
                nueva_novedad = {
                    "id": str(time.time()), 
                    "mensaje": m, 
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "archivo_link": drive_link
                }
                st.session_state.historial_novedades.insert(0, nueva_novedad)
                # Resetear el estado de clave para que pida de nuevo la próxima vez (opcional)
                # st.session_state.pass_novedades_valida = False
                st.success("¡Publicado exitosamente!")
                st.rerun()
