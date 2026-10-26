import streamlit as st
import pandas as pd
import datetime

# 1. Configuración de página
st.set_page_config(page_title="Gestión SAES / Reclamos", layout="wide")

# Estilos visuales
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# Título y botón de volver
st.title("📦 Control de Reclamos y Gestiones SAES")
st.markdown("---")

if st.button("⬅️ Volver al Menú Principal"):
    st.switch_page("app.py")  # O el nombre de tu archivo principal (ej: main.py)

# Formulario de carga de reclamos
st.subheader("📋 Cargar nuevo reclamo / seguimiento")

col1, col2 = st.columns(2)

with col1:
    dni = st.text_input("DNI del Beneficiario:")
    nombre = st.text_input("Nombre y Apellido:")
    programa = st.selectbox(
        "Programa / Medicamento:", 
        ["EPILEPSIA", "DIABETES (DBT2)", "ONCOLOGIA", "HIV / HELIOS", "REINTEGROS", "OTROS"]
    )

with col2:
    estado_saes = st.selectbox(
        "Estado en SAES:", 
        ["AUTORIZADO", "PENDIENTE", "DESPACHADO / REMITO", "RECHAZADO"]
    )
    nro_solicitud = st.text_input("Nro. Solicitud / OP:")
    observaciones = st.text_area("Detalle del Reclamo / Observaciones:")

if st.button("💾 Guardar Gestión"):
    if dni and nombre:
        st.success(f"✅ Gestión registrada correctamente para DNI {dni}")
    else:
        st.warning("⚠️ Complete al menos DNI y Nombre para guardar.")
