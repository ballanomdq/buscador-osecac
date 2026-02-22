import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE APP
st.set_page_config(page_title="OSECAC MDP", page_icon="LOGO1.png", layout="wide")

# --- CLAVE JEFE ---
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

# Historial de Chat
if 'chat_mensajes' not in st.session_state:
    st.session_state.chat_mensajes = [
        {"rol": "Jefe", "texto": "Hola equipo, bienvenidos al nuevo chat interno.", "hora": "09:00"}
    ]

# 3. CSS: ESTILO WHATSAPP / CHAT INTERNO
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #e2e8f0; }
    
    /* Alerta de mensaje nuevo */
    @keyframes pulse-red {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 82, 82, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 82, 82, 0); }
    }
    .dot { height: 10px; width: 10px; background-color: #ff5252; border-radius: 50%; display: inline-block; animation: pulse-red 2s infinite; margin-right: 8px; }

    /* Burbujas de Chat */
    .chat-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 20px;
        height: 400px;
        overflow-y: auto;
        border: 1px solid rgba(56, 189, 248, 0.2);
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .bubble {
        max-width: 80%;
        padding: 10px 15px;
        border-radius: 15px;
        font-size: 14px;
        position: relative;
        margin-bottom: 5px;
    }
    .bubble-jefe {
        background: #1e3a8a;
        color: white;
        align-self: flex-start;
        border-bottom-left-radius: 2px;
    }
    .meta-chat {
        font-size: 10px;
        opacity: 0.7;
        margin-top: 5px;
        text-align: right;
    }
    
    .header-master { text-align: center; margin-bottom: 20px; }
    .logo-fijo { width: 80px; margin: 10px auto; display: block; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><h1>OSECAC MDP</h1></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="logo-fijo">', unsafe_allow_html=True)
except: pass

st.markdown("---")

# === SECCIONES DE BUSQUEDA (Igual que antes) ===
with st.expander("📂 1. NOMENCLADORES"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")

with st.expander("📂 4. GESTIONES"):
    busqueda_t = st.text_input("Buscá trámites...", key="t")
    # ... Lógica de búsqueda ...

st.markdown("<br><br>", unsafe_allow_html=True)

# === SISTEMA DE CHAT (AL FINAL) ===
st.markdown('### <span class="dot"></span> Chat Interno de Agencia', unsafe_allow_html=True)

# Contenedor de burbujas
chat_html = '<div class="chat-container">'
for m in st.session_state.chat_mensajes:
    chat_html += f'''
    <div class="bubble bubble-jefe">
        <b>{m['rol']}</b><br>
        {m['texto']}
        <div class="meta-chat">{m['hora']}</div>
    </div>
    '''
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Input de mensaje (Solo con clave)
with st.popover("✍️ Escribir mensaje (Jefe)"):
    clave = st.text_input("Clave de Jefe:", type="password")
    if clave == PASSWORD_JEFE:
        with st.form("enviar_chat", clear_on_submit=True):
            nuevo_txt = st.text_input("Escribí tu mensaje aquí...")
            if st.form_submit_button("Enviar"):
                hora_actual = datetime.now().strftime("%H:%M")
                st.session_state.chat_mensajes.append({"rol": "Jefe", "texto": nuevo_txt, "hora": hora_actual})
                st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
