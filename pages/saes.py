
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
# Diccionario para guardar los enlaces reales
if "menu_urls" not in st.session_state:
    st.session_state.menu_urls = {}

# ============================================================
# FUNCIÓN PARA EXTRAER LOS ENLACES REALES
# ============================================================
def obtener_urls_reales(session, headers):
    try:
        # Vamos a la página principal donde está el menú
        r = session.get("http://portal.gmssa.com.ar/saes/welcome.aspx", headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        urls = {}
        # Buscamos todos los enlaces <a> y guardamos su texto y su href
        for a in soup.find_all('a'):
            texto = a.text.strip()
            href = a.get('href', '')
            # Solo guardamos los que tengan un link válido
            if texto and href and 'javascript' not in href:
                # Armamos la URL completa
                if href.startswith('http'):
                    url_completa = href
                else:
                    url_completa = "http://portal.gmssa.com.ar/saes/" + href
                urls[texto] = url_completa
                
        return urls
    except Exception as e:
        st.error(f"No se pudieron leer los enlaces del menú: {e}")
        return {}

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
                            
                            # ACÁ EXTRAEMOS LAS URLS REALES
                            with st.spinner("Leyendo el menú de SAES..."):
                                st.session_state.menu_urls = obtener_urls_reales(session, headers)
                            
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado al conectar: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ============================================================
# 2. PORTAL ESPEJO (CON ENLACES REALES)
# ============================================================
else:
    session = st.session_state.session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # --- BARRA LATERAL CON EL MENÚ REAL ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('usuario', 'rballano')}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        if not st.session_state.menu_urls:
            st.warning("No se pudieron cargar los enlaces del menú. Cerrá sesión y volvé a entrar.")
        else:
            # Creamos dos columnas para simular el menú de la izquierda
            for texto, url in st.session_state.menu_urls.items():
                # Mostramos el botón con el texto real del link
                if st.button(f"📂 {texto}", use_container_width=True):
                    st.session_state.current_url = url
                    st.rerun()
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.session = None
            st.session_state.menu_urls = {}
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
