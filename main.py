import streamlit as st
import time

# 1. CONFIGURACIÓN DE PÁGINA (Esto controla el icono en el celular)
st.set_page_config(
    page_title="OSECAC MDP - Acceso",
    page_icon="LOGO1.png", 
    layout="centered"
)

# 2. ESTILO VISUAL (Para que se vea como una entrada profesional)
st.markdown("""
    <style>
    /* Fondo oscuro como tu buscador */
    .stApp { 
        background-color: #0b0e14; 
        color: #e2e8f0; 
    }
    /* Estilo del botón de ingreso */
    div.stButton > button {
        width: 100%;
        background-color: #38bdf8 !important;
        color: white !important;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }
    /* Ocultar menús de Streamlit para que parezca una App propia */
    #MainMenu, footer, header {visibility: hidden;}
    
    .contenedor-login {
        text-align: center;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONTENIDO DE LA PANTALLA
st.markdown('<div class="contenedor-login">', unsafe_allow_html=True)

# Mostramos tu logo central
try:
    st.image("LOGO1.png", width=150)
except:
    pass

st.title("Portal Agencias")
st.write("Identifíquese para ingresar al sistema")

# 4. FORMULARIO DE ACCESO
with st.container():
    user_input = st.text_input("Usuario")
    pass_input = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR AL BUSCADOR"):
        if user_input.lower() == "osecac" and pass_input == "2026":
            with st.spinner("Cargando base de datos..."):
                time.sleep(1)
                # IMPORTANTE: Esta ruta debe coincidir con tu carpeta en GitHub
                st.switch_page("pages/buscador.py")
        else:
            st.error("Credenciales incorrectas. Intente de nuevo.")

st.markdown('</div>', unsafe_allow_html=True)
