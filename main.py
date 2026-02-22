import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="OSECAC MDP", page_icon="LOGO1.png", layout="wide")

# --- CLAVE DEL JEFE ---
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
    st.session_state.chat_historial = [{"usuario": "Jefe", "mensaje": "Bienvenidos al portal. Revisen las novedades aquí abajo.", "fecha": "21/02 23:00"}]

# 3. CSS: ANIMACIÓN DE LUZ DE ALERTA
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14); color: #e2e8f0; }
    
    /* Animación del punto rojo de alerta */
    @keyframes pulso-alerta {
        0% { box-shadow: 0 0 0 0px rgba(255, 0, 0, 0.7); }
        100% { box-shadow: 0 0 0 15px rgba(255, 0, 0, 0); }
    }
    .luz-alerta {
        width: 12px; height: 12px;
        background-color: #ff0000;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulso-alerta 1.5s infinite;
        vertical-align: middle;
    }

    .header-master { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .capsula-header-mini { padding: 10px 25px; background: rgba(56, 189, 248, 0.05); border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.5); margin-bottom: 10px; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; }
    
    .logo-container { display: flex; justify-content: center; margin: 15px 0; }
    .logo-fijo { width: 85px; height: auto; }
    
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    .chat-box { background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 15px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA Y LOGO ===
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{img_b64}" class="logo-fijo"></div>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# ==========================================
# BLOQUE 1: BOTONES RÁPIDOS
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BLOQUE 2: BUSCADORES (EL CUERPO)
# ==========================================
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="t")
    if busqueda_t and not df_tramites.empty:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.warning(f"📋 {row['TRAMITE']}\n\n{row['DESCRIPCIÓN Y REQUISITOS']}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    busqueda_a = st.text_input("Buscá contactos...", key="a")
    if busqueda_a and not df_agendas.empty:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.info(f"👤 {row.iloc[0]}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# BLOQUE 3: CHAT AL FINAL CON LUZ DE ALERTA
# ==========================================
st.markdown("---")
# Aquí está el truco: el título tiene la clase 'luz-alerta'
st.markdown('### <span class="luz-alerta"></span> NOVEDADES DEL JEFE', unsafe_allow_html=True)

with st.container():
    # Espacio para que el jefe publique
    with st.popover("🔑 Acceso Jefe"):
        pw = st.text_input("Clave:", type="password")
        if pw == PASSWORD_JEFE:
            with st.form("form_novedad", clear_on_submit=True):
                txt = st.text_area("Escribí el comunicado oficial:")
                if st.form_submit_button("📢 PUBLICAR PARA TODOS"):
                    fecha = datetime.now().strftime("%d/%m %H:%M")
                    st.session_state.chat_historial.insert(0, {"usuario": "Jefe", "mensaje": txt, "fecha": fecha})
                    st.rerun()
    
    # Lista de mensajes
    for m in st.session_state.chat_historial:
        st.markdown(f"""
        <div class="chat-box">
            <div style="color:#ff4b4b; font-size:11px; font-weight:bold;">⚠️ COMUNICADO URGENTE</div>
            <div style="font-size:16px; margin: 5px 0;">{m['mensaje']}</div>
            <div style="font-size:10px; color:#64748b; text-align:right;">{m['fecha']}</div>
        </div>
        """, unsafe_allow_html=True)
