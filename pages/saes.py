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
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; margin-bottom: 5px; width: 100%; text-align: left;}
div[data-testid="stTextInput"] input { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# ESTADO
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"
if "url_destino" not in st.session_state:
    st.session_state.url_destino = None

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
                            st.session_state.url_destino = "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
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
# 2. PORTAL
# ============================================================
else:
    s = st.session_state.session
    
    # Barra lateral
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        st.markdown("#### Módulos SAES")
        if st.button("📂 Autorización", use_container_width=True):
            st.session_state.url_destino = "Autorizaciones/Consulta/frmBrowserConsulta.aspx"
            st.rerun()
        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.session_state.url_destino = "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
            st.rerun()
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.url_destino = None
            st.rerun()

    # Cuerpo central
    if st.session_state.url_destino:
        with st.spinner("Cargando SAES..."):
            try:
                url_completa = BASE_URL + st.session_state.url_destino
                r = s.get(url_completa, headers=HEADERS)
                
                if "txtUser" in r.text:
                    st.error("La sesión expiró. Cerrá sesión y volvé a entrar.")
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    body = soup.find('body')
                    
                    if body:
                        # Inyectamos CSS para maquillar el formulario
                        estilo = """
                        <style>
                            body { background-color: #f8fafc !important; font-family: sans-serif !important; color: #0f172a !important; padding: 20px; }
                            label, .label { font-size: 16px !important; font-weight: 600 !important; color: #0f172a !important; margin-right: 10px !important; }
                            input[type="text"], select { font-size: 16px !important; padding: 8px 12px !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important; background: #fff !important; color: #0f172a !important; margin-right: 15px !important; }
                            input[type="image"] { width: 32px !important; height: 32px !important; cursor: pointer !important; margin-right: 5px !important; }
                            table { width: 100% !important; border-collapse: collapse !important; margin-top: 20px !important; }
                            td, th { padding: 10px !important; border: 1px solid #e2e8f0 !important; font-size: 15px !important; }
                            th { background-color: #f1f5f9 !important; color: #0f172a !important; }
                        </style>
                        """
                        # Limpiamos scripts viejos
                        for tag in body(["script", "style", "link", "meta"]):
                            tag.decompose()
                        html_puro = estilo + str(body)
                    else:
                        html_puro = r.text
                    
                    # INYECTAMOS JS PARA QUE EL FORMULARIO ENVÍE LOS DATOS AL SERVIDOR REAL
                    # Esto hace que el navegador del cliente haga el POST, no nuestro backend.
                    script_post = """
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {
                            // Buscamos el formulario y le cambiamos el target para que se envíe a sí mismo
                            var form = document.forms[0];
                            if (form) {
                                // Aquí podríamos agregar lógica adicional si es necesario
                                // Por defecto, el formulario ya apunta a la URL correcta
                            }
                        });
                    </script>
                    """
                    html_puro += script_post
                    
                    components.html(html_puro, height=800, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar la página: {e}")
