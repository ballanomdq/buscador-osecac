import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP", layout="wide")

# 2. CSS: DISEÑO OSCURO Y POSICIONAMIENTO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    .block-container { max-width: 1200px !important; padding-top: 1.5rem !important; }

    /* Estilo del Logo centrado */
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        mix-blend-mode: screen;
        filter: brightness(1.1);
    }

    /* ESTILO BOTONES */
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

    /* COLORES BOTONES */
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] {
        color: #38bdf8 !important; border: 1px solid #00529b !important; background-color: rgba(0, 82, 155, 0.2) !important;
    }
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"] { color: #ff85a2 !important; border: 1px solid #ff85a2 !important; background-color: rgba(255, 133, 162, 0.1) !important; }
    div.stLinkButton > a[href*="MlwRSUf6dAww"] { color: #2dd4bf !important; border: 1px solid #2dd4bf !important; background-color: rgba(45, 212, 191, 0.1) !important; }
    div.stLinkButton > a[href*="21d6f3bf-24c1"] { color: #a78bfa !important; border: 1px solid #a78bfa !important; background-color: rgba(167, 139, 250, 0.1) !important; }

    .stExpander { background-color: rgba(23, 32, 48, 0.8) !important; border: 1px solid #1e293b !important; border-radius: 10px !important; }
    
    /* Buscador */
    .stTextInput > div > div > input { background-color: #172030 !important; color: white !important; height: 45px !important; }

    h1 { font-weight: 900; color: #e2e8f0; text-align: center; margin-bottom: 0px; padding-bottom: 0px; font-size: 2.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.title("OSECAC MDP / AGENCIAS")

# LOGO DEBAJO DEL TÍTULO
col_espacio1, col_logo, col_espacio2 = st.columns([2, 1, 2])
with col_logo:
    try:
        st.image("LOGO.jpg", width=90) # Tamaño bien discreto
    except:
        pass

st.markdown("---")

# ==========================================
# MENÚS (NOMENCLADORES Y PEDIDOS)
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
# BUSCADOR AGENDAS (BÚSQUEDA EN VIVO + COPIAR)
# ==========================================
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        url_unica = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        df = pd.read_csv(url_unica)
        return df
    except: return pd.DataFrame()

df = cargar_datos()

st.subheader("AGENDAS/MAILS")
pregunta = st.text_input("Buscador", placeholder="Escribí para buscar...", label_visibility="collapsed")

if pregunta:
    pregunta = pregunta.strip()
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]
    
    if not resultados.empty:
        # Usamos data_editor para permitir copiar con un clic
        st.data_editor(
            resultados,
            use_container_width=True,
            hide_index=True,
            disabled=True # Evita que borren datos, solo lectura/copia
        )
    else:
        st.info("No se encontraron coincidencias.")
else:
    st.write("Escribí arriba para filtrar los datos.")
