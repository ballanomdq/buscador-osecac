import streamlit as st
import pandas as pd
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# --- Configuración de la página ---
st.set_page_config(page_title="HACER LA PC - PUCO", layout="wide")

st.title("💻 HACER LA PC - Consulta Masiva PUCO (SISA)")
st.markdown("""
    <style>
    .result-container {
        border: 1px solid #38bdf8;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        background-color: rgba(30, 41, 59, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.subheader("📋 Ingreso de DNI")
    dni_input = st.text_area("Escribí un DNI por línea:", height=150, placeholder="12345678\n87654321\n...")
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        buscar_btn = st.button("🚀 Buscar", type="primary", use_container_width=True)
    with col2:
        descargar_btn = st.button("📥 Descargar", disabled=True, use_container_width=True)

result_container = st.container()
with result_container:
    st.subheader("📊 Resultados de la consulta")
    progress_bar = st.progress(0, text="Esperando consulta...")
    status_text = st.empty()

def consultar_puco_con_selenium(dni_list):
    resultados = []
    total = len(dni_list)
    
    # --- CONFIGURACIÓN ULTRA-COMPATIBLE PARA NUBE ---
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--single-process") # Crucial para evitar errores de memoria en la nube
    
    # Ruta del binario instalado por packages.txt
    chrome_options.binary_location = "/usr/bin/chromium"
    
    driver = None
    try:
        # Instalación del driver
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        status_text.text("Conectando con SISA...")
        time.sleep(6)
        
        # Click en módulo PUCO
        try:
            puco_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PUCO') or contains(text(), 'consulta de cobertura')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", puco_element)
            time.sleep(2)
            driver.execute_script("arguments[0].click();", puco_element)
        except Exception:
            raise Exception("No se pudo acceder al módulo PUCO.")

        # Esperar campo de texto
        dni_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni') or contains(@id, 'dni')]"))
        )
        
        for idx, dni in enumerate(dni_list):
            status_text.text(f"Consultando DNI {dni} ({idx+1}/{total})...")
            dni_field.clear()
            for char in str(dni):
                dni_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            
            btn_buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']")
            btn_buscar.click()
            
            try:
                tabla = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.XPATH, "//table"))
                )
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                if len(filas) > 1:
                    celdas = filas[1].find_elements(By.TAG_NAME, "td")
                    cobertura = celdas[0].text.strip()
                    denominacion = celdas[1].text.strip()
                else:
                    cobertura = denominacion = "Sin datos"
            except:
                cobertura = "No hallado"
                denominacion = "-"
            
            resultados.append({
                "DNI": dni,
                "Cobertura Social": cobertura,
                "Denominación": denominacion,
                "Estado": "OK" if cobertura != "No hallado" else "Error"
            })
            
            progress_bar.progress((idx + 1) / total)
            if idx < total - 1:
                pausa = random.uniform(5, 9)
                status_text.text(f"Pausa de seguridad: {pausa:.1f}s...")
                time.sleep(pausa)
        
        status_text.text("¡Listo! Consulta terminada.")
        
    except Exception as e:
        st.error(f"❌ Error crítico: {str(e)[:200]}")
    finally:
        if driver:
            driver.quit()
    
    return pd.DataFrame(resultados)

# Lógica del botón
if buscar_btn:
    if not dni_input.strip():
        st.warning("Escribí los DNIs primero.")
    else:
        lista_dni = [d.strip() for d in dni_input.split('\n') if d.strip()]
        with st.spinner("Procesando consulta masiva..."):
            df_final = consultar_puco_con_selenium(lista_dni)
        
        if not df_final.empty:
            with result_container:
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte CSV",
                    data=csv,
                    file_name=f"reporte_sisa_{time.strftime('%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
