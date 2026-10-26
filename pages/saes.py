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

st.title("🔐 Consulta Automática de Autorizaciones SAES")
st.markdown("---")

if st.button("⬅️ Volver al Menú Principal"):
    st.switch_page("main.py")

# Formulario unificado de consulta
with st.form("form_saes"):
    st.subheader("📋 Datos de Acceso y Consulta")
    
    col1, col2 = st.columns(2)
    with col1:
        # Puedes dejar tu usuario predeterminado para no tipear de más
        usuario_saes = st.text_input("Usuario SAES:", value="rballano")
    with col2:
        pass_saes = st.text_input("Contraseña SAES:", type="password")
    
    st.markdown("---")
    dni_ingresado = st.text_input("🔍 DNI del Beneficiario a consultar:")
    
    btn_consultar = st.form_submit_button("🚀 CONSULTAR EN SAES", use_container_width=True)

# Al presionar el botón de consulta
if btn_consultar:
    if not usuario_saes or not pass_saes:
        st.error("❌ Por favor completa el usuario y la contraseña.")
    elif not dni_ingresado:
        st.warning("⚠️ Por favor ingresa un DNI para buscar.")
    else:
        with st.spinner(f"Conectando a SAES con usuario '{usuario_saes}' y buscando DNI {dni_ingresado}..."):
            
            # --- AQUÍ CONECTAREMOS EL RASPADO/PLAYWRIGHT ---
            # Por ahora simulamos la lectura para ver el resultado en pantalla:
            
            datos_simulados = {
                "DNI": [dni_ingresado],
                "Beneficiario": ["PEREZ JUAN CARLOS"],
                "Programa": ["EPILEPSIA"],
                "Estado en SAES": ["AUTORIZADO"],
                "Nro. Solicitud / OP": ["OP-998231"],
                "Fecha Autorización": ["26/10/2026"]
            }
            
            df_res = pd.DataFrame(datos_simulados)
            
            st.success("✅ Datos recuperados de SAES correctamente:")
            st.dataframe(df_res, use_container_width=True)
