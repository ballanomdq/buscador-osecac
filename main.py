import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# Estilo sutil para mantener el modo oscuro pero asegurar clics
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f8fafc;
    }
    .stExpander {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    h1 { font-weight: 800; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# MENÚ DESPLEGABLE REAGRUPADO
# ==========================================
with st.expander("MENU"):
    
    st.markdown("### 🔍 Nomencladores")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
    with col2:
        st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)
    with col3:
        st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📦 Gestión de Pedidos")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)
    with col5:
        st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
    with col6:
        st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
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

# =========================
# BUSCADOR
# =========================
st.subheader("BÚSQUEDA DE AGENDA Y CONTACTOS")
pregunta = st.text_input("", placeholder="Escriba aquí para buscar...")

if pregunta and not df.empty:
    pregunta = pregunta.strip()
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]

    if not resultados.empty:
        st.success(f"REGISTROS ENCONTRADOS: {len(resultados)}")
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("SIN RESULTADOS")
