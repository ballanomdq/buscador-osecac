import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="OSECAC MDQ / AGENCIAS", layout="wide")

# CSS para Diseño Ultra Moderno y Serio
st.markdown("""
    <style>
    /* Fondo Profundo Moderno */
    .stApp {
        background-color: #0e1117;
        color: #f8fafc;
    }

    /* Contenedor del menú desplegable estilizado */
    .stExpander {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 20px !important;
    }

    /* Botones Estilo Minimalista Pro */
    div.stLinkButton > a {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-decoration: none !important;
        display: block !important;
        text-align: center !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    
    /* Efecto Hover Tecnológico */
    div.stLinkButton > a:hover {
        background-color: #334155 !important;
        color: #38bdf8 !important; /* Azul eléctrico */
        border-color: #38bdf8 !important;
        box-shadow: 0px 0px 20px rgba(56, 189, 248, 0.2) !important;
        transform: translateY(-2px) !important;
    }

    /* Buscador Minimalista */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* Títulos */
    h1 {
        font-weight: 800 !important;
        color: #f8fafc !important;
        letter-spacing: -1px !important;
    }
    
    h3 {
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }

    /* Línea divisoria sutil */
    hr {
        border-top: 1px solid #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("OSECAC MDQ / AGENCIAS")

# ==========================================
# MENÚ DESPLEGABLE TÉCNICO
# ==========================================
with st.expander("SISTEMAS Y HERRAMIENTAS EXTERNAS"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
        st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)
    
    with col2:
        st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)
        st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)
    
    with col3:
        st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
        st.link_button("PROGRAMA LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)

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

if df.empty:
    st.error("ERROR: NO SE PUDO SINCRONIZAR CON LAS BASES DE DATOS")
