import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO (Versión Camuflada)")

dni_input = st.text_area("Ingresá los DNIs:", height=150)
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def consultar_sisa_humano(dni):
    # Intentamos obtener una sesión limpia en cada tanda
    session = requests.Session()
    
    # Headers MUY realistas
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "Origin": "https://sisa.msal.gov.ar",
        "Referer": "https://sisa.msal.gov.ar/sisa/",
    }

    # Payload corregido (7|0|14...)
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"

    try:
        # Primero "tocamos" la puerta
        session.get("https://sisa.msal.gov.ar/sisa/", timeout=10)
        
        # Tiramos el centro
        res = session.post(
            "https://sisa.msal.gov.ar/sisa/sisa/service/list", 
            data=payload, 
            headers=headers, 
            timeout=15
        )
        
        # Si SISA responde, buscamos tu DNI en el texto
        if str(dni) in res.text:
            # Buscamos patrones de texto entre comillas
            strings = re.findall(r'"([^"]*)"', res.text)
            idx = strings.index(str(dni))
            # OSECAC suele estar 2 o 3 posiciones después del DNI
            return {"DNI": dni, "Cobertura": strings[idx+2], "Beneficiario": strings[idx+3], "Estado": "✅"}
        
        return {"DNI": dni, "Cobertura": "No detectado", "Beneficiario": "-", "Estado": "❓"}
    except:
        return {"DNI": dni, "Cobertura": "Error de Red", "Beneficiario": "-", "Estado": "📡"}

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    resultados = []
    barra = st.progress(0)
    for i, d in enumerate(dnis):
        resultados.append(consultar_sisa_humano(d))
        barra.progress((i + 1) / len(dnis))
        time.sleep(1) # Pausa más larga para que no nos bloqueen
    st.dataframe(pd.DataFrame(resultados))
