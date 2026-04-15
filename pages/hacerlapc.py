import streamlit as st
import asyncio
import time
import os
import zipfile
from pathlib import Path
from playwright.async_api import async_playwright

st.set_page_config(page_title="Robot OSECAC", layout="wide")
st.title("🤖 Robot OSECAC - Descarga Masiva de Actas")

# Carpeta de descargas
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
    
    submit = st.form_submit_button("🚀 INICIAR DESCARGA MASIVA", use_container_width=True)

if submit:
    if not usuario or not password:
        st.error("❌ Completá usuario y contraseña")
    else:
        status_text = st.empty()
        log_area = st.empty()
        logs = []
        
        def add_log(msg):
            logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
            log_area.code("\n".join(logs[-25:]), language="text")
        
        add_log("🚀 Iniciando robot en la nube...")
        
        try:
            async def ejecutar_robot():
                add_log("🌐 Lanzando navegador headless...")
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(accept_downloads=True)
                    page = await context.new_page()
                    
                    # 1. Login
                    add_log("🔐 Accediendo a login...")
                    await page.goto("http://200.51.42.41:7980/Login.aspx")
                    await page.wait_for_timeout(2000)
                    
                    add_log(f"📝 Escribiendo usuario...")
                    await page.fill("#ctl00_uLogin1_txtUsuario", usuario)
                    await page.fill("#ctl00_uLogin1_txtClave", password)
                    await page.keyboard.press("Enter")
                    
                    add_log("⏳ Esperando ingreso...")
                    await page.wait_for_timeout(5000)
                    
                    # 2. Ir a sincronización
                    add_log("📂 Navegando a actas...")
                    await page.goto("http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx")
                    await page.wait_for_timeout(3000)
                    
                    # 3. Completar legajo
                    add_log(f"🔢 Legajo: {legajo}")
                    await page.fill("#ctl00_cMain_gvActasSincronizadas_Legajo", legajo)
                    
                    # 4. Ver actas impresas
                    if ver_impresas:
                        try:
                            await page.check("#ctl00_cMain_gvActasSincronizadas_VerImpresas")
                            add_log("☑️ Activado 'Ver Actas ya Impresas'")
                        except:
                            pass
                    
                    # 5. Buscar
                    add_log("🔍 Buscando actas...")
                    await page.click("#ctl00_cMain_gvActasSincronizadas_btnBuscar")
                    await page.wait_for_timeout(5000)
                    
                    # 6. Obtener actas
                    await page.wait_for_selector("#ctl00_cMain_gvActasSincronizadas", timeout=10000)
                    checkboxes = await page.query_selector_all("#ctl00_cMain_gvActasSincronizadas input[type='checkbox']")
                    
                    habilitados = []
                    for cb in checkboxes:
                        if await cb.is_enabled():
                            habilitados.append(cb)
                    
                    total_actas = len(habilitados)
                    add_log(f"📊 Total actas encontradas: {total_actas}")
                    
                    if total_actas == 0:
                        st.warning("⚠️ No se encontraron actas. Verificá el legajo.")
                        return
                    
                    # 7. Procesar de a 2
                    for i in range(0, total_actas, 2):
                        status_text.text(f"📄 Procesando actas {i+1}-{min(i+2, total_actas)} de {total_actas}")
                        
                        # Seleccionar/deseleccionar
                        for j, cb in enumerate(habilitados):
                            if j >= i and j < i+2:
                                if not await cb.is_checked():
                                    await cb.click()
                            else:
                                if await cb.is_checked():
                                    await cb.click()
                        
                        await page.wait_for_timeout(1000)
                        
                        # Click imprimir
                        add_log(f"🖨️ Abriendo lote {i//2 + 1}")
                        await page.click("#ctl00_cMain_gvActasSincronizadas_6")
                        await page.wait_for_timeout(4000)
                        
                        # Esperar nueva ventana
                        try:
                            async with context.expect_page() as nueva:
                                pass
                            modal = await nueva.value
                            await modal.wait_for_load_state()
                            
                            add_log("🪟 Ventana modal detectada")
                            await page.wait_for_timeout(2000)
                            
                            # Marcar S/Ciudad
                            try:
                                await modal.check("#chkImpSCiudad")
                                add_log("☑️ Marcado 'Imprimir S/Ciudad'")
                            except:
                                add_log("⚠️ No se encontró checkbox de ciudad")
                            
                            await page.wait_for_timeout(1000)
                            
                            # Click Imprimir y descargar
                            try:
                                async with modal.expect_download() as descarga_info:
                                    await modal.click("#lbGrabar")
                                descarga = await descarga_info.value
                                
                                nombre_archivo = f"acta_{i+1}_{i+2}_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
                                ruta_descarga = os.path.join(DOWNLOAD_DIR, nombre_archivo)
                                await descarga.save_as(ruta_descarga)
                                add_log(f"💾 Descargado: {nombre_archivo}")
                            except Exception as e:
                                add_log(f"⚠️ Error en descarga: {str(e)[:50]}")
                            
                            await modal.close()
                            add_log("↩️ Modal cerrado")
                            
                        except Exception as e:
                            add_log(f"⚠️ Error con ventana modal: {str(e)[:50]}")
                        
                        await page.wait_for_timeout(3000)
                    
                    add_log("✅ PROCESO COMPLETADO!")
                    status_text.text(f"✅ {total_actas} actas descargadas correctamente")
                    
                    # Crear ZIP
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
                    
                    await browser.close()
                    return "OK"
            
            # Ejecutar el robot
            asyncio.run(ejecutar_robot())
            
        except Exception as e:
            add_log(f"❌ ERROR: {str(e)}")
            st.error(f"Error: {str(e)}")
