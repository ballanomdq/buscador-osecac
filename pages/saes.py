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

# ================= 1. LOGIN REAL (CON DISFRAZ) =================
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
                with st.spinner("Conectando con SAES... (Paso 1: Obteniendo página)"):
                    session = requests.Session()
                    # Disfrazamos la petición para que SAES crea que somos Google Chrome
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
                    }
                    login_url = "https://portal.gmssa.com.ar/saes/Login.aspx"
                    
                    try:
                        # timeout=15 significa: si en 15 segundos no responde, cortá.
                        r = session.get(login_url, headers=headers, timeout=15)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        
                        # Verificamos qué encontramos en la página
                        st.info(f"Página obtenida. Código HTTP: {r.status_code}")
                        
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        txt_user = soup.find('input', {'name': 'txtUsuario'})
                        
                        if not viewstate or not txt_user:
                            st.error("⚠️ No se encontraron los campos del formulario. La página de login cambió o bloqueó la conexión.")
                            st.write("Campos encontrados en la página:")
                            st.write([i.get('name') for i in soup.find_all('input')][:20]) # Mostramos los primeros 20 inputs
                            st.stop()
                        
                        # Si encontramos los campos, seguimos
                        payload = {
                            '__VIEWSTATE': viewstate['value'],
                            'txtUsuario': usuario,
                            'txtPassword': password,
                            'btnIngresar': 'Ingresar'
                        }
                        
                        with st.spinner("Paso 2: Enviando credenciales..."):
                            r_post = session.post(login_url, data=payload, headers=headers, timeout=15)
                            
                            # Verificamos si entramos
                            if "Login" not in r_post.text and r_post.status_code == 200:
                                st.session_state.saes_logueado = True
                                st.session_state.usuario = usuario
                                st.session_state.password = password
                                st.session_state.session_cookies = session.cookies
                                st.success("✅ Acceso correcto.")
                                st.rerun()
                            else:
                                st.error(f"❌ Falló el login. Código HTTP: {r_post.status_code}")
                                st.write("Posiblemente el usuario o la contraseña sean incorrectos, o el botón de login se llame distinto.")
                                st.write("Nombre del botón de login real:")
                                st.write([i.get('name') for i in soup.find_all('input', type='submit')])
                                
                    except requests.exceptions.Timeout:
                        st.error("⏳ El servidor de SAES tardó demasiado en responder (Timeout). Puede estar caído.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")
