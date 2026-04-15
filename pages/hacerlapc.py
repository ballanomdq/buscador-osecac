if submit:
    log_area = st.empty()
    logs = []

    def add_log(msg):
        logs.append(msg)
        log_area.code("\n".join(logs[-30:]), language="text")

    add_log("🚀 Iniciando navegador en modo Internet Explorer (IE Mode)...")

    try:
        from selenium import webdriver
        from selenium.webdriver.ie.service import Service as IEService
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        # ================== CONFIGURACIÓN ==================
        # Cambia esta ruta por la ubicación real de tu IEDriverServer.exe
        ie_driver_path = r"C:\ruta\a\tu\IEDriverServer.exe"   # ←←← AJUSTA ESTO

        # Ruta al ejecutable de Microsoft Edge (normalmente esta)
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

        # Configuración para IE Mode
        ie_options = webdriver.IeOptions()
        ie_options.attach_to_edge_chrome = True
        ie_options.edge_executable_path = edge_path
        
        # Opcionales recomendadas para IE Mode
        ie_options.ignore_zoom_level = True
        ie_options.require_window_focus = True   # ayuda con popups y foco

        # Crear servicio
        service = IEService(executable_path=ie_driver_path)

        # Iniciar driver en IE Mode
        driver = webdriver.Ie(service=service, options=ie_options)
        wait = WebDriverWait(driver, 25)

        add_log("🌐 Navegador IE Mode iniciado correctamente")

        # ================== LOGIN ==================
        add_log("📝 Abriendo página de login...")
        driver.get("http://200.51.42.41:7980/Login.aspx")

        wait.until(EC.presence_of_element_located((By.ID, "ctl00_UcLogin1_txtUsuario")))
        driver.find_element(By.ID, "ctl00_UcLogin1_txtUsuario").clear()
        driver.find_element(By.ID, "ctl00_UcLogin1_txtUsuario").send_keys(usuario)
        driver.find_element(By.ID, "ctl00_UcLogin1_txtClave").clear()
        driver.find_element(By.ID, "ctl00_UcLogin1_txtClave").send_keys(password)
        driver.find_element(By.ID, "ctl00_UcLogin1_btnIngresar").click()

        add_log("🔐 Login enviado... esperando redirección")
        time.sleep(5)

        # ================== IR A ACTAS ==================
        add_log("📂 Navegando a la página de actas...")
        driver.get("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")
        time.sleep(4)

        # ================== BUSCAR POR LEGAJO ==================
        add_log(f"🔍 Buscando legajo {legajo}...")
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo")))
        
        legajo_field = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo")
        legajo_field.clear()
        legajo_field.send_keys(legajo)
        
        driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_btnBuscar").click()
        time.sleep(6)

        # ================== SELECCIONAR ACTAS (ejemplo: primeras 2) ==================
        add_log("☑️ Seleccionando actas...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id*='gvActasSincronizadas']")
        seleccionadas = 0
        for cb in checkboxes:
            if not cb.is_selected():
                cb.click()
                seleccionadas += 1
            if seleccionadas >= 2:
                break

        add_log(f"✅ {seleccionadas} actas seleccionadas")

        # ================== ABRIR MODAL DE IMPRESIÓN ==================
        add_log("🖨️ Abriendo ventana/modal de impresión...")
        btn_imprimir = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_6")
        btn_imprimir.click()

        time.sleep(4)   # espera crítica para que aparezca el modal/popup

        # ================== AUTOMATIZAR DENTRO DEL MODAL ==================
        add_log("🔧 Intentando activar 'Imprimir S/Ciudad' y clic en Imprimir...")

        try:
            # Buscar checkbox por texto (funciona bien en IE)
            chk_sin_ciudad = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox'][following-sibling::label[contains(text(),'Imprimir S/Ciudad')]]"))
            )
            if not chk_sin_ciudad.is_selected():
                chk_sin_ciudad.click()
            add_log("✅ Checkbox 'Imprimir S/Ciudad' activado")
        except:
            add_log("⚠️ No se encontró el checkbox S/Ciudad automáticamente")

        try:
            # Clic en el link "Imprimir"
            link_imprimir = driver.find_element(By.XPATH, "//a[contains(text(),'Imprimir') or contains(.,'Imprimir')]")
            link_imprimir.click()
            add_log("✅ Clic en 'Imprimir' ejecutado - La descarga debería comenzar")
        except:
            add_log("❌ No se encontró el link 'Imprimir'")

        st.success("🚀 Proceso lanzado en el navegador. Revisa la ventana de Edge (IE Mode) para ver si se descargan los PDFs.")

    except Exception as e:
        add_log(f"❌ Error: {str(e)}")
        st.error(f"Ocurrió un error: {str(e)}")
    finally:
        # No hacemos driver.quit() para que puedas ver qué pasa en el navegador
        pass
