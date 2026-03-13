import streamlit as st
import pandas as pd
import requests
import time

# --- Configuración Visual ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido")
st.markdown("---")

dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150, placeholder="25131361")
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    # El ADN de la consulta que capturamos
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
        
        # Verificamos si la respuesta trajo datos (buscamos la marca de fila de SISA)
        if "ar.gob.msal.sisa.client.entitys.list.Row" in text:
            # Limpiamos el texto para convertirlo en una lista de Python
            # Buscamos la parte que tiene los nombres (entre los corchetes [ ])
            if "[" in text and "]" in text:
                data_str = text.split("[")[1].split("]")[0]
                partes = [p.strip('"') for p in data_str.split(',')]
                
                # Según tu respuesta //OK:
                # El DNI está en una posición, la Obra Social 2 lugares después, y el Nombre 3 después.
                try:
                    idx = partes.index(str(dni))
                    return {
                        "DNI": dni,
                        "Cobertura": partes[idx + 2], 
                        "Beneficiario": partes[idx + 3],
                        "Estado": "✅ OK"
                    }
                except:
                    # Intento alternativo si el índice falla
                    return {
                        "DNI": dni, 
                        "Cobertura": partes[-2], # Penúltimo
                        "Beneficiario": partes[-1], # Último
                        "Estado": "✅ OK (Alt)"
                    }
        
        return {"DNI": dni, "Cobertura": "Sin Cobertura / No hallado", "Beneficiario": "-", "Estado": "❌ Vacío"}
            
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error de Red", "Beneficiario": "-", "Estado": "📡 Fallo"}

if buscar_btn and dni_input:
    dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    res_list = []
    
    prog = st.progress(0)
    status = st.empty()
    
    for i, d in enumerate(dnis):
        status.markdown(f"Consultando: **{d}**")
        res_list.append(consultar_sisa_directo(d))
        prog.progress((i + 1) / len(dnis))
        time.sleep(0.2)
        
    status.success(f"¡Procesados {len(dnis)} documentos!")
    df = pd.DataFrame(res_list)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Descargar Planilla CSV", df.to_csv(index=False).encode('utf-8'), "puco_sisa.csv", "text/csv")
