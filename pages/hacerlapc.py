import streamlit as st
import pandas as pd
import requests
import time
import re

# --- Configuración Visual ---
st.set_page_config(page_title="PUCO RÁPIDO - OSECAC", layout="wide")
st.title("⚡ Buscador PUCO Ultrarrápido (Versión Blindada)")
st.markdown("---")

# --- Entrada de datos ---
dni_input = st.text_area("Ingresá los DNIs (uno por línea):", height=150, placeholder="Ejemplo:\n25131361\n25808007")
buscar_btn = st.button("🚀 Consultar Ahora", type="primary")

# --- Función de parseo mejorada ---
def parsear_respuesta_gwt(respuesta_texto, dni_buscado):
    """
    Parsea la respuesta GWT-RPC de SISA y extrae cobertura y denominación para un DNI.
    """
    try:
        # 1. Verificar que empiece con //OK
        if not respuesta_texto.startswith("//OK"):
            st.error("La respuesta no comienza con //OK")
            return None, None
        
        # 2. Quitar el prefijo
        contenido = respuesta_texto[4:]
        
        # 3. Encontrar el bloque principal (todo entre corchetes)
        balance = 0
        inicio = -1
        bloque_principal = ""
        for i, ch in enumerate(contenido):
            if ch == '[':
                if balance == 0:
                    inicio = i
                balance += 1
            elif ch == ']':
                balance -= 1
                if balance == 0 and inicio != -1:
                    bloque_principal = contenido[inicio:i+1]
                    break
        if not bloque_principal:
            st.error("No se encontró bloque principal")
            return None, None
        
        # 4. Extraer todos los arrays anidados dentro del bloque principal
        arrays_anidados = []
        i = 0
        while i < len(bloque_principal):
            if bloque_principal[i] == '[':
                j = i + 1
                sub_balance = 1
                while j < len(bloque_principal):
                    if bloque_principal[j] == '[':
                        sub_balance += 1
                    elif bloque_principal[j] == ']':
                        sub_balance -= 1
                        if sub_balance == 0:
                            arrays_anidados.append(bloque_principal[i:j+1])
                            break
                    j += 1
                i = j + 1
            else:
                i += 1
        
        if not arrays_anidados:
            st.error("No se encontraron arrays anidados")
            return None, None
        
        # 5. El último array suele contener los datos (lista de strings)
        datos_array_str = arrays_anidados[-1]
        
        # 6. Extraer todos los strings entre comillas (manejando escapes)
        # Usamos una expresión regular que captura el contenido de comillas dobles,
        # permitiendo escapes como \"
        patron_string = r'"((?:\\"|[^"\\]|\\.)*?)"'
        strings_encontrados = re.findall(patron_string, datos_array_str)
        
        # 7. Limpiar los strings (reemplazar escapes)
        strings_limpios = []
        for s in strings_encontrados:
            # Reemplazar \" por " y \\ por \
            s = s.replace('\\"', '"').replace('\\\\', '\\')
            strings_limpios.append(s)
        
        # (Opcional) Mostrar los strings para depuración
        # st.write("Strings encontrados:", strings_limpios)
        
        # 8. Buscar el DNI en la lista
        dni_str = str(dni_buscado)
        try:
            idx = strings_limpios.index(dni_str)
            # Verificar que haya suficientes elementos para las posiciones +2 y +3
            if idx + 3 < len(strings_limpios):
                cobertura = strings_limpios[idx + 2]
                denominacion = strings_limpios[idx + 3]
                return cobertura, denominacion
            else:
                st.warning(f"Índice fuera de rango: idx={idx}, longitud={len(strings_limpios)}")
                return None, None
        except ValueError:
            # DNI no encontrado
            return "No hallado", "No hallado"
        
    except Exception as e:
        st.error(f"Error en parseo: {str(e)}")
        return None, None

# --- Función de consulta directa a SISA ---
def consultar_sisa_directo(dni):
    url = "https://sisa.msal.gov.ar/sisa/sisa/list"
    
    # Payload - reemplazar {dni} por el número real
    payload = f"7|0|14|https://sisa.msal.gov.ar/sisa/sisa/|5CFBDB55F3DE4A47FE42E765E5AA02D3|ar.gob.msal.sisa.client.commons.components.lista.service.ListService|getPage|java.lang.Integer/3438268394|java.util.List|Z|ar.gob.msal.sisa.shared.model.list.ComplexFilter/30068811|java.util.ArrayList/4159755760|ar.gob.msal.sisa.client.commons.components.lista.simple.SearchFilter/1978531670|97390|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATION/3408968308|ar.gob.msal.sisa.client.entitys.list.Filter$OPERATOR/860546718|{dni}|1|2|3|4|10|5|5|5|6|6|5|7|5|6|8|5|790|5|1|-2|9|0|9|1|10|11|12|0|13|0|0|14|0|0|1|5|25|0|0|"
    
    headers = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Module-Base": "https://sisa.msal.gov.ar/sisa/sisa/",
        "X-GWT-Permutation": "AC8C40F803E54F7569451C561053A1B6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://sisa.msal.gov.ar/sisa/"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {"DNI": dni, "Cobertura": f"HTTP {response.status_code}", "Beneficiario": "-", "Estado": "❌ Error"}
        
        # Mostrar parte de la respuesta para depuración (opcional)
        # st.write(f"Respuesta para DNI {dni}:", response.text[:300])
        
        cobertura, nombre = parsear_respuesta_gwt(response.text, dni)
        
        if cobertura is None:
            return {"DNI": dni, "Cobertura": "Error de Parseo", "Beneficiario": "-", "Estado": "⚠️ Formato"}
        elif cobertura == "No hallado":
            return {"DNI": dni, "Cobertura": "Sin Cobertura", "Beneficiario": "-", "Estado": "❌ Vacío"}
        else:
            return {"DNI": dni, "Cobertura": cobertura, "Beneficiario": nombre, "Estado": "✅ OK"}
            
    except requests.exceptions.Timeout:
        return {"DNI": dni, "Cobertura": "Timeout", "Beneficiario": "-", "Estado": "⏱️"}
    except Exception as e:
        return {"DNI": dni, "Cobertura": f"Error: {str(e)[:30]}", "Beneficiario": "-", "Estado": "📡 Fallo"}

# --- Lógica principal ---
if buscar_btn and dni_input:
    lista_dnis = [d.strip() for d in dni_input.split('\n') if d.strip()]
    if not lista_dnis:
        st.warning("Ingresá al menos un DNI válido.")
    else:
        resultados = []
        barra = st.progress(0)
        info = st.empty()
        
        for i, dni in enumerate(lista_dnis):
            info.markdown(f"Consultando: **{dni}**...")
            resultados.append(consultar_sisa_directo(dni))
            barra.progress((i + 1) / len(lista_dnis))
            # Pausa corta para no saturar
            time.sleep(0.3)
        
        info.success("¡Proceso completado!")
        
        # Mostrar resultados
        df = pd.DataFrame(resultados)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Botón de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="resultados_puco.csv",
            mime="text/csv"
        )
