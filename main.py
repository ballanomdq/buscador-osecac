import streamlit as st
import pandas as pd
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# Función para convertir el logo en marca de agua (fondo)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    bin_str = get_base64("LOGO1.png")
    marca_agua = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 300px; /* Ajusta el tamaño de la marca de agua */
        opacity: 0.05; /* La hace muy sutil para que no moleste */
    }}
    </style>
    """
except:
    marca_agua = ""

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

# 3. CSS: CARTEL, FRASE Y MARCA DE AGUA
st.markdown(f"""
    <style>
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    @keyframes shine {{
        0% {{ left: -100%; opacity: 0; }}
        50% {{ opacity: 0.8; }}
        100% {{ left: 100%; opacity: 0; }}
    }}

    .stApp {{ 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }}
    
    {marca_agua}

    .block-container {{ max-width: 1000px !important; padding-top: 2rem !important; }}

    .cabecera-unificada {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin-top: 20px;
    }}

    .capsula-header-mini {{
        position: relative;
        padding: 10px 40px;
        background: rgba(56, 189, 248, 0.08);
        border-radius: 35px;
        border: 1px solid rgba(56, 189, 248, 0.6);
        overflow: hidden;
        margin-bottom: 10px; /* Espacio para que la frase venga a continuación */
    }}

    .titulo-mini {{
        font-family: 'sans-serif';
        font-weight: 800;
        font-size: 1.5rem;
        color: #ffffff;
        margin: 0;
        z-index: 2;
        position: relative;
    }}

    .shimmer-efecto {{
        position: absolute;
        top: 0;
        width: 100px;
        height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent);
        transform: skewX(-20deg);
        animation: shine 4s infinite linear;
        z-index: 1;
    }}

    .subtitulo-lema {{
        color: #94a3b8;
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
        font-weight: 500;
    }}

    /* Estilos de botones y buscadores originales */
    .stExpander {{ background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; }}
    .buscador-gestion {{ border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }}
    .buscador-agenda {{ border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# === CABECERA: CARTEL -> FRASE ===
st.markdown("""
    <div class="cabecera-unificada">
        <div class="capsula-header-mini">
            <div class="shimmer-efecto"></div>
            <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
        </div>
        <div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# RESTO DEL CÓDIGO (BOTONES Y BUSCADORES)
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")

st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**"):
    st.text_input("Buscá trámites...", key="t")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**"):
    st.text_input("Buscá contactos...", key="a")
st.markdown('</div>', unsafe_allow_html=True)
