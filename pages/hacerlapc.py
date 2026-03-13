import streamlit as st
import pandas as pd
import requests
import time

# --- Configuración ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (SISA)")

# UI
dni_input = st.text_area("Ingresá DNIs (uno por línea):", height=150)
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    # Este es el "ADN" que capturamos del Payload
    # Reemplazamos el DNI en la posición correcta de la cadena
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"

    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6", # Este código es la llave
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        text = response.text
        
        # Si la respuesta contiene los datos (como el que me pasaste)
        if "ar.gob.msal.sisa.client.entitys.list.Row" in text:
            # Extraemos los datos basándonos en la estructura del Response que me diste
            partes = text.split('"')
            # En tu respuesta: [..., "DNI", "DNI_NUM", "SEXO", "OBRA_SOCIAL", "NOMBRE"]
            # Buscamos la posición del DNI y tomamos los siguientes
            idx = partes.index(str(dni))
            return {
                "DNI": dni,
                "Cobertura": partes[idx + 2], # Obra Social
                "Beneficiario": partes[idx + 3], # Nombre Completo
                "Estado": "✅ OK"
            }
        else:
            return {"DNI": dni, "Cobertura": "Sin Cobertura", "Beneficiario": "-", "Estado": "⚠️ No hallado"}
            
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error de conexión", "Beneficiario": "-", "Estado": "❌ Error"}

if buscar_btn and dni_input:
    lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    resultados = []
    
    progreso = st.progress(0)
    status = st.empty()
    
    for i, dni in enumerate(lista_dnis):
        status.text(f"Consultando {dni}...")
        res = consultar_sisa_directo(dni)
        resultados.append(res)
        progreso.progress((i + 1) / len(lista_dnis))
        time.sleep(0.2) # Casi no necesita espera
        
    df = pd.DataFrame(resultados)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Descarga
    st.download_button("📥 Descargar Resultados", df.to_csv(index=False).encode('utf-8'), "consulta_sisa.csv")
