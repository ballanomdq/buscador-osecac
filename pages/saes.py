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
</style>
""", unsafe_allow_html=True)

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# --- ESTADO ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "session" not in st.session_state:
    st.session_state.session = None
if "usuario" not in st.session_state:
    st.session_state.usuario = "rballano"

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
# 2. PORTAL (CON EL IFRAME Y LOS TOKENS REALES)
# ============================================================
else:
    s = st.session_state.session

    # Barra lateral
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.rerun()

    st.markdown("## 🏥 Portal SAES - Consultas")

    try:
        # 1. Obtenemos la página de consultas REAL (con sus tokens)
        url_cons = BASE_URL + "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
        r_cons = s.get(url_cons, headers=HEADERS)
        soup_cons = BeautifulSoup(r_cons.text, 'html.parser')
        
        vs = soup_cons.find('input', {'name': '__VIEWSTATE'})
        ev = soup_cons.find('input', {'name': '__EVENTVALIDATION'})

        if not vs:
            st.error("No se pudo cargar el formulario.")
        else:
            # 2. Construimos el HTML que vamos a inyectar en el iframe
            #    Este HTML contiene el formulario con los tokens reales
            #    y su acción apunta a la URL correcta.
            html_form = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ background-color: #f8fafc; font-family: sans-serif; color: #0f172a; padding: 20px; }}
                    label {{ font-size: 16px; font-weight: 600; margin-right: 10px; }}
                    input[type="text"], select {{ font-size: 16px; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; margin-right: 15px; }}
                    input[type="submit"] {{ font-size: 16px; padding: 10px 20px; background: #0284c7; color: white; border: none; border-radius: 6px; cursor: pointer; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    td, th {{ padding: 10px; border: 1px solid #e2e8f0; font-size: 15px; }}
                    th {{ background-color: #f1f5f9; color: #0f172a; }}
                </style>
            </head>
            <body>
                <form method="post" action="{url_cons}">
                    <input type="hidden" name="__VIEWSTATE" value="{vs['value']}">
                    <input type="hidden" name="__EVENTVALIDATION" value="{ev['value'] if ev else ''}">
                    <input type="hidden" name="__EVENTTARGET" value="txtDocumento">
                    <input type="hidden" name="__EVENTARGUMENT" value="">
                    
                    <label>Nro. Orden:</label>
                    <input type="text" name="txtNroOp" value="">
                    
                    <label>Nro. Documento:</label>
                    <select name="cboTipoDoc">
                        <option value="1">DNI</option>
                        <option value="2" selected>LC</option>
                        <option value="3">LE</option>
                        <option value="4">CI</option>
                        <option value="5">PAS</option>
                        <option value="6">S/D</option>
                    </select>
                    <input type="text" name="txtDocumento" value="6705303">
                    
                    <label>Ver sólo disposiciones:</label>
                    <input type="checkbox" name="chkSoloDisposiciones">
                    
                    <br><br>
                    <input type="submit" value="🔍 Buscar">
                </form>
            </body>
            </html>
            """
            
            # 3. Mostramos el iframe con el formulario inyectado
            components.html(html_form, height=600, scrolling=True)

    except Exception as e:
        st.error(f"Error al cargar el formulario: {e}")
