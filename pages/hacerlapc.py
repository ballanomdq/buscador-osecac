import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuración de la página ---
st.set_page_config(page_title="HACER LA PC - PUCO", layout="wide")

st.title("💻 HACER LA PC - Consulta Masiva PUCO (SISA)")

# UI de entrada
with st.container():
    st.subheader("📋 Ingreso de DNI")
    dni_input = st.text_area("Escribí un DNI por línea:", height=150)
    buscar_btn = st.button("🚀 Buscar", type="primary")

result_container = st.container()
with result_container:
    st.subheader("📊 Resultados de la consulta")
    status_text = st.empty()
    progress_bar = st.progress(0)

def consultar(dni_list):
    resultados = []
    
    # --- CONFIGURACIÓN PARA STREAMLIT CLOUD ---
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium" # Ruta fija del packages.txt

    # Intentamos abrir el driver con la ruta directa del sistema
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        st.error(f"Error al iniciar navegador: {e}")
        return pd.DataFrame()

    try:
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        time.sleep(5)
        
        # Click en PUCO
        puco = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'PUCO')]"))
        )
        driver.execute_script("arguments[0].click();", puco)
        
        # Campo DNI
        dni_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni')]"))
        )

        for idx, dni in enumerate(dni_list):
            status_text.text(f"Consultando {dni}...")
            dni_field.clear()
            dni_field.send_keys(str(dni))
            
            # Click buscar
            driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']").click()
            
            try:
                # Esperar tabla
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table")))
                celdas = driver.find_elements(By.TAG_NAME, "td")
                cobertura = celdas[0].text if celdas else "Sin datos"
                denom = celdas[1].text if len(celdas) > 1 else "-"
            except:
                cobertura = "No hallado"
                denom = "-"

            resultados.append({"DNI": dni, "Cobertura": cobertura, "Obra Social": denom})
            progress_bar.progress((idx + 1) / len(dni_list))
            time.sleep(random.uniform(3, 5))

    except Exception as e:
        st.error(f"Error durante la consulta: {e}")
    finally:
        driver.quit()
    
    return pd.DataFrame(resultados)

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    df = consultar(dnis)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Descargar CSV", df.to_csv(index=False), "resultado.csv")
