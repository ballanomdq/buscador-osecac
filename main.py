import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE "APP" PROFESIONAL
# Esto es lo que define cómo se ve el ícono y el nombre al instalarlo
st.set_page_config(
    page_title="OSECAC MDP", 
    page_icon="LOGO1.png", # Asegurate de que el archivo se llame así
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONTRASEÑA PARA QUE SOLO EL JEFE ESCRIBA ---
PASSWORD_JEFE = "osecac2024"

# 2. CARGA DE DATOS
@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# URLs de tus planillas
URL_AGENDAS = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS)
df_tramites = cargar_datos(URL_TRAMITES)

# --- LÓGICA DEL CHAT (Temporal en memoria hasta que conectes la 3ra hoja) ---
if 'chat_historial' not in st.session_state:
    st.session_state.chat_historial = [
        {"usuario": "Jefe de Agencia", "mensaje": "Bienvenidos al portal oficial. Instalalo en tu pantalla de inicio.", "fecha": "20/05 09:00"}
    ]

# 3. CSS: ADAPTACIÓN TOTAL PARA CELULAR
st.markdown("""
    <style>
    /* Fondo y animaciones */
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        color: #e2e8f0; 
    }
    
    .block-container { padding-top: 1rem !important; }

    /* Cartel Adaptativo */
    .header-master { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .capsula-header-mini {
        padding: 10px 25px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 30px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        margin-bottom: 10px;
    }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; }
    
    @media (max-width: 600px) {
        .titulo-mini { font-size: 1.1rem !important; }
        .logo-fijo { width: 70px !important; }
    }

    /* Estilo de los Mensajes del Jefe */
    .chat-box {
        background: rgba(56, 189, 248, 0.1);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 5px solid #38bdf8;
    }
    .msg-texto { font-size: 15px; color: #f1f5f9; margin-top: 4px; }
    .msg-fecha { font-size: 10px; color: #64748b; text-align: right; }

    /* Logo */
    .logo-container { display: flex; justify-content: center; margin: 15px 0; }
    .logo-fijo { width: 85px; height: auto; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown("""
    <div class="header-master">
        <div class="capsula-header-mini">
            <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
        </div>
        <div style="color: #94a3b8; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;">
            Portal de Apoyo para Compañeros
        </div>
    </div>
    """, unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{img_b64}" class="logo-fijo"></div>', unsafe_allow_html=True)
except:
    st.write("")

st.markdown("---")

# === SECCIÓN: NOVEDADES DEL JEFE ===
with st.expander("📢 **NOVEDADES Y COMUNICADOS**", expanded=True):
    
    # Botón oculto para el jefe
    with st.popover("🔑 Publicar como Jefe"):
        pw = st.text_input("Contraseña:", type="password")
        if pw == PASSWORD_JEFE:
            with st.form("form_chat", clear_on_submit=True):
                txt = st.text_area("Mensaje para el equipo:")
                if st.form_submit_button("Enviar Comunicado"):
                    fecha_msg = datetime.now().strftime("%d/%m %H:%M")
                    st.session_state.chat_historial.insert(0, {"usuario": "Jefe", "mensaje": txt, "fecha": fecha_msg})
                    st.success("Mensaje publicado")
                    st.rerun()
        elif pw != "":
            st.error("Acceso denegado")

    # Mostrar mensajes
    for m in st.session_state.chat_historial:
        st.markdown(f"""
        <div class="chat-box">
            <div style="color:#38bdf8; font-size:11px; font-weight:bold;">COMUNICADO OFICIAL</div>
            <div class="msg-texto">{m['mensaje']}</div>
            <div class="msg-fecha">{m['fecha']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# === BUSCADORES (EL RESTO DEL CÓDIGO) ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    # ... (Tu lógica de búsqueda de trámites aquí)
    busqueda_t = st.text_input("Buscá trámites...", key="t")
    if busqueda_t and not df_tramites.empty:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False)]
        for i, row in res_t.iterrows():
            st.info(f"📋 {row['TRAMITE']}\n\n{row['DESCRIPCIÓN Y REQUISITOS']}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    # ... (Tu lógica de búsqueda de agendas aquí)
    busqueda_a = st.text_input("Buscá contactos...", key="a")
    if busqueda_a and not df_agendas.empty:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.success(f"👤 {row.iloc[0]}")
st.markdown('</div>', unsafe_allow_html=True)
