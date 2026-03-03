import streamlit as st
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN GOOGLE SHEETS & DRIVE ---
# Usamos el ID de tu Excel para gspread (Escritura)
ID_SHEET = "1vQYQEeH8WWh8EK3ee3HLnSmW0VHPu9LTfXsCRdGuVPoIAa-qzdSZxjwfjq2UgitFU0MG2mRdX8wCzEb"
# Usamos el link CSV para lectura rápida (Lectura)
URL_NOVEDADES_CSV = f"https://docs.google.com/spreadsheets/d/e/2PACX-{ID_SHEET}/pub?gid=0&single=true&output=csv"
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIONES DE CONEXIÓN ---
def obtener_creds():
    return service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    )

def subir_a_drive(file_path, file_name):
    try:
        creds = obtener_creds()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error Drive: {e}")
        return None

def guardar_novedad_permanente(fecha, mensaje, link):
    try:
        creds = obtener_creds()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(ID_SHEET).sheet1
        sheet.append_row([fecha, mensaje, link])
        return True
    except Exception as e:
        st.error(f"Error Sheets: {e}")
        return False

# --- INICIALIZACIÓN DE SESIÓN (ESTRUCTURA ORIGINAL) ---
if 'novedades_vistas' not in st.session_state: st.session_state.novedades_vistas = set()
if 'pass_novedades_valida' not in st.session_state: st.session_state.pass_novedades_valida = False
if 'pass_f_valida' not in st.session_state: st.session_state.pass_f_valida = False
if 'pass_o_valida' not in st.session_state: st.session_state.pass_o_valida = False
if 'faba_check' not in st.session_state: st.session_state.faba_check = True
if 'osecac_check' not in st.session_state: st.session_state.osecac_check = False
if 'novedades_expandido' not in st.session_state: st.session_state.novedades_expandido = False

def toggle_faba():
    st.session_state.osecac_check = not st.session_state.faba_check
def toggle_osecac():
    st.session_state.faba_check = not st.session_state.osecac_check
def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== TU CSS ORIGINAL COMPLETO ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
div[data-testid="stExpander"] details summary { background-color: rgba(30, 41, 59, 0.9) !important; color: #ffffff !important; border-radius: 14px !important; border: 2px solid rgba(56, 189, 248, 0.4) !important; padding: 14px 18px !important; font-weight: 600 !important; }
.ficha { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 12px; }
.stButton > button { background: linear-gradient(145deg, #1e293b, #0f172a) !important; color: white !important; border: 2px solid #38bdf8 !important; border-radius: 10px !important; font-weight: bold !important; }
.stButton > button:has(span:contains("🔴")) { background: linear-gradient(145deg, #ff4b4b, #ff0000) !important; animation: parpadeo 1.2s infinite; }
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=60)
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
df_novedades = cargar_datos(URL_NOVEDADES_CSV) # Lectura desde tu Excel nuevo

# ================= TU HEADER ORIGINAL =================
st.markdown('<h1 style="text-align:center; font-size:2.8rem; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
if os.path.exists('logo original.jpg'):
    st.image('logo original.jpg', width=160)

c_h1, c_h2 = st.columns(2)
with c_h1:
    if not df_novedades.empty:
        st.button("🔴 NOVEDAD", on_click=abrir_novedades)
with c_h2:
    popover_novedades = st.popover("✏️ Cargar Novedades")

st.markdown("---")

# ================= POPOVER ADMINISTRACIÓN (CORREGIDO) =================
with popover_novedades:
    if not st.session_state.pass_novedades_valida:
        with st.form("auth"):
            cl = st.text_input("Ingrese Clave:", type="password")
            if st.form_submit_button("✅ OK"):
                if cl == "*": 
                    st.session_state.pass_novedades_valida = True
                    st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        st.success("✅ Modo Editor Activo")
        with st.form("form_nueva_novedad"):
            msg_nov = st.text_area("📄 Mensaje de la novedad:")
            file_nov = st.file_uploader("📎 Adjuntar PDF o Imagen:", type=["pdf", "png", "jpg", "jpeg"])
            if st.form_submit_button("📢 PUBLICAR AHORA"):
                link_drive = ""
                if file_nov:
                    with open("temp_file", "wb") as f: f.write(file_nov.getbuffer())
                    link_drive = subir_a_drive("temp_file", file_nov.name)
                
                fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                if guardar_novedad_permanente(fecha_str, msg_nov, link_drive):
                    st.success("¡Publicado en Google Sheets!")
                    time.sleep(1)
                    st.rerun()

# ================= EXPANDERS 1 AL 6 (TU LÓGICA ORIGINAL) =================

with st.expander("📂 1. NOMENCLADORES"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📈 NOMENCLADOR EXEL OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    st.link_button("📈 NOMENCLADOR EXEL FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns([0.4, 1, 0.4, 1])
    with c2: st.checkbox("FABA", key="faba_check", on_change=toggle_faba)
    with c4: st.checkbox("OSECAC", key="osecac_check", on_change=toggle_osecac)
    term = st.text_input("🔍 Buscar término...")
    if st.button("Buscar") and term:
        df_u = df_osecac_busq if st.session_state.osecac_check else df_faba
        mask = df_u.apply(lambda row: term.lower() in str(row).lower(), axis=1)
        res = df_u[mask]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{k}:</b> {v}" for k,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

with st.expander("🌐 3. PÁGINAS ÚTILES"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")

with st.expander("📂 4. GESTIONES / DATOS"):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items()])}</div>', unsafe_allow_html=True)
        re = df_especialistas[df_especialistas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False).any(), axis=1)]
        for i, row in re.iterrows():
            st.markdown(f'<div class="ficha">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items()])}</div>', unsafe_allow_html=True)

with st.expander("📞 6. AGENDAS / MAILS"):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: bus_a.lower() in r.str.lower(), axis=1).any(axis=1)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{k}:</b> {v}" for k,v in row.items()])}</div>', unsafe_allow_html=True)

# ================= 7. NOVEDADES (TU LÓGICA + EXCEL) =================
with st.expander("📢 7. NOVEDADES", expanded=st.session_state.novedades_expandido):
    st.markdown("## 📢 Últimos Comunicados")
    st.markdown("---")
    if not df_novedades.empty:
        # Mostramos las novedades que vienen del Google Sheet
        for i, row in df_novedades.iloc[::-1].iterrows():
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-left: 8px solid #ff4b4b; border-radius: 16px; padding: 25px; margin: 20px 0;">
                <div style="color: #94a3b8; font-size: 0.9rem;">📅 {row.get('Fecha', '')}</div>
                <div style="color: white; font-size: 1.2rem; line-height: 1.6; white-space: pre-wrap;">{row.get('Mensaje', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if pd.notna(row.get('Archivo')) and str(row['Archivo']).startswith('http'):
                st.markdown(f'<a href="{row["Archivo"]}" target="_blank" style="display: inline-block; background: #38bdf8; color: black; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold;">📂 Ver archivo adjunto</a>', unsafe_allow_html=True)
    
    if st.button("❌ Cerrar Novedades"):
        st.session_state.novedades_expandido = False
        st.rerun()
