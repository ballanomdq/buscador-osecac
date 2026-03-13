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

# Estilo para los resultados
st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #38bdf8; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# UI de entrada
with st.container():
    st.subheader("📋 Ingreso de DNI")
    dni_input = st.text_area("Escribí un DNI por línea:", height=150, placeholder="Ejemplo:\n20333444\n40555666")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        buscar_btn = st.button("🚀 Buscar", type="primary")

# Contenedor para estados y progreso
status_container = st.container()

def consultar_sisa(dni_list):
    resultados = []
    
    # 1. Configuración de Opciones (Específicas para Linux/Streamlit)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium" # Ruta instalada por packages.txt

    # 2. Iniciar el Driver usando el Service con ruta fija
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        st.error(f"Error al iniciar el motor del navegador: {e}")
        return pd.DataFrame()

    try:
        # Ir a la web de SISA
        driver.get("https://sisa.msal.gov.ar/sisa/#sisa")
        msg_estado.info("Conectando con el portal SISA...")
        time.sleep(5)
        
        # Click en PUCO usando JavaScript para mayor efectividad
        puco = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'PUCO')]"))
        )
        driver.execute_script("arguments[0].click();", puco)
        
        # Esperar a que cargue el campo DNI
        dni_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'dni')]"))
        )

        for idx, dni in enumerate(dni_list):
            msg_estado.warning(f"Procesando DNI: {dni} ({idx+1}/{len(dni_list)})")
            progreso.progress((idx + 1) / len(dni_list))
            
            dni_field.clear()
            dni_field.send_keys(str(dni))
            
            # Click en el botón de búsqueda de la web
            boton_sisa = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or @type='submit']")
            driver.execute_script("arguments[0].click();", boton_sisa)
            
            # Extraer datos de la tabla resultante
            try:
                WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//table")))
                celdas = driver.find_elements(By.TAG_NAME, "td")
                
                cobertura = celdas[0].text if len(celdas) > 0 else "Sin datos"
                obra_social = celdas[1].text if len(celdas) > 1 else "No especifica"
            except:
                cobertura = "No encontrado / Error"
                obra_social = "-"

            resultados.append({
                "DNI": dni,
                "Cobertura": cobertura,
                "Obra Social": obra_social
            })
            
            # Pausa aleatoria para no ser bloqueados
            if idx < len(dni_list) - 1:
                time.sleep(random.uniform(3, 6))

        msg_estado.success("¡Consulta finalizada!")

    except Exception as e:
        st.error(f"Se produjo un error durante la navegación: {e}")
    finally:
        driver.quit()
    
    return pd.DataFrame(resultados)

# Lógica al presionar el botón
if buscar_btn:
    if not dni_input.strip():
        st.warning("Por favor, ingresá al menos un DNI.")
    else:
        lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
        
        with status_container:
            msg_estado = st.empty()
            progreso = st.progress(0)
            
            df_final = consultar_sisa(lista_dnis)
            
            if not df_final.empty:
                st.subheader("📋 Resultados Obtenidos")
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                
                # Botón de descarga
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte CSV",
                    data=csv,
                    file_name="consulta_puco.csv",
                    mime="text/csv",
                    use_container_width=True
                )
