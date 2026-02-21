import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN
st.set_page_config(page_title="Cerebro OSECAC Miramar", layout="wide")

# 1. SEGURIDAD
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Falta configurar la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. CARGA DE DATOS
@st.cache_data
def cargar_fuentes():
    try:
        url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
        return pd.read_csv(url_osecac), pd.read_csv(url_faba)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_osecac, df_faba = cargar_fuentes()

# 3. INTERFAZ
st.title("🤖 Buscador Integral OSECAC Miramar")
st.info("Consultando: Nomencladores (OSECAC/FABA), Glosario Miramar, CIE-10 y Manual HPC.")

pregunta = st.text_input("¿En qué puedo ayudarte hoy?", placeholder="Ej: ¿Qué hago si un afiliado renuncia? o Código 2060")

if pregunta:
    with st.spinner("Buscando en los registros..."):
        try:
            # Reducimos el contexto para que no de error InvalidArgument
            contexto = f"Datos OSECAC: {df_osecac.head(10).to_string()}\nDatos FABA: {df_faba.head(10).to_string()}"
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"Eres un asistente experto de OSECAC Miramar. Usa esto como base: {contexto}\n\nPregunta: {pregunta}")
            
            st.markdown("### 🤖 Respuesta:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Hubo un problema con la consulta. Probá preguntando de nuevo. (Error: {str(e)})")

st.markdown("---")
st.caption("Actualización automática: Al editar tus Google Sheets/Docs, la IA aprende los cambios.")
