import streamlit as st
import os
from supabase import create_client, Client

st.set_page_config(page_title="Boletín Oficial", layout="wide")

st.title("📰 Boletín Oficial - Fiscalización")

def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except:
        pass
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key
    return None, None

SUPABASE_URL, SUPABASE_KEY = get_credentials()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("""
    ❌ **Faltan las credenciales de Supabase.**

    En Streamlit Cloud, agrégalas en **Settings → Secrets**:
SUPABASE_URL = "https://vuxchvmixyuwoltletio.supabase.co"
SUPABASE_KEY = "sb_publishable_7ibXM7nyiR7tFImAD-K5dw_qtVm6H1c"

text
Luego reinicia la app (tres puntos → Reboot).
""")
st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.success("✅ Conexión a Supabase configurada correctamente.")

if st.button("🔌 Probar conexión a Supabase"):
try:
    data = supabase.table("edictos").select("*").limit(1).execute()
    st.success("✅ Conexión exitosa. Datos obtenidos:")
    st.write(data)
except Exception as e:
    st.error(f"❌ Error en la conexión: {e}")
    st.info("Revisá que la tabla 'edictos' exista en tu proyecto de Supabase.")
