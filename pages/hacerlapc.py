import streamlit as st
import pandas as pd
import requests
import time
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (SISA)")
st.markdown("---")

# --- INTERFAZ DE USUARIO ---
dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=200, placeholder="Ejemplo:\n25131361\n25808007")
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

def obtener_cookies_frescas():
    """Obtiene una sesión nueva de SISA automáticamente"""
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        }
        # Entramos a la web para recibir la cookie JSESSIONID
        session.get("https://sisa.msal.gov.ar/sisa/", headers=headers, timeout=10)
        return session.cookies.get_dict()
    except:
        return {}

def extraer_datos_gwt(texto, dni_buscado):
    """Busca el DNI y extrae los datos en las posiciones i+2 e i+3"""
    try:
        # Buscamos la lista de strings donde viajan los datos
        match = re.search(r'\["(ar\.gob\.msal\.sisa\.client\.entitys\.list\.PageList.*?)\]', texto)
        if not match:
            match = re.search(r'(\["DNI".*?\])', texto)
            
        if match:
            contenido = match.group(1)
            # Limpiamos comillas y dividimos la lista
            partes = [p.strip().replace('"', '') for p in contenido.split(',')]
            
            if str(dni_buscado) in partes:
                idx = partes.index(str(dni_buscado))
                # La Obra Social está 2 posiciones adelante y el Nombre 3
                return partes[idx + 2], partes[idx + 3]
        return "No hallado", "No hallado"
    except:
        return None, None

def consultar_sisa_directo(dni, cookies):
    """Envía la petición técnica al servidor de SISA"""
    url = "https://sisa.msal.gov.ar/sisa/sisa/service/list"
    
    # El payload exacto que interceptamos del tráfico real
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"
    
    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://sisa.msal.gov.ar/sisa/",
        "Origin": "https://sisa.msal.gov.ar"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, cookies=cookies, timeout=15)
        cobertura, nombre = extraer_datos_gwt(response.text, dni)
        
        if cobertura == "No hallado":
            return {"DNI": dni, "Cobertura": "Sin datos en SISA", "Beneficiario": "-", "Estado": "❌ Vacío"}
        elif cobertura:
            return {"DNI": dni, "Cobertura": cobertura, "Beneficiario": nombre, "Estado": "✅ OK"}
        else:
            return {"DNI": dni, "Cobertura": "Error de formato", "Beneficiario": "-", "Estado": "⚠️ Reintentar"}
    except:
        return {"DNI": dni, "Cobertura": "Fallo conexión", "Beneficiario": "-", "Estado": "📡 Error"}

# --- LÓGICA PRINCIPAL ---
if buscar_btn and dni_input:
    with st.spinner("🔄 Conectando con SISA y renovando sesión..."):
        cookies_sesion = obtener_cookies_frescas()
    
    if not cookies_sesion:
        st.error("Error: No se pudo obtener una sesión de SISA. Intentá de nuevo.")
    else:
        dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
        total = len(dnis)
        resultados = []
        
        barra = st.progress(0)
        status_msg = st.empty()
        
        for i, dni in enumerate(dnis):
            status_msg.text(f"Procesando {i+1} de {total}: DNI {dni}")
            resultados.append(consultar_sisa_directo(dni, cookies_sesion))
            barra.progress((i + 1) / total)
            time.sleep(0.3) # Pausa de seguridad para evitar bloqueos
            
        status_msg.success(f"¡Listo! Se procesaron {total} consultas.")
        
        # Mostramos la tabla final
        df_final = pd.DataFrame(resultados)
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        
        # Opción de descarga
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte (CSV)", csv, "reporte_sisa.csv", "text/csv")
