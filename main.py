import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": datetime.now(), "tipo": "texto", "archivo": None, "nombre_archivo": ""}
    ]
if 'visto' not in st.session_state:
    st.session_state.visto = False

# 2. CSS CORREGIDO + ANIMACIÓN DE LUZ ROJA
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes blinker { 50% { opacity: 0; } }

    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    .luz-roja {
        height: 12px; width: 12px; background-color: #ff4b4b;
        border-radius: 50%; display: inline-block;
        margin-right: 8px; box-shadow: 0 0 10px #ff4b4b;
        animation: blinker 1s linear infinite;
    }

    .stMarkdown p, label { color: #ffffff !important; }

    .stLinkButton a {
        background-color: rgba(23, 32, 48, 0.9) !important;
        color: white !important; border: 1px solid #38bdf8 !important; border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] {
        background-color: #ffffff !important; border: 2px solid #38bdf8 !important; border-radius: 8px !important;
    }
    input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: bold !important; }

    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-novedad { border-left-color: #ff4b4b; }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS (Mismo sistema anterior) ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/edit",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=0",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/edit",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/edit"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

# --- HEADER ---
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

# --- SECCIONES 1 A 6 (SIN CAMBIOS) ---
with st.expander("📂 **1. NOMENCLADORES**"):
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    with c1: cl_f = st.popover("✏️").text_input("Clave FABA:", type="password", key="p_f")
    with c2: sel_faba = st.checkbox("FABA", value=True, key="chk_f")
    with c3: cl_o = st.popover("✏️").text_input("Clave OSECAC:", type="password", key="p_o")
    with c4: sel_osecac = st.checkbox("OSECAC", key="chk_o")
    
    opcion = "OSECAC" if sel_osecac else "FABA"
    cl_actual = cl_o if sel_osecac else cl_f
    df_u = df_osecac_busq if sel_osecac else df_faba
    url_u = URLs["osecac"] if sel_osecac else URLs["faba"]

    bus_nom = st.text_input(f"🔍 Buscar en {opcion}...")
    if bus_nom:
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_nom.lower().split()), axis=1)
        for i, row in df_u[mask].iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
            if cl_actual == "*":
                with st.expander(f"📝 Editar fila {i}"):
                    c_edit = st.selectbox("Columna:", row.index, key=f"sel_{i}")
                    v_edit = st.text_input("Nuevo valor:", value=row[c_edit], key=f"val_{i}")
                    if st.button("Guardar", key=f"btn_{i}"):
                        if editar_celda_google_sheets(url_u, i, c_edit, v_edit):
                            st.success("¡Sincronizado!"); st.cache_data.clear(); st.rerun()

# (Secciones 2 a 6 omitidas por brevedad, mantenlas igual)
with st.expander("📝 **2. PEDIDOS**"): st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
with st.expander("🌐 **3. PÁGINAS ÚTILES**"): st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
with st.expander("📂 **4. GESTIONES**"): st.text_input("Buscá trámites...", key="bt_alt")
with st.expander("🩺 **5. PRÁCTICAS**"): st.text_input("Buscá prácticas...", key="bp_alt")
with st.expander("📞 **6. AGENDAS**"): st.text_input("Buscá contactos...", key="ba_alt")

# --- 7. NOVEDADES (SISTEMA MEJORADO) ---
ultima_novedad = st.session_state.historial_novedades[0]['fecha']
hay_nueva = (datetime.now() - ultima_novedad) < timedelta(hours=24) and not st.session_state.visto

label_novedades = "📢 **7. NOVEDADES**"
if hay_nueva:
    label_novedades = f'<span class="luz-roja"></span> 📢 **7. NOVEDADES**'

with st.expander(label_novedades, expanded=hay_nueva):
    if st.button("Marcar todo como leído"):
        st.session_state.visto = True
        st.rerun()

    for n in st.session_state.historial_novedades:
        with st.container():
            st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"].strftime("%d/%m/%Y %H:%M")}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
            if n["archivo"]:
                if n["tipo"] == "Imagen":
                    st.image(n["archivo"], width=300)
                else:
                    st.download_button(f"📥 Descargar {n['nombre_archivo']}", n["archivo"], file_name=n["nombre_archivo"])

    st.markdown("---")
    with st.popover("✏️ PANEL JEFE"):
        if st.text_input("Clave Maestro:", type="password") == "*":
            with st.form("form_jefe", clear_on_submit=True):
                msg = st.text_area("Mensaje del comunicado:")
                archivo = st.file_uploader("Subir Imagen o PDF (opcional)", type=['png', 'jpg', 'pdf'])
                if st.form_submit_button("PUBLICAR COMUNICADO"):
                    tipo = "Imagen" if archivo and archivo.type != "application/pdf" else "Archivo"
                    nueva = {
                        "id": str(time.time()),
                        "mensaje": msg,
                        "fecha": datetime.now(),
                        "tipo": tipo,
                        "archivo": archivo.getvalue() if archivo else None,
                        "nombre_archivo": archivo.name if archivo else ""
                    }
                    st.session_state.historial_novedades.insert(0, nueva)
                    st.session_state.visto = False
                    st.success("¡Publicado con éxito!")
                    st.rerun()
