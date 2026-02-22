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

# 3. CSS: RECUPERANDO TU DISEÑO (FONDO OSCURO + BOTONES COMPACTOS)
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #e2e8f0; }
    
    /* Luz de alerta */
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    }
    .punto-alerta {
        width: 10px; height: 10px; background-color: #ff4b4b; border-radius: 50%;
        display: inline-block; margin-right: 8px; animation: pulso 1.5s infinite;
    }

    /* Títulos de sección como en tu imagen */
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 8px !important; border: none !important; }
    
    /* Buscadores con colores */
    .buscador-gestion { border-bottom: 2px solid #fbbf24 !important; margin-bottom: 10px; padding-bottom: 10px; }
    .buscador-agenda { border-bottom: 2px solid #38bdf8 !important; margin-bottom: 10px; padding-bottom: 10px; }
    
    /* Fichas de resultados */
    .ficha { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 5px; }
    .ficha-novedad { border-left: 5px solid #ff4b4b; margin-top: 10px; }
    
    /* Estilo de fecha en novedades */
    .fecha-nov { font-size: 14px; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# === LOGO Y TÍTULO ===
st.markdown("<h1 style='text-align: center; font-size: 1.5rem;'>OSECAC MDP / AGENCIAS</h1>", unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" width="80"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# ==========================================
# SECCIÓN 1: NOMENCLADORES (BOTONES EN FILA)
# ==========================================
with st.expander("📂 1. NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    c1.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    c2.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    c3.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

# ==========================================
# SECCIÓN 2: PEDIDOS (BOTONES EN FILA)
# ==========================================
with st.expander("📝 2. PEDIDOS"):
    c1, c2, c3 = st.columns(3)
    c1.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    c2.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    c3.link_button("📊 ESTADÍSTICA", "https://docs.google.com/forms/d/e/1FAIpQLSclR_u076y_mNshv_O0T9_i5rFzS02_TzR_e7I7B1u7_S_T-w/viewform")

# ==========================================
# SECCIÓN 3: PÁGINAS ÚTILES
# ==========================================
with st.expander("🌐 3. PÁGINAS ÚTILES"):
    c1, c2, c3, c4 = st.columns(4)
    c1.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    c2.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
    c3.link_button("🆔 ANSES", "https://servicioswww.anses.gob.ar/ooss2/")
    c4.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")

# ==========================================
# BUSCADORES (DISEÑO LIMPIO)
# ==========================================
with st.expander("📂 4. GESTIONES / DATOS"):
    st.markdown('<div class="buscador-gestion"></div>', unsafe_allow_html=True)
    busqueda_t = st.text_input("Buscá trámites...", key="t")
    if busqueda_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for _, r in res.iterrows():
            st.markdown(f'<div class="ficha"><b style="color:#fbbf24;">📋 {r["TRAMITE"]}</b><br>{r["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

with st.expander("📞 5. AGENDAS / MAILS"):
    st.markdown('<div class="buscador-agenda"></div>', unsafe_allow_html=True)
    busqueda_a = st.text_input("Buscá contactos...", key="a")
    if busqueda_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda x: x.str.contains(busqueda_a, case=False).any(), axis=1)]
        for _, r in res.iterrows():
            st.markdown(f'<div class="ficha"><b style="color:#38bdf8;">👤 {r.iloc[0]}</b></div>', unsafe_allow_html=True)

# ==========================================
# SECCIÓN 6: NOVEDADES (AL FINAL Y DISCRETO)
# ==========================================
with st.expander("📢 6. NOVEDADES"):
    st.markdown("<div><span class='punto-alerta'></span> <b>Comunicados Recientes</b></div>", unsafe_allow_html=True)
    for n in st.session_state.historial_novedades:
        st.markdown(f"""
        <div class="ficha ficha-novedad">
            <div class="fecha-nov">📅 {n['fecha']}</div>
            <div style="font-size:16px;">{n['mensaje']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botón discreto para escribir/borrar
    with st.popover("✍️ Escribir"):
        clave = st.text_input("Contraseña:", type="password")
        if clave == PASSWORD_JEFE:
            with st.form("f_nov", clear_on_submit=True):
                msg = st.text_area("Mensaje:", height=150)
                if st.form_submit_button("Publicar"):
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.historial_novedades.insert(0, {"id": datetime.now().timestamp(), "mensaje": msg, "fecha": ahora})
                    st.rerun()
            
            st.write("---")
            for i, n in enumerate(st.session_state.historial_novedades):
                if st.button(f"🗑️ Borrar: {n['mensaje'][:20]}...", key=f"del_{i}"):
                    st.session_state.historial_novedades.pop(i)
                    st.rerun()
