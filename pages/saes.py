import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Automatización SAES", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔐 Módulo de Acceso y Consulta SAES")
st.markdown("---")

if st.button("⬅️ Volver al Menú Principal"):
    st.switch_page("main.py")  # Cambia por el nombre de tu archivo principal si es distinto

# PASO 1: Credenciales de acceso
st.subheader("1️⃣ Credenciales de SAES")
col1, col2 = st.columns(2)
with col1:
    usuario_saes = st.text_input("Usuario:")
with col2:
    pass_saes = st.text_input("Contraseña:", type="password")

# Botón para simular / realizar el login
if st.button("🔑 Conectar e Iniciar Sesión"):
    if usuario_saes and pass_saes:
        st.session_state["saes_conectado"] = True
        st.success("✅ Conectado a SAES correctamente. Ya puedes buscar por DNI.")
    else:
        st.warning("⚠️ Debes ingresar usuario y contraseña.")

# PASO 2: Búsqueda por DNI (se activa solo si está conectado)
if st.session_state.get("saes_conectado", False):
    st.markdown("---")
    st.subheader("2️⃣ Consulta de Beneficiario")
    
    dni_ingresado = st.text_input("Ingrese DNI a buscar:")
    
    if st.button("🔍 Buscar en SAES"):
        if dni_ingresado:
            with st.spinner(f"Consultando DNI {dni_ingresado} en el portal..."):
                
                # --- AQUÍ ES DONDE SE CONECTARÁ EL AUTOMATIZADOR ---
                # Simulamos la respuesta para que veas cómo se dibuja la tabla en pantalla:
                
                datos_simulados = {
                    "DNI": [dni_ingresado],
                    "Beneficiario": ["PEREZ JUAN CARLOS"],
                    "Prestación / Medicamento": ["EPILEPSIA - TRATAMIENTO PROLONGADO"],
                    "Estado SAES": ["AUTORIZADO"],
                    "Nro. Solicitud": ["OP-998231"],
                    "Fecha Actualización": ["2026-10-26"]
                }
                df_res = pd.DataFrame(datos_simulados)
                
                st.markdown("### 📋 Datos extraídos del portal:")
                st.dataframe(df_res, use_container_width=True)
                st.success("¡Datos recuperados con éxito!")
        else:
            st.warning("Escribe un DNI para realizar la búsqueda.")
