import streamlit as st
import time

st.set_page_config(page_title="OSECAC MDP", page_icon="LOGO1.png")

st.image("LOGO1.png", width=120)
st.title("Acceso")

user = st.text_input("Usuario")
pw = st.text_input("Clave", type="password")

if st.button("INGRESAR"):
    if user.lower() == "osecac" and pw == "2026":
        st.switch_page("pages/buscador.py")
    else:
        st.error("Datos incorrectos")
