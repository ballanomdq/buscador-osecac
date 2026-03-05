import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Reclamos - OSECAC", layout="centered")

# CSS para mantener la estética oscura pero con texto legible
st.markdown("""
<style>
.stApp { background-color: #0f172a; color: white; }
h1 { color: #38bdf8; text-align: center; }
/* Forzar color blanco en textos de inputs, selects, etc. */
.stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
    color: white !important;
}
/* Texto dentro de los selects y inputs */
.stSelectbox div[data-baseweb="select"] span, 
.stTextInput input, .stTextArea textarea {
    color: black !important; /* Fondo blanco, texto negro */
}
/* Para los botones, mantener estilo similar al main */
.stButton > button {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-size: 1rem !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background: #38bdf8 !important;
    color: black !important;
    transform: scale(1.05) !important;
}
/* Para el botón de volver, que ya es un link button, lo estilizamos similar */
.stLinkButton a {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    color: white !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-size: 1rem !important;
    font-weight: bold !important;
    text-decoration: none !important;
}
.stLinkButton a:hover {
    background: #38bdf8 !important;
    color: black !important;
    transform: scale(1.05) !important;
}
/* Para mensajes de éxito/error */
.stAlert {
    color: white !important;
}
.stSuccess, .stError {
    background-color: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid #38bdf8 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📩 Centro de Reclamos y Consultas")
st.write("Seleccioná tu agencia y el sector para iniciar el trámite.")

# Lista de agencias según lo solicitado
agencias = [
    "MAIPU", "S TERESITA", "MAR DE AJO", "MIRAMAR", "PINAMAR", 
    "S CLEMENTE", "MECHONGUE", "DOLORES", "M CHIQUITA", 
    "GESELL", "VIDAL", "PIRAN", "MADARIAGA"
]

# Lista de sectores
sectores = [
    "auditoria medica", "contaduria", "reintegros", "medicamentos", 
    "empadronamiento", "despacho", "sistemas", "fiscalizacion", 
    "personal", "Sebastian Lopez"
]

with st.form("form_reclamo"):
    agencia = st.selectbox("Agencia", agencias)
    sector = st.selectbox("Sector Destino", sectores)
    mensaje = st.text_area("Detalle del Reclamo/Consulta")
    archivo = st.file_uploader("Adjuntar documentación (PDF/Imagen)", type=["pdf", "jpg", "png"])
    
    enviar = st.form_submit_button("ENVIAR RECLAMO")
    
    if enviar:
        if mensaje:
            st.success(f"¡Reclamo de {agencia} enviado a {sector}!")
            # Aquí es donde luego pegaremos el código de subida a Drive
        else:
            st.error("Por favor, escribí un mensaje.")

# Botón para volver al buscador principal
st.link_button("⬅️ Volver al Buscador", "/")
