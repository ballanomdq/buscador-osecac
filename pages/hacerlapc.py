import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido")

dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150)
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"

    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://sisa.msal.gov.ar/sisa/"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        text = response.text
        
        # El secreto: extraer la lista de strings que viene entre corchetes
        if "[" in text and "]" in text:
            # Limpiamos el texto para quedarnos solo con lo que está dentro de [ ]
            match = re.search(r'\[(.*)\]', text)
            if match:
                lista_datos = [s.strip('"') for s in match.group(1).split(',')]
                
                # Buscamos si "BALLANO" o la Obra Social están en esa lista
                # Generalmente el nombre es el último elemento y la obra social el penúltimo
                nombre = "-"
                obra_social = "Sin Cobertura"
                
                # Buscamos texto que parezca una obra social (en mayúsculas largas)
                for item in lista_datos:
                    if "OBRA SOCIAL" in item or "OSECAC" in item or "UNION" in item:
                        obra_social = item
                    if dni not in item and len(item) > 15 and "ar.gob" not in item and "java" not in item:
                        nombre = item

                if obra_social != "Sin Cobertura" or nombre != "-":
                    return {"DNI": dni, "Cobertura": obra_social, "Beneficiario": nombre, "Estado": "✅ OK"}
        
        return {"DNI": dni, "Cobertura": "No hallado", "Beneficiario": "-", "Estado": "❌ Vacío"}
            
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error", "Beneficiario": "-", "Estado": "📡 Fallo"}

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    res_list = []
    prog = st.progress(0)
    for i, d in enumerate(dnis):
        res_list.append(consultar_sisa_directo(d))
        prog.progress((i + 1) / len(dnis))
        time.sleep(0.2)
        
    st.dataframe(pd.DataFrame(res_list), use_container_width=True, hide_index=True)
