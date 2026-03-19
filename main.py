import streamlit as st
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2 import service_account
import os
import base64
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DRIVE ---
FOLDER_ID = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"

# --- FUNCIÓN SUBIR A DRIVE ---
def subir_a_drive(file_path, file_name):
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
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
        st.error(f"Error al subir a Drive: {str(e)}")
        return None

# --- PLACEHOLDER PARA EDICIÓN (para que no rompa) ---
def editar_celda_google_sheets(url, row_index, col_name, new_value):
    st.warning("Edición de Google Sheets aún no implementada. Implementar con gspread si es necesario.")
    return False

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
if 'pass_pc_valida' not in st.session_state:
    st.session_state.pass_pc_valida = False

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

def abrir_novedades():
    st.session_state.novedades_expandido = True

# ================== CSS MEJORADO ==================
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
    .stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
    .stMarkdown p, label { color: #ffffff !important; }
    div[data-testid="stExpander"] details summary { 
        background-color: rgba(30, 41, 59, 0.9) !important; 
        color: #ffffff !important; 
        border-radius: 14px !important; 
        border: 2px solid rgba(56, 189, 248, 0.4) !important; 
        padding: 14px 18px !important; 
        font-weight: 600 !important; 
    }
    div[data-testid="stExpander"] details[open] summary { 
        border: 2px solid #ff4b4b !important; 
        box-shadow: 0 0 12px rgba(255, 75, 75, 0.6) !important; 
    }
    .ficha { 
        background: rgba(30, 41, 59, 0.6); 
        backdrop-filter: blur(6px); 
        border: 1px solid rgba(255,255,255,0.08); 
        border-radius: 16px; 
        padding: 20px; 
        margin-bottom: 12px; 
        color: #ffffff !important; 
    }
    .ficha-novedad { border-left: 6px solid #ff4b4b; }
    h1 { 
        text-align: center !important; 
        width: 100% !important; 
        margin: 0.5rem auto 1.2rem auto !important; 
        font-weight:800 !important; 
        font-size:2.8rem !important; 
        color:#ffffff !important; 
        text-shadow:2px 2px 6px rgba(0,0,0,0.5) !important; 
    }
    .block-container { max-width: 1100px !important; padding-top: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    hr { border: 1px solid #38bdf8; opacity: 0.4; margin: 1.5rem 0; }
    /* Botón Buscar más visible */
    button[kind="primary"] { background: #38bdf8 !important; color: black !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: 
        return pd.DataFrame()

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

# ================= HEADER CENTRADO MEJORADO =================
st.markdown("""
<div style="
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 0;
    text-align: center;
">
""", unsafe_allow_html=True)

st.markdown('<h1>OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)

# Logo centrado con base64
def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if os.path.exists('logo original.jpg'):
    b64_img = image_to_base64('logo original.jpg')
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0 1.8rem 0;">
            <img src="data:image/jpeg;base64,{b64_img}"
                 style="width: 160px; max-width: 100%; height: auto; display: block;"
                 alt="Logo OSECAC">
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 1rem 0 1.8rem 0;">
            <div style="width:160px; height:70px; background: rgba(30,41,59,0.5); border-radius:16px; border:2px solid #38bdf8;"></div>
        </div>
    """, unsafe_allow_html=True)

# Botón NOVEDAD
ultima_novedad_id = st.session_state.historial_novedades[0]["id"] if st.session_state.historial_novedades else None
hay_novedades_nuevas = ultima_novedad_id and ultima_novedad_id not in st.session_state.novedades_vistas
if hay_novedades_nuevas:
    st.button("🔴 NOVEDAD", key="btn_novedad_header", on_click=abrir_novedades)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ================= EXPANDERS (el resto igual, solo agrego primary al buscar) =================

# 1. NOMENCLADORES
with st.expander("📂 1. NOMENCLADORES", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📈 NOMENCLADOR EXEL OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    st.link_button("📈 NOMENCLADOR EXEL FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns([0.4, 1, 0.4, 1])
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
   
    sel_faba = st.session_state.faba_check
    sel_osecac = st.session_state.osecac_check
    opcion = "OSECAC" if sel_osecac else "FABA"
   
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
   
    term = st.text_input(f"🔍 Escriba término de búsqueda en {opcion}...", key="busqueda_input")
    if st.button("🔍 Buscar", type="primary", use_container_width=True):
        with st.spinner("Buscando..."):
            if term:
                mask = df_u.apply(lambda row: all(p in str(row).lower() for p in term.lower().split()), axis=1)
                results = df_u[mask]
                if results.empty:
                    st.warning("No se encontraron resultados.")
                else:
                    for i, row in results.iterrows():
                        st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
                        if edicion_habilitada:
                            with st.expander(f"📝 Editar fila {i}"):
                                c_edit = st.selectbox("Columna:", row.index, key=f"sel_{i}")
                                v_edit = st.text_input("Nuevo valor:", value=row[c_edit], key=f"val_{i}")
                                if st.button("Guardar Cambios", key=f"btn_{i}"):
                                    try:
                                        if editar_celda_google_sheets(url_u, i, c_edit, v_edit):
                                            st.success("✅ ¡Sincronizado!")
                                            st.cache_data.clear()
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
            else:
                st.info("Escriba algo en el buscador.")
    if not edicion_habilitada:
        st.info("💡 Para editar, ingrese la clave correspondiente en el lápiz ✏️")

# (el resto de los expanders siguen exactamente igual que en tu versión anterior)
# Puedes copiarlos directamente desde tu código: MEDICAMENTOS, PEDIDOS, PÁGINAS ÚTILES, GESTIONES/DATOS, PRÁCTICAS Y ESPECIALISTAS, AGENDAS/MAILS, NOVEDADES, botones finales, popovers, etc.

# Para no alargar más el mensaje, dejo aquí solo la parte modificada del header y el expander de nomencladores.
# El resto (desde "with st.expander("💊 MEDICAMENTOS" ... hasta el final) pegalo tal cual tenías.

st.markdown("---")
st.markdown('<div style="text-align:center; color:#94a3b8; font-size:0.9rem;">Portal Agencias OSECAC MDP - v2026</div>', unsafe_allow_html=True)
