import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Diagnóstico SAES", layout="wide")
st.title("🔍 Diagnóstico de Búsqueda")

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

if st.button("Ejecutar Diagnóstico"):
    with st.spinner("Conectando..."):
        s = requests.Session()
        
        # 1. LOGIN
        r = s.get(BASE_URL + "Login.aspx", headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        vs = soup.find('input', {'name': '__VIEWSTATE'})
        payload = {
            "__EVENTTARGET": "", "__EVENTARGUMENT": "",
            "__VIEWSTATE": vs['value'],
            "txtUser": "rballano", "txtPassword": "654321",
            "imgbtnSend.x": "0", "imgbtnSend.y": "0"
        }
        r2 = s.post(BASE_URL + "Login.aspx", data=payload, headers=HEADERS)
        st.write(f"Login exitoso: `{'txtUser' not in r2.text}`")
        
        # 2. GET a la página de consultas
        url_cons = BASE_URL + "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
        r_cons = s.get(url_cons, headers=HEADERS)
        soup_cons = BeautifulSoup(r_cons.text, 'html.parser')
        
        vs_cons = soup_cons.find('input', {'name': '__VIEWSTATE'})
        ev_cons = soup_cons.find('input', {'name': '__EVENTVALIDATION'})
        
        st.write(f"GET a consultas: `{r_cons.status_code}`")
        st.write(f"¿Tiene __VIEWSTATE? `{vs_cons is not None}`")
        st.write(f"¿Tiene __EVENTVALIDATION? `{ev_cons is not None}`")
        
        # 3. POST de búsqueda
        payload_busqueda = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": vs_cons['value'],
            "cboTipoDoc": "2",  # LC
            "txtDocumento": "6705303",
            "txtNroOp": "",
            "imgConsultarOT.x": "10",
            "imgConsultarOT.y": "10"
        }
        if ev_cons: payload_busqueda["__EVENTVALIDATION"] = ev_cons['value']
        
        r_res = s.post(url_cons, data=payload_busqueda, headers=HEADERS)
        soup_res = BeautifulSoup(r_res.text, 'html.parser')
        
        st.write(f"POST a consultas: `{r_res.status_code}`")
        st.write(f"¿La respuesta tiene 'txtUser' (es login)? `{'txtUser' in r_res.text}`")
        
        # Buscamos la tabla
        tabla = soup_res.find('table', {'id': 'dgBusquedaBenef'})
        st.write(f"¿Se encontró la tabla? `{tabla is not None}`")
        
        # Mostramos las primeras 2000 letras de la respuesta
        st.write("### Primeros 2000 caracteres de la respuesta del POST:")
        st.code(r_res.text[:2000])
        
        # Mostramos los nombres de las tablas que hay en la respuesta
        st.write("### Tablas encontradas en la respuesta:")
        tablas = soup_res.find_all('table')
        for t in tablas:
            st.write(f"- id: `{t.get('id')}` | class: `{t.get('class')}`")
