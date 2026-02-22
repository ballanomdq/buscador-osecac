import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# --- CLAVE SEGÚN TUS INSTRUCCIONES ---
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
        {"id": 0, "mensaje": "Bienvenidos al portal oficial. Las novedades se publicarán aquí.", "fecha": "21/02/2026 23:30"}
    ]

# 3. CSS: RESTAURACIÓN DEL DISEÑO OSCURO / ROSA / SOBRIO
st.markdown("""
    <style>
    /* Fondo oscuro con el tono rosa/violeta que pediste */
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #1a1b2e, #0b0e14, #2d1b2e);
        background-size: 400% 400%;
        color: #e2e8f0; 
    }
    
    /* Luz de alerta parpadeante */
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    }
    .punto-alerta {
        width: 10px; height: 10px; background-color: #ff4b4b; border-radius: 50%;
        display: inline-block; margin-right: 10px; animation: pulso 1.5s infinite;
    }

    /* Estilo de los expansores (sobrio, sin bordes blancos) */
    .stExpander { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important; 
        margin-bottom: 10px !important;
    }
    
    /* Líneas de color identificatorias */
    .linea-gestion { border-bottom: 3px solid #fbbf24; margin-bottom: 15px; }
    .linea-agenda { border-bottom: 3px solid #38bdf8; margin-bottom: 15px; }
    .linea-novedad { border-bottom: 3px solid #ff4b4b; margin-bottom: 15px; }
    
    /* Fichas de resultados */
    .ficha { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.05); }
    .ficha-novedad { border-left: 5px solid #ff4b4b; }
    
    /* Fecha grande en novedades */
    .fecha-destacada { font-size: 16px; color: #ff4b4b; font-weight: 800; display: block; margin-bottom: 5px; }
    
    /* Botones centrados y limpios */
    div.stLinkButton > a { width: 100% !important; text-align: center !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown("<h2 style='text-align: center; font-weight: 300; letter-spacing: 4px; color: white;'>OSECAC MDP / AGENCIAS</h2>", unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" width="75"></center>', unsafe_allow_html=True)
except: pass

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. NOMENCLADORES
# ==========================================
with st.expander("📂 1. NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    c1.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    c2.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    c3.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

# ==========================================
# 2. PEDIDOS
# ==========================================
with st.expander("📝 2. PEDIDOS"):
    c1, c2, c3 = st.columns(3)
    c1.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    c2.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    c3.link_button("ESTADÍSTICA", "https://docs.google.com/forms/d/e/1FAIpQLSclR_u076y_mNshv_O0T9_i5rFzS02_TzR_e7I7B1u7_S_T-w/viewform")

# ==========================================
# 3. PÁGINAS ÚTILES (TODAS LAS QUE TENÍAS)
# ==========================================
with st.expander("🌐 3. PÁGINAS ÚTILES"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.link_button("SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("GMS WEB", "https://www.gmssa.com.ar/")
    with c2:
        st.link_button("ANSES CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
    with c3:
        st.link_button("MICROSITIO", "https://micrositio.osecac.org.ar/")
        st.link_button("SISTEMA OSECAC", "https://sistema.osecac.org.ar/")
    with c4:
        st.link_button("PADRÓN", "https://padronelectoral.org/")
        st.link_button("SISA", "https://sisa.msal.gov.ar/sisa/")

# ==========================================
# 4. GESTIONES
# ==========================================
with st.expander("📂 4. GESTIONES / DATOS"):
    st.markdown('<div class="linea-gestion"></div>', unsafe_allow_html=True)
    busqueda_t = st.text_input("Buscá trámites...", key="t_in")
    if busqueda_t:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for _, r in res.iterrows():
            st.markdown(f'<div class="ficha"><b style="color:#fbbf24;">📋 {r["TRAMITE"]}</b><br><small>{r["DESCRIPCIÓN Y REQUISITOS"]}</small></div>', unsafe_allow_html=True)

# ==========================================
# 5. AGENDAS
# ==========================================
with st.expander("📞 5. AGENDAS / MAILS"):
    st.markdown('<div class="linea-agenda"></div>', unsafe_allow_html=True)
    busqueda_a = st.text_input("Buscá contactos...", key="a_in")
    if busqueda_a:
        res = df_agendas[df_agendas.astype(str).apply(lambda x: x.str.contains(busqueda_a, case=False).any(), axis=1)]
        for _, r in res.iterrows():
            st.markdown(f'<div class="ficha"><b style="color:#38bdf8;">👤 {r.iloc[0]}</b><br><small>{r.iloc[1]}</small></div>', unsafe_allow_html=True)

# ==========================================
# 6. NOVEDADES (FINAL)
# ==========================================
with st.expander("📢 6. NOVEDADES"):
    st.markdown('<div class="linea-novedad"></div>', unsafe_allow_html=True)
    st.markdown("<div><span class='punto-alerta'></span> <b>NOVEDADES DEL DÍA</b></div>", unsafe_allow_html=True)
    
    for n in st.session_state.historial_novedades:
        st.markdown(f"""
        <div class="ficha ficha-novedad">
            <span class="fecha-destacada">📅 FECHA: {n['fecha']}</span>
            <div style="font-size:17px; color:white;">{n['mensaje']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.popover("✍️ Panel Jefe"):
        clave = st.text_input("Clave:", type="password")
        if clave == PASSWORD_JEFE:
            with st.form("f_jefe", clear_on_submit=True):
                m = st.text_area("Mensaje:", height=150)
                if st.form_submit_button("PUBLICAR"):
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.historial_novedades.insert(0, {"id": datetime.now().timestamp(), "mensaje": m, "fecha": ahora})
                    st.rerun()
            for i, n in enumerate(st.session_state.historial_novedades):
                if st.button(f"🗑️ Borrar: {n['mensaje'][:20]}...", key=f"d_{i}"):
                    st.session_state.historial_novedades.pop(i)
                    st.rerun()
