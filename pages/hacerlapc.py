import streamlit as st
import pandas as pd
import requests
import time
import re

# --- Configuración Visual ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (Versión Blindada)")
st.markdown("---")

dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150, placeholder="Ejemplo:\n25131361\n25808007")
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def parsear_respuesta_gwt(respuesta_texto, dni_buscado):
    """ Función robusta aportada para desencriptar el mensaje //OK """
    try:
        if not respuesta_texto.startswith("//OK"):
            return None, None
        
        contenido = respuesta_texto[4:]
        # Buscamos el bloque principal de datos
        pila = []
        inicio_bloque = None
        bloque_principal = ""
        
        for i, char in enumerate(contenido):
            if char == '[':
                if not pila: inicio_bloque = i
                pila.append(i)
            elif char == ']':
                pila.pop()
                if not pila:
                    bloque_principal = contenido[inicio_bloque:i+1]
                    break
        
        if not bloque_principal: return None, None

        # Extraemos los arrays anidados y buscamos el que tiene los strings
        arrays_anidados = re.findall(r'\[(.*?)\]', bloque_principal, re.DOTALL)
        if not arrays_anidados: return None, None
        
        datos_array_str = arrays_anidados[-1] 
        # Capturamos strings entre comillas (manejando escapes)
        patron_string = r'"((?:\\"|[^"])*?)"'
        strings_encontrados = re.findall(patron_string, datos_array_str)
        strings_limpios = [s.replace('\\"', '"').replace('\\\\', '\\') for s in strings_encontrados]

        # Buscamos el DNI y extraemos posiciones +2 y +3
        try:
            idx = strings_limpios.index(str(dni_buscado))
            cobertura = strings_limpios[idx + 2] if idx + 2 < len(strings_limpios) else "No disponible"
            denominacion = strings_limpios[idx + 3] if idx + 3 < len(strings_limpios) else "No disponible"
            return cobertura, denominacion
        except ValueError:
            return "No hallado", "No hallado"
    except:
        return None, None

def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    # Payload y Headers que descubrimos nosotros
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
        cobertura, nombre = parsear_respuesta_gwt(response.text, dni)
        
        if cobertura and nombre:
            if cobertura == "No hallado":
                return {"DNI": dni, "Cobertura": "Sin Cobertura", "Beneficiario": "-", "Estado": "❌ Vacío"}
            return {"DNI": dni, "Cobertura": cobertura, "Beneficiario": nombre, "Estado": "✅ OK"}
        else:
            return {"DNI": dni, "Cobertura": "Error de Parseo", "Beneficiario": "-", "Estado": "⚠️ Formato"}
            
    except Exception as e:
        return {"DNI": dni, "Cobertura": "Error de Red", "Beneficiario": "-", "Estado": "📡 Fallo"}

# Lógica de la interfaz
if buscar_btn and dni_input:
    lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    resultados = []
    barra = st.progress(0)
    info = st.empty()
    
    for i, dni in enumerate(lista_dnis):
        info.markdown(f"Consultando: **{dni}**...")
        resultados.append(consultar_sisa_directo(dni))
        barra.progress((i + 1) / len(lista_dnis))
        time.sleep(0.4)
        
    info.success("¡Proceso completado!")
    st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
    st.download_button("📥 Descargar CSV", pd.DataFrame(resultados).to_csv(index=False).encode('utf-8'), "puco.csv")
