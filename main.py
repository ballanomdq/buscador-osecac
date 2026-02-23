import streamlit as st
import time

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP",
    page_icon="LOGO1.png", 
    layout="centered"
)

# CSS PARA QUITAR EL MODO "APP" Y FORZAR EL ICONO
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0b0e14; color: white; }
    div.stButton > button {
        width: 100%;
        background-color: #38bdf8 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.image("LOGO1.png", width=120)
st.title("Acceso al Portal")

# LOGIN
usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if st.button("INGRESAR"):
    if usuario.lower() == "osecac" and clave == "2026":
        with st.spinner("Cargando..."):
            time.sleep(0.5)
            # PRUEBA ESTA RUTA SIMPLIFICADA:
            st.switch_page("pages/buscador.py")
    else:
        st.error("Datos incorrectos")
