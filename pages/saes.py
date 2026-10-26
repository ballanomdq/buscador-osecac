import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
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

if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "menu_abierto" not in st.session_state:
    st.session_state.menu_abierto = None
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
                h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                r = s.get("http://portal.gmssa.com.ar/saes/Login.aspx", headers=h)
                soup = BeautifulSoup(r.text, 'html.parser')
                payload = {
                    "__EVENTTARGET": "", "__EVENTARGUMENT": "",
                    "__VIEWSTATE": soup.find('input', {'name': '__VIEWSTATE'})['value'],
                    "txtUser": user, "txtPassword": pwd,
                    "imgbtnSend.x": "0", "imgbtnSend.y": "0"
                }
                r2 = s.post("http://portal.gmssa.com.ar/saes/Login.aspx", data=payload, headers=h)
                if "txtUser" not in r2.text:
                    st.session_state.saes_logueado = True
                    st.session_state.session = s
                    st.session_state.usuario = user
                    st.rerun()
                else:
                    st.error("Usuario o clave incorrectos.")
            else:
                st.warning("Completá los datos.")

# ============================================================
# 2. PORTAL
# ============================================================
else:
    s = st.session_state.session
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        # --- MENÚ 1: AUTORIZACIÓN ---
        if st.button("📂 Autorización", use_container_width=True):
            st.session_state.menu_abierto = "auto" if st.session_state.menu_abierto != "auto" else None
        
        if st.session_state.menu_abierto == "auto":
            if st.button("↳ Consultas y Listados", use_container_width=True):
                st.session_state.url_destino = "auto_consultas"
                st.rerun()
            if st.button("↳ Autorizaciones", use_container_width=True):
                st.session_state.url_destino = "auto_autorizaciones"
                st.rerun()
            if st.button("↳ Listados por Período", use_container_width=True):
                st.session_state.url_destino = "auto_listados"
                st.rerun()

        # --- MENÚ 2: MEDICAMENTOS ---
        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.session_state.menu_abierto = "med" if st.session_state.menu_abierto != "med" else None
            
        if st.session_state.menu_abierto == "med":
            if st.button("↳ Listados", use_container_width=True):
                st.session_state.url_destino = "med_listados"
                st.rerun()
            if st.button("↳ Consultas", use_container_width=True):
                st.session_state.url_destino = "med_consultas"
                st.rerun()
            if st.button("↳ Consultas por delegación", use_container_width=True):
                st.session_state.url_destino = "med_delegacion"
                st.rerun()
            if st.button("↳ Solicitudes de trámite", use_container_width=True):
                st.session_state.url_destino = "med_solicitudes"
                st.rerun()
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.url_destino = None
            st.rerun()

    # --- CUERPO CENTRAL (BÚSQUEDA Y TABLA) ---
    st.markdown("## 🔎 Consulta de Trámites (Medicamentos)")
    
    with st.form("busqueda"):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: tipo = st.selectbox("Tipo Doc", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
        with c2: dni = st.text_input("Nro. de Documento", value="6705303")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.form_submit_button("🔍 Buscar en SAES", use_container_width=True)
    
    if buscar:
        with st.spinner("Conectando con SAES..."):
            try:
                # 1. Vamos a la página principal de SAES para obtener el menú
                r_main = s.get("http://portal.gmssa.com.ar/saes/welcome.aspx", headers=h)
                soup_main = BeautifulSoup(r_main.text, 'html.parser')
                
                # Buscamos el frame de WorkSpace (que contiene la página de consultas)
                frames = soup_main.find_all("frame")
                url_workspace = None
                for f in frames:
                    if f.get("name") == "WorkSpace" or "frmBrowser" in f.get("src", ""):
                        url_workspace = f.get("src")
                        break
                
                if not url_workspace:
                    st.error("No se encontró el frame de trabajo.")
                else:
                    # Armamos la URL completa
                    if not url_workspace.startswith("http"):
                        url_workspace = "http://portal.gmssa.com.ar/saes/" + url_workspace.lstrip("/")
                    
                    # 2. Pedimos la página de consultas
                    r_consulta = s.get(url_workspace, headers=h)
                    soup_consulta = BeautifulSoup(r_consulta.text, 'html.parser')
                    
                    # 3. Buscamos el formulario dentro de esa página
                    viewstate = soup_consulta.find('input', {'name': '__VIEWSTATE'})
                    eventval = soup_consulta.find('input', {'name': '__EVENTVALIDATION'})
                    
                    if not viewstate:
                        st.error(f"No se encontró el formulario en: {url_workspace}")
                    else:
                        # 4. Armamos el POST de búsqueda
                        payload = {
                            "__EVENTTARGET": "",
                            "__EVENTARGUMENT": "",
                            "__VIEWSTATE": viewstate['value'],
                            "cboTipoDoc": tipo,
                            "txtDocumento": dni,
                            "imgConsultar.x": "10",
                            "imgConsultar.y": "10"
                        }
                        if eventval:
                            payload["__EVENTVALIDATION"] = eventval['value']
                        
                        # 5. Hacemos la búsqueda
                        r_resultado = s.post(url_workspace, data=payload, headers=h)
                        soup_res = BeautifulSoup(r_resultado.text, 'html.parser')
                        
                        # 6. Extraemos la tabla
                        tabla = soup_res.find('table', {'id': 'dgBusquedaBenef'})
                        if tabla:
                            filas = tabla.find_all('tr')
                            datos = []
                            for f in filas[1:]:
                                celdas = f.find_all('td')
                                if len(celdas) >= 9:
                                    datos.append({
                                        "Nro. Autorización": celdas[1].text.strip(),
                                        "OP": celdas[2].text.strip(),
                                        "AUT Desde": celdas[3].text.strip(),
                                        "AUT Hasta": celdas[4].text.strip(),
                                        "OP Desde": celdas[5].text.strip(),
                                        "OP Hasta": celdas[6].text.strip(),
                                        "Programa": celdas[7].text.strip(),
                                        "Farmacia": celdas[8].text.strip(),
                                    })
                            
                            if datos:
                                st.success(f"Se encontraron {len(datos)} trámites.")
                                st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)
                            else:
                                st.warning("No se encontraron resultados.")
                        else:
                            st.warning("No se pudo leer la tabla de resultados.")
            except Exception as e:
                st.error(f"Error: {e}")
