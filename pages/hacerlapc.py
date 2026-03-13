import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

st.set_page_config(page_title="PUCO RÁPIDO - SELENIUM", layout="wide")
st.title("🛡️ Buscador PUCO (Modo Selenium)")
st.info("Este modo es más lento pero más seguro contra bloqueos.")

dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150)
buscar_btn = st.button("🚀 Iniciar Búsqueda Segura", type="primary")

def consultar_con_selenium(dni):
    options = Options()
    options.add_argument("--headless") # No abre ventana física
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 1. Entrar a la web
        driver.get("https://sisa.msal.gov.ar/sisa/#pms/pms_poblacion_padrones_consulta_publica")
        
        # 2. Esperar al campo de texto del DNI
        wait = WebDriverWait(driver, 15)
        campo_dni = wait.until(EC.presence_of_element_status(By.CSS_SELECTOR, "input[type='text']"))
        
        # 3. Limpiar e ingresar DNI
        campo_dni.clear()
        campo_dni.send_keys(str(dni))
        
        # 4. Click en buscar (buscamos por texto o clase)
        boton = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar')]")
        boton.click()
        
        # 5. Esperar a que aparezca la tabla de resultados
        time.sleep(3) # Pausa necesaria para que cargue el GWT
        
        # 6. Extraer datos de la tabla
        filas = driver.find_elements(By.TAG_NAME, "tr")
        if len(filas) > 1:
            columnas = filas[1].find_elements(By.TAG_NAME, "td")
            # Ajustamos índices según lo que ves en pantalla (DNI, Nombre, Obra Social)
            return {
                "DNI": dni,
                "Cobertura": columnas[2].text if len(columnas) > 2 else "Sin Datos",
                "Beneficiario": columnas[3].text if len(columnas) > 3 else "-",
                "Estado": "✅ OK"
            }
        return {"DNI": dni, "Cobertura": "No hallado", "Beneficiario": "-", "Estado": "❌ Vacío"}

    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error de carga", "Beneficiario": str(e)[:30], "Estado": "📡 Error"}
    finally:
        driver.quit()

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    res = []
    barra = st.progress(0)
    
    for i, d in enumerate(dnis):
        st.write(f"🕵️ Buscando DNI: {d}...")
        res.append(consultar_con_selenium(d))
        barra.progress((i + 1) / len(dnis))
    
    st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
