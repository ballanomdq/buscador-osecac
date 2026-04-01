import streamlit as st
import os
from supabase import create_client, Client

st.set_page_config(page_title="Boletín Oficial", layout="wide")

st.title("📰 Boletín Oficial - Fiscalización")

# ----- Función para obtener las credenciales de forma segura -----
def get_supabase_credentials():
    # Priorizar st.secrets (para Streamlit Cloud)
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except Exception:
        pass

    # Fallback: variables de entorno (para GitHub Actions o local)
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key

    return None, None

# ----- Mostrar estado de la conexión -----
SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("""
    ⚠️ **Faltan las credenciales de Supabase.**

    En Streamlit Cloud, debes agregarlas en **Settings → Secrets** con estos nombres:
    - `SUPABASE_URL`
    - `SUPABASE_KEY`

    Ejemplo:
