import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

def ejecutar_robot_osecac():
    # Contenedor para el informe en tiempo real en la página
    status = st.empty()
    log_area = st.empty()
    informe = []

    def actualizar_informe(mensaje):
        informe.append(f"[{time.strftime('%H:%M:%S')}] {mensaje}")
        log_area.code("\n".join(informe))

    # Configuración de Edge
    options = Options()
    # options.add_argument("--headless") # Descomenta esto si querés que no se vea la ventana del robot
    
    try:
        actualizar_informe("Iniciando navegador Edge...")
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        wait = WebDriverWait(driver, 15)
        
        actualizar_informe("Accediendo al Portal OSECAC...")
        driver.get("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")
        driver.maximize_window()

        while True:
            # Buscar checkboxes pendientes
            xpath = "//input[contains(@id, 'gvActasSincronizadas') and @type='checkbox' and not(@checked)]"
            checkboxes = driver.find_elements(By.XPATH, xpath)

            if not checkboxes:
                actualizar_informe(">>> FIN DEL PROCESO: No quedan actas pendientes.")
                break

            actualizar_informe(f"Procesando tanda de {min(2, len(checkboxes))} actas...")
            
            # Marcar 2 actas
            for i in range(min(2, len(checkboxes))):
                actualizar_informe(f"Marcando acta fila {i+1}...")
                checkboxes[i].click()
                time.sleep(0.5)

            # Click en Imprimir Masivo
            ventana_principal = driver.current_window_handle
            btn_masivo = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_6")
            btn_masivo.click()

            # Manejo de la ventana flotante
            actualizar_informe("Esperando ventana de impresión...")
            wait.until(lambda d: len(d.window_handles) > 1)

            for handle in driver.window_handles:
                if handle != ventana_principal:
                    driver.switch_to.window(handle)
                    break

            # --- ACCIONES DENTRO DE LA VENTANA ---
            try:
                # Tildar S/Ciudad
                chk_ciudad = wait.until(EC.element_to_be_clickable((By.ID, "chkImpSCiudad")))
                if not chk_ciudad.is_selected():
                    chk_ciudad.click()
                    actualizar_informe("✓ Casillero 'S/Ciudad' tildado.")

                # Click en Imprimir (lbGrabar)
                btn_imprimir = driver.find_element(By.ID, "lbGrabar")
                btn_imprimir.click()
                actualizar_informe("✓ Orden de impresión enviada.")
                
                time.sleep(6) # Espera para que inicie la descarga
                driver.close()
            except Exception as e:
                actualizar_informe(f"⚠️ Error en ventana: {str(e)}")
                if len(driver.window_handles) > 1: driver.close()

            driver.switch_to.window(ventana_principal)
            actualizar_informe("Esperando 3 segundos para la siguiente tanda...")
            time.sleep(3)

    except Exception as e:
        st.error(f"Error crítico: {e}")
        actualizar_informe(f"❌ ERROR: {str(e)}")
    finally:
        actualizar_informe("Cerrando navegador...")
        driver.quit()

# --- INTERFAZ DE STREAMLIT ---
st.title("🤖 Automatizador de Actas OSECAC")
st.info("Este robot marcará de a 2 actas, tildará 'S/Ciudad' y descargará los archivos automáticamente.")

if st.button("🚀 INICIAR DESCARGA MASIVA"):
    ejecutar_robot_osecac()
