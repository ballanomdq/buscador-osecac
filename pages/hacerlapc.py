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
        from selenium.webdriver.ie.options import IeOptions
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.microsoft import IEDriverManager
        import time

        # ================== CONFIGURACIÓN IE MODE ==================
        ie_options = IeOptions()
        ie_options.attach_to_edge_chrome = True
        # ie_options.edge_executable_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # normalmente no es necesario

        ie_options.ignore_zoom_level = True
        ie_options.require_window_focus = True

        # webdriver-manager descarga IEDriverServer automáticamente
        driver_path = IEDriverManager().install()
        service = IEService(driver_path)

        driver = webdriver.Ie(service=service, options=ie_options)
        wait = WebDriverWait(driver, 25)

        add_log("🌐 Navegador IE Mode iniciado correctamente (usando webdriver-manager)")

        # ================== LOGIN ==================
        add_log("📝 Abriendo página de login...")
        driver.get("http://200.51.42.41:7980/Login.aspx")

        wait.until(EC.presence_of_element_located((By.ID, "ctl00_UcLogin1_txtUsuario")))
        driver.find_element(By.ID, "ctl00_UcLogin1_txtUsuario").send_keys(usuario)
        driver.find_element(By.ID, "ctl00_UcLogin1_txtClave").send_keys(password)
        driver.find_element(By.ID, "ctl00_UcLogin1_btnIngresar").click()

        add_log("🔐 Login enviado...")
        time.sleep(5)

        # ================== IR A ACTAS Y BUSCAR LEGAJO ==================
        add_log("📂 Navegando a actas...")
        driver.get("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")
        time.sleep(4)

        add_log(f"🔍 Buscando legajo {legajo}...")
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo")))
        driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo").send_keys(legajo)
        driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_btnBuscar").click()
        time.sleep(6)

        # ================== TILDAR ACTAS (primeras 2) ==================
        add_log("☑️ Seleccionando actas...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id*='gvActasSincronizadas']")
        cont = 0
        for cb in checkboxes:
            if not cb.is_selected():
                cb.click()
                cont += 1
            if cont >= 2:
                break
        add_log(f"✅ {cont} actas seleccionadas")

        # ================== ABRIR MODAL ==================
        add_log("🖨️ Abriendo modal de impresión...")
        btn = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_6")
        btn.click()
        time.sleep(4)

        # ================== DENTRO DEL MODAL ==================
        add_log("🔧 Automatizando 'Imprimir S/Ciudad' + Imprimir...")
        try:
            # Checkbox Imprimir S/Ciudad (ajusta el XPath si no lo encuentra)
            chk = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Imprimir S/Ciudad')]/preceding-sibling::input")))
            if not chk.is_selected():
                chk.click()
            add_log("✅ Checkbox 'Imprimir S/Ciudad' activado")
        except:
            add_log("⚠️ No se encontró checkbox S/Ciudad (puede variar)")

        try:
            link_imprimir = driver.find_element(By.XPATH, "//a[contains(text(),'Imprimir')]")
            link_imprimir.click()
            add_log("✅ ¡Clic en Imprimir ejecutado! Revisa la ventana del navegador.")
        except:
            add_log("❌ No se encontró el link 'Imprimir'")

        st.success("✅ Proceso iniciado en el navegador Edge (IE Mode). La descarga debería comenzar ahí.")

    except Exception as e:
        add_log(f"❌ Error: {str(e)}")
        st.error(f"Error durante la automatización: {str(e)}")
    finally:
        # driver.quit()  # Descomenta solo cuando todo funcione bien
        pass
