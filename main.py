import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: FONDO OSCURO Y AZUL LOGO (#00529b es el azul de OSECAC)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    .block-container { max-width: 850px !important; padding-top: 1rem !important; }

    /* Efecto para disimular el fondo blanco del logo */
    [data-testid="stImage"] img {
        mix-blend-mode: screen; /* Esto hace que el blanco se vuelva transparente en fondo oscuro */
        object-fit: contain;
    }

    /* ESTILO BASE BOTONES */
    div.stLinkButton > a {
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 10px 15px !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }

    /* --- NOMENCLADORES (Azul OSECAC del Logo) --- */
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] {
        color: #38bdf8 !important; /* Celeste brillante para que se lea bien */
        border: 1px solid #00529b !important; /* Azul del logo */
        background-color: rgba(0, 82, 155, 0.2) !important;
    }

    /* --- PEDIDOS (Tus colores hermosos originales) --- */
    /* Rosa para Leches */
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"] { 
        color: #ff85a2 !important;
        border: 1px solid #ff85a2 !important;
        background-color: rgba(255, 133, 162, 0.1) !important;
    }
    /* Verde para Suministros */
    div.stLinkButton > a[href*="MlwRSUf6dAww"] { 
        color: #2dd4bf !important;
        border: 1px solid #2dd4bf !important;
        background-color: rgba(45, 212, 191, 0.1) !important;
    }
    /* Violeta para Estado */
    div.stLinkButton > a[href*="21d6f3bf-24c1"] { 
        color: #a78bfa !important;
        border: 1px solid #a78bfa !important;
        background-color: rgba(167, 139, 250, 0.1) !important;
    }

    div.stLinkButton > a:hover { transform: scale(1.02); filter: brightness(1.2); }

    .stExpander {
        background-color: rgba(23, 32, 48, 0.8) !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
    }
    .stTextInput > div > div > input { background-color: #172030 !important; color: white !important; }
    
    /* Título en el azul del logo */
    h1 { font-weight: 900; text-align: left; color: #00529b; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA: LOGO IZQUIERDA Y TÍTULO ===
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
    try:
        st.image("LOGO.jpg", width=120)
    except:
        st.write(" ")

with col_titulo:
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("OSECAC MDQ / AGENCIAS")

st.markdown("---")

# ==========================================
# MENÚS (Nomencladores y Pedidos)
# ==========================================
with st.expander("NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("PEDIDOS"):
    col_l, col_s, col_e = st.columns(3)
    with col_l: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    with col_s: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    with col_e: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BUSCADOR AGENDAS/MAILS (PLANILLA NUEVA)
# ==========================================
@st.cache_data
def cargar_datos():
    try:
        url_unica = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        df = pd.read_csv(url_unica)
        return df
    except:
        return pd.DataFrame()

df = cargar_datos()

st.subheader("AGENDAS/MAILS")
col_busc, col_borrar = st.columns([5, 1])
with col_busc:
    pregunta = st.text_input("Buscador", placeholder="Buscar...", label_visibility="collapsed", key="input_busqueda")
with col_borrar:
    if st.button("LIMPIAR"):
        st.rerun()

if pregunta:
    pregunta = pregunta.strip()
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]
    if not resultados.empty:
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("SIN COINCIDENCIAS")
