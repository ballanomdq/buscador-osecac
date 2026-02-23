import streamlit as st
import time

# 1. CONFIGURACIÓN AGRESIVA DE ICONO
# Usamos el logo de OSECAC directamente para que el navegador lo capture primero
st.set_page_config(
    page_title="OSECAC Portal",
    page_icon="LOGO1.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. EL TRUCO MAESTRO: CSS PARA "DESACTIVAR" EL MODO APP
st.markdown("""
    <style>
    /* Ocultamos todo lo que haga parecer esto una aplicación de Streamlit */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    /* Fondo sólido sin gradientes complejos que activen el detector de PWA */
    .stApp {
        background-color: #0b0e14;
        color: white;
    }
    
    .login-box {
        text-align: center;
        padding: 40px;
        border-radius: 20px;
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    
    div.stButton > button {
        width: 100%;
        background-color: #007bff !important;
        color: white !important;
        height: 3em;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="login-box">', unsafe_allow_html=True)
st.image("LOGO1.png", width=120)
st.title("Acceso Agencias")

# Formulario simple
usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if st.button("INGRESAR"):
    if usuario.lower() == "osecac" and clave == "2026":
        with st.spinner("Conectando..."):
            time.sleep(0.5)
            # Cambiamos a la página del buscador
            st.switch_page("pages/buscador.py")
    else:
        st.error("Credenciales no válidas")

st.markdown('</div>', unsafe_allow_html=True)
