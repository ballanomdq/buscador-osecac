import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: COLORES DIFERENCIADOS POR CAJA
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    .block-container { max-width: 850px !important; }

    /* ESTILO BASE PARA TODOS LOS BOTONES */
    div.stLinkButton > a {
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 10px 15px !important;
        display: inline-block !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* --- BOTONES DE ARRIBA (NOMENCLADORES): SE QUEDAN EN AZUL/CELESTE --- */
    .nomen-container div.stLinkButton > a {
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        background-color: #172030 !important;
    }
    .nomen-container div.stLinkButton > a:hover {
        background-color: #38bdf8 !important;
        color: #0b0e14 !important;
    }

    /* --- BOTONES DE ABAJO (PEDIDOS): TUS COLORES HERMOSOS --- */
    /* 1. Rosa para Leches */
    .pink-btn div.stLinkButton > a {
        color: #ff85a2 !important;
        border: 1px solid #ff85a2 !important;
        background-color: rgba(255, 133, 162, 0.1) !important;
    }
    .pink-btn div.stLinkButton > a:hover {
        background-color: #ff85a2 !important;
        color: #0b0e14 !important;
    }

    /* 2. Verde para Suministros */
    .green-btn div.stLinkButton > a {
        color: #2dd4bf !important;
        border: 1px solid #2dd4bf !important;
        background-color: rgba(45, 212, 191, 0.1) !important;
    }
    .green-btn div.stLinkButton > a:hover {
        background-color: #2dd4bf !important;
        color: #0b0e14 !important;
    }

    /* 3. Violeta para Estado */
    .purple-btn div.stLinkButton > a {
        color: #a78bfa !important;
        border: 1px solid #a78bfa !important;
        background-color: rgba(167, 139, 250, 0.1) !important;
    }
    .purple-btn div.stLinkButton > a:hover {
        background-color: #a78bfa !important;
        color: #0b0e14 !important;
    }

    .stExpander {
        background-color: rgba(23, 32, 48, 0.8) !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
    }
    .stTextInput > div > div > input { background-color: #172030 !important; color: white !important; }
    h1 { font-weight: 900; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# NOMENCLADORES (Caja de arriba)
# ==========================================
with st.expander("NOMENCLADORES"):
    # Envolvemos en un div para fijar el color azul
    st.markdown('<div class="nomen-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PEDIDOS (Caja de abajo con colores hermosos)
# ==========================================
with st.expander("PEDIDOS"):
    col_l, col_s, col_e = st.columns(3)
    with col_l: 
        st.markdown('<div class="pink-btn">', unsafe_allow_html=True)
        st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_s: 
        st.markdown('<div class="green-btn">', unsafe_allow_html=True)
        st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_e: 
        st.markdown('<div class="purple-btn">', unsafe_allow_html=True)
        st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# AGENDAS/MAILS (Lógica intacta)
# ==========================================
@st.cache_data
def cargar_datos():
    try:
        url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
        df1 = pd.read_csv(url_osecac)
        df1["Origen"] = "OSECAC"
        df2 = pd.read_csv(url_faba)
        df2["Origen"] = "FABA"
        return pd.concat([df1, df2], ignore_index=True)
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
        
