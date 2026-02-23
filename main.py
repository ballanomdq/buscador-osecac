import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP", layout="wide", initial_sidebar_state="collapsed")

# --- HACK DE INTERFAZ LIMPIA ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 900px !important; }
    
    /* Fondo animado y Estética */
    .stApp { 
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #111827);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    /* Fichas Estilo Card Moderno */
    .card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #38bdf8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    .card-tramite { border-left-color: #fbbf24; }
    .card-practica { border-left-color: #10b981; }
    .card-novedad { border-left-color: #f43f5e; border-top: 1px solid rgba(244,63,94,0.2); }
    
    b { color: #38bdf8; }
    .date-tag { font-size: 0.8rem; color: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA INTELIGENTE DE DATOS
@st.cache_data(ttl=600)
def get_data(url):
    try:
        # Forzar exportación CSV de Google Sheets
        u = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(u, dtype=str).fillna("")
    except:
        return pd.DataFrame()

# URLs (Asegurando formato export)
URL_TRAMITES = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_NOMENCLADOR = "https://docs.google.com/spreadsheets/d/1pc0ioT9lWLzGHDiifJLYyrXHv-NFsT3UDIDt951CTGc/export?format=csv"

df_t = get_data(URL_TRAMITES)
df_n = get_data(URL_NOMENCLADOR)

# 3. CABECERA Y LOGO
st.markdown("<center><h2 style='color:white; margin-bottom:0;'>OSECAC MDP</h2><p style='color:#38bdf8;'>Portal de Agencias</p></center>", unsafe_allow_html=True)

# 4. BUSCADOR INTELIGENTE (Simulando RAG futuro)
st.markdown("### 🔍 Buscador Unificado")
query = st.text_input("¿Qué estás buscando? (Ej: Resonancia, Plan Materno...)", placeholder="Escribí aquí...")

if query:
    q = query.lower()
    
    # Búsqueda en Trámites
    if not df_t.empty:
        res_t = df_t[df_t.apply(lambda x: q in x.astype(str).str.lower().values, axis=1)]
        if not res_t.empty:
            st.subheader("📋 Trámites Relacionados")
            for _, r in res_t.iterrows():
                st.markdown(f"""<div class="card card-tramite">
                    <b>{r.get('TRAMITE', 'Trámite')}</b><br>
                    <p style='font-size:0.9rem;'>{r.get('DESCRIPCIÓN Y REQUISITOS', '')}</p>
                </div>""", unsafe_allow_html=True)

    # Búsqueda en Nomenclador
    if not df_n.empty:
        res_n = df_n[df_n.apply(lambda x: q in x.astype(str).str.lower().values, axis=1)]
        if not res_n.empty:
            st.subheader("🔬 Nomenclador")
            for _, r in res_n.iterrows():
                st.markdown(f"""<div class="card">
                    <b style="color:#f97316;">FABA:</b> {r.get('DESCRIPCIÓN FABA', 'N/A')}<br>
                    <b style="color:#38bdf8;">OSECAC:</b> {r.get('DESCRIPCIÓN OSECAC', 'N/A')}<br>
                    <code style="background:transparent; color:#94a3b8;">Cod: {r.get('CODIGO OSECAC', 'N/A')}</code>
                </div>""", unsafe_allow_html=True)

st.markdown("---")

# 5. BOTONERA DE ACCESOS RÁPIDOS
st.subheader("⚡ Accesos Rápidos")
c1, c2 = st.columns(2)
with c1:
    st.link_button("🍼 Pedido de Leches", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/", use_container_width=True)
with c2:
    st.link_button("📦 Suministros", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/", use_container_width=True)

# 6. NOVEDADES (Session State)
st.markdown("---")
st.subheader("📢 Novedades")
if 'news' not in st.session_state:
    st.session_state.news = [{"txt": "Portal actualizado con éxito.", "f": "23/02/2026"}]

for n in st.session_state.news:
    st.markdown(f"""<div class="card card-novedad">
        <span class="date-tag">📅 {n['f']}</span><br>{n['txt']}
    </div>""", unsafe_allow_html=True)

# 7. PANEL DE CONTROL OCULTO (PopOver)
with st.sidebar:
    st.title("Configuración")
    pass_boss = st.text_input("Clave Jefe:", type="password")
    if pass_boss == "2026":
        new_n = st.text_area("Nueva Novedad:")
        if st.button("Publicar"):
            st.session_state.news.insert(0, {"txt": new_n, "f": datetime.now().strftime("%d/%m/%Y")})
            st.rerun()
