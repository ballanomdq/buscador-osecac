import streamlit as st
import pandas as pd
from google import genai

# CONFIGURACIÓN NUEVA (API v1 Estable)
CLAVE_DIRECTA = "AIzaSyDRxaZXnAdEDt-C-AZvjqa004dwII8KesQ"
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
    with st.spinner("Buscando con IA estable..."):
        try:
            contexto = f"Datos OSECAC: {df1.head(10).to_string()}\nDatos FABA: {df2.head(10).to_string()}"
            
            # NUEVA FORMA DE LLAMAR A GEMINI
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"{contexto}\n\nPregunta: {pregunta}"
            )
            
            st.success("Respuesta:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error técnico: {e}")
