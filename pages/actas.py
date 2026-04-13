import streamlit as st
import pandas as pd
import sqlite3

# Configuración inicial
st.title("Sistema de Carga - Padrón OSECAC")

# 1. Definimos las columnas que NO pueden faltar
COLUMNAS_CRITICAS = ['CUIT', 'RAZON SOCIAL', 'DEUDA PRESUNTA']

# 2. El Cargador (Uploader)
archivo = st.file_uploader("Subir Padrón de Deuda Presunta", type=["xlsx", "xls"])

if archivo:
    try:
        # Leemos el archivo
        df = pd.read_excel(archivo)
        
        # Estandarizamos los nombres de las columnas (quitamos espacios y pasamos a mayúsculas)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # VALIDACIÓN: Verificamos si están las columnas críticas
        faltantes = [c for c in COLUMNAS_CRITICAS if c not in df.columns]
        
        if faltantes:
            st.error(f"❌ El archivo no es correcto. Faltan las columnas: {', '.join(faltantes)}")
        else:
            st.success("✅ Estructura de Excel validada.")
            
            # --- LIMPIEZA DE DATOS ---
            # Quitamos el signo $ y convertimos la deuda a número para que la DB lo acepte
            if 'DEUDA PRESUNTA' in df.columns:
                df['DEUDA PRESUNTA'] = df['DEUDA PRESUNTA'].replace({'\$': '', '\.': '', ',': '.'}, regex=True).astype(float)
            
            # --- RESUMEN ANTES DE GUARDAR ---
            num_registros = len(df)
            deuda_total = df['DEUDA PRESUNTA'].sum()
            
            st.write("### Resumen del archivo detectado:")
            col1, col2 = st.columns(2)
            col1.metric("Total de Registros", f"{num_registros:,}")
            col2.metric("Monto Total en Excel", f"${deuda_total:,.2f}")
            
            st.warning("¿Deseas integrar estos datos a la base de datos permanente?")
            
            # --- BOTÓN DE CONFIRMACIÓN FINAL ---
            if st.button("Confirmar y Guardar en Base de Datos"):
                try:
                    # Conectamos a la base de datos (se crea si no existe)
                    conn = sqlite3.connect('base_osecac_miramar.db')
                    
                    # Guardamos los datos
                    # 'append' agrega lo nuevo a lo que ya existía
                    df.to_sql('padron_historico', conn, if_exists='append', index=False)
                    
                    conn.close()
                    st.success(f"🎊 ¡Éxito! Se han procesado e insertado {num_registros} registros correctamente.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al escribir en la base de datos: {e}")

    except Exception as e:
        st.error(f"No se pudo leer el archivo. Asegúrate de que no esté abierto en Excel. Error: {e}")
