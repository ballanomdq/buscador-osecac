from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Configuración local (con ventana visible para ver qué pasa)
options = Options()
# options.add_argument("--headless=new") # Descomentá si querés que sea invisible

driver = webdriver.Chrome(options=options)

try:
    print("1. Abriendo login...")
    driver.get("http://portal.gmssa.com.ar/saes/Login.aspx")
    wait = WebDriverWait(driver, 15)
    
    print("2. Logueando...")
    wait.until(EC.presence_of_element_located((By.NAME, "txtUser"))).send_keys("rballano")
    driver.find_element(By.NAME, "txtPassword").send_keys("654321")
    driver.find_element(By.NAME, "imgbtnSend").click()
    time.sleep(3)
    
    print(f"   URL después del login: {driver.current_url}")
    
    print("3. Haciendo clic en 'Adm. de Medicamentos'...")
    menu_med = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Adm. de Medicamentos')]")))
    menu_med.click()
    time.sleep(1)
    
    print("4. Haciendo clic en 'Consultas'...")
    link_consultas = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consultas')]")))
    link_consultas.click()
    time.sleep(3)
    
    # CAMBIAMOS AL FRAME DE TRABAJO PARA VER LA URL REAL
    print("5. Cambiando al frame de trabajo...")
    driver.switch_to.frame("WorkSpace")
    
    print("==================================================")
    print(f"✅ URL REAL DE CONSULTAS: {driver.current_url}")
    print("==================================================")
    
    print("6. Cookies actuales:")
    for cookie in driver.get_cookies():
        print(f"   - {cookie['name']}: {cookie['value']}")
        
    input("Presioná Enter para cerrar el navegador...")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
