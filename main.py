import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE APP PROFESIONAL
st.set_page_config(
    page_title="OSECAC MDP", 
    page_icon="LOGO1.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLAVE SEGÚN TUS INSTRUCCIONES ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

URL_AGENDAS = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS)
df_tramites = cargar_datos(URL_TRAMITES)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"usuario": "Jefe", "mensaje": "Bienvenidos al portal. Revisen las novedades aquí debajo.", "fecha": "21/02 23:00"}
    ]

# 3. CSS: ESTILO COMPLETO (COLORES + ALERTA + RESPONSIVO)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14); color: #e2e8f0; }
    
    /* Luz de alerta */
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    }
    .punto-alerta { width: 10px; height: 10px; background-color: #ff4b4b; border-radius: 50%; display: inline-block; margin-right: 10px; animation: pulso 1.5s infinite; }

    .header-master { text-align: center; margin-bottom: 20px; }
    .capsula { padding: 10px 25px; background: rgba(56, 189, 248, 0.05); border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.5); display: inline-block; }
    .logo-fijo { width: 85px; margin: 15px auto; display: block; }
    
    /* Estilos de los Buscadores (Colores Prometidos) */
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 15px; padding: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 15px; padding: 10px; }
    
    .ficha-t { border-left: 5px solid #fbbf24; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .ficha-a { border-left: 5px solid #38bdf8; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 10px; }

    .novedad-box { background: rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    div.stLinkButton > a { width: 100% !important; text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA Y LOGO ===
st.markdown('<div class="header-master"><div class="capsula"><h1 style="font-size:1.5rem; margin:0;">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="logo-fijo">', unsafe_allow_html=True)
except: pass

st.markdown("---")

# ==========================================
# SECCIONES 1, 2 y 3 (RECUPERADAS)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIONES 4 y 5 (BUSCADORES CON COLORES)
# ==========================================
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha-t"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br><small>{row["DESCRIPCIÓN Y REQUISITOS"]}</small></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.markdown(f'<div class="ficha-a"><b style="color:#38bdf8;">👤 {row.iloc[0]}</b><br><small>{row.iloc[1]}</small></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECCIÓN NOVEDADES (AL FINAL)
# ==========================================
st.markdown('<br><hr>', unsafe_allow_html=True)
st.markdown('### <span class="punto-alerta"></span> NOVEDADES', unsafe_allow_html=True)

for n in st.session_state.historial_novedades:
    st.markdown(f"""<div class="novedad-box">
        <div style="color:#ff4b4b; font-size:11px; font-weight:bold;">OFICIAL</div>
        <div style="font-size:15px;">{n['mensaje']}</div>
        <div style="font-size:10px; color:#64748b; text-align:right;">{n['fecha']}</div>
    </div>""", unsafe_allow_html=True)

with st.expander("✍️ Escribir"):
    clave = st.text_input("Contraseña:", type="password")
    if clave == PASSWORD_JEFE:
        with st.form("form_final", clear_on_submit=True):
            nuevo_msg = st.text_area("Mensaje:")
            if st.form_submit_button("Publicar"):
                ahora = datetime.now().strftime("%d/%m %H:%M")
                st.session_state.historial_novedades.insert(0, {"usuario": "Jefe", "mensaje": nuevo_msg, "fecha": ahora})
                st.rerun()
