import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
import zipfile

st.set_page_config(page_title="Robot OSECAC", layout="wide")
st.title("🤖 Robot OSECAC - Descarga Masiva de Actas (IE Mode)")

with st.form("datos_acceso"):
    usuario = st.text_input("👤 Usuario OSECAC", value="FBOVONE")
    password = st.text_input("🔒 Contraseña", type="password", value="FBOVONE")
    legajo = st.text_input("📋 Número de Legajo", value="7713")
    submit = st.form_submit_button("🚀 INICIAR DESCARGA")

if submit:
    log_area = st.empty()
    logs = []

    def add_log(msg):
        logs.append(msg)
        log_area.code("\n".join(logs[-30:]), language="text")

    add_log("🚀 Iniciando navegador en modo Internet Explorer...")

    # Configuración de Edge en modo IE (Compatibility Mode)
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--ie-mode")                    # Fuerza IE Mode
    edge_options.add_argument("--inprivate")                  # Opcional
    # edge_options.add_argument("--headless")                 # Descomenta si quieres sin ventana (puede fallar en IE Mode)

    # Ruta al driver de Edge (msedgedriver). Debe coincidir con tu versión de Edge.
    driver_path = "msedgedriver.exe"   # ← Cambia por la ruta completa si es necesario

    try:
        driver = webdriver.Edge(options=edge_options, executable_path=driver_path)
        wait = WebDriverWait(driver, 20)

        add_log("🌐 Abriendo página de login...")
        driver.get("http://200.51.42.41:7980/Login.aspx")

        # Login
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_UcLogin1_txtUsuario")))
        driver.find_element(By.ID, "ctl00_UcLogin1_txtUsuario").send_keys(usuario)
        driver.find_element(By.ID, "ctl00_UcLogin1_txtClave").send_keys(password)
        driver.find_element(By.ID, "ctl00_UcLogin1_btnIngresar").click()

        add_log("🔐 Login enviado...")

        # Esperar redirección y ir a la página de actas
        time.sleep(4)
        driver.get("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")

        add_log(f"🔍 Buscando legajo {legajo}...")

        # Buscar por legajo (ajusta los IDs si cambian)
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo")))
        driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo").send_keys(legajo)
        driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_btnBuscar").click()

        time.sleep(5)

        # Aquí puedes agregar lógica para seleccionar las actas (tildar checkboxes)
        # Ejemplo simple: tildar las primeras 2 checkboxes de la grilla
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id*='gvActasSincronizadas']")
        for cb in checkboxes[:2]:   # primeras 2
            if not cb.is_selected():
                cb.click()

        add_log("✅ Actas seleccionadas")

        # Clic en el botón que abre el modal de impresión (ajusta el ID)
        btn_imprimir = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_6")  # el mismo que usabas antes
        btn_imprimir.click()

        add_log("🖨️ Abriendo modal de impresión...")

        # Esperar al modal y automatizar "Imprimir S/Ciudad" + Imprimir
        time.sleep(3)   # espera a que aparezca el popup/modal

        # Buscar checkbox "Imprimir S/Ciudad" (ajusta según el texto o ID exacto)
        try:
            chk_sin_ciudad = driver.find_element(By.XPATH, "//label[contains(text(),'Imprimir S/Ciudad')]/preceding-sibling::input[@type='checkbox']")
            if not chk_sin_ciudad.is_selected():
                chk_sin_ciudad.click()
            add_log("☑️ Checkbox 'Imprimir S/Ciudad' activado")
        except:
            add_log("⚠️ No se encontró checkbox S/Ciudad (puede estar en popup)")

        # Clic en link "Imprimir"
        try:
            imprimir_link = driver.find_element(By.XPATH, "//a[contains(text(),'Imprimir')]")
            imprimir_link.click()
            add_log("✅ Clic en Imprimir ejecutado")
        except:
            add_log("❌ No se encontró el link 'Imprimir'")

        st.success("Proceso completado. Revisa la ventana del navegador.")
        add_log("🎉 Proceso finalizado. Descarga debería iniciarse en el navegador.")

    except Exception as e:
        add_log(f"❌ Error: {str(e)}")
        st.error("Ocurrió un error durante la automatización.")
    finally:
        # driver.quit()   # Descomenta si quieres cerrar automáticamente (mejor dejar abierto para ver qué pasa)
        pass
