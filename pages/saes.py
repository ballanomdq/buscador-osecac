import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="Diagnóstico SAES v3", layout="wide")
st.title("🔍 Diagnóstico de POST real")

BASE_URL = "http://portal.gmssa.com.ar/SAES/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def form_payload(html):
    """Extrae todos los campos de un formulario HTML."""
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
        
        # 3. Extraer TODOS los campos con el helper
        data, action = form_payload(r_cons.text)
        st.write(f"**Action del form:** `{action}`")
        st.write(f"**Cantidad de campos extraídos:** `{len(data)}`")
        st.write("**Campos extraídos (sin tokens):**")
        for k, v in data.items():
            if "VIEWSTATE" not in k and "EVENTVALIDATION" not in k:
                st.write(f"- `{k}`: `{v}`")
        
        # 4. Completar los campos de búsqueda
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
        st.write(f"**URL del POST:** `{post_url}`")
        
        r_res = s.post(post_url, data=data, headers={"Referer": url_cons})
        
        # 6. Verificar si trae la tabla
        tiene_tabla = "dgBusquedaBenef" in r_res.text
        st.write(f"**Status:** `{r_res.status_code}`")
        st.write(f"**¿Tiene la tabla 'dgBusquedaBenef'?** `{tiene_tabla}`")
        st.write(f"**Largo de la respuesta:** `{len(r_res.text)}` caracteres")
        
        if tiene_tabla:
            # Extraer tabla
            soup_res = BeautifulSoup(r_res.text, 'html.parser')
            tabla = soup_res.find('table', {'id': 'dgBusquedaBenef'})
            if tabla:
                filas = tabla.find_all('tr')
                datos = []
                for f in filas[1:]:
                    celdas = f.find_all('td')
                    if len(celdas) >= 9:
                        datos.append({
                            "Nro. Autorización": celdas[1].text.strip(),
                            "OP": celdas[2].text.strip(),
                            "AUT Desde": celdas[3].text.strip(),
                            "AUT Hasta": celdas[4].text.strip(),
                            "OP Desde": celdas[5].text.strip(),
                            "OP Hasta": celdas[6].text.strip(),
                            "Programa": celdas[7].text.strip(),
                            "Farmacia": celdas[8].text.strip(),
                        })
                st.dataframe(datos, use_container_width=True, hide_index=True)
        else:
            # Mostrar el HTML para comparar
            st.warning("No se encontró la tabla. Mostrando el HTML de la respuesta para comparar con Chrome:")
            st.code(r_res.text[:3000])
