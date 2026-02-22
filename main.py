import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# --- CLAVE CONFIGURADA ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": 0, "mensaje": "Bienvenidos al portal oficial. Revisen aquí los comunicados.", "fecha": "21/02/2026 23:30"}
    ]

# 3. CSS: ESTILO COMPLETO CON ALERTA Y DISEÑO TUYO
st.markdown("""
    <style>
    .stApp { background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14); background-size: 400% 400%; color: #e2e8f0; }
    
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 12px rgba(255, 75, 75, 0); }
    }
    .punto-alerta {
        width: 12px; height: 12px; background-color: #ff4b4b; border-radius: 50%;
        display: inline-block; margin-right: 12px; animation: pulso 1.5s infinite;
        vertical-align: middle;
    }

    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.05); border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5); display: inline-block; }
    .logo-fijo { width: 85px !important; margin: 15px auto; display: block; }
    
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    
    .buscador-novedades { border: 2px solid #ff4b4b !important; border-radius: 12px; margin-top: 10px; }
    .ficha-novedad { border-left: 6px solid #ff4b4b; margin-top: 10px; }
    .novedad-fecha-grande { font-size: 14px; color: #ff4b4b; font-weight: bold; margin-bottom: 5px; display: block; }
    .novedad-texto-grande { font-size: 17px; line-height: 1.4; color: #ffffff; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    
    div.stLinkButton > a { width: 100% !important; text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA Y LOGO ===
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 style="font-size:1.4rem; color:white; margin:0;">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="logo-fijo">', unsafe_allow_html=True)
except: pass

st.markdown("---")

# ==========================================
# SECCIONES 1, 2 y 3 (RECUPERADAS COMPLETAS)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADÍSTICA", "https://docs.google.com/forms/d/e/1FAIpQLSclR_u076y_mNshv_O0T9_i5rFzS02_TzR_e7I7B1u7_S_T-w/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

st.markdown("<br>", unsafe_allow_html=True)

# === SECCIÓN 4 y 5 (BUSCADORES) ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.markdown(f'<div class="ficha ficha-agenda"><b style="color:#38bdf8;">👤 {row.iloc[0]}</b></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 6: NOVEDADES (CON TODO) ===
st.markdown('<div class="buscador-novedades">', unsafe_allow_html=True)
with st.expander("📢 **<span class='punto-alerta'></span> 6. NOVEDADES**"):
    for n in st.session_state.historial_novedades:
        st.markdown(f"""
        <div class="ficha ficha-novedad">
            <span class="novedad-fecha-grande">📅 FECHA: {n['fecha']}</span>
            <div class="novedad-texto-grande">{n['mensaje']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    with st.popover("✍️ PANEL DE CONTROL"):
        clave = st.text_input("Contraseña:", type="password")
        if clave == PASSWORD_JEFE:
            with st.form("form_novedad_grande", clear_on_submit=True):
                msg = st.text_area("Escribí el comunicado:", height=200)
                if st.form_submit_button("📢 PUBLICAR"):
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    nuevo_id = datetime.now().timestamp()
                    st.session_state.historial_novedades.insert(0, {"id": nuevo_id, "mensaje": msg, "fecha": ahora})
                    st.rerun()
            
            st.write("**Borrar mensajes:**")
            for i, n in enumerate(st.session_state.historial_novedades):
                c1, c2 = st.columns([4, 1])
                c1.caption(f"{n['fecha']}")
                if c2.button("🗑️", key=f"del_{i}"):
                    st.session_state.historial_novedades.pop(i)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
