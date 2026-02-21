import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Buscador OSECAC Miramar", layout="wide")

# 1. CONEXIÓN CON LA LLAVE (SECRET)
try:
    # Usamos st.secrets que es la forma correcta en Streamlit Cloud
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Error con la API KEY. Revisá los Secrets en Streamlit.")
    st.stop()

# 2. CARGA DE DATOS DESDE GOOGLE SHEETS
@st.cache_data
def cargar_datos():
    # Nomenclador OSECAC
    url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
    # Nomenclador FABA
    url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
    
    df1 = pd.read_csv(url_osecac)
    df2 = pd.read_csv(url_faba)
    return df1, df2

df_osecac, df_faba = cargar_datos()

# 3. INTERFAZ DE USUARIO
st.title("🤖 Buscador Integral OSECAC Miramar")
st.markdown("---")

pregunta = st.text_input("¿Qué información buscás hoy?", placeholder="Ej: Precio código 2060 o datos de FABA")

if pregunta:
    with st.spinner("Pensando..."):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            # Limitamos los datos que le enviamos para que no se sature
            contexto = f"OSECAC: {df_osecac.head(20).to_string()}\nFABA: {df_faba.head(20).to_string()}"
            
            prompt = f"Sos un asistente de la oficina de OSECAC Miramar. Basándote en estos datos:\n{contexto}\n\nPregunta del usuario: {pregunta}"
            
            response = model.generate_content(prompt)
            st.success("Respuesta:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error al generar respuesta: {e}")

st.sidebar.write("✅ Conectado a Gemini 1.5 Flash")
