import streamlit as st
import os
from supabase import create_client

st.set_page_config(page_title="Boletín Oficial", layout="wide")
st.title("📰 Boletín Oficial - Diagnóstico")

# ── Diagnóstico de secrets ──────────────────────────────────────────────────
st.subheader("🔍 Claves disponibles en st.secrets")
try:
    claves = list(st.secrets.keys())
    st.write(claves)

    # Verificar cada clave importante
    for clave in ["SUPABASE_URL", "SUPABASE_KEY", "GH_TOKEN"]:
        if clave in claves:
            valor = st.secrets[clave]
            st.success(f"✅ {clave} encontrada — primeros 10 chars: `{str(valor)[:10]}...`")
        else:
            st.error(f"❌ {clave} NO encontrada en secrets")

except Exception as e:
    st.error(f"Error leyendo secrets: {e}")

st.divider()

# ── Prueba de conexión a Supabase ───────────────────────────────────────────
st.subheader("🔌 Prueba de conexión a Supabase")
if st.button("Probar Supabase"):
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)
        data = supabase.table("edictos").select("*").limit(1).execute()
        st.success("✅ Conexión exitosa")
        st.write(data)
    except Exception as e:
        st.error(f"❌ Error: {e}")

st.divider()

# ── Prueba del token de GitHub ──────────────────────────────────────────────
st.subheader("🐙 Prueba del token de GitHub")
if st.button("Verificar GH_TOKEN"):
    try:
        token = st.secrets["GH_TOKEN"]
        import urllib.request
        import json
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            st.success(f"✅ Token válido — usuario: `{data.get('login')}`")
    except KeyError:
        st.error("❌ GH_TOKEN no está en secrets")
    except Exception as e:
        st.error(f"❌ Error verificando token: {e}")
