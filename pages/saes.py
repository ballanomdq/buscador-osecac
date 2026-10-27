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
if "menu_abierto" not in st.session_state:
    st.session_state.menu_abierto = None

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
# 2. PORTAL (CON MENÚS Y BÚSQUEDA POR ENTER)
# ============================================================
else:
    s = st.session_state.session

    # --- BARRA LATERAL CON LOS MENÚS ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        st.markdown("#### Módulos SAES")
        
        if st.button("📂 Autorización", use_container_width=True):
            st.session_state.menu_abierto = "auto" if st.session_state.menu_abierto != "auto" else None
        
        if st.session_state.menu_abierto == "auto":
            if st.button("↳ Consultas y Listados", use_container_width=True):
                st.info("Módulo Autorización - Consultas")
            if st.button("↳ Autorizaciones", use_container_width=True):
                st.info("Módulo Autorización - Autorizaciones")
            if st.button("↳ Listados por Período", use_container_width=True):
                st.info("Módulo Autorización - Listados")

        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.session_state.menu_abierto = "med" if st.session_state.menu_abierto != "med" else None
            
        if st.session_state.menu_abierto == "med":
            if st.button("↳ Consultas", use_container_width=True):
                st.info("Usá el formulario de abajo para buscar el DNI.")
            if st.button("↳ Listados", use_container_width=True):
                st.info("Módulo Medicamentos - Listados")
            if st.button("↳ Consultas por delegación", use_container_width=True):
                st.info("Módulo Medicamentos - Delegación")
            if st.button("↳ Solicitudes de trámite", use_container_width=True):
                st.info("Módulo Medicamentos - Solicitudes")
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.rerun()

    # --- CUERPO CENTRAL (BÚSQUEDA) ---
    st.markdown("## 🔎 Consulta de Trámites (Medicamentos)")
    
    with st.form("busqueda"):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: tipo = st.selectbox("Tipo Doc", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
        with c2: dni = st.text_input("Nro. de Documento", value="6705303")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.form_submit_button("🔍 Buscar en SAES", use_container_width=True)
    
    if buscar:
        with st.spinner("Buscando en SAES..."):
            try:
                url_cons = BASE_URL + "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
                
                # 1. GET para obtener los tokens frescos
                r_cons = s.get(url_cons, headers=HEADERS)
                soup_cons = BeautifulSoup(r_cons.text, 'html.parser')
                
                vs = soup_cons.find('input', {'name': '__VIEWSTATE'})
                ev = soup_cons.find('input', {'name': '__EVENTVALIDATION'})
                
                if not vs:
                    st.error("No se pudo obtener el formulario de consulta del servidor.")
                else:
                    # 2. Armamos el POST simulando la tecla Enter
                    # El __EVENTTARGET es "txtDocumento" (el nombre del campo)
                    payload = {
                        "__EVENTTARGET": "txtDocumento",
                        "__EVENTARGUMENT": "",
                        "__VIEWSTATE": vs['value'],
                        "cboTipoDoc": tipo,
                        "txtDocumento": dni,
                    }
                    if ev: payload["__EVENTVALIDATION"] = ev['value']
                    
                    # 3. Hacemos el POST
                    r_res = s.post(url_cons, data=payload, headers=HEADERS)
                    soup_res = BeautifulSoup(r_res.text, 'html.parser')
                    
                    # 4. Buscamos la tabla de resultados
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
                            st.warning("No se encontraron resultados para ese documento.")
                    else:
                        st.warning("No se pudo leer la tabla de resultados. Es posible que el servidor haya devuelto la página sin resultados.")
            except Exception as e:
                st.error(f"Error al realizar la búsqueda: {e}")
