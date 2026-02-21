import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDQ", layout="wide")

# 2. CSS: AZULES PROFUNDOS + ESTILO TECNOLÓGICO
st.markdown("""
    <style>
    /* Fondo Azul Noche Profundo */
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }

    /* Contenedor central */
    .block-container { max-width: 850px !important; }

    /* Menús Desplegables (Efecto Cristal) */
    .stExpander {
        background-color: rgba(23, 32, 48, 0.8) !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }

    /* BOTONES: Cortos, modernos y con brillo azul al pasar el mouse */
    div.stLinkButton > a {
        background-color: #172030 !important;
        color: #38bdf8 !important; /* El celeste que te gustaba */
        border: 1px solid #334155 !important;
        border-radius: 4px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 10px 15px !important;
        display: inline-block !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-decoration: none !important;
    }
    
    div.stLinkButton > a:hover {
        background-color: #38bdf8 !important;
        color: #0b0e14 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0px 0px 12px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Buscador Minimalista */
    .stTextInput > div > div > input {
        background-color: #172030 !important;
        border: 1px solid #334155 !important;
        border-radius: 4px !important;
        color: white !important;
        height: 45px;
    }

    /* Títulos */
    h1 { 
        font-size: 2.2rem !important;
        font-weight: 900 !important; 
        color: #f8fafc; 
        text-align: center;
        letter-spacing: -1px;
    }
    
    h3 { 
        font-size: 0.9rem !important; 
        font-weight: 800 !important;
        color: #64748b !important; 
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# MENÚS (Sin iconos, estilo sobrio)
# ==========================================
with st.expander("NOMENCLADORES"):
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
# AGENDAS/MAILS
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
    pregunta = st.text_input("Buscador", placeholder="Buscar en la base de datos...", label_visibility="collapsed", key="input_busqueda")
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
