import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }
html, body, [class*="css"] { font-size: 17px; }
</style>
""", unsafe_allow_html=True)

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"

# ============================================================
# 1. LOGIN
# ============================================================
if not st.session_state.saes_logueado:
    st.markdown("## 🔑 Acceso al SAES")
    with st.form("login"):
        c1, c2 = st.columns(2)
        with c1: user = st.text_input("Usuario:", value="rballano")
        with c2: pwd = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("🚀 Entrar", use_container_width=True):
            if user and pwd:
                s = requests.Session()
                try:
                    r = s.get(BASE_URL + "Login.aspx", headers=HEADERS)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    vs = soup.find('input', {'name': '__VIEWSTATE'})
                    if vs:
                        payload = {
                            "__EVENTTARGET": "", "__EVENTARGUMENT": "",
                            "__VIEWSTATE": vs['value'],
                            "txtUser": user, "txtPassword": pwd,
                            "imgbtnSend.x": "0", "imgbtnSend.y": "0"
                        }
                        r2 = s.post(BASE_URL + "Login.aspx", data=payload, headers=HEADERS)
                        if "txtUser" not in r2.text:
                            st.session_state.saes_logueado = True
                            st.session_state.session = s
                            st.session_state.usuario = user
                            st.rerun()
                        else:
                            st.error("Usuario o clave incorrectos.")
                    else:
                        st.error("No se pudo conectar con el formulario de login.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            else:
                st.warning("Completá los datos.")

# ============================================================
# 2. PORTAL (DOS IFRAMES: MENÚ Y CONTENIDO)
# ============================================================
else:
    s = st.session_state.session

    # --- BARRA LATERAL (INFO) ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.rerun()

    # --- CUERPO CENTRAL (DOS IFRAMES) ---
    st.markdown("## 🏥 Portal SAES")
    
    col_menu, col_content = st.columns([1, 4])
    
    with col_menu:
        st.markdown("### Menú")
        try:
            # Cargamos NavigBar.aspx (el menú de la izquierda)
            r_menu = s.get(BASE_URL + "NavigBar.aspx", headers=HEADERS)
            if "txtUser" in r_menu.text:
                st.error("Sesión expirada.")
            else:
                # Mostramos el menú en un iframe
                components.html(r_menu.text, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error al cargar menú: {e}")
    
    with col_content:
        st.markdown("### Contenido")
        try:
            # Cargamos frmBrowserConsulta.aspx (la página de consultas)
            r_content = s.get(BASE_URL + "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx", headers=HEADERS)
            if "txtUser" in r_content.text:
                st.error("Sesión expirada.")
            else:
                # Mostramos la página de consultas en un iframe
                components.html(r_content.text, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error al cargar contenido: {e}")
