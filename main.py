import streamlit as st

# Forzamos el logo con un enlace directo de GitHub para que el celular lo vea rápido
logo_url = "https://raw.githubusercontent.com/ballanomdq/buscador-osecac/main/LOGO1.png"

st.set_page_config(
    page_title="OSECAC MDP",
    page_icon=logo_url, # Usamos la URL directa, no el archivo local
    layout="centered"
)

# Esto elimina el menú de Streamlit arriba a la derecha para que parezca menos "App"
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
