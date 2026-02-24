import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# ✅ CONFIGURACIÓN DE PÁGINA (IMPORTANTE QUE ESTÉ ARRIBA DE TODO)
st.set_page_config(
    page_title="Buscador OSECAC MDP",
    page_icon="LOGO1.png",
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

# --- CSS ---
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }

.stApp { 
    background-color: #0b0e14;
    color: #e2e8f0; 
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

.ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
.ficha-tramite { border-left-color: #fbbf24; }
.ficha-agenda { border-left-color: #38bdf8; }
.ficha-practica { border-left-color: #10b981; } 
.ficha-faba { border-left-color: #f97316; }
.ficha-novedad { border-left-color: #ff4b4b; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# === CABECERA ===
st.markdown("<h1 style='text-align:center;'>OSECAC MDP / AGENCIAS</h1>", unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except:
    pass

st.markdown("---")

# --- SECCIÓN 1 ---
with st.expander("📂 NOMENCLADORES"):
    opcion_busqueda = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True)
    busqueda = st.text_input("Buscar...")
    if busqueda:
        df_a_usar = df_faba if opcion_busqueda == "FABA" else df_osecac_busq
        if not df_a_usar.empty:
            res = df_a_usar[df_a_usar.astype(str).apply(lambda r: r.str.contains(busqueda, case=False).any(), axis=1)]
            for _, row in res.iterrows():
                datos = "<br>".join([f"<b>{c}:</b> {v}" for c, v in row.items() if pd.notna(v)])
                st.markdown(f'<div class="ficha ficha-faba">{datos}</div>', unsafe_allow_html=True)

# --- NOVEDADES ---
with st.expander("📢 NOVEDADES", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ PANEL"):
        if st.text_input("Clave:", type="password") == PASSWORD_JEFE:
            with st.form("form_nov", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("PUBLICAR"):
                    st.session_state.historial_novedades.insert(
                        0,
                        {
                            "id": str(datetime.now().timestamp()),
                            "mensaje": msg,
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                    )
                    st.rerun()
