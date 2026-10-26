import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }
.saes-card { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-top: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.badge-verde { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
.badge-rojo { background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; }
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

if st.button("← Volver al Menú Principal"):
    try:
        st.switch_page("main.py")
    except Exception:
        st.warning("Función de retorno al menú principal no disponible en este entorno.")

if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "saes_menu" not in st.session_state:
    st.session_state.saes_menu = "consultas"
if "session_cookies" not in st.session_state:
    st.session_state.session_cookies = None

# ================= 1. LOGIN REAL (CON TODOS LOS TOKENS) =================
if not st.session_state.saes_logueado:
    st.markdown("## 🔑 Acceso al SAES")
    st.markdown("Ingrese sus datos de usuario para ingresar al portal de OSECAC.")
    
    with st.form("form_login_saes"):
        c_usr, c_pwd = st.columns(2)
        with c_usr:
            usuario = st.text_input("Usuario:", value="rballano")
        with c_pwd:
            password = st.text_input("Contraseña:", type="password")
            
        btn_ingresar = st.form_submit_button("🚀 Entrar al SAES", use_container_width=True)
        
        if btn_ingresar:
            if usuario and password:
                with st.spinner("Conectando con SAES..."):
                    session = requests.Session()
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
                    }
                    login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
                    
                    try:
                        # 1. Obtenemos la página
                        r = session.get(login_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        
                        # 2. Extraemos TODOS los campos ocultos (ViewState, EventValidation, etc.)
                        payload = {}
                        for input_tag in soup.find_all('input', type='hidden'):
                            if input_tag.get('name'):
                                payload[input_tag.get('name')] = input_tag.get('value', '')
                        
                        # 3. Agregamos usuario y clave
                        payload['txtUsuario'] = usuario
                        payload['txtPassword'] = password
                        # A veces el botón tiene un name distinto, probamos los más comunes
                        if soup.find('input', {'name': 'btnIngresar'}):
                            payload['btnIngresar'] = 'Ingresar'
                        elif soup.find('input', {'name': 'btnAceptar'}):
                            payload['btnAceptar'] = 'Aceptar'
                        
                        # 4. Hacemos el POST con todos los campos
                        r_post = session.post(login_url, data=payload, headers=headers, timeout=30)
                        
                        # 5. Verificamos si entramos
                        # Si la página resultante NO tiene el input de password, es porque entramos
                        soup_post = BeautifulSoup(r_post.text, 'html.parser')
                        if not soup_post.find('input', {'type': 'password'}):
                            st.session_state.saes_logueado = True
                            st.session_state.usuario = usuario
                            st.session_state.password = password
                            st.session_state.session_cookies = session.cookies
                            st.success("✅ Acceso correcto.")
                            st.rerun()
                        else:
                            st.error("❌ El servidor de SAES rechazó las credenciales. Puede haber un CAPTCHA o un token extra.")
                            # Mostramos ayuda para depurar
                            with st.expander("Ver detalles técnicos del error"):
                                st.write("Código de estado:", r_post.status_code)
                                st.write("URL final:", r_post.url)
                                st.write("¿Hay captcha en la página?", "sí" if soup_post.find('img', {'id': 'captcha'}) else "no")
                                
                    except requests.exceptions.Timeout:
                        st.error("⏳ El servidor de SAES tardó demasiado en responder.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")
# El resto del código (el portal) sigue igual que antes...
