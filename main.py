import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE APP PROFESIONAL
st.set_page_config(page_title="OSECAC MDP", page_icon="LOGO1.png", layout="wide")

# --- CLAVE ACTUALIZADA ---
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
        {"usuario": "Jefe", "mensaje": "Bienvenidos al portal. Las novedades importantes se verán en este espacio.", "fecha": "21/02 23:00"}
    ]

# 3. CSS: DISEÑO LIMPIO
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #e2e8f0; }
    
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    }
    .punto-alerta {
        width: 10px; height: 10px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulso 1.5s infinite;
    }

    .header-master { text-align: center; margin-bottom: 20px; }
    .capsula { padding: 10px 25px; background: rgba(56, 189, 248, 0.05); border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.5); display: inline-block; }
    .logo-fijo { width: 85px; margin: 15px auto; display: block; }
    
    .novedad-box {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .novedad-texto { font-size: 15px; color: #f1f5f9; }
    .novedad-fecha { font-size: 10px; color: #64748b; text-align: right; margin-top: 5px; }
    
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><div class="capsula"><h1 style="font-size:1.5rem; margin:0;">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="logo-fijo">', unsafe_allow_html=True)
except: pass

st.markdown("---")

# === BLOQUES DE BOTONES Y BUSQUEDA ===
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")

with st.expander("📂 **4. GESTIONES / DATOS**"):
    busqueda_t = st.text_input("Buscá trámites...", key="t")

with st.expander("📞 **5. AGENDAS / MAILS**"):
    busqueda_a = st.text_input("Buscá contactos...", key="a")

st.markdown("<br><br>", unsafe_allow_html=True)

# === SECCIÓN NOVEDADES (AL FINAL) ===
st.markdown('---')
st.markdown('### <span class="punto-alerta"></span> NOVEDADES', unsafe_allow_html=True)

# Lista de Novedades existentes
for n in st.session_state.historial_novedades:
    st.markdown(f"""
    <div class="novedad-box">
        <div style="color:#ff4b4b; font-size:11px; font-weight:bold; text-transform:uppercase;">Comunicado Oficial</div>
        <div class="novedad-texto">{n['mensaje']}</div>
        <div class="novedad-fecha">{n['fecha']}</div>
    </div>
    """, unsafe_allow_html=True)

# Botón desplegable para escribir (No invasivo)
with st.expander("✍️ Escribir"):
    clave = st.text_input("Contraseña:", type="password")
    if clave == PASSWORD_JEFE:
        with st.form("form_novedades_final", clear_on_submit=True):
            mensaje = st.text_area("Nuevo mensaje:")
            if st.form_submit_button("Publicar"):
                ahora = datetime.now().strftime("%d/%m %H:%M")
                st.session_state.historial_novedades.insert(0, {"usuario": "Jefe", "mensaje": mensaje, "fecha": ahora})
                st.rerun()
