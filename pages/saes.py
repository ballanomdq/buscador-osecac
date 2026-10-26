
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }
.saes-card { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-top: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.badge-verde { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
.badge-rojo { background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; }
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

if st.button("← Volver al Menú Principal"):
    try:
        st.switch_page("main.py")
    except Exception:
        st.warning("Función de retorno al menú principal no disponible en este entorno.")

if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "saes_menu" not in st.session_state:
    st.session_state.saes_menu = "consultas"
if "session_cookies" not in st.session_state:
    st.session_state.session_cookies = None

# ================= 1. LOGIN REAL (CORREGIDO A HTTP) =================
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
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
                    }
                    # ⬇️ ACÁ ESTÁ EL ARREGLO: HTTP en vez de HTTPS ⬇️
                    login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
                    
                    try:
                        r = session.get(login_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        
                        if not viewstate:
                            st.error("No se encontró el formulario de login. Puede que la página haya cambiado.")
                            st.stop()
                        
                        payload = {
                            '__VIEWSTATE': viewstate['value'],
                            'txtUsuario': usuario,
                            'txtPassword': password,
                            'btnIngresar': 'Ingresar'
                        }
                        
                        r_post = session.post(login_url, data=payload, headers=headers, timeout=30)
                        
                        if "Login" not in r_post.text and r_post.status_code == 200:
                            st.session_state.saes_logueado = True
                            st.session_state.usuario = usuario
                            st.session_state.password = password
                            st.session_state.session_cookies = session.cookies
                            st.success("✅ Acceso correcto.")
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos.")
                            
                    except requests.exceptions.Timeout:
                        st.error("⏳ El servidor de SAES tardó demasiado en responder.")
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ================= 2. PORTAL =================
else:
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.markdown("### 🏥 Sistema para OSECAC — Portal SAES")
        st.caption(f"Sesión activa | Usuario: {st.session_state.get('usuario', 'rballano')}")
    with head_col2:
        if st.button("🔒 Cerrar Sesión"):
            st.session_state.saes_logueado = False
            st.session_state.saes_menu = "consultas"
            st.session_state.session_cookies = None
            st.rerun()

    st.markdown("<hr style='margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

    menu_col, body_col = st.columns([1, 4])

    with menu_col:
        st.markdown("#### Menú Principal")
        if st.button("📁 Listados", use_container_width=True):
            st.session_state.saes_menu = "listados"
        if st.button("💊 Consultas (Medicamentos)", use_container_width=True):
            st.session_state.saes_menu = "consultas"
        if st.button("🌐 Consultas por delegación", use_container_width=True):
            st.session_state.saes_menu = "delegacion"
        if st.button("📋 Solicitudes de trámite", use_container_width=True):
            st.session_state.saes_menu = "solicitudes"

    with body_col:
        if st.session_state.saes_menu == "consultas":
            st.markdown("### Medicamentos - Consultas")
            
            with st.form("form_consulta_beneficiario"):
                col_orden, col_tipo, col_doc, col_check = st.columns([1, 1, 2, 2])
                with col_orden:
                    nro_orden = st.text_input("Nro. Orden:")
                with col_tipo:
                    tipo_doc = st.selectbox("Tipo Doc:", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
                with col_doc:
                    nro_doc = st.text_input("Nro. de Documento:", value="6705303")
                with col_check:
                    st.write("")
                    ver_solo_disp = st.checkbox("Ver sólo disposiciones")
                
                btn_buscar = st.form_submit_button("🔍 Consultar en SAES", use_container_width=True)

            if btn_buscar:
                with st.spinner("Buscando en SAES..."):
                    session = requests.Session()
                    session.cookies.update(st.session_state.session_cookies)
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    
                    # ⬇️ ACÁ TAMBIÉN HTTP ⬇️
                    consulta_url = "http://portal.gmssa.com.ar/saes/MedicamentosConsultas.aspx"
                    
                    try:
                        r = session.get(consulta_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        
                        if viewstate:
                            payload = {
                                '__VIEWSTATE': viewstate['value'],
                                'ddlTipoDocumento': tipo_doc,
                                'txtNroDocumento': nro_doc,
                                'btnBuscar': 'Buscar'
                            }
                            
                            r_resultado = session.post(consulta_url, data=payload, headers=headers, timeout=30)
                            soup_res = BeautifulSoup(r_resultado.text, 'html.parser')
                            tabla = soup_res.find('table', {'id': 'dgBusquedaBenef'})
                            
                            tramites_reales = []
                            if tabla:
                                filas = tabla.find_all('tr')
                                for fila in filas[1:]:
                                    celdas = fila.find_all('td')
                                    if len(celdas) >= 9:
                                        tramites_reales.append({
                                            "id": len(tramites_reales)+1,
                                            "aut": celdas[1].text.strip(),
                                            "op": celdas[2].text.strip(),
                                            "f_desde_aut": celdas[3].text.strip(),
                                            "f_hasta_aut": celdas[4].text.strip(),
                                            "f_desde_op": celdas[5].text.strip(),
                                            "f_hasta_op": celdas[6].text.strip(),
                                            "programa": celdas[7].text.strip(),
                                            "farmacia": celdas[8].text.strip(),
                                            "estado": "Ver detalle",
                                            "badge": "verde"
                                        })
                            
                            if tramites_reales:
                                st.session_state['resultados_reales'] = tramites_reales
                                st.success(f"Se encontraron {len(tramites_reales)} trámites.")
                            else:
                                st.warning("No se encontraron resultados para ese documento.")
                                st.session_state['resultados_reales'] = []
                        else:
                            st.error("La sesión expiró. Volvé a loguearte.")
                    except Exception as e:
                        st.error(f"Error en la búsqueda: {e}")

            if st.session_state.get('resultados_reales'):
                tramites = st.session_state['resultados_reales']
                df = pd.DataFrame(tramites)
                df_vis = df[["aut", "op", "programa", "f_desde_aut", "f_hasta_aut", "farmacia", "estado"]].copy()
                df_vis.columns = ["Nro. Autorización", "OP", "Programa", "AUT Desde", "AUT Hasta", "Farmacia", "Estado"]

                evento = st.dataframe(
                    df_vis,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="tabla_tramites_saes",
                )

                if evento and evento.selection and evento.selection.rows:
                    idx = evento.selection.rows[0]
                    fila_dict = tramites[idx]

                    @st.dialog("📄 Detalle del trámite", width="large")
                    def mostrar_detalle(fila):
                        st.markdown(f"### Nro. Autorización: **{fila['aut']}** (OP {fila['op']})")
                        st.divider()
                        st.markdown(f"""
                        <div class="saes-card">
                            <h4>Datos generales</h4>
                            <p><b>Programa:</b> {fila['programa']}</p>
                            <p><b>Farmacia:</b> {fila['farmacia']}</p>
                            <p><b>AUT:</b> {fila['f_desde_aut']} al {fila['f_hasta_aut']}</p>
                            <p><b>OP:</b> {fila['f_desde_op']} al {fila['f_hasta_op']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info("Los datos médicos y logísticos se extraerán en el próximo paso.")
                        if st.button("Cerrar", use_container_width=True):
                            st.rerun()

                    mostrar_detalle(fila_dict)

        elif st.session_state.saes_menu == "listados":
            st.markdown("### 📁 Listados")
            st.info("Módulo en construcción.")
        elif st.session_state.saes_menu == "delegacion":
            st.markdown("### 🌐 Consultas por delegación")
            st.info("Módulo en construcción.")
        elif st.session_state.saes_menu == "solicitudes":
            st.markdown("### 📋 Solicitudes de trámite")
            st.info("Módulo en construcción.")
