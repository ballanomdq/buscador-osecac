import streamlit as st
import time
import base64

# CONFIGURACIÓN PARA EL CELULAR (Aquí es donde definimos tu logo)
st.set_page_config(
    page_title="OSECAC MDP - Portal",
    page_icon="LOGO1.png", # Esto es lo que se verá como icono en el celular
    layout="centered"
)

# Estilo para la animación de carga (usando el color azul de tu diseño)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; text-align: center; }
    .loader {
        border: 4px solid #1e1b2e;
        border-top: 4px solid #38bdf8; /* Tu azul celeste */
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .btn-entrar {
        background-color: #38bdf8 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo central
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" style="width:120px; margin-top:50px;">', unsafe_allow_html=True)
except:
    pass

st.title("¡Bienvenido!")
st.write("Iniciando el portal de Agencias...")

# Animación de carga
placeholder = st.empty()
with placeholder.container():
    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
    time.sleep(1.5) # Tiempo de la animación
placeholder.empty()

# Botón para entrar
if st.button("🚪 INGRESAR AL SISTEMA", use_container_width=True):
    st.switch_page("pages/buscador.py")

st.info("💡 Consejo: Para guardar esta página en tu pantalla de inicio, usa la opción 'Añadir a la pantalla de inicio' en el menú de tu navegador.")
