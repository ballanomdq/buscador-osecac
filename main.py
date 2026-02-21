import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# CSS para un estilo moderno, limpio y profesional
st.markdown("""
    <style>
    /* Fondo general más suave */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Personalización del contenedor colapsable */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #d1d9e6 !important;
        font-weight: bold !important;
        color: #1e3a5a !important;
    }

    /* Estilo minimalista para los botones */
    div.stLinkButton > a {
        background-color: #ffffff !important;
        color: #1e3a5a !important;
        border: 1px solid #cbd5e0 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: block !important;
        text-align: center !important;
        font-size: 14px !important;
    }
    
    div.stLinkButton > a:hover {
        background-color: #e2e8f0 !important;
        border-color: #4a90e2 !important;
        color: #4a90e2 !important;
        transform: scale(1.02);
    }

    /* Títulos limpios */
    h1 {
        color: #1e3a5a !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }

    /* Input de búsqueda moderno */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 1px solid #cbd5e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔎 OSECAC MDQ / AGENCIAS")

# =========================
# MENÚ DESPLEGABLE (MODERNO)
# =========================
with st.expander("🚀 ACCESOS DIRECTOS Y HERRAMIENTAS"):
    st.write("Seleccioná la herramienta que necesites utilizar:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.link_button("🤖 Nomenclador IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
        st.link_button("📊 Nomenclador FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)
    
    with col2:
        st.link_button("🏥 Nomenclador OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)
        st.link_button("📈 Estado de Pedidos", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)
    
    with col3:
        st.link_button("📦 Útiles / Tóner", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
        st.link_button("🍼 Pedido Leches", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)

st.markdown("---")

# =========================
# CARGA DE DATOS (AGENDA)
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
# BUSCADOR PRINCIPAL
# =========================
st.subheader("📞 Buscador de Agenda y Contactos")
pregunta = st.text_input("Ingresá nombre, interno, dirección o mail...", placeholder="Ej: Miramar, Juan Pérez, Auditoría...")

if pregunta and not df.empty:
    pregunta = pregunta.strip()
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]

    if not resultados.empty:
        st.success(f"Se encontraron {len(resultados)} coincidencia(s):")
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("No se encontraron resultados.")

if df.empty:
    st.warning("⚠️ Error de conexión con las planillas de Google.")
