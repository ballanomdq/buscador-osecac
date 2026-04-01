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
