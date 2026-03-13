import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (SISA)")

# --- INPUTS (SIEMPRE ARRIBA) ---
dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150)
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")   # <--- DEFINICIÓN ANTES DEL IF

# --- FUNCIONES ---
def extraer_datos_gwt(texto, dni_buscado):
    try:
        match = re.search(r'\["(ar\.gob\.msal\.sisa\.client\.entitys\.list\.PageList.*?)\]', texto)
        if not match:
            match = re.search(r'(\["DNI".*?\])', texto)
        if match:
            contenido = match.group(1)
            partes = [p.strip().replace('"', '') for p in contenido.split(',')]
            if str(dni_buscado) in partes:
                idx = partes.index(str(dni_buscado))
                return partes[idx + 2], partes[idx + 3]
        return "No hallado", "No hallado"
    except:
        return None, None

def obtener_cookies_frescas():
    """Obtiene cookies nuevas de SISA (JSESSIONID y las otras)"""
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8",
    }
    session.get("https://sisa.msal.gov.ar/sisa/", headers=headers, timeout=10)
    return session.cookies.get_dict()

def consultar_sisa_con_cookies(dni, cookies):
    url = "https://sisa.msal.gov.ar/sisa/sisa/service/list"
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"
    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://sisa.msal.gov.ar/sisa/",
        "Origin": "https://sisa.msal.gov.ar",
        "Accept": "*/*"
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
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Fallo conexión", "Beneficiario": "-", "Estado": "📡 Error"}

# --- LÓGICA PRINCIPAL ---
if buscar_btn and dni_input:
    with st.spinner("Obteniendo sesión nueva..."):
        cookies_nuevas = obtener_cookies_frescas()
    
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    resultados = []
    barra = st.progress(0)
    for i, d in enumerate(dnis):
        resultados.append(consultar_sisa_con_cookies(d, cookies_nuevas))
        barra.progress((i + 1) / len(dnis))
        time.sleep(0.3)
    
    st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
    csv = pd.DataFrame(resultados).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "resultados_puco.csv")
