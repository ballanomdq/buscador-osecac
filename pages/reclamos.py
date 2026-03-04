import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Reclamos - OSECAC", layout="centered")

# CSS para mantener la estética oscura
st.markdown("""
<style>
.stApp { background-color: #0f172a; color: white; }
h1 { color: #38bdf8; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("📩 Centro de Reclamos y Consultas")
st.write("Seleccioná tu agencia y el sector para iniciar el trámite.")

with st.form("form_reclamo"):
    agencia = st.selectbox("Agencia", ["Miramar", "Villa Gesell", "Pinamar", "Mar del Plata"])
    sector = st.selectbox("Sector Destino", ["Facturación", "Reintegros", "Auditoría Médica", "Suministros"])
    mensaje = st.text_area("Detalle del Reclamo/Consulta")
    archivo = st.file_uploader("Adjuntar documentación (PDF/Imagen)", type=["pdf", "jpg", "png"])
    
    enviar = st.form_submit_button("ENVIAR RECLAMO")
    
    if enviar:
        if mensaje:
            st.success(f"¡Reclamo de {agencia} enviado a {sector}!")
            # Aquí es donde luego pegaremos el código de subida a Drive
        else:
            st.error("Por favor, escribí un mensaje.")

if st.button("⬅️ Volver al Buscador"):
    st.switch_page("main.py") # Esto te devuelve a la principal sin recargar
