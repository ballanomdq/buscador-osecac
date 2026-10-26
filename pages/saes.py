import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# ============================================================
# CONFIGURACIÓN GENERAL (ACCESIBILIDAD VISUAL)
# ============================================================
st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
/* Fondo claro e institucional */
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }

/* Mejoras de accesibilidad visual */
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; margin-bottom: 5px; width: 100%; text-align: left;}
div[data-testid="stTextInput"] input { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ESTADO DE LA SESIÓN Y NAVEGACIÓN
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "current_url" not in st.session_state:
    st.session_state.current_url = "http://portal.gmssa.com.ar/saes/welcome.aspx"
if "menu_abierto" not in st.session_state:
    st.session_state.menu_abierto = None

# ============================================================
# 1. PANTALLA DE LOGIN
# ============================================================
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
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
                    
                    try:
                        r = session.get(login_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        
                        if not viewstate:
                            st.error("No se pudo cargar la página de login.")
                            st.stop()
                            
                        payload = {
                            "__EVENTTARGET": "",
                            "__EVENTARGUMENT": "",
                            "__VIEWSTATE": viewstate['value'],
                            "txtUser": usuario,
                            "txtPassword": password,
                            "imgbtnSend.x": "0",
                            "imgbtnSend.y": "0"
                        }
                        
                        r_post = session.post(login_url, data=payload, headers=headers, timeout=30)
                        soup_post = BeautifulSoup(r_post.text, 'html.parser')
                        
                        if not soup_post.find('input', {'type': 'password'}):
                            st.session_state.saes_logueado = True
                            st.session_state.session = session
                            st.session_state.usuario = usuario
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado al conectar: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ============================================================
# 2. PORTAL ESPEJO (CON BOTONES FIJOS Y URLS REALES)
# ============================================================
else:
    session = st.session_state.session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # --- BARRA LATERAL CON EL MENÚ ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('usuario', 'rballano')}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        # --- MENÚ 1: AUTORIZACIÓN ---
        if st.button("📂 Autorización", use_container_width=True):
            st.session_state.menu_abierto = "autorizacion" if st.session_state.menu_abierto != "autorizacion" else None
        
        if st.session_state.menu_abierto == "autorizacion":
            st.markdown("<div style='margin-left: 20px;'>", unsafe_allow_html=True)
            if st.button("↳ Consultas y Listados", use_container_width=True):
                # El archivo real es frmBrowserConsulta.aspx
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserConsulta.aspx"
                st.rerun()
            if st.button("↳ Autorizaciones", use_container_width=True):
                # Intentamos con la misma lógica, pero este puede variar
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserAutorizacion.aspx"
                st.rerun()
            if st.button("↳ Listados por Período", use_container_width=True):
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserListados.aspx"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- MENÚ 2: ADM. DE MEDICAMENTOS ---
        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.session_state.menu_abierto = "medicamentos" if st.session_state.menu_abierto != "medicamentos" else None
            
        if st.session_state.menu_abierto == "medicamentos":
            st.markdown("<div style='margin-left: 20px;'>", unsafe_allow_html=True)
            if st.button("↳ Listados", use_container_width=True):
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserListados.aspx"
                st.rerun()
            if st.button("↳ Consultas", use_container_width=True):
                # ACÁ ES DONDE VA LA URL REAL DE LA PANTALLA DE CONSULTAS
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserConsulta.aspx"
                st.rerun()
            if st.button("↳ Consultas por delegación", use_container_width=True):
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserConsultaDelegacion.aspx"
                st.rerun()
            if st.button("↳ Solicitudes de trámite", use_container_width=True):
                st.session_state.current_url = "http://portal.gmssa.com.ar/saes/frmBrowserSolicitudes.aspx"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.session = None
            st.session_state.menu_abierto = None
            st.rerun()

    # --- CUERPO CENTRAL (MOSTRANDO LA PÁGINA REAL DE SAES) ---
    st.markdown(f"### 🏥 Visualizando módulo SAES")
    
    with st.spinner("Cargando página de SAES..."):
        try:
            r = session.get(st.session_state.current_url, headers=headers, timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            body_content = soup.find('body')
            
            if body_content:
                for tag in body_content(["script", "style", "link", "meta", "iframe", "frame"]):
                    tag.decompose()
                html_puro = str(body_content)
            else:
                html_puro = r.text
                
            components.html(html_puro, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"Error al cargar la página de SAES: {e}")
