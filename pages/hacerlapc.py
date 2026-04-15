import streamlit as st
import requests
import time
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="Robot OSECAC", layout="wide")
st.title("🤖 Robot OSECAC - Descarga Masiva de Actas")

with st.form("datos_acceso"):
    usuario = st.text_input("👤 Usuario OSECAC", value="FBOVONE")
    password = st.text_input("🔒 Contraseña", type="password", value="FBOVONE")
    legajo = st.text_input("📋 Número de Legajo", value="7713")
    submit = st.form_submit_button("🚀 INICIAR DESCARGA")

if submit:
    with st.spinner("Conectando a OSECAC..."):
        
        # Crear sesión
        session = requests.Session()
        
        # 1. Obtener página de login y tokens
        st.write("📝 1. Iniciando sesión...")
        login_url = "http://200.51.42.41:7980/Login.aspx"
        resp = session.get(login_url)
        
        # Extraer tokens ASP.NET
        soup = BeautifulSoup(resp.text, 'html.parser')
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        
        # Datos de login
        login_data = {
            '__VIEWSTATE': viewstate['value'] if viewstate else '',
            '__EVENTVALIDATION': eventvalidation['value'] if eventvalidation else '',
            'ctl00$uLogin1$txtUsuario': usuario,
            'ctl00$uLogin1$txtClave': password,
            'ctl00$uLogin1$btnIngresar': 'Ingresar'
        }
        
        # Enviar login
        resp = session.post(login_url, data=login_data)
        
        if "default.aspx" in resp.url or "Sincronizacion" in resp.url:
            st.success("✅ Login exitoso!")
            
            # 2. Ir a página de actas
            st.write("📝 2. Buscando actas...")
            actas_url = "http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx"
            resp = session.get(actas_url)
            
            # 3. Buscar por legajo
            soup = BeautifulSoup(resp.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            busqueda_data = {
                '__VIEWSTATE': viewstate['value'] if viewstate else '',
                '__EVENTVALIDATION': eventvalidation['value'] if eventvalidation else '',
                'ctl00$cMain$gvActasSincronizadas$Legajo': legajo,
                'ctl00$cMain$gvActasSincronizadas$btnBuscar': 'Buscar'
            }
            
            resp = session.post(actas_url, data=busqueda_data)
            
            # 4. Extraer números de acta
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Buscar todas las filas de la tabla
            tabla = soup.find('table', {'id': 'ctl00_cMain_gvActasSincronizadas'})
            if tabla:
                filas = tabla.find_all('tr')
                numeros_acta = []
                
                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) > 1:
                        # Buscar el número de acta (normalmente en la segunda columna)
                        texto = celdas[1].get_text().strip() if len(celdas) > 1 else ""
                        if texto.isdigit():
                            numeros_acta.append(texto)
                
                st.write(f"📊 Se encontraron {len(numeros_acta)} actas")
                st.write(f"📄 Números: {', '.join(numeros_acta[:10])}...")
                
                # 5. Generar PDFs
                st.write("📝 3. Generando PDFs...")
                
                pdfs_generados = []
                for i in range(0, len(numeros_acta), 2):
                    grupo = numeros_acta[i:i+2]
                    nros = ','.join(grupo)
                    
                    # URL de generación de PDF
                    pdf_url = f"http://200.51.42.41:7980/FiscaPDA/Sincronizacion/frmPrintMasivo.aspx?PrintNew=1&Usuario={usuario}&NrosActa={nros}&OrigCopy=0&ImpSinCiudad=1&Docs=A:1,V:1,I:1,P:1,L:1,D:1&HistorialActas=0"
                    
                    resp_pdf = session.get(pdf_url)
                    
                    if resp_pdf.status_code == 200 and len(resp_pdf.content) > 1000:
                        nombre = f"actas_{nros}.pdf"
                        pdfs_generados.append((nombre, resp_pdf.content))
                        st.write(f"✅ Descargado: {nombre}")
                    
                    time.sleep(2)
                
                # 6. Ofrecer descarga
                if pdfs_generados:
                    import zipfile
                    import io
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for nombre, contenido in pdfs_generados:
                            zip_file.writestr(nombre, contenido)
                    
                    st.success(f"✅ Se generaron {len(pdfs_generados)} PDFs")
                    st.download_button(
                        label="📥 DESCARGAR TODOS LOS PDFS (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="actas_osecac.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("❌ No se pudo generar ningún PDF")
            else:
                st.error("❌ No se encontró la tabla de actas")
        else:
            st.error("❌ Error de login. Verificá usuario y contraseña")
