import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
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

if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"
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
# 2. PORTAL
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
                st.session_state.url_destino = "Autorizaciones/Consulta/frmBrowserConsulta.aspx"
                st.rerun()

        if st.button("📂 Adm. de Medicamentos", use_container_width=True):
            st.session_state.menu_abierto = "med" if st.session_state.menu_abierto != "med" else None
            
        if st.session_state.menu_abierto == "med":
            if st.button("↳ Consultas", use_container_width=True):
                st.session_state.url_destino = "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
                st.rerun()
                
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.url_destino = None
            st.rerun()

    # --- CUERPO CENTRAL ---
    st.markdown("## 🔎 Consulta de Trámites (Medicamentos)")
    
    if st.session_state.url_destino:
        with st.spinner("Cargando sección de SAES..."):
            try:
                url_completa = BASE_URL + st.session_state.url_destino
                r = s.get(url_completa, headers=HEADERS)
                
                if "txtUser" in r.text:
                    st.error("La sesión expiró. Cerrá sesión y volvé a entrar.")
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    body = soup.find('body')
                    
                    if body:
                        # --- ACÁ INYECTAMOS EL CSS PARA MAQUILLAR ---
                        estilo_maquillaje = """
                        <style>
                            body {
                                background-color: #f8fafc !important;
                                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                                color: #0f172a !important;
                                padding: 20px;
                            }
                            /* Agrandar las letras de los labels */
                            label, .label {
                                font-size: 16px !important;
                                font-weight: 600 !important;
                                color: #0f172a !important;
                                margin-right: 10px !important;
                            }
                            /* Agrandar los inputs de texto */
                            input[type="text"], select {
                                font-size: 16px !important;
                                padding: 8px 12px !important;
                                border: 1px solid #cbd5e1 !important;
                                border-radius: 6px !important;
                                background-color: #ffffff !important;
                                color: #0f172a !important;
                                margin-right: 15px !important;
                            }
                            /* Agrandar los botones (que son imágenes) */
                            input[type="image"] {
                                width: 32px !important;
                                height: 32px !important;
                                cursor: pointer !important;
                                margin-right: 5px !important;
                                vertical-align: middle !important;
                            }
                            /* Arreglar la tabla de resultados si aparece */
                            table {
                                width: 100% !important;
                                border-collapse: collapse !important;
                                margin-top: 20px !important;
                            }
                            td, th {
                                padding: 10px !important;
                                border: 1px solid #e2e8f0 !important;
                                font-size: 15px !important;
                            }
                            th {
                                background-color: #f1f5f9 !important;
                                color: #0f172a !important;
                            }
                        </style>
                        """
                        
                        # Limpiamos el body de scripts viejos pero dejamos el HTML
                        for tag in body(["script", "style", "link", "meta", "iframe", "frame"]):
                            tag.decompose()
                            
                        html_puro = estilo_maquillaje + str(body)
                    else:
                        html_puro = r.text
                        
                    components.html(html_puro, height=800, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar la página: {e}")
    else:
        st.info("👈 Seleccioná una opción del menú lateral o realizá una consulta directa por documento.")
        
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
                    r_cons = s.get(url_cons, headers=HEADERS)
                    soup_cons = BeautifulSoup(r_cons.text, 'html.parser')
                    
                    vs = soup_cons.find('input', {'name': '__VIEWSTATE'})
                    ev = soup_cons.find('input', {'name': '__EVENTVALIDATION'})
                    
                    if not vs:
                        st.error("No se pudo obtener el formulario de consulta del servidor.")
                    else:
                        payload = {
                            "__EVENTTARGET": "", "__EVENTARGUMENT": "",
                            "__VIEWSTATE": vs['value'],
                            "cboTipoDoc": tipo,
                            "txtDocumento": dni,
                            "imgConsultar.x": "10", "imgConsultar.y": "10"
                        }
                        if ev: payload["__EVENTVALIDATION"] = ev['value']
                        
                        r_res = s.post(url_cons, data=payload, headers=HEADERS)
                        soup_res = BeautifulSoup(r_res.text, 'html.parser')
                        
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
                            st.warning("No se pudo leer la tabla de resultados de la consulta.")
                except Exception as e:
                    st.error(f"Error al realizar la búsqueda: {e}")
