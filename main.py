import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS COMPLETO
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes shine { 0% { left: -100%; opacity: 0; } 50% { opacity: 0.6; } 100% { left: 100%; opacity: 0; } }

    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    label, .stRadio label, .stRadio div[data-testid="stMarkdown"] p, .stTextInput label, .st-emotion-cache-15ruxrl, .st-emotion-cache-1v0mbdj p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    input::placeholder {
        color: #d1d5db !important;
        opacity: 1 !important;
    }
    
    .stRadio div[role="radiogroup"] label p {
        color: #ffffff !important;
    }
    
    .stRadio label {
        color: #ffffff !important;
    }

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold !important; 
    }

    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.05); border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5); display: inline-block; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; }
    .shimmer-efecto { position: absolute; top: 0; width: 100px; height: 100%; background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent); transform: skewX(-20deg); animation: shine 4s infinite linear; }
    
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-especialista { border-left-color: #8b5cf6; }
    .ficha-novedad { border-left-color: #ff4b4b; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    
    .edit-icon {
        display: inline-block;
        margin-left: 8px;
        cursor: pointer;
        opacity: 0.5;
        transition: opacity 0.2s;
        font-size: 1.2rem;
    }
    .edit-icon:hover {
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA ESCRIBIR EN SHEETS ---
@st.cache_resource
def get_sheets_service():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=credentials)

def escribir_en_sheet(spreadsheet_id, range_name, valores):
    service = get_sheets_service()
    body = {"values": valores}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    return result

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
}

# IDs de sheets para escritura
SHEETS_IDS = {
    "faba": "1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0",
    "osecac": "1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]
if 'mostrar_editor_faba' not in st.session_state:
    st.session_state.mostrar_editor_faba = False
if 'mostrar_editor_osecac' not in st.session_state:
    st.session_state.mostrar_editor_osecac = False

# --- INTERFAZ DEL PORTAL ---
st.markdown('<div class="header-master"><div class="capsula-header-mini"><div class="shimmer-efecto"></div><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# 1. NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    # Título con íconos de edición
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        st.markdown("**FABA**")
        if st.button("✏️", key="edit_faba", help="Editar nomenclador FABA"):
            st.session_state.mostrar_editor_faba = True
    with col2:
        st.markdown("**OSECAC**")
        if st.button("✏️", key="edit_osecac", help="Editar nomenclador OSECAC"):
            st.session_state.mostrar_editor_osecac = True
    
    opcion = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True, key="rad_nom")
    
    # Editor FABA
    if st.session_state.mostrar_editor_faba:
        with st.form("editor_faba"):
            st.markdown("---")
            st.subheader("✏️ EDITOR NOMENCLADOR FABA")
            clave = st.text_input("Clave de edición:", type="password")
            
            if clave == "*":
                st.success("✓ Clave correcta - Podés agregar registros")
                col1_f, col2_f = st.columns(2)
                with col1_f:
                    codigo = st.text_input("Código:")
                    descripcion = st.text_input("Descripción:")
                with col2_f:
                    observaciones = st.text_input("Observaciones:")
                
                col_guardar, col_cancelar = st.columns(2)
                with col_guardar:
                    guardado = st.form_submit_button("💾 GUARDAR")
                with col_cancelar:
                    cancelar = st.form_submit_button("❌ CANCELAR")
                
                if guardado:
                    if codigo and descripcion:
                        try:
                            valores = [[codigo, descripcion, observaciones, datetime.now().strftime("%d/%m/%Y %H:%M")]]
                            escribir_en_sheet(SHEETS_IDS["faba"], "A:D", valores)
                            st.success("✅ Registro guardado en FABA")
                            st.session_state.mostrar_editor_faba = False
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ Código y Descripción son obligatorios")
                if cancelar:
                    st.session_state.mostrar_editor_faba = False
                    st.rerun()
            else:
                if clave:
                    st.error("❌ Clave incorrecta")
                if st.form_submit_button("CANCELAR"):
                    st.session_state.mostrar_editor_faba = False
                    st.rerun()
    
    # Editor OSECAC
    if st.session_state.mostrar_editor_osecac:
        with st.form("editor_osecac"):
            st.markdown("---")
            st.subheader("✏️ EDITOR NOMENCLADOR OSECAC")
            clave = st.text_input("Clave de edición:", type="password")
            
            if clave == "*":
                st.success("✓ Clave correcta - Podés agregar registros")
                col1_o, col2_o = st.columns(2)
                with col1_o:
                    codigo = st.text_input("Código:")
                    descripcion = st.text_input("Descripción:")
                with col2_o:
                    observaciones = st.text_input("Observaciones:")
                
                col_guardar, col_cancelar = st.columns(2)
                with col_guardar:
                    guardado = st.form_submit_button("💾 GUARDAR")
                with col_cancelar:
                    cancelar = st.form_submit_button("❌ CANCELAR")
                
                if guardado:
                    if codigo and descripcion:
                        try:
                            valores = [[codigo, descripcion, observaciones, datetime.now().strftime("%d/%m/%Y %H:%M")]]
                            escribir_en_sheet(SHEETS_IDS["osecac"], "A:D", valores)
                            st.success("✅ Registro guardado en OSECAC")
                            st.session_state.mostrar_editor_osecac = False
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ Código y Descripción son obligatorios")
                if cancelar:
                    st.session_state.mostrar_editor_osecac = False
                    st.rerun()
            else:
                if clave:
                    st.error("❌ Clave incorrecta")
                if st.form_submit_button("CANCELAR"):
                    st.session_state.mostrar_editor_osecac = False
                    st.rerun()
    
    # Buscador
    bus_nom = st.text_input("🔍 Buscar en nomencladores...", key="bus_n")
    if bus_nom:
        df_u = df_faba if opcion == "FABA" else df_osecac_busq
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_nom.lower().split()), axis=1)
        for i, row in df_u[mask].iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# 2. PEDIDOS
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with cols[1]:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
        st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# 4. GESTIONES
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha ficha-practica">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        re = df_especialistas[df_especialistas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in re.iterrows():
            st.markdown(f'<div class="ficha ficha-especialista">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 6. AGENDAS
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ PANEL"):
        if st.text_input("Clave de edición:", type="password", key="ed_pass") == "2026":
            with st.form("n_form", clear_on_submit=True):
                m = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
