import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from io import StringIO
import pandas as pd
import re

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
# FUNCIÓN PARA EXTRAER CAMPOS DEL FORMULARIO
# ============================================================
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

# ============================================================
# ESTADO
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"
if "resultados" not in st.session_state:
    st.session_state.resultados = None

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
# 2. PORTAL (BÚSQUEDA POR DNI)
# ============================================================
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
        with c1: tipo_label = st.selectbox("Tipo Doc", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
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
                
                # Mapear el tipo doc
                soup_c = BeautifulSoup(r_cons.text, "html.parser")
                sel = soup_c.find("select", {"name": "cboTipoDoc"})
                if sel:
                    opciones = {o.get_text(strip=True).upper(): o.get("value", "") for o in sel.find_all("option")}
                    tipo_val = opciones.get(tipo_label.upper())
                    if tipo_val is None:
                        st.error(f"'{tipo_label}' no existe en el combo del portal.")
                        st.stop()
                else:
                    tipo_val = "2"
                
                # POST para búsqueda
                data.update({
                    "__EVENTTARGET": "",
                    "__EVENTARGUMENT": "",
                    "txtDocumento": dni,
                    "cboTipoDoc": tipo_val,
                    "txtNroOp": "",
                    "dgBusquedaBenef_NotReload": "",
                    "imgConsultarOT.x": "5",
                    "imgConsultarOT.y": "5",
                })
                
                post_url = urljoin(url_cons, action)
                r_res = s.post(post_url, data=data, headers={"Referer": url_cons})
                
                # Extraer la tabla de trámites
                soup_res = BeautifulSoup(r_res.text, 'html.parser')
                grid = soup_res.find(id="dgBusquedaBenef")
                
                if not grid:
                    st.warning("No se encontró la tabla de trámites. Revisá el HTML de la respuesta.")
                    st.code(r_res.text[:3000])
                else:
                    filas = grid.find_all('tr')
                    trámites = []
                    for f in filas[1:]:
                        celdas = f.find_all('td')
                        if len(celdas) >= 9:
                            # Extraer los IDs del trámite (pueden estar en un onclick o en un href)
                            # Buscamos el enlace del "ojito" o el onclick de la fila
                            link_detalle = f.find('a', href=True)
                            if link_detalle:
                                href = link_detalle['href']
                                # Buscamos los parámetros en el href (si es que los tiene)
                                # Si no, usamos los datos de la celda
                                pass
                            
                            # Por ahora, extraemos los datos visibles de la tabla
                            trámites.append({
                                "Nro. Autorización": celdas[1].text.strip(),
                                "OP": celdas[2].text.strip(),
                                "AUT Desde": celdas[3].text.strip(),
                                "AUT Hasta": celdas[4].text.strip(),
                                "OP Desde": celdas[5].text.strip(),
                                "OP Hasta": celdas[6].text.strip(),
                                "Programa": celdas[7].text.strip(),
                                "Farmacia": celdas[8].text.strip(),
                            })
                    
                    if trámites:
                        st.session_state.resultados = trámites
                        st.success(f"Se encontraron {len(trámites)} trámites.")
                    else:
                        st.warning("No se encontraron resultados para ese documento.")
                        st.session_state.resultados = None
                        
            except Exception as e:
                st.error(f"Error al buscar: {e}")
    
    if st.session_state.resultados:
        df = pd.DataFrame(st.session_state.resultados)
        st.dataframe(df, use_container_width=True, hide_index=True)
