import streamlit as st

st.set_page_config(
    page_title="Boletín Oficial - Fiscalización",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📰 Boletín Oficial - Fiscalización")
st.markdown("Esta página mostrará los edictos judiciales, sucesorios, transferencias y concursos filtrados por las localidades de interés.")

# Aquí luego agregaremos la lógica para consultar la base de datos
# y mostrar los resultados con filtros.

st.info("🛠️ Página en construcción. Próximamente se mostrarán los resultados automáticos del scraping diario.")
