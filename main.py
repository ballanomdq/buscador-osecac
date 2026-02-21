import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# 2. DISEÑO MODERNO (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 2rem !important; }
    
    /* Estilo de Menús */
    .stExpander {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }

    /* Botones */
    div.stLinkButton > a {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        text-align: center !important;
        display: block !important;
        transition: 0.3s;
    }
    div.stLinkButton > a:hover { border-color: #38bdf8; transform: scale(1.02); }

    /* Input Buscador */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    h1 { text-align: center; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# MENÚS DESPLEGABLES
# ==========================================
with st.expander("📖 NOMENCLADORES"):
    col1, col2, col3 = st.columns(3)
    with col1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
    with col2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)
    with col3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)

with st.expander("📦 PEDIDOS"):
    col4, col5, col6 = st.columns(3)
    with col4: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)
    with col5: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
    with col6: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)

st.markdown("---")

# ==========================================
# BUSCADOR DE AGENDA (EL CORAZÓN DE LA APP)
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
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

df = cargar_datos()

st.subheader("📞 Búsqueda de Agenda y Contactos")
pregunta = st.text_input("", placeholder="Buscá por nombre, interno, ciudad o sector...")

if pregunta:
    pregunta = pregunta.strip()
    # Esta línea hace la magia de buscar en toda la tabla
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]

    if not resultados.empty:
        st.success(f"Se encontraron {len(resultados)} resultados")
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("No hay coincidencias para esa búsqueda.")

# Mostrar aviso si las planillas no cargan
if df.empty:
    st.error("⚠️ No se pudieron cargar las bases de datos desde Google Sheets.")
