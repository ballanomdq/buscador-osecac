import streamlit as st
import requests
import time
import io
import zipfile
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Robot OSECAC", layout="wide")
st.title("🤖 Robot OSECAC - Descarga Masiva de Actas")

with st.form("datos_acceso"):
    usuario = st.text_input("👤 Usuario OSECAC", value="FBOVONE")
    legajo = st.text_input("📋 Número de Legajo", value="7713")
    submit = st.form_submit_button("🚀 INICIAR DESCARGA")

if submit:
    log_area = st.empty()
    logs = []
    
    def add_log(msg):
        logs.append(msg)
        log_area.code("\n".join(logs[-20:]), language="text")
    
    add_log("🚀 Iniciando...")
    
    # Cookie Usuario en formato XML
    cookie_usuario = f'%3c%3fxml+version%3d%221.0%22+encoding%3d%22utf-16%22%3f%3e%0d%0a%3cWebUser+xmlns%3axsi%3d%22http%3a%2f%2fwww.w3.org%2f2001%2fXMLSchema-instance%22+xmlns%3axsd%3d%22http%3a%2f%2fwww.w3.org%2f2001%2fXMLSchema%22%3e%0d%0a++%3cIdLugar%3e-1%3c%2fIdLugar%3e%0d%0a++%3cLugar+%2f%3e%0d%0a++%3cIdApp%3e25%3c%2fIdApp%3e%0d%0a++%3cIdUsuario%3e{usuario}%3c%2fIdUsuario%3e%0d%0a++%3cLogin%3e{usuario}%3c%2fLogin%3e%0d%0a++%3cClave%3eGD6E0FBF4DFD945%3c%2fClave%3e%0d%0a++%3cUltimo+xsi%3anil%3d%22true%22+%2f%3e%0d%0a++%3cIdModulo%3e-1%3c%2fIdModulo%3e%0d%0a++%3cIdFuncion%3e-1%3c%2fIdFuncion%3e%0d%0a++%3cListaPermisos+%2f%3e%0d%0a%3c%2fWebUser%3e'
    
    session = requests.Session()
    
    # Establecer las cookies
    session.cookies.set('ASP.NET_SessionId', '4jzaar3qvp4etr45lrefpmql')
    session.cookies.set('Usuario', cookie_usuario)
    
    # 1. Ir a página de actas
    add_log("📂 Accediendo a página de actas...")
    actas_url = "http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx"
    resp = session.get(actas_url)
    
    add_log(f"📍 Status: {resp.status_code}")
    
    if resp.status_code == 200:
        add_log("✅ Acceso exitoso")
        
        # 2. Buscar por legajo
        add_log(f"🔢 Buscando legajo {legajo}...")
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
        
        # === DIAGNÓSTICO ===
        add_log("🔍 Ejecutando diagnóstico...")
        
        # Guardar HTML para debug
        with open("debug_osecac.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        add_log("✅ HTML guardado en debug_osecac.html")
        
        # Buscar todas las tablas
        soup = BeautifulSoup(resp.text, 'html.parser')
        todas_tablas = soup.find_all('table')
        add_log(f"📊 Total tablas encontradas: {len(todas_tablas)}")
        
        for idx, t in enumerate(todas_tablas):
            add_log(f"  Tabla {idx}: id={t.get('id', 'sin id')}")
        
        # Buscar el legajo en la página
        if legajo in resp.text:
            add_log(f"✅ El legajo {legajo} aparece en la página")
        else:
            add_log(f"❌ El legajo {legajo} NO aparece en la página")
        
        # Buscar mensaje de error común
        if "error" in resp.text.lower():
            add_log("⚠️ Se detectó la palabra 'error' en la página")
        
        # Mostrar HTML para inspección visual
        st.subheader("🔍 Diagnóstico - HTML recibido")
        st.text_area("Primeros 3000 caracteres", resp.text[:3000], height=400)
        
        # Buscar tabla específica de actas
        tabla = soup.find('table', {'id': 'ctl00_cMain_gvActasSincronizadas'})
        if tabla:
            add_log("✅ Tabla de actas ENCONTRADA!")
            numeros_acta = []
            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 2:
                    texto = celdas[1].get_text().strip()
                    if texto.isdigit() and len(texto) >= 6:
                        numeros_acta.append(texto)
            
            add_log(f"📊 Encontradas {len(numeros_acta)} actas")
            
            if numeros_acta:
                pdfs = []
                progress = st.progress(0)
                
                for i in range(0, len(numeros_acta), 2):
                    grupo = numeros_acta[i:i+2]
                    nros = ','.join(grupo)
                    
                    pdf_url = f"http://200.51.42.41:7980/FiscaPDA/Sincronizacion/frmPrintMasivo.aspx?PrintNew=1&Usuario={usuario}&NrosActa={nros}&OrigCopy=0&ImpSinCiudad=1&Docs=A:1,V:1,I:1,P:1,L:1,D:1&HistorialActas=0"
                    
                    add_log(f"🖨️ Generando PDF: actas {nros}")
                    resp_pdf = session.get(pdf_url)
                    
                    if resp_pdf.status_code == 200 and len(resp_pdf.content) > 1000:
                        pdfs.append((f"actas_{nros}.pdf", resp_pdf.content))
                        add_log(f"✅ OK: actas_{nros}.pdf")
                    else:
                        add_log(f"❌ Error: {nros}")
                    
                    progress.progress(min((i+2)/len(numeros_acta), 1.0))
                    time.sleep(1)
                
                if pdfs:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                        for nombre, contenido in pdfs:
                            zipf.writestr(nombre, contenido)
                    
                    st.success(f"✅ {len(pdfs)} PDFs generados")
                    st.download_button(
                        label="📥 DESCARGAR ZIP",
                        data=zip_buffer.getvalue(),
                        file_name=f"actas_legajo_{legajo}.zip",
                        mime="application/zip"
                    )
            else:
                st.warning("⚠️ No se encontraron números de acta en la tabla")
        else:
            add_log("❌ Tabla de actas NO encontrada")
            st.error("No se encontró la tabla de actas. Revisá el diagnóstico arriba.")
    else:
        add_log(f"❌ Error de acceso: {resp.status_code}")
        st.error(f"No se pudo acceder a la página de actas")
