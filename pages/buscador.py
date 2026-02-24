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

# --- CLAVE DE ACCESO ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

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
    st.session_state.historial_novedades = [{"mensaje": "Portal oficial activo.", "fecha": "22/02/2026"}]

# 3. CSS DE ALTO CONTRASTE (PARA VER LO QUE ESCRIBÍS)
st.markdown("""
    <style>
    /* OCULTAR MENÚS */
    [data-testid="stSidebar"], #MainMenu, footer, header { display: none !important; }
    
    /* FONDO GENERAL */
    .stApp { background-color: #0b0e14; color: #ffffff; }

    /* --- EL ARREGLO DE LOS BUSCADORES --- */
    /* Fondo Gris Carbón para el cuadro y Texto Amarillo para que resalte sí o sí */
    div[data-baseweb="input"] {
        background-color: #262730 !important;
        border: 2px solid #38bdf8 !important;
    }
    input {
        color: #ffff00 !important; /* AMARILLO NEÓN AL ESCRIBIR */
        -webkit-text-fill-color: #ffff00 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    
    /* Títulos de las secciones */
    .stWidgetLabel p, .stExpander p { color: white !important; font-weight: bold !important; }

    /* DISEÑO DE FICHAS */
    .ficha { background: rgba(30, 41, 59, 0.9); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #38bdf8; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-practica { border-left-color: #10b981; }
    .ficha-novedad { border-left-color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# === ENCABEZADO ===
st.title("🏥 OSECAC MDP / AGENCIAS")

# --- 1. NOMENCLADORES (Buscador Principal) ---
with st.expander("📂 1. NOMENCLADORES", expanded=True):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    opcion = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True)
    busq_main = st.text_input("🔍 Escribí para buscar...", key="main")
    if busq_main:
        df = df_faba if opcion == "FABA" else df_osecac_busq
        res = df[df.astype(str).apply(lambda x: x.str.contains(busq_main, case=False)).any(axis=1)]
        for _, r in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in r.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# --- 2. PEDIDOS ---
with st.expander("📝 2. PEDIDOS"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# --- 3. PÁGINAS ÚTILES ---
with st.expander("🌐 3. PÁGINAS ÚTILES"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")

# --- 4. GESTIONES ---
with st.expander("📂 4. GESTIONES / DATOS"):
    busq_t = st.text_input("Buscá trámites...", key="t")
    if busq_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busq_t.lower(), na=False)]
        for _, r in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {r["TRAMITE"]}</b><br>{r["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# --- 5. PRÁCTICAS ---
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    busq_p = st.text_input("Buscá prácticas...", key="p")
    if busq_p:
        for d, t in [(df_practicas, "📑 PRÁCTICA"), (df_especialistas, "👨‍⚕️ ESPECIALISTA")]:
            if not d.empty:
                res = d[d.astype(str).apply(lambda x: x.str.contains(busq_p, case=False)).any(axis=1)]
                for _, r in res.iterrows():
                    st.markdown(f'<div class="ficha ficha-practica"><b>{t}</b><br>{"<br>".join([f"{c}: {v}" for c,v in r.items()])}</div>', unsafe_allow_html=True)

# --- 6. AGENDAS ---
with st.expander("📞 6. AGENDAS / MAILS"):
    busq_a = st.text_input("Buscá contactos...", key="a")
    if busq_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda x: x.str.contains(busq_a, case=False)).any(axis=1)]
        for _, r in res_a.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in r.items()])}</div>', unsafe_allow_html=True)

# --- 7. NOVEDADES ---
with st.expander("📢 7. NOVEDADES", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ EDITAR"):
        if st.text_input("Clave:", type="password") == PASSWORD_JEFE:
            msg = st.text_area("Nuevo mensaje:")
            if st.button("Publicar"):
                st.session_state.historial_novedades.insert(0, {"mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y")})
                st.rerun()
