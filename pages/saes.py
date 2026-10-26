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
# ESTADO DE LA SESIÓN
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "menu_items" not in st.session_state:
    st.session_state.menu_items = []
if "current_url" not in st.session_state:
    st.session_state.current_url = "http://portal.gmssa.com.ar/saes/welcome.aspx"

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
                        # 1. GET para obtener el token de la página de login
                        r = session.get(login_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        
                        if not viewstate:
                            st.error("No se pudo cargar la página de login de SAES. Verifique su conexión.")
                            st.stop()
                            
                        # 2. POST con las credenciales
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
                        
                        # 3. Verificamos si entramos
                        if not soup_post.find('input', {'type': 'password'}):
                            st.session_state.saes_logueado = True
                            st.session_state.session = session
                            st.session_state.usuario = usuario
                            
                            # 4. Extraemos el menú real de SAES desde la barra de navegación (¡EL CAMBIO CLAVE!)
                            try:
                                # En vez de ir a welcome.aspx, vamos a NavigBar.aspx
                                r_menu = session.get("http://portal.gmssa.com.ar/saes/NavigBar.aspx", headers=headers, timeout=30)
                                soup_menu = BeautifulSoup(r_menu.text, 'html.parser')
                                menu = []
                                for a in soup_menu.find_all('a'):
                                    if a.text.strip() and 'href' in a.attrs:
                                        menu.append({"texto": a.text.strip(), "href": a['href']})
                                st.session_state.menu_items = menu
                            except Exception as e:
                                print(f"Error al extraer menú: {e}")
                                st.session_state.menu_items = []
                                
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado al conectar: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ============================================================
# 2. PORTAL ESPEJO (PÁGINA COMPLETA)
# ============================================================
else:
    session = st.session_state.session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # --- BARRA LATERAL CON EL MENÚ DE SAES ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('usuario', 'rballano')}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        # Mostramos los botones del menú
        if not st.session_state.menu_items:
            st.warning("No se pudieron cargar los módulos del menú. Revisá la conexión.")
        else:
            for item in st.session_state.menu_items:
                if st.button(f"📂 {item['texto']}", use_container_width=True):
                    # Armar la URL completa (si viene con ../ o similar)
                    url_base = "http://portal.gmssa.com.ar/saes/"
                    st.session_state.current_url = url_base + item['href'].replace("../", "")
                    st.rerun()
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.session = None
            st.session_state.menu_items = []
            st.rerun()

    # --- CUERPO CENTRAL (MOSTRANDO LA PÁGINA REAL DE SAES) ---
    st.markdown(f"### 🏥 Visualizando módulo SAES")
    
    with st.spinner("Cargando página de SAES..."):
        try:
            # Pedimos la página de SAES usando la misma sesión logueada
            r = session.get(st.session_state.current_url, headers=headers, timeout=30)
            
            # Parseamos el HTML de la página
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extraemos solo el cuerpo de la página para mostrarlo limpio
            body_content = soup.find('body')
            
            if body_content:
                # Limpiamos etiquetas que puedan romper el navegador dentro de Streamlit
                for tag in body_content(["script", "style", "link", "meta", "iframe", "frame"]):
                    tag.decompose()
                html_puro = str(body_content)
            else:
                html_puro = r.text
                
            # Inyectamos el HTML con un iframe para que se renderice correctamente
            components.html(html_puro, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"Error al cargar la página de SAES: {e}")
