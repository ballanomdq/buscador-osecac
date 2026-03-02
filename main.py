import streamlit as st
import pandas as pd
import time
from datetime import datetime
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIÓN PARA SUBIR A DRIVE (Corregida para carga múltiple) ---
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
        st.error(f"Error al subir: {str(e)}")
        return None

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00", "archivo_links": []}]
if 'novedades_vistas' not in st.session_state:
    st.session_state.novedades_vistas = {st.session_state.historial_novedades[0]["id"]}
if 'pass_novedades_valida' not in st.session_state: st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state: st.session_state.novedades_expandido = False

def toggle_faba():
    if st.session_state.faba_check: st.session_state.osecac_check = False
    else: st.session_state.osecac_check = True

def toggle_osecac():
    if st.session_state.osecac_check: st.session_state.faba_check = False
    else: st.session_state.faba_check = True

# ================== CSS ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; font-weight: bold !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; margin-bottom: 12px; }
div[data-baseweb="input"] { background-color: #ffffff !important; border-radius: 10px !important; }
input { color: #000000 !important; }
.stButton > button { background: #1e293b !important; color: white !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; font-weight: bold !important; }
.stButton > button:has(span:contains("🔴")) { background: linear-gradient(145deg, #ff4b4b, #ff0000) !important; animation: parpadeo 1.2s infinite; }
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
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit?gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit?gid=1119565576",
}

df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])
df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])

# ================= HEADER =================
st.markdown('<h1 style="text-align:center; font-weight:800; font-size:2.8rem; color:#ffffff;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
col_h1, col_h2, col_h3 = st.columns([1,2,1])
with col_h2:
    if os.path.exists('logo original.jpg'): st.image('logo original.jpg', width=160)
    st.markdown('<div style="display:flex; gap:16px; justify-content:center; margin-bottom:20px;">', unsafe_allow_html=True)
    ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
    if ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas:
        if st.button("🔴 NOVEDAD", key="btn_novedad_header"): st.session_state.novedades_expandido = True
    popover_novedades = st.popover("✏️ Cargar Novedades")
    st.markdown('</div>', unsafe_allow_html=True)

with popover_novedades:
    if not st.session_state.pass_novedades_valida:
        with st.form("form_novedades_admin"):
            cl_admin = st.text_input("Clave Admin:", type="password")
            if st.form_submit_button("✅ OK"):
                if cl_admin == "*": st.session_state.pass_novedades_valida = True; st.rerun()
                else: st.error("Clave incorrecta")
    else:
        accion = st.radio("Acción:", ["➕ Agregar nueva", "✏️ Editar", "🗑️ Eliminar"])
        if accion == "➕ Agregar nueva":
            with st.form("nueva_novedad_form", clear_on_submit=True):
                m = st.text_area("📄 Mensaje:")
                files = st.file_uploader("📎 Adjuntar:", accept_multiple_files=True)
                if st.form_submit_button("📢 PUBLICAR"):
                    links = []
                    for f in (files or []):
                        temp = f"temp_{int(time.time())}_{f.name}"
                        with open(temp, "wb") as t: t.write(f.getbuffer())
                        link = subir_a_drive(temp, f.name)
                        if os.path.exists(temp): os.remove(temp)
                        if link: links.append(link)
                    st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "archivo_links": links})
                    st.session_state.novedades_vistas = set(); st.success("✅ Publicado"); st.rerun()

# ================== SECCIONES ==================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    c1, c2, c3, c4 = st.columns([0.5, 2, 0.5, 2])
    with c1: 
        if st.popover("🔑").form("f").text_input("FABA Pass:", type="password") == "*": 
            st.session_state.pass_f_valida = True; st.rerun()
    with c2: st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
    with c3: 
        if st.popover("🔑").form("o").text_input("OSECAC Pass:", type="password") == "*": 
            st.session_state.pass_o_valida = True; st.rerun()
    with c4: st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)
    
    op = "OSECAC" if st.session_state.osecac_check else "FABA"
    df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
    term = st.text_input(f"🔍 Búsqueda en {op}...")
    if st.button("Buscar"):
        if term:
            res = df_u[df_u.apply(lambda r: all(p in str(r).lower() for p in term.lower().split()), axis=1)]
            for _, row in res.iterrows():
                st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 2. PEDIDOS", expanded=False):
    st.link_button("🍼 LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    with st.popover("🔑 ADMIN"):
        if st.text_input("Clave:", type="password") == "2025":
            components.html("<script>window.top.location.href='https://sites.google.com/view/osecacmdpadm?usp=sharing'</script>", height=0)

# 3. PÁGINAS ÚTILES
with st.expander("🌐 3. PÁGINAS ÚTILES", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🆔 CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with c2:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC", "https://www.osecac.org.ar/")

# 4. GESTIONES
with st.expander("📂 4. GESTIONES / DATOS", expanded=False):
    bt = st.text_input("Buscá trámites...")
    if bt and not df_tramites.empty:
        r = df_tramites[df_tramites['TRAMITE'].str.contains(bt, case=False, na=False)]
        for _, row in r.iterrows(): st.markdown(f'<div class="ficha"><b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS (La sección que faltaba)
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS", expanded=False):
    bp = st.text_input("Buscá práctica o médico:")
    if bp:
        # Buscar en Prácticas
        rp = df_practicas[df_practicas.astype(str).apply(lambda x: x.str.contains(bp, case=False).any(), axis=1)]
        for _, row in rp.iterrows(): st.markdown(f'<div class="ficha">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        # Buscar en Especialistas
        re = df_especialistas[df_especialistas.astype(str).apply(lambda x: x.str.contains(bp, case=False).any(), axis=1)]
        for _, row in re.iterrows(): st.markdown(f'<div class="ficha">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 6. AGENDAS
with st.expander("📞 6. AGENDAS / MAILS", expanded=False):
    ba = st.text_input("Buscá contactos...")
    if ba and not df_agendas.empty:
        r = df_agendas[df_agendas.astype(str).apply(lambda x: x.str.contains(ba, case=False).any(), axis=1)]
        for _, row in r.iterrows(): st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items()])}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    for n in st.session_state.historial_novedades:
        if n["id"] not in st.session_state.novedades_vistas: st.session_state.novedades_vistas.add(n["id"])
        st.markdown(f'<div style="border-left:5px solid #ff4b4b; padding:15px; background:#1e293b; border-radius:10px; margin-bottom:10px;">'
                    f'<small>{n["fecha"]}</small><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
        for link in n.get("archivo_links", []): st.markdown(f'<a href="{link}" target="_blank" style="color:#38bdf8;">📂 Ver adjunto</a>', unsafe_allow_html=True)
    if st.button("❌ Cerrar"): st.session_state.novedades_expandido = False; st.rerun()
