import streamlit as st
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP",
    page_icon="LOGO1.png", 
    layout="centered",
    initial_sidebar_state="collapsed" # Fuerza a que el panel empiece cerrado
)

# 2. CSS PARA QUITAR EL PANEL LATERAL, EL MODO "APP" Y LOGO
st.markdown("""
    <style>
    /* ESTO ESCONDE EL PANEL DE LA IZQUIERDA */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }
    /* ESTO QUITA EL MENÚ DE ARRIBA Y EL FOOTER */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* TU DISEÑO */
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

# 3. CONTENIDO VISUAL
st.image("LOGO1.png", width=120)
st.title("Acceso al Portal")

# 4. SISTEMA DE LOGIN
usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if st.button("INGRESAR"):
    if usuario.lower() == "osecac" and clave == "2026":
        with st.spinner("Cargando..."):
            time.sleep(0.5)
            # Navegación al buscador
            st.switch_page("pages/buscador.py")
    else:
        st.error("Datos incorrectos")
