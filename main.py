import streamlit as st
import pandas as pd
import google.generativeai as genai

# Conexión con los Secrets de Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ No se encontró la clave en Secrets.")
    st.stop()

st.title("🤖 Buscador OSECAC Miramar")

# Carga de planillas
@st.cache_data
def cargar_datos():
    url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
    url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
    return pd.read_csv(url_osecac), pd.read_csv(url_faba)

df1, df2 = cargar_datos()

pregunta = st.text_input("¿Qué buscamos?")

if pregunta:
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Le pasamos un resumen de las planillas como contexto
    contexto = f"Datos: {df1.head(10).to_string()} {df2.head(10).to_string()}"
    res = model.generate_content(f"{contexto}\n\nPregunta: {pregunta}")
    st.write(res.text)
