import streamlit as st
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from PIL import Image
import io
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIÓN PARA SUBIR A DRIVE (OAuth) ---
def subir_a_drive(file_path, file_name):
    try:
        REFRESH_TOKEN = "1//04wm475WZT5NrCgYIARAAGAQSNwF-L9IrV1Wnk6hUFxlYb0yoyKnATPFKvPc_2QCZ4bkqmuWnBVreI6v5DFKr-u8q6lCJfZFLwOg"
        ACCESS_TOKEN = "ya29.a0ATkoCc5F9aJgCfAbzdQvZYGc_wCBLgiWOyTwOjWDj1vsMAPc8stwgbHXOhxPdcghSqKXJx8mtmp_WA6kZAO_2aENwpQE-3CzcHvTiYkUTKdDfxxE5BddS7QrB0SESbasc9vshiLDAdq6wErDbgIAiU835mB7hGX-LDCSVKD4L68cpFhHco6eeRdHVRnC2kJ4D7fkuS8aCgYKARgSARQSFQHGX2MiLUw0IpD5eh_zyfX7QeL-og0206"

        creds = OAuthCredentials(
            token=ACCESS_TOKEN,
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id="407408718192.apps.googleusercontent.com",
            client_secret="",
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

        try:
            service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        except:
            pass
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error al subir archivo: {str(e)}")
        return None

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00", "archivo_links": []}]
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = {st.session_state.historial_novedades[0]["id"]}
if 'pass_novedades_valida' not in st.session_state:
    st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state:
    st.session_state.novedades_expandido = False

def toggle_faba():
    if st.session_state.faba_check: st.session_state.osecac_check = False
    else: st.session_state.osecac_check = True

def toggle_osecac():
    if st.session_state.osecac_check: st.session_state.faba_check = False
    else: st.session_state.faba_check = True

def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] details[open] summary { border: 2px solid #ff4b4b !important; box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; color: #ffffff !important; }
.stLinkButton a { background-color: rgba(30, 41, 59, 0.8) !important; color: #ffffff !important; border: 1px solid rgba(56,189,248,0.5) !important; border-radius: 10px !important; }
div[data-baseweb="input"] { background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; }
input { color: #000000 !important; font-weight: bold !important; }
.block-container { max-width: 1100px !important; padding-top: 1rem !important; }
.stButton > button {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-size: 1rem !important;
    font-weight: bold !important;
}
.stButton > button:hover { background: #38bdf8 !important; color: black !important; }
.stButton > button:has(span:contains("🔴")) {
    background: linear-gradient(145deg, #ff4b4b, #ff0000) !important;
    border: 2px solid #ff4b4b !important;
    animation: parpadeo 1.2s infinite;
}
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
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

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:2.8rem; color:#ffffff; margin-bottom:1.2rem;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([1,2,1])
with col_h2:
    try:
        if os.path.exists('logo original.jpg'): st.image('logo original.jpg', width=160)
    except: pass
    
    st.markdown('<div style="display:flex; gap:16px; justify-content:center; margin:1rem 0;">', unsafe_allow_html=True)
    ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
    if ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas:
        st.button("🔴 NOVEDAD", key="btn_novedad_header", on_click=abrir_novedades)
    popover_novedades = st.popover("✏️ Cargar Novedades")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================= POPOVER CARGAR NOVEDADES =================
with popover_novedades:
    st.markdown("### 🔐 Clave Administración")
    if not st.session_state.pass_novedades_valida:
        with st.form("form_novedades_admin"):
            cl_admin = st.text_input("Ingrese Clave:", type="password")
            if st.form_submit_button("✅ OK"):
                if cl_admin == "*":
                    st.session_state.pass_novedades_valida = True
                    st.rerun()
                else: st.error("❌ Clave incorrecta")
    else:
        st.success("✅ Acceso concedido")
        accion = st.radio("Acción:", ["➕ Agregar nueva", "✏️ Editar existente", "🗑️ Eliminar"])
        if accion == "➕ Agregar nueva":
            with st.form("nueva_novedad_form"):
                m = st.text_area("📄 Nuevo comunicado:")
                uploaded_files = st.file_uploader("📎 Adjuntar:", type=["pdf", "png", "jpg"], accept_multiple_files=True)
                if st.form_submit_button("📢 PUBLICAR"):
                    if m.strip():
                        links = []
                        for f in (uploaded_files or []):
                            temp_path = f"temp_{f.name}"
                            with open(temp_path, "wb") as file_temp: file_temp.write(f.getbuffer())
                            link = subir_a_drive(temp_path, f.name)
                            if os.path.exists(temp_path): os.remove(temp_path)
                            if link: links.append(link)
                        st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "archivo_links": links})
                        st.session_state.novedades_vistas = set()
                        st.rerun()

# ================== SECCIONES ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    with c1:
        if st.popover("🔑 FABA").form("f").text_input("Clave:", type="password") == "*": st.session_state.pass_f_valida = True
    with c2: st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
    with c3:
        if st.popover("🔑 OSECAC").form("o").text_input("Clave:", type="password") == "*": st.session_state.pass_o_valida = True
    with c4: st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)
    
    op = "OSECAC" if st.session_state.osecac_check else "FABA"
    df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
    term = st.text_input(f"🔍 Búsqueda en {op}...")
    if st.button("Buscar"):
        if term:
            results = df_u[df_u.apply(lambda row: all(p in str(row).lower() for p in term.lower().split()), axis=1)]
            for i, row in results.iterrows():
                st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS (CORREGIDO CON REDIRECCIÓN DIRECTA)
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")
    
    st.markdown("---")
    with st.popover("🔑 ADMINISTRADORES"):
        st.markdown("### 🔐 Acceso Directo")
        with st.form("form_admin_directo", clear_on_submit=True):
            cl_ingresada = st.text_input("Ingrese Clave:", type="password")
            if st.form_submit_button("✅ ACCEDER"):
                if cl_ingresada == "2025":
                    # REDIRECCIÓN ROBUSTA SIN ICONOS DE ERROR
                    url_destino = "https://sites.google.com/view/osecacmdpadm?usp=sharing"
                    components.html(f"""
                        <script>
                            window.top.location.href = '{url_destino}';
                        </script>
                    """, height=0)
                    st.success("Redirigiendo...")
                else:
                    st.error("❌ Clave incorrecta")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 3. PÁGINAS ÚTILES", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
    with c2:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")

# 4. GESTIONES / DATOS
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bus_t = st.text_input("Buscá trámites...")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha">📑 PRÁCTICA: {row.get("PRÁCTICA", i)}</div>', unsafe_allow_html=True)

# 6. AGENDAS / MAILS
with st.expander("📞 6. AGENDAS / MAILS", expanded=False):
    bus_a = st.text_input("Buscá contactos...")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    for n in st.session_state.historial_novedades:
        if n["id"] not in st.session_state.novedades_vistas: st.session_state.novedades_vistas.add(n["id"])
        st.markdown(f'<div style="border-left:8px solid #ff4b4b; padding:20px; background:#1e293b; border-radius:12px; margin-bottom:15px;">'
                    f'<small>📅 {n["fecha"]}</small><br><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
        for link in n.get("archivo_links", []):
            st.markdown(f'<a href="{link}" target="_blank" style="color:#38bdf8;">📂 Ver adjunto</a>', unsafe_allow_html=True)
    if st.button("❌ Cerrar"):
        st.session_state.novedades_expandido = False
        st.rerun()
