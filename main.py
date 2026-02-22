import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

# 3. CSS PERMANENTE CON BRILLO NEÓN INTENSO
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Brillo Neón Celeste Intenso */
    @keyframes neonShine {
        0% { left: -150%; opacity: 0; }
        50% { opacity: 1; }
        100% { left: 150%; opacity: 0; }
    }

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    .block-container { max-width: 1000px !important; padding-top: 3rem !important; }

    /* Contenedor Flex para alinear Cartel + Logo a la derecha */
    .header-flex {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 10px;
    }

    /* Cápsula OSECAC con Brillo Neón */
    .capsula-neon {
        position: relative;
        padding: 12px 35px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 35px;
        border: 2px solid #38bdf8;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }

    .titulo-neon {
        font-family: 'sans-serif';
        font-weight: 900;
        font-size: 1.6rem;
        color: #ffffff;
        text-shadow: 0 0 10px #38bdf8;
        margin: 0;
        z-index: 2;
        position: relative;
    }

    /* Logo1 a la derecha con el mismo efecto */
    .logo-derecha {
        position: relative;
        overflow: hidden;
        border-radius: 10px;
        display: flex;
        align-items: center;
    }

    /* El rayo de luz neón */
    .shimmer-neon {
        position: absolute;
        top: 0;
        width: 120px;
        height: 100%;
        background: linear-gradient(to right, transparent, #38bdf8, #ffffff, #38bdf8, transparent);
        transform: skewX(-30deg);
        animation: neonShine 4s infinite linear;
        z-index: 1;
        filter: blur(5px);
    }

    .subtitulo-lema {
        color: #94a3b8;
        font-size: 13px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 15px;
        text-align: center;
    }

    /* Estilos de Fichas (Mantenidos) */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }

    div.stLinkButton > a {
        border-radius: 8px !important; font-weight: 700 !important;
        text-transform: uppercase !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA: CARTEL + LOGO A LA DERECHA CON BRILLO ===
st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <div class="header-flex">
            <div class="capsula-neon">
                <div class="shimmer-neon"></div>
                <h1 class="titulo-neon">OSECAC MDP / AGENCIAS</h1>
            </div>
            <div class="logo-derecha">
                <div class="shimmer-neon" style="animation-delay: 0.5s;"></div>
    """, unsafe_allow_html=True)

# Insertamos la imagen con Streamlit dentro del div anterior
col_logo = st.columns([1, 0.2, 1])[1] # Pequeño truco para posicionar si el CSS falla
try:
    st.image("LOGO1.png", width=80)
except:
    st.markdown('<p style="color:#38bdf8; font-size:30px; margin:0;">★</p>', unsafe_allow_html=True)

st.markdown("""
            </div>
        </div>
        <div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECCIONES (Orden solicitado)
# ==========================================

# 1. NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

# 2. PEDIDOS
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    with c2: st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with c3: st.link_button("🧪 PORTAL MEDICAMENTOS", "http://servicios-externos.osecac.org.ar/SolicitudTramitesMpp/tramites")

st.markdown("<br>", unsafe_allow_html=True)

# 4. GESTIONES / DATOS
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_tramites")
    if busqueda_t:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False) | df_tramites['PALABRA CLAVE'].str.lower().str.contains(t, na=False)]
        if not res_t.empty:
            for i, row in res_t.iterrows():
                st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 5. AGENDAS / MAILS
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá un contacto...", key="search_agendas")
    if busqueda_a:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        if not res_a.empty:
            for i, row in res_a.iterrows():
                st.markdown(f'<div class="ficha ficha-agenda">👤 {row.iloc[0]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
