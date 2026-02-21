import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: ESTILO PREMIUM SIN ICONOS (CHAU OCHENTAS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #f8fafc;
    }

    .block-container { max-width: 900px !important; }

    /* Menús Desplegables Minimalistas */
    .stExpander {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }

    /* BOTONES MODERNOS: Cortos, sin iconos, fuente limpia */
    div.stLinkButton > a {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 8px 15px !important;
        width: auto !important;
        display: inline-block !important;
        transition: all 0.2s ease !important;
    }
    
    div.stLinkButton > a:hover {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        border-color: #38bdf8 !important;
    }

    /* Buscador Serio */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        color: white !important;
    }
    
    h1 { font-weight: 700; letter-spacing: -2px; text-align: center; }
    h3 { font-size: 14px !important; color: #94a3b8 !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# MENÚS (Sin iconos, texto limpio)
# ==========================================
with st.expander("NOMENCLADORES"):
    # Usamos 3 columnas para que los botones queden cortitos uno al lado del otro
    c1, c2, c3 = st.columns(3)
    c1.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    c2.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    c3.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("PEDIDOS"):
    c4, c5, c6 = st.columns(3)
    c4.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    c5.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    c6.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN AGENDAS/MAILS
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
