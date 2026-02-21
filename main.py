import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: ESTILO MODERNO Y COLORES ARMÓNICOS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    .block-container { max-width: 850px !important; }

    /* Botones Base */
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

    /* COLORES ESPECÍFICOS PEDIDOS */
    /* Leches: Rosa */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stLinkButton > a {
        color: #ff85a2 !important;
        border: 1px solid #ff85a2 !important;
        background-color: rgba(255, 133, 162, 0.1) !important;
    }
    /* Suministros: Verde */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stLinkButton > a {
        color: #2dd4bf !important;
        border: 1px solid #2dd4bf !important;
        background-color: rgba(45, 212, 191, 0.1) !important;
    }
    /* Estado: Violeta */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div.stLinkButton > a {
        color: #a78bfa !important;
        border: 1px solid #a78bfa !important;
        background-color: rgba(167, 139, 250, 0.1) !important;
    }

    .stExpander {
        background-color: rgba(23, 32, 48, 0.8) !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
    }

    .stTextInput > div > div > input {
        background-color: #172030 !important;
        border: 1px solid #334155 !important;
        color: white !important;
    }

    h1 { font-weight: 900; text-align: center; }
    h3 { font-size: 0.9rem !important; color: #64748b !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# NOMENCLADORES
# ==========================================
with st.expander("NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

# ==========================================
# PEDIDOS (Rosa, Verde, Violeta)
# ==========================================
with st.expander("PEDIDOS"):
    col_l, col_s, col_e = st.columns(3)
    with col_l: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    with col_s: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    with col_e: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# AGENDAS/MAILS (CON CARGA CORREGIDA)
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
        # AQUÍ ESTABA EL ERROR: Cerramos bien el paréntesis ahora
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
