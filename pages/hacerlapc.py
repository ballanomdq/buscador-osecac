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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# --- Configuración de la página ---
st.set_page_config(page_title="HACER LA PC - PUCO", layout="wide")

st.title("💻 HACER LA PC - Consulta Masiva PUCO (SISA)")

# Estilo sutil para resultados
st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #38bdf8; border-radius: 10px; }
    .error-msg { color: #ff4b4b; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# --- UI de entrada ---
with st.container():
    st.subheader("📋 Ingreso de DNI")
    dni_input = st.text_area("Escribí un DNI por línea:", height=150, placeholder="Ejemplo:\n20333444\n40555666")
    col1, col2 = st.columns([1, 5])
    with col1:
        buscar_btn = st.button("🚀 Buscar", type="primary")

# --- Contenedor para estados y resultados ---
status_container = st.container()

def iniciar_driver():
    """
    Intenta iniciar el driver de Chrome con múltiples rutas de binario y opciones de estabilidad.
    """
    posibles_rutas = [
        "/usr/bin/chromium-browser",   # Ruta común en Ubuntu
        "/usr/bin/chromium",           # Alternativa
        "/usr/bin/google-chrome",      # Por si acaso
    ]
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")  # Ayuda a evitar crashes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Intentar con cada ruta
    for ruta in posibles_rutas:
        try:
            options.binary_location = ruta
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            # Si llega aquí, funcionó
            return driver
        except:
            continue
    
    # Si ninguna ruta funcionó, probar sin especificar binary_location (usa el default)
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"No se pudo iniciar el navegador: {e}")
        return None

def consultar_sisa(dni_list, status_placeholder, progress_placeholder):
    """
    Realiza la consulta para una lista de DNIs.
    Retorna un DataFrame con resultados.
    """
    resultados = []
    driver = iniciar_driver()
    if driver is None:
        return pd.DataFrame()
    
    try:
        status_placeholder.info("🌐 Accediendo a SISA...")
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        time.sleep(5)  # Espera inicial para carga pesada
        
        # --- Buscar y hacer clic en el módulo PUCO (con XPath robusto) ---
        status_placeholder.info("🔍 Localizando módulo PUCO...")
        try:
            # Intentamos primero con texto exacto 'PUCO'
            puco = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PUCO')]"))
            )
        except TimeoutException:
            # Si no aparece, puede que el texto sea 'Módulo PUCO' o similar
            puco = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'consulta de cobertura')]"))
            )
        
        # Scroll y click con JavaScript (más confiable)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", puco)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", puco)
        
        # --- Esperar campo DNI ---
        status_placeholder.info("⏳ Esperando campo DNI...")
        dni_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni') or contains(@id, 'dni')]"))
        )
        
        total = len(dni_list)
        for idx, dni in enumerate(dni_list):
            status_placeholder.warning(f"🔎 Procesando DNI {dni} ({idx+1}/{total})")
            progress_placeholder.progress((idx + 1) / total)
            
            # Ingresar DNI
            dni_field.clear()
            dni_field.send_keys(str(dni))
            
            # Hacer clic en botón Buscar
            try:
                buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']")
                driver.execute_script("arguments[0].click();", buscar)
            except NoSuchElementException:
                resultados.append({"DNI": dni, "Cobertura": "Error", "Obra Social": "No se encontró botón"})
                continue
            
            # Esperar resultados (tabla o mensaje)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//table | //div[contains(text(), 'sin resultados')]"))
                )
                
                # Intentar extraer datos de la tabla
                celdas = driver.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 2:
                    cobertura = celdas[0].text.strip()
                    obra_social = celdas[1].text.strip()
                else:
                    cobertura = "Sin datos"
                    obra_social = "Sin datos"
            except TimeoutException:
                cobertura = "No encontrado"
                obra_social = "-"
            
            resultados.append({
                "DNI": dni,
                "Cobertura": cobertura,
                "Obra Social": obra_social
            })
            
            # Pausa aleatoria para evitar bloqueos
            if idx < total - 1:
                pausa = random.uniform(4, 8)
                status_placeholder.info(f"😴 Esperando {pausa:.1f} segundos...")
                time.sleep(pausa)
        
        status_placeholder.success("✅ Consulta finalizada correctamente.")
        
    except Exception as e:
        st.error(f"❌ Error durante la automatización: {str(e)[:200]}")
        # Mostramos también el tipo de error para depurar
        st.exception(e)  # Esto mostrará el stacktrace completo en el log
    finally:
        driver.quit()
    
    return pd.DataFrame(resultados)

# --- Lógica principal al presionar el botón ---
if buscar_btn:
    if not dni_input.strip():
        st.warning("Por favor, ingresá al menos un DNI.")
    else:
        lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
        
        with status_container:
            status_placeholder = st.empty()
            progress_placeholder = st.progress(0)
            
            df_resultados = consultar_sisa(lista_dnis, status_placeholder, progress_placeholder)
            
            if not df_resultados.empty:
                st.subheader("📋 Resultados Obtenidos")
                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
                
                csv = df_resultados.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte CSV",
                    data=csv,
                    file_name="consulta_puco.csv",
                    mime="text/csv",
                    use_container_width=True
                )
