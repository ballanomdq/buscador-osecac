import streamlit as st
import pandas as pd
import requests
import time

# --- Configuración de la página ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")

st.title("⚡ Buscador PUCO Ultrarrápido (SISA)")

# UI de entrada
with st.container():
    st.subheader("📋 Consulta Masiva")
    dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150, placeholder="Ejemplo:\n25131361\n20444555")
    buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    # Payload capturado (ADN de la consulta)
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"

    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        text = response.text
        
        # Verificamos si la respuesta tiene datos reales
        if "ar.gob.msal.sisa.client.entitys.list.Row" in text:
            # Dividimos el texto por comillas para encontrar los datos
            partes = text.split('"')
            
            try:
                # Buscamos dónde está el DNI en la lista
                idx = partes.index(str(dni))
                
                # Ajuste de puntería según el Response capturado:
                # El Sexo está en idx + 1
                # La Obra Social está en idx + 2
                # El Nombre Completo está en idx + 3
                
                return {
                    "DNI": dni,
                    "Cobertura": partes[idx + 2],
                    "Beneficiario": partes[idx + 3],
                    "Estado": "✅ OK"
                }
            except:
                return {"DNI": dni, "Cobertura": "Error de lectura", "Beneficiario": "-", "Estado": "⚠️ Formato raro"}
        else:
            return {"DNI": dni, "Cobertura": "Sin Cobertura / No hallado", "Beneficiario": "-", "Estado": "❌ Vacío"}
            
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error de Conexión", "Beneficiario": "-", "Estado": "📡 Fallo red"}

# Lógica principal
if buscar_btn:
    if not dni_input.strip():
        st.warning("Por favor, ingresá al menos un DNI.")
    else:
        lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
        resultados = []
        
        # Barras de estado
        progreso = st.progress(0)
        status_text = st.empty()
        
        for i, dni in enumerate(lista_dnis):
            status_text.markdown(f"**Consultando:** `{dni}`...")
            res = consultar_sisa_directo(dni)
            resultados.append(res)
            progreso.progress((i + 1) / len(lista_dnis))
            time.sleep(0.3) # Pequeña pausa para no saturar
            
        status_text.success("¡Consulta finalizada!")
        
        # Mostrar tabla de resultados
        df = pd.DataFrame(resultados)
        st.subheader("📋 Resultados de la búsqueda")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Botón de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte CSV",
            data=csv,
            file_name="consulta_puco_sisa.csv",
            mime="text/csv",
            use_container_width=True
        )
