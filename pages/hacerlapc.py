import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import zipfile
from pathlib import Path

st.set_page_config(page_title="Robot OSECAC", layout="wide")
st.title("🤖 Robot OSECAC - Descarga Masiva de Actas")

# Crear carpeta de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "descargas_osecac")
Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

with st.form("datos_acceso"):
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("👤 Usuario OSECAC", value="FBOVONE")
        legajo = st.text_input("📋 Número de Legajo", value="7713")
    with col2:
        password = st.text_input("🔒 Contraseña", type="password", value="FBOVONE")
        ver_impresas = st.checkbox("✅ Ver Actas ya Impresas", value=True)
    
    col3, col4, col5 = st.columns([1,1,1])
    with col3:
        submit = st.form_submit_button("🚀 INICIAR DESCARGA MASIVA", use_container_width=True)

if submit:
    if not usuario or not password:
        st.error("❌ Completá usuario y contraseña")
    else:
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_area = st.empty()
        logs = []
        
        def add_log(msg):
            logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
            log_area.code("\n".join(logs[-20:]), language="text")
        
        add_log("🚀 Iniciando robot...")
        
        # Configurar Edge
        options = webdriver.EdgeOptions()
        options.add_argument("--disable-notifications")
        options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })
        
        driver = None
        
        try:
            add_log("🌐 Abriendo navegador...")
            driver = webdriver.Edge(options=options)
            driver.maximize_window()
            
            # 1. Login
            add_log("🔐 Accediendo a página de login...")
            driver.get("http://200.51.42.41:7980/Login.aspx")
            time.sleep(2)
            
            add_log(f"📝 Escribiendo usuario: {usuario}")
            campo_usuario = driver.find_element(By.ID, "ctl00_uLogin1_txtUsuario")
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)
            
            add_log("📝 Escribiendo clave...")
            campo_clave = driver.find_element(By.ID, "ctl00_uLogin1_txtClave")
            campo_clave.clear()
            campo_clave.send_keys(password)
            campo_clave.send_keys(Keys.ENTER)
            
            add_log("⏳ Esperando ingreso al sistema...")
            time.sleep(5)
            
            # 2. Navegar a la página de actas
            add_log("📂 Navegando a sincronización...")
            driver.get("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")
            time.sleep(3)
            
            # 3. Completar legajo
            add_log(f"🔢 Ingresando legajo: {legajo}")
            campo_legajo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_cMain_gvActasSincronizadas_Legajo"))
            )
            campo_legajo.clear()
            campo_legajo.send_keys(legajo)
            
            # 4. Tildar "Ver Actas ya Impresas" (si existe)
            if ver_impresas:
                try:
                    add_log("☑️ Activando 'Ver Actas ya Impresas'...")
                    chk_impresas = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_VerImpresas")
                    if not chk_impresas.is_selected():
                        chk_impresas.click()
                except:
                    add_log("⚠️ No se encontró el checkbox 'Ver Actas ya Impresas'")
            
            # 5. Buscar actas
            add_log("🔍 Buscando actas...")
            btn_buscar = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_btnBuscar")
            btn_buscar.click()
            time.sleep(5)
            
            # 6. Función para obtener actas
            def obtener_actas():
                tabla = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas")
                checkboxes = tabla.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                actas = []
                for cb in checkboxes:
                    if cb.is_enabled():
                        actas.append(cb)
                return actas
            
            # 7. Función para procesar lote
            def procesar_lote(inicio, total):
                status_text.text(f"📄 Procesando actas {inicio+1} a {min(inicio+2, total)} de {total}")
                progress_bar.progress((inicio+2)/total if inicio+2 <= total else 1.0)
                
                # Seleccionar 2 actas
                actas = obtener_actas()
                for i, cb in enumerate(actas):
                    if i < inicio or i >= inicio+2:
                        if cb.is_selected():
                            cb.click()
                    else:
                        if not cb.is_selected():
                            cb.click()
                
                time.sleep(1)
                
                # Click en imprimir
                btn_imprimir = driver.find_element(By.ID, "ctl00_cMain_gvActasSincronizadas_6")
                btn_imprimir.click()
                add_log(f"🖨️ Abriendo impresión para actas {inicio+1}-{inicio+2}")
                
                time.sleep(4)
                
                # Cambiar a la ventana modal
                ventanas = driver.window_handles
                if len(ventanas) > 1:
                    driver.switch_to.window(ventanas[1])
                    add_log("🪟 Cambiando a ventana modal...")
                    
                    time.sleep(2)
                    
                    # Tildar "Imprimir S/Ciudad"
                    try:
                        chk_ciudad = driver.find_element(By.ID, "chkImpSCiudad")
                        if not chk_ciudad.is_selected():
                            chk_ciudad.click()
                            add_log("☑️ Marcando 'Imprimir S/Ciudad'")
                    except:
                        add_log("⚠️ No se encontró 'chkImpSCiudad'")
                    
                    time.sleep(1)
                    
                    # Click en Imprimir
                    try:
                        btn_imprimir_modal = driver.find_element(By.ID, "lbGrabar")
                        btn_imprimir_modal.click()
                        add_log("🖨️ Click en 'Imprimir' dentro del modal")
                    except:
                        add_log("⚠️ No se encontró 'lbGrabar', intentando __doPostBack")
                        driver.execute_script("__doPostBack('lbGrabar','');")
                    
                    time.sleep(5)
                    
                    # Volver a la ventana principal
                    driver.close()
                    driver.switch_to.window(ventanas[0])
                    add_log("↩️ Volviendo a ventana principal")
                
                time.sleep(3)
            
            # 8. Obtener todas las actas y procesar
            actas = obtener_actas()
            total_actas = len(actas)
            add_log(f"📊 Total de actas encontradas: {total_actas}")
            
            if total_actas == 0:
                st.warning("⚠️ No se encontraron actas. Verificá el legajo y los filtros.")
            else:
                status_text.text(f"📊 Se encontraron {total_actas} actas para descargar")
                
                for inicio in range(0, total_actas, 2):
                    procesar_lote(inicio, total_actas)
                
                add_log("✅ PROCESO COMPLETADO!")
                status_text.text(f"✅ Descarga completada. {total_actas} actas procesadas.")
                progress_bar.progress(1.0)
                
                # Crear ZIP con todas las descargas
                add_log("📦 Creando archivo ZIP...")
                zip_path = os.path.join(DOWNLOAD_DIR, "actas_osecac.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for archivo in os.listdir(DOWNLOAD_DIR):
                        if archivo.endswith('.pdf'):
                            zipf.write(os.path.join(DOWNLOAD_DIR, archivo), archivo)
                
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="📥 DESCARGAR TODAS LAS ACTAS (ZIP)",
                        data=f,
                        file_name="actas_osecac.zip",
                        mime="application/zip"
                    )
                
        except Exception as e:
            add_log(f"❌ ERROR: {str(e)}")
            st.error(f"Error: {str(e)}")
        
        finally:
            if driver:
                add_log("👋 Cerrando navegador...")
                driver.quit()
