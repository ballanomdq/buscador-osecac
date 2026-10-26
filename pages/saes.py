import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

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

# ============================================================
# ESTADO DE LA SESIÓN
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"

# ============================================================
# 1. LOGIN (El que ya sabemos que funciona)
# ============================================================
if not st.session_state.saes_logueado:
    st.markdown("## 🔑 Acceso al SAES")
    with st.form("form_login"):
        c_usr, c_pwd = st.columns(2)
        with c_usr: usuario = st.text_input("Usuario:", value="rballano")
        with c_pwd: password = st.text_input("Contraseña:", type="password")
        
        if st.form_submit_button("🚀 Entrar al SAES", use_container_width=True):
            if usuario and password:
                # Hacemos el login real con requests
                session = requests.Session()
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
                
                r = session.get(login_url, headers=headers)
                soup = BeautifulSoup(r.text, 'html.parser')
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
                
                payload = {
                    "__EVENTTARGET": "", "__EVENTARGUMENT": "",
                    "__VIEWSTATE": viewstate,
                    "txtUser": usuario, "txtPassword": password,
                    "imgbtnSend.x": "0", "imgbtnSend.y": "0"
                }
                
                r_post = session.post(login_url, data=payload, headers=headers)
                
                if "txtUser" not in r_post.text:
                    st.session_state.saes_logueado = True
                    st.session_state.usuario = usuario
                    st.session_state.session = session
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ============================================================
# 2. PORTAL (CON EL MENÚ LATERAL Y LA BÚSQUEDA REAL)
# ============================================================
else:
    session = st.session_state.session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # --- BARRA LATERAL (Menús visuales) ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        if st.button("📂 Autorización", use_container_width=True):
            st.info("Módulo de Autorización (en desarrollo)")
            
        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.info("Módulo de Medicamentos (abajo para buscar)")
            
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.rerun()

    # --- CUERPO CENTRAL (BÚSQUEDA) ---
    st.markdown("## 🔎 Consulta de Trámites (Medicamentos)")
    
    with st.form("form_busqueda"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            tipo_doc = st.selectbox("Tipo Doc", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
        with col2:
            nro_doc = st.text_input("Nro. de Documento", value="6705303")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_buscar = st.form_submit_button("🔍 Buscar en SAES", use_container_width=True)

    if btn_buscar:
        with st.spinner("Conectando con SAES..."):
            try:
                # 1. Vamos a la página de búsqueda (la que usa SAES internamente)
                # Usamos la URL que descubrimos con SingleFile: frmBrowserConsulta.aspx
                url_busqueda = "http://portal.gmssa.com.ar/saes/frmBrowserConsulta.aspx"
                
                # Hacemos un GET para obtener el formulario y el __VIEWSTATE de esa página
                r = session.get(url_busqueda, headers=headers)
                
                if "Login.aspx" in r.url:
                    st.error("La sesión expiró. Volvé a loguearte.")
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    
                    # Buscamos los campos ocultos del formulario
                    viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                    
                    if not viewstate:
                        st.error("No se pudo cargar el formulario de búsqueda.")
                    else:
                        # Armamos el payload con los datos de búsqueda
                        payload = {
                            "__EVENTTARGET": "",
                            "__EVENTARGUMENT": "",
                            "__VIEWSTATE": viewstate['value'],
                            "cboTipoDoc": tipo_doc,
                            "txtDocumento": nro_doc,
                            "imgConsultar.x": "10", # Coordenadas del clic en la lupa
                            "imgConsultar.y": "10"
                        }
                        
                        if eventvalidation:
                            payload["__EVENTVALIDATION"] = eventvalidation['value']
                        
                        # Hacemos el POST para buscar
                        r_resultado = session.post(url_busqueda, data=payload, headers=headers)
                        
                        # Parseamos la tabla de resultados
                        soup_res = BeautifulSoup(r_resultado.text, 'html.parser')
                        tabla = soup_res.find('table', {'id': 'dgBusquedaBenef'})
                        
                        if tabla:
                            filas = tabla.find_all('tr')
                            resultados = []
                            for fila in filas[1:]:
                                celdas = fila.find_all('td')
                                if len(celdas) >= 9:
                                    resultados.append({
                                        "Nro. Autorización": celdas[1].text.strip(),
                                        "OP": celdas[2].text.strip(),
                                        "AUT Desde": celdas[3].text.strip(),
                                        "AUT Hasta": celdas[4].text.strip(),
                                        "OP Desde": celdas[5].text.strip(),
                                        "OP Hasta": celdas[6].text.strip(),
                                        "Programa": celdas[7].text.strip(),
                                        "Farmacia": celdas[8].text.strip(),
                                    })
                            
                            if resultados:
                                st.success(f"Se encontraron {len(resultados)} trámites.")
                                st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
                            else:
                                st.warning("No se encontraron resultados para ese documento.")
                        else:
                            st.warning("No se pudo leer la tabla de resultados. Puede que el documento no exista o la página haya cambiado.")
            except Exception as e:
                st.error(f"Error al buscar: {e}")
