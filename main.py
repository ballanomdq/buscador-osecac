import streamlit as st
import pandas as pd
from google import genai

# CONFIGURACIÓN (Asegurate que esta clave sea la que creaste en AI Studio)
CLAVE_DIRECTA = "AIzaSyDRxaZXnAdEDt-C-AZvjqa004dwII8KesQ"

# Inicializamos el cliente
client = genai.Client(api_key=CLAVE_DIRECTA)

st.set_page_config(page_title="Buscador OSECAC Miramar", layout="centered")
st.title("🤖 Buscador OSECAC Miramar")

@st.cache_data
def cargar_datos():
    try:
        url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
        return pd.read_csv(url_osecac), pd.read_csv(url_faba)
    except:
        return pd.DataFrame(), pd.DataFrame()

df1, df2 = cargar_datos()
pregunta = st.text_input("¿Qué dato buscás hoy?")

if pregunta:
    with st.spinner("Consultando a Gemini 1.5..."):
        try:
            # Formateamos el contexto para la IA
            contexto = f"Datos OSECAC:\n{df1.head(20).to_string()}\n\nDatos FABA:\n{df2.head(20).to_string()}"
            
            # CAMBIO CLAVE: Usamos el nombre técnico completo del modelo
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=f"Sos un asistente experto en trámites de OSECAC. Basándote en estos datos:\n{contexto}\n\nResponde a esta pregunta: {pregunta}"
            )
            
            st.success("Respuesta:")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Si el error persiste, es probable que la API Key necesite permisos de 'Generative Language API' en Google Cloud.")
