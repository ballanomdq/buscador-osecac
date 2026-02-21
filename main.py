import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. LLAVE DE SEGURIDAD
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave en Secrets")
    st.stop()

st.title("🤖 Buscador Exclusivo OSECAC Miramar")
st.write("Consultando únicamente tus archivos de Google Sheets y Documentos.")

# 2. CARGA DE TUS ARCHIVOS (Sheets y Docs)
@st.cache_data
def cargar_datos_propios():
    try:
        # Aquí cargamos tu planilla de OSECAC/FABA
        url_hoja = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        # Aquí podrías poner el link de exportación de tu Google Doc si lo tenés como CSV o texto
        df = pd.read_csv(url_hoja)
        return df
    except:
        return pd.DataFrame()

df_propio = cargar_datos_propios()

# 3. INTERFAZ DE BÚSQUEDA
pregunta = st.text_input("¿Qué dato de tus archivos necesitás buscar?")

if pregunta:
    with st.spinner("Buscando en tus documentos personales..."):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Le pasamos solo las filas más importantes para que no se sature
            contexto = df_propio.head(100).to_string() 
            
            prompt = f"Sos el asistente privado de la oficina. Basate SOLO en esta información de tus archivos:\n{contexto}\n\nPregunta: {pregunta}"
            
            res = model.generate_content(prompt)
            st.success("Información encontrada:")
            st.write(res.text)
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.caption("Nota: Este buscador solo usa la información de tus Google Sheets configurados.")
