import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Cerebro OSECAC Miramar", layout="wide")

# 1. SEGURIDAD (API KEY)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Falta configurar la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. CARGA DE FUENTES (Excels y Glosario)
@st.cache_data
def cargar_fuentes():
    # Nomencladores
    url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
    url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
    
    df_o = pd.read_csv(url_osecac)
    df_f = pd.read_csv(url_faba)
    return df_o, df_f

df_osecac, df_faba = cargar_fuentes()

# INTERFAZ DE USUARIO
st.title("🤖 Buscador Integral OSECAC Miramar")
st.markdown("---")
st.info("Consultando: Nomencladores (OSECAC/FABA), Glosario Miramar, CIE-10 y Manual HPC.")

pregunta = st.text_input("¿En qué puedo ayudarte hoy?", placeholder="Ej: ¿Qué hago si un afiliado renuncia? o Código 2060")

if pregunta:
    with st.spinner("Consultando el cerebro de la agencia..."):
        # Le damos las instrucciones a Gemini
        contexto = f"""
        Eres el Asistente Experto de OSECAC Miramar. 
        REGLA DE ORO: Si la respuesta está en el GLOSARIO OSECAC o NOMENCLADORES, úsalos.
        
        DATOS DE REFERENCIA:
        - NOMENCLADOR OSECAC: {df_osecac.head(50).to_string()}
        - NOMENCLADOR FABA: {df_faba.head(50).to_string()}
        
        SABERES DEL GLOSARIO INTERNO:
        - Renuncias: 90 días de extensión con telegrama.
        - Abogado: Ramiro (2236210387).
        - Diabetes: Cristian Liberatore (insulinasmdp@osecac.org.ar).
        - Abreviaturas: BEG (Buen estado general), HDA (Hemorragia digestiva alta).
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        respuesta = model.generate_content(f"{contexto}\n\nPregunta: {pregunta}")
        
        st.subheader("Respuesta:")
        st.success(respuesta.text)

st.divider()
st.caption("Actualización automática: Al editar tus Google Sheets/Docs, la IA aprende los cambios.")
