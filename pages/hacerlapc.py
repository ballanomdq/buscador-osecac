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
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

# --- Configuración de la página ---
st.set_page_config(page_title="HACER LA PC - PUCO", layout="wide")

# --- Título y descripción ---
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

# --- Contenedor para entrada de datos ---
with st.container():
    st.subheader("📋 Ingreso de DNI")
    dni_input = st.text_area("Escribí un DNI por línea:", height=150, placeholder="12345678\n87654321\n...")
    
    # Botones en columnas
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        buscar_btn = st.button("🚀 Buscar", type="primary", use_container_width=True)
    with col2:
        descargar_btn = st.button("📥 Descargar", disabled=True, use_container_width=True)

# --- Contenedor para resultados ---
result_container = st.container()
with result_container:
    st.subheader("📊 Resultados de la consulta")
    progress_bar = st.progress(0, text="Esperando consulta...")
    status_text = st.empty()
    df_placeholder = st.empty()

# --- Función de automatización con Selenium ---
def consultar_puco_con_selenium(dni_list):
    resultados = []
    total = len(dni_list)
    
    # Configurar opciones de Chrome para estabilidad en servidor (Streamlit Cloud)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # RUTA CRUCIAL PARA LA NUBE
    chrome_options.binary_location = "/usr/bin/chromium"
    
    # Inicializar el Service con la ruta del driver de Linux
    service = Service("/usr/bin/chromedriver")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Ir a SISA
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        status_text.text("Cargando SISA (puede tardar la primera vez)...")
        time.sleep(5)
        
        # Localizar PUCO
        try:
            puco_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PUCO') or contains(text(), 'consulta de cobertura')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", puco_element)
            time.sleep(1)
            
            try:
                puco_element.click()
            except:
                driver.execute_script("arguments[0].click();", puco_element)
                
        except TimeoutException:
            raise Exception("No se pudo localizar el módulo PUCO en la web de SISA.")
        
        # Esperar campo DNI
        dni_input_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni') or contains(@id, 'dni')]"))
        )
        
        for idx, dni in enumerate(dni_list):
            status_text.text(f"Consultando DNI {dni} ({idx+1}/{total})...")
            
            dni_input_field.clear()
            for char in str(dni):
                dni_input_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            
            # Botón Buscar
            btn_buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']")
            btn_buscar.click()
            
            # Resultados
            try:
                tabla = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//table"))
                )
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                if len(filas) > 1:
                    celdas = filas[1].find_elements(By.TAG_NAME, "td")
                    cobertura = celdas[0].text.strip() if len(celdas) > 0 else "Sin datos"
                    denominacion = celdas[1].text.strip() if len(celdas) > 1 else "Sin datos"
                else:
                    cobertura = denominacion = "No encontrado"
            except:
                cobertura = "Error/No hallado"
                denominacion = "-"
            
            resultados.append({
                "DNI": dni,
                "Cobertura Social": cobertura,
                "Denominación": denominacion,
                "Estado": "OK" if cobertura != "Error/No hallado" else "Fallido"
            })
            
            progress_bar.progress((idx + 1) / total)
            
            if idx < total - 1:
                pausa = random.uniform(4, 7)
                status_text.text(f"Pausa de seguridad: {pausa:.1f}s...")
                time.sleep(pausa)
        
        status_text.text("¡Consulta completada con éxito!")
        
    except Exception as e:
        st.error(f"❌ Error crítico: {str(e)[:150]}")
        return pd.DataFrame(resultados)
    finally:
        if 'driver' in locals():
            driver.quit()
    
    return pd.DataFrame(resultados)

# --- Lógica principal ---
if buscar_btn:
    if not dni_input.strip():
        st.warning("Por favor, ingresá al menos un DNI.")
    else:
        lista_dni = [d.strip() for d in dni_input.split('\n') if d.strip()]
        with st.spinner("Conectando con SISA..."):
            df_final = consultar_puco_con_selenium(lista_dni)
        
        if not df_final.empty:
            with result_container:
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte CSV",
                    data=csv,
                    file_name=f"puco_osecac_{time.strftime('%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
