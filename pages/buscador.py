import streamlit as st

# Configuración básica para el Login
st.set_page_config(page_title="Acceso OSECAC", layout="centered")

st.title("🔐 Control de Acceso")

# Si no existe la variable, la creamos
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

password = st.text_input("Ingresá la clave de acceso:", type="password")

if st.button("Entrar"):
    if password == "osecac2026": # O la clave que elijas
        st.session_state.autenticado = True
        st.success("Acceso concedido. Cargando portal...")
        st.rerun()
    else:
        st.error("Clave incorrecta")

# Solo si está autenticado, mostramos un botón para ir al portal o lo direccionamos
if st.session_state.autenticado:
    st.info("Ya podés navegar por el menú lateral hacia el Portal.")
