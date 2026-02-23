import streamlit as st
import time

# Configuración de página con URL directa para forzar el ícono
st.set_page_config(
    page_title="OSECAC MDP - Acceso",
    page_icon="https://raw.githubusercontent.com/ballanomdq/buscador-osecac/main/LOGO1.png",
    layout="centered"
)

# Estilo para que parezca una página de entrada y no una App
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    div.stButton > button {
        width: 100%;
        background-color: #38bdf8;
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .main-text { text-align: center; margin-top: 50px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Imagen del logo
st.image("https://raw.githubusercontent.com/ballanomdq/buscador-osecac/main/LOGO1.png", width=120)

st.markdown('<div class="main-text">', unsafe_allow_html=True)
st.title("Portal Agencias")
st.write("Ingrese sus credenciales para continuar")

# Control de Acceso
with st.container():
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR"):
        if usuario.lower() == "osecac" and clave == "2026": # Puedes cambiar esto
            with st.spinner("Verificando..."):
                time.sleep(1)
                st.switch_page("pages/buscador.py")
        else:
            st.error("Usuario o clave incorrectos")

st.markdown('</div>', unsafe_allow_html=True)
