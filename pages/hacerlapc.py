import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    # La col3 vacía para equilibrar

# --- Contenedor para resultados (inicialmente vacío) ---
result_container = st.container()
with result_container:
    st.subheader("📊 Resultados de la consulta")
    # Placeholder para la barra de progreso y el dataframe
    progress_bar = st.progress(0, text="Esperando consulta...")
    status_text = st.empty()
    df_placeholder = st.empty()

# --- Función de automatización con Selenium ---
def consultar_puco_con_selenium(dni_list):
    """
    Itera sobre una lista de DNIs, consulta en SISA y devuelve un DataFrame.
    """
    resultados = []
    total = len(dni_list)
    
    # Configurar opciones de Chrome para headless y estabilidad en servidor
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")          # Modo sin cabeza (comentar para debug)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Ir a SISA
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        status_text.text("Cargando SISA (puede tardar hasta 30s la primera vez)...")
        time.sleep(5)  # Espera inicial
        
        # --- Buscar y hacer clic en el módulo PUCO (con doble estrategia) ---
        try:
            # Intentar localizar por XPath que contenga "PUCO" o "consulta de cobertura"
            puco_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PUCO') or contains(text(), 'consulta de cobertura')]"))
            )
            # Scroll hacia el elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", puco_element)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Intentar clic normal
            try:
                puco_element.click()
            except ElementClickInterceptedException:
                # Si el clic normal falla, usar JavaScript
                driver.execute_script("arguments[0].click();", puco_element)
                
        except TimeoutException:
            # Si no encuentra por texto, buscar en el carrusel (selector genérico)
            # Podríamos intentar desplazar el carrusel, pero lo dejamos como último recurso
            status_text.text("No se encontró PUCO por texto, intentando con slider...")
            # Aquí podrías agregar lógica para mover el carrusel, pero por ahora lanzamos error
            raise Exception("No se pudo localizar el módulo PUCO")
        
        # Esperar que aparezca el campo DNI
        dni_input_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni') or contains(@id, 'dni')]"))
        )
        
        # Iterar sobre cada DNI
        for idx, dni in enumerate(dni_list):
            status_text.text(f"Consultando DNI {dni} ({idx+1}/{total})...")
            
            # Limpiar campo y escribir DNI con pausa humana
            dni_input_field.clear()
            for char in str(dni):
                dni_input_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            
            # Buscar botón "Buscar" (por texto o tipo)
            try:
                buscar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']")
            except:
                buscar_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            buscar_btn.click()
            
            # Esperar resultados (puede ser una tabla o un mensaje)
            try:
                # Esperar a que aparezca la tabla de resultados
                tabla = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//table"))
                )
                # Extraer la primera fila de datos (ignorar encabezados)
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                if len(filas) > 1:
                    celdas = filas[1].find_elements(By.TAG_NAME, "td")
                    # Asumimos que las columnas son: Cobertura Social y Denominación (ajustar índices)
                    cobertura = celdas[0].text.strip() if len(celdas) > 0 else ""
                    denominacion = celdas[1].text.strip() if len(celdas) > 1 else ""
                else:
                    cobertura = denominacion = "Sin datos"
            except TimeoutException:
                # Puede que no haya tabla y haya un mensaje de error
                cobertura = "No encontrado"
                denominacion = ""
            
            resultados.append({
                "DNI": dni,
                "Cobertura Social": cobertura,
                "Denominación": denominacion,
                "Estado": "OK" if cobertura and cobertura != "No encontrado" else "Error"
            })
            
            # Actualizar barra de progreso
            progress_bar.progress((idx + 1) / total)
            
            # Pausa aleatoria entre consultas (cadencia humana)
            if idx < total - 1:
                pausa = random.uniform(5, 10)
                status_text.text(f"Esperando {pausa:.1f} segundos para la próxima consulta...")
                time.sleep(pausa)
        
        status_text.text("Consulta finalizada.")
        
    except Exception as e:
        st.error(f"❌ Error en automatización: {str(e)[:100]}")
        resultados = []  # Vacío para evitar datos corruptos
    finally:
        driver.quit()
    
    return pd.DataFrame(resultados)

# --- Lógica principal ---
if buscar_btn:
    if not dni_input.strip():
        st.warning("Ingresá al menos un DNI.")
    else:
        dni_lista = [d.strip() for d in dni_input.split('\n') if d.strip()]
        with st.spinner("Iniciando automatización..."):
            df_resultados = consultar_puco_con_selenium(dni_lista)
        
        if not df_resultados.empty:
            # Mostrar dataframe en el contenedor de resultados
            with result_container:
                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
                # Habilitar botón de descarga
                csv = df_resultados.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"resultados_puco_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            with result_container:
                st.info("No se obtuvieron resultados. Verificá los DNI o la conexión.")
