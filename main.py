import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN DIRECTA
CLAVE_DIRECTA = "AIzaSyDRxaZXnAdEDt-C-AZvjqa004dwII8KesQ"

# Forzamos la configuración para evitar el error 404
genai.configure(api_key=CLAVE_DIRECTA)

st.set_page_config(page_title="Buscador OSECAC Miramar", layout="centered")
st.title("🤖 Buscador OSECAC Miramar")

@st.cache_data
def cargar_datos():
    try:
        url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
        return pd.read_csv(url_osecac), pd.read_csv(url_faba)
    except Exception as e:
        st.error(f"Error cargando planillas: {e}")
        return pd.DataFrame(), pd.DataFrame()

df1, df2 = cargar_datos()

pregunta = st.text_input("¿Qué dato buscás hoy?")

if pregunta:
    with st.spinner("Buscando..."):
        try:
            # CAMBIO CLAVE: Usamos el nombre del modelo sin el prefijo 'models/'
            # y dejamos que la librería elija la versión de API correcta (v1)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            contexto = f"Datos OSECAC: {df1.head(10).to_string()}\nDatos FABA: {df2.head(10).to_string()}"
            res = model.generate_content(f"{contexto}\n\nPregunta: {pregunta}")
            
            st.success("Respuesta:")
            st.write(res.text)
        except Exception as e:
            # Si vuelve a fallar, mostramos un mensaje más claro
            st.error(f"Hubo un problema con la conexión a la IA: {e}")
