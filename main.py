import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE "APP" PROFESIONAL
st.set_page_config(
    page_title="OSECAC MDP", 
    page_icon="LOGO1.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONTRASEÑA JEFE ---
PASSWORD_JEFE = "osecac2024"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

URL_AGENDAS = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS)
df_tramites = cargar_datos(URL_TRAMITES)

if 'chat_historial' not in st.session_state:
    st.session_state.chat_historial = [{"usuario": "Jefe", "mensaje": "Bienvenidos al portal oficial. Instalalo en tu inicio.", "fecha": "20/05 09:00"}]

# 3. CSS ADAPTATIVO
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14); background-size: 400% 400%; color: #e2e8f0; }
    .header-master { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .capsula-header-mini { padding: 10px 25px; background: rgba(56, 189, 248, 0.05); border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.5); margin-bottom: 10px; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; }
    @media (max-width: 600px) { .titulo-mini { font-size: 1.1rem !important; } .logo-fijo { width: 75px !important; } }
    .chat-box { background: rgba(56, 189, 248, 0.1); border-radius: 12px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #38bdf8; }
    .logo-container { display: flex; justify-content: center; margin: 15px 0; }
    .logo-fijo { width: 85px; height: auto; }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    div.stLinkButton > a { border-radius: 8px !important; font-size: 12px !important; font-weight: 700 !important; text-transform: uppercase !important; width: 100% !important; text-align: center !important; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div><div style="color: #94a3b8; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;">Portal de Apoyo para Compañeros</div></div>', unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{img_b64}" class="logo-fijo"></div>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# ==========================================
# SECCIONES: 1, 2 y 3 (LAS QUE FALTABAN)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

st.markdown("<br>", unsafe_allow_html=True)

# === SECCIÓN: NOVEDADES DEL JEFE ===
with st.expander("📢 **NOVEDADES Y COMUNICADOS**", expanded=True):
    with st.popover("🔑 Publicar como Jefe"):
        pw = st.text_input("Contraseña:", type="password")
        if pw == PASSWORD_JEFE:
            with st.form("form_chat", clear_on_submit=True):
                txt = st.text_area("Mensaje:")
                if st.form_submit_button("Enviar"):
                    fecha = datetime.now().strftime("%d/%m %H:%M")
                    st.session_state.chat_historial.insert(0, {"usuario": "Jefe", "mensaje": txt, "fecha": fecha})
                    st.rerun()
    for m in st.session_state.chat_historial:
        st.markdown(f'<div class="chat-box"><div style="color:#38bdf8; font-size:11px; font-weight:bold;">OFICIAL</div><div style="font-size:15px;">{m["mensaje"]}</div><div style="font-size:10px; color:#64748b; text-align:right;">{m["fecha"]}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# === SECCIÓN 4: GESTIONES ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div style="background:rgba(23,32,48,0.9); padding:15px; border-radius:10px; border-left:5px solid #fbbf24; margin-bottom:10px;"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br><small>{row["DESCRIPCIÓN Y REQUISITOS"]}</small></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 5: AGENDAS ===
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.markdown(f'<div style="background:rgba(23,32,48,0.9); padding:15px; border-radius:10px; border-left:5px solid #38bdf8; margin-bottom:10px;"><b style="color:#38bdf8;">👤 {row.iloc[0]}</b><br><small>{row.iloc[1]}</small></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
