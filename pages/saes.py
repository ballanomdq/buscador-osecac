import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIÓN MAESTRA: SCRAPING CON SELENIUM (configurada para Streamlit Cloud)
# ============================================================
def buscar_en_saes(usuario, password, tipo_doc, nro_doc):
    # Configuramos el navegador invisible
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # En Streamlit Cloud, el binario de chrome está en /usr/bin/chromium
    options.binary_location = "/usr/bin/chromium"
    
    try:
        # Usamos webdriver-manager para descargar el driver correcto
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        st.error(f"Error al iniciar el navegador: {e}")
        return None

    try:
        # 1. LOGIN
        driver.get("http://portal.gmssa.com.ar/saes/Login.aspx")
        wait = WebDriverWait(driver, 20)
        
        # Completamos usuario y clave
        wait.until(EC.presence_of_element_located((By.NAME, "txtUser"))).send_keys(usuario)
        driver.find_element(By.NAME, "txtPassword").send_keys(password)
        driver.find_element(By.NAME, "imgbtnSend").click()
        
        # 2. VERIFICAMOS QUE ENTRÓ
        time.sleep(3)
        if "welcome" not in driver.current_url and "Login" in driver.current_url:
            st.error("Login fallido. Verificá usuario y contraseña.")
            driver.quit()
            return None
        
        # 3. HACEMOS CLIC EN EL MENÚ
        # Buscamos el link de "Adm. de Medicamentos"
        menu_medicamentos = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Adm. de Medicamentos')]")))
        menu_medicamentos.click()
        time.sleep(1)
        
        # Ahora buscamos el link de "Consultas"
        link_consultas = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consultas')]")))
        link_consultas.click()
        time.sleep(2)
        
        # 4. COMPLETAMOS EL FORMULARIO DE BÚSQUEDA
        # Tipo de documento
        select_tipo = wait.until(EC.presence_of_element_located((By.ID, "cboTipoDoc")))
        Select(select_tipo).select_by_visible_text(tipo_doc)
        
        # Número de documento
        input_doc = driver.find_element(By.ID, "txtDocumento")
        input_doc.clear()
        input_doc.send_keys(nro_doc)
        
        # Hacemos clic en el botón de buscar (el icono de la lupa)
        boton_buscar = driver.find_element(By.ID, "imgConsultar")
        boton_buscar.click()
        time.sleep(3) # Esperamos a que cargue la tabla
        
        # 5. EXTRAEMOS LA TABLA DE RESULTADOS
        tabla = driver.find_element(By.ID, "dgBusquedaBenef")
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        
        resultados = []
        for fila in filas[1:]: # Saltamos el encabezado
            celdas = fila.find_elements(By.TAG_NAME, "td")
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
        
        driver.quit()
        return resultados
        
    except Exception as e:
        st.error(f"Error durante el scraping: {e}")
        driver.quit()
        return None

# ============================================================
# INTERFAZ DE USUARIO
# ============================================================
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False

if not st.session_state.saes_logueado:
    st.markdown("## 🔑 Acceso al SAES")
    with st.form("form_login"):
        c_usr, c_pwd = st.columns(2)
        with c_usr: usuario = st.text_input("Usuario:", value="rballano")
        with c_pwd: password = st.text_input("Contraseña:", type="password")
        
        if st.form_submit_button("🚀 Entrar al SAES", use_container_width=True):
            if usuario and password:
                st.session_state.saes_logueado = True
                st.session_state.usuario = usuario
                st.session_state.password = password
                st.rerun()
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.saes_logueado = False
            st.rerun()
    
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
        with st.spinner("Conectando con SAES (esto puede tardar unos segundos)..."):
            resultados = buscar_en_saes(
                st.session_state.usuario, 
                st.session_state.password, 
                tipo_doc, 
                nro_doc
            )
            
            if resultados:
                st.success(f"Se encontraron {len(resultados)} trámites.")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron resultados para ese documento.")
