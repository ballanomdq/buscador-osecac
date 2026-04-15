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
    log_area = st.empty()
    logs = []
    
    def add_log(msg):
        logs.append(msg)
        log_area.code("\n".join(logs[-20:]), language="text")
    
    add_log("🚀 Iniciando...")
    
    session = requests.Session()
    
    # 1. Obtener página de login
    add_log("📝 Obteniendo página de login...")
    login_url = "http://200.51.42.41:7980/Login.aspx"
    resp = session.get(login_url)
    
    # Extraer tokens
    soup = BeautifulSoup(resp.text, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})
    viewstategen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
    
    # Datos del login (con el botón que ahora sé que existe)
    login_data = {
        '__VIEWSTATE': viewstate['value'] if viewstate else '',
        '__VIEWSTATEGENERATOR': viewstategen['value'] if viewstategen else '',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        'ctl00$hdnModulo': '',
        'ctl00$hdnFunction': '',
        'ctl00$hdnPermisos': '',
        'ctl00$UcLogin1$txtUsuario': usuario,
        'ctl00$UcLogin1$txtClave': password,
        'ctl00$UcLogin1$btnIngresar': 'Ingresar'
    }
    
    add_log(f"🔐 Enviando login...")
    
    # Enviar login SIN seguir redirecciones automáticas
    resp = session.post(login_url, data=login_data, allow_redirects=False)
    
    add_log(f"📍 Status: {resp.status_code}")
    
    # Verificar si hay redirección
    if resp.status_code == 302:
        add_log("✅ Redirección detectada (login exitoso)")
        
        # Seguir la redirección manualmente
        location = resp.headers.get('Location', '')
        add_log(f"📍 Redirigiendo a: {location}")
        
        resp = session.get(f"http://200.51.42.41:7980{location}")
        
        # También seguir a default.aspx si es necesario
        if "default.aspx" in location.lower():
            add_log("✅ Llegamos a default.aspx")
        
        # 2. Ir a página de actas
        add_log("📂 Navegando a actas...")
        actas_url = "http://200.51.42.41:7980/FiscaPDA/Sincronizacion/default.aspx"
        resp = session.get(actas_url)
        add_log(f"📄 Status actas: {resp.status_code}")
        
        # 3. Buscar por legajo
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
        
        # 4. Extraer números de acta
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar la tabla por ID o por clase
        tabla = soup.find('table', {'id': re.compile(r'gvActasSincronizadas')})
        if not tabla:
            tabla = soup.find('table', {'class': re.compile(r'grilla', re.I)})
        
        if tabla:
            numeros_acta = []
            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 2:
                    # Buscar números de acta (solo dígitos, longitud > 5)
                    for celda in celdas:
                        texto = celda.get_text().strip()
                        if texto.isdigit() and len(texto) >= 6:
                            numeros_acta.append(texto)
                            break
            
            # Eliminar duplicados y ordenar
            numeros_acta = list(dict.fromkeys(numeros_acta))
            
            add_log(f"📊 Encontradas {len(numeros_acta)} actas")
            
            if numeros_acta:
                st.write(f"📄 Actas encontradas: {', '.join(numeros_acta[:20])}")
                
                # 5. Generar PDFs
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
                        add_log(f"✅ OK: actas_{nros}.pdf ({len(resp_pdf.content)} bytes)")
                    else:
                        add_log(f"❌ Error: {nros} - status: {resp_pdf.status_code}")
                    
                    progress.progress(min((i+2)/len(numeros_acta), 1.0))
                    time.sleep(1)
                
                # 6. Crear ZIP
                if pdfs:
                    import zipfile
                    import io
                    
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
                    st.error("❌ No se generó ningún PDF")
            else:
                st.warning("⚠️ No se encontraron números de acta")
        else:
            add_log("❌ No se encontró la tabla de actas")
            st.error("No se encontró la tabla de actas. Mostrando HTML para debug:")
            st.code(resp.text[:2000], language="html")
    else:
        add_log(f"❌ Login fallido. Status: {resp.status_code}")
        st.error(f"Error de login. Status code: {resp.status_code}")
