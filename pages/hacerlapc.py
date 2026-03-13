import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (SISA)")

dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150)
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def extraer_datos_gwt(texto, dni_buscado):
    try:
        # Buscamos la lista de strings que contiene la data real
        match = re.search(r'\["(ar\.gob\.msal\.sisa\.client\.entitys\.list\.PageList.*?)\]', texto)
        if not match:
            match = re.search(r'(\["DNI".*?\])', texto)
            
        if match:
            contenido = match.group(1)
            # Limpiamos comillas y dividimos
            partes = [p.strip().replace('"', '') for p in contenido.split(',')]
            
            if str(dni_buscado) in partes:
                idx = partes.index(str(dni_buscado))
                # Estructura: DNI, Sexo, Obra Social, Nombre
                return partes[idx + 2], partes[idx + 3]
        return "No hallado", "No hallado"
    except:
        return None, None

def consultar_sisa_directo(dni):
    # URL corregida según tu CURL
    url = "https://sisa.msal.gov.ar/sisa/sisa/service/list"
    
    # Payload exacto
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"
    
    # Headers extraídos de tu comando CURL
    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://sisa.msal.gov.ar/sisa/",
        "Origin": "https://sisa.msal.gov.ar",
        "Accept": "*/*"
    }
    
    # Cookies de tu sesión actual para evitar el bloqueo
    cookies = {
        "JSESSIONID": "8D8157B77E8C0245E781574189F72C16.jvm1",
        "6c28aa23ecdbb138ddc0208f3645ebd7": "4dddbce1737103b9671169f1197f761f",
        "a28d40bfc02d38069ca0e0818f0ce5e3": "a4a3b370f140ab3c87f722952f7818f9"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, cookies=cookies, timeout=15)
        cobertura, nombre = extraer_datos_gwt(response.text, dni)
        
        if cobertura == "No hallado":
            return {"DNI": dni, "Cobertura": "Sin datos en SISA", "Beneficiario": "-", "Estado": "❌ No hallado"}
        elif cobertura:
            return {"DNI": dni, "Cobertura": cobertura, "Beneficiario": nombre, "Estado": "✅ OK"}
        else:
            return {"DNI": dni, "Cobertura": "Error de formato", "Beneficiario": "-", "Estado": "⚠️ Reintentar"}
    except:
        return {"DNI": dni, "Cobertura": "Fallo conexión", "Beneficiario": "-", "Estado": "📡 Error"}

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    res = []
    barra = st.progress(0)
    for i, d in enumerate(dnis):
        res.append(consultar_sisa_directo(d))
        barra.progress((i + 1) / len(dnis))
        time.sleep(0.3)
    
    st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
