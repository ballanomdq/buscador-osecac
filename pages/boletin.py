import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Boletín Oficial", layout="wide")

# Leer los secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Conectar
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📰 Boletín Oficial - Fiscalización")

# Botón de prueba
if st.button("Probar conexión a Supabase"):
    try:
        # Intentar leer un solo registro
        data = supabase.table("edictos").select("*").limit(1).execute()
        st.success("✅ Conexión exitosa. Datos obtenidos:")
        st.write(data)
    except Exception as e:
        st.error(f"❌ Error: {e}")
