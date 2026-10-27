import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import StringIO
import pandas as pd

st.set_page_config(page_title="Diagnóstico SAES v5", layout="wide")
st.title("🔍 Diagnóstico de POST real - Paso 3")

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def form_payload(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        return {}, ""
    data = {}
    for el in form.find_all(["input", "select", "textarea"]):
        name = el.get("name")
        if not name:
            continue
        if el.name == "select":
            opt = el.find("option", selected=True) or el.find("option")
            data[name] = opt.get("value", "") if opt else ""
        elif el.name == "textarea":
            data[name] = el.text
        else:
            t = (el.get("type") or "text").lower()
            if t in ("submit", "button", "image", "file"):
                continue
            if t in ("checkbox", "radio") and not el.has_attr("checked"):
                continue
            data[name] = el.get("value", "")
    return data, form.get("action", "")

if st.button("Ejecutar Diagnóstico"):
    with st.spinner("Conectando..."):
        s = requests.Session()
        
        # 1. LOGIN
        r = s.get(BASE_URL + "Login.aspx", headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        vs = soup.find('input', {'name': '__VIEWSTATE'})
        payload_login = {
            "__EVENTTARGET": "", "__EVENTARGUMENT": "",
            "__VIEWSTATE": vs['value'],
            "txtUser": "rballano", "txtPassword": "654321",
            "imgbtnSend.x": "0", "imgbtnSend.y": "0"
        }
        r2 = s.post(BASE_URL + "Login.aspx", data=payload_login, headers=HEADERS)
        st.write(f"Login exitoso: `{'txtUser' not in r2.text}`")
        
        # 2. GET a la página de consultas
        url_cons = BASE_URL + "Medicamentos/ConsultaOrdenes/frmBrowserConsulta.aspx"
        r_cons = s.get(url_cons, headers=HEADERS)
        
        # 3. Extraer campos
        data, action = form_payload(r_cons.text)
        st.write(f"**Action del form:** `{action}`")
        st.write(f"**Cantidad de campos extraídos:** `{len(data)}`")
        
        # 4. Completar búsqueda
        data.update({
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "txtDocumento": "6705303",
            "cboTipoDoc": "2",  # LC
            "txtNroOp": "",
            "imgConsultarOT.x": "5",
            "imgConsultarOT.y": "5",
        })
        
        # 5. POST real
        post_url = urljoin(url_cons, action)
        r_res = s.post(post_url, data=data, headers={"Referer": url_cons})
        
        # 6. Analizar respuesta
        st.write(f"**Status:** `{r_res.status_code}`")
        st.write(f"**Largo de la respuesta:** `{len(r_res.text)}` caracteres")
        st.write(f"**¿Tiene 'txtUser' (es login)?** `{'txtUser' in r_res.text}`")
        
        soup_res = BeautifulSoup(r_res.text, 'html.parser')
        
        # Buscar todas las tablas y mostrar sus IDs
        tablas = soup_res.find_all('table')
        st.write(f"**Cantidad de tablas encontradas:** `{len(tablas)}`")
        for i, t in enumerate(tablas):
            st.write(f"- Tabla {i}: id=`{t.get('id')}`, class=`{t.get('class')}`")
        
        # Si no hay tabla, mostrar el HTML de la respuesta
        if not any(t.get('id') == 'dgBusquedaBenef' for t in tablas):
            st.warning("No se encontró la tabla 'dgBusquedaBenef'. Mostrando HTML de la respuesta:")
            st.code(r_res.text[:3000])
        
        # Si hay tabla, mostrar el DataFrame
        grid = soup_res.find(id="dgBusquedaBenef")
        if grid:
            try:
                df = pd.read_html(StringIO(str(grid)))[0]
                st.write("**Tabla encontrada:**")
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"No se pudo convertir a DataFrame: {e}")
