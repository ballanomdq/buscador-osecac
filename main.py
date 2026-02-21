import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Portal OSECAC Miramar", layout="wide")

st.title("🔎 Portal Interno OSECAC Miramar")
st.markdown("---")

# ==========================================
# SECCIÓN DE BOTONES DE ACCESO RÁPIDO
# ==========================================
st.subheader("🚀 Accesos Directos")

# Primera fila de botones
col1, col2, col3 = st.columns(3)

with col1:
    st.link_button("🤖 Buscador Nomenclador con IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc", use_container_width=True)
    st.link_button("📊 Nomenclador FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF", use_container_width=True)

with col2:
    st.link_button("🏥 Nomenclador OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF", use_container_width=True)
    st.link_button("📈 Estado de Pedidos", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true", use_container_width=True)

with col3:
    st.link_button("📝 Pedido Útiles, Resmas y Tóner", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform", use_container_width=True)
    st.link_button("🍼 Pedido de Leches", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform", use_container_width=True)

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
    except Exception as e:
        st.error(f"Error cargando planillas: {e}")
        return pd.DataFrame()

df = cargar_datos()

# =========================
# BUSCADOR INTERNO
# =========================
st.subheader("📞 Buscador de Agenda y Contactos")
pregunta = st.text_input("Ingresá nombre, teléfono o dato a buscar:")

if pregunta and not df.empty:
    pregunta = pregunta.strip()
    # Filtro inteligente en todas las columnas
    resultados = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]

    if not resultados.empty:
        st.success(f"Se encontraron {len(resultados)} coincidencia(s):")
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("No se encontraron resultados para esa búsqueda.")

if df.empty:
    st.warning("Aviso: No se pudo conectar con las planillas de Google.")
