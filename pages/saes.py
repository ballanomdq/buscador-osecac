import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import StringIO
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

def form_payload(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        return {}, ""
    data = {}
    for el in form.find_all(["input", "select", "textarea"]):
        name = el.get("name")
        if not name:
            continue
        if el.name == "select":
            opt = el.find("option", selected=True) or el.find("option")
            data[name] = opt.get("value", "") if opt else ""
        elif el.name == "textarea":
            data[name] = el.text
        else:
            t = (el.get("type") or "text").lower()
            if t in ("submit", "button", "image", "file"):
                continue
            if t in ("checkbox", "radio") and not el.has_attr("checked"):
                continue
            data[name] = el.get("value", "")
    return data, form.get("action", "")

# --- ESTADO ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"
if "resultados" not in st.session_state:
    st.session_state.resultados = None

# --- LOGIN ---
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

# --- PORTAL ---
else:
    s = st.session_state.session

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.session_state.resultados = None
            st.rerun()

    st.markdown("## 🏥 Portal SAES - Consultas")
    
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
                data, action = form_payload(r_cons.text)
                
                # --- LA CLAVE: FORZAR NotReload A False ---
                data.update({
                    "__EVENTTARGET": "",
                    "__EVENTARGUMENT": "",
                    "txtDocumento": dni,
                    "cboTipoDoc": tipo,
                    "txtNroOp": "",
                    "dgBusquedaBenef_NotReload": "False",  # <--- ACÁ
                    "imgConsultarOT.x": "5",
                    "imgConsultarOT.y": "5",
                })
                
                post_url = urljoin(url_cons, action)
                r_res = s.post(post_url, data=data, headers={"Referer": url_cons})
                
                soup_res = BeautifulSoup(r_res.text, 'html.parser')
                grid = soup_res.find(id="dgBusquedaBenef")
                
                if grid:
                    try:
                        df = pd.read_html(StringIO(str(grid)))[0]
                        st.session_state.resultados = df
                        st.success(f"Se encontraron {len(df)} trámites.")
                    except Exception:
                        st.session_state.resultados = "no_data"
                        st.warning("La tabla no tiene datos legibles.")
                else:
                    st.session_state.resultados = None
                    st.warning("No se encontró la tabla de resultados. Revisá el HTML de la respuesta.")
                    st.code(r_res.text[:3000])
                    
            except Exception as e:
                st.error(f"Error al buscar: {e}")
    
    if st.session_state.resultados is not None:
        if isinstance(st.session_state.resultados, pd.DataFrame):
            st.dataframe(st.session_state.resultados, use_container_width=True, hide_index=True)
        else:
            st.info("No se encontraron resultados para ese documento.")
