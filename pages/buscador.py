import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLAVE DE ACCESO PERSONALIZADA ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS (CSV DESDE GOOGLE SHEETS)
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        if '/edit' in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        return pd.read_csv(csv_url, dtype=str)
    except:
        return pd.DataFrame()

# URLs DE TODAS LAS PLANILLAS
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_FABA = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
URL_OSECAC_BUSQ = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_faba = cargar_datos(URL_FABA)
df_osecac_busq = cargar_datos(URL_OSECAC_BUSQ)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS REFORZADO: VISIBILIDAD TOTAL
st.markdown("""
    <style>
    /* OCULTAR PANEL LATERAL */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* --- REFUERZO DE COLOR BLANCO PARA TEXTOS --- */
    /* Texto de Radio Buttons (FABA/OSECAC) */
    div[data-testid="stWidgetLabel"] p {
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    
    div[role="radiogroup"] label p {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Títulos de los inputs (Buscar en...) */
    .stTextInput label p {
        color: white !important;
        font-weight: bold !important;
    }

    /* Texto que escribes dentro de los buscadores */
    input[data-testid="stTextInputRootElement"] {
        color: white !important;
    }
    
    /* Color del cursor y texto activo */
    input {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* --- DISEÑO ORIGINAL --- */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes shine { 0% { left: -100%; opacity: 0; } 50% { opacity: 0.6; } 100% { left: 100%; opacity: 0; } }
    @keyframes pulso { 0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); } 100% { box-shadow: 0 0 0 12px rgba(255, 75, 75, 0); } }

    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }
    .punto-alerta { width: 12px; height: 12px; background-color: #ff4b4b; border-radius: 50%; display: inline-block; margin-right: 12px; animation: pulso 1.5s infinite; vertical-align: middle; }
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.05); border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5); overflow: hidden; margin-bottom: 12px; display: inline-block; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; z-index: 2; position: relative; }
    .shimmer-efecto { position: absolute; top: 0; width: 100px; height: 100%; background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent); transform: skewX(-20deg); animation: shine 4s infinite linear; z-index: 1; }
    
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-faba { border-left-color: #f97316; }
    .ficha-novedad { border-left-color: #ff4b4b; margin-top: 10px; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-practica { border: 2px solid #10b981 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-novedades { border: 2px solid #ff4b4b !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><div class="capsula-header-mini"><div class="shimmer-efecto"></div><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# --- SECCIÓN 1: NOMENCLADORES ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    opcion_busqueda = st.radio("Seleccione el origen de datos:", ["FABA", "OSECAC"], horizontal=True, key="switch_busq")
    busqueda_unificada = st.text_input(f"🔍 Buscar en {opcion_busqueda}...", key="main_search")
    
    if busqueda_unificada:
        df_a_usar = df_faba if opcion_busqueda == "FABA" else df_osecac_busq
        clase_ficha = "ficha-faba" if opcion_busqueda == "FABA" else "ficha-agenda"
        
        if not df_a_usar.empty:
            palabras = busqueda_unificada.lower().split()
            mask = df_a_usar.apply(lambda row: all(p in str(row).lower() for p in palabras), axis=1)
            resultados = df_a_usar[mask]
            
            if not resultados.empty:
                for i, row in resultados.iterrows():
                    datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
                    st.markdown(f'<div class="ficha {clase_ficha}">{"<br>".join(datos)}</div>', unsafe_allow_html=True)
            else:
                st.warning(f"No se encontraron resultados en {opcion_busqueda}.")
        else:
            st.error(f"Error al cargar la base de datos.")

# --- SECCIÓN 2: PEDIDOS ---
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# --- SECCIÓN 3: PÁGINAS ÚTILES ---
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    st.link_button("🏥 SSSALUD (Consultas)", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
    st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
    st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
    st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# --- GESTIONES ---
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PRÁCTICAS ---
st.markdown('<div class="buscador-practica">', unsafe_allow_html=True)
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    busqueda_p = st.text_input("Buscá prácticas o especialistas...", key="search_p")
    if busqueda_p:
        for df_actual, tipo in [(df_practicas, "📑 PRÁCTICA"), (df_especialistas, "👨‍⚕️ ESPECIALISTA")]:
            if not df_actual.empty:
                res = df_actual[df_actual.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
                for i, row in res.iterrows():
                    datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
                    st.markdown(f'<div class="ficha ficha-practica"><span style="color:#10b981; font-weight:bold;">{tipo}:</span><br>{"<br>".join(datos)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- AGENDAS ---
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- NOVEDADES ---
st.markdown('<div class="buscador-novedades">', unsafe_allow_html=True)
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    st.markdown("<div><span class='punto-alerta'></span><b>ÚLTIMOS COMUNICADOS</b></div>", unsafe_allow_html=True)
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad"><span class="novedad-fecha-grande">📅 {n["fecha"]}</span><div class="novedad-texto">{n["mensaje"]}</div></div>', unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL DE CONTROL"):
        clave_n = st.text_input("Clave de edición:", type="password")
        if clave_n == PASSWORD_JEFE:
            with st.form("form_nov", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("📢 PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(datetime.now().timestamp()), "mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
