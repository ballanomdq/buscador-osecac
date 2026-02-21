import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN
CLAVE_DIRECTA = "AIzaSyDRxaZXnAdEDt-C-AZvjqa004dwII8KesQ"
genai.configure(api_key=CLAVE_DIRECTA)

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
    with st.spinner("Buscando..."):
        try:
            # ESTA ES LA SOLUCIÓN AL ERROR 404:
            # Usamos el nombre del modelo tal cual lo pide la versión estable
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            contexto = f"Datos: {df1.head(10).to_string()}"
            # Forzamos la llamada sin usar v1beta internamente
            res = model.generate_content(f"{contexto}\n\nPregunta: {pregunta}")
            
            st.success("Respuesta:")
            st.write(res.text)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Si el error persiste, probá reiniciar la app desde el menú 'Manage App'.")
