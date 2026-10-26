import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Diagnóstico Login SAES", layout="wide")
st.title("🔍 Diagnóstico de Login")

BASE = "http://portal.gmssa.com.ar/saes/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

if st.button("Ejecutar Diagnóstico"):
    with st.spinner("Conectando..."):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})

        # 1) GET previo
        r = s.get(BASE + "Login.aspx", timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        data = {i["name"]: i.get("value", "") for i in soup.find_all("input", {"type": "hidden"}) if i.get("name")}

        st.write("### 1. Hidden fields encontrados en Login.aspx")
        st.write(list(data.keys()))

        # 2) Completar credenciales
        data.update({
            "txtUser": "rballano",
            "txtPassword": "654321",
            "imgbtnSend.x": "10",
            "imgbtnSend.y": "10",
        })

        # 3) POST SIN seguir redirects
        r2 = s.post(BASE + "Login.aspx", data=data, headers={"Referer": BASE + "Login.aspx"}, allow_redirects=False, timeout=30)

        st.write("### 2. Resultado del POST al login")
        st.write(f"**Status code:** `{r2.status_code}` (esperamos 302)")
        st.write(f"**Location:** `{r2.headers.get('Location')}`")
        st.write(f"**Set-Cookie:** `{r2.headers.get('Set-Cookie')}`")

        st.write("### 3. Cookies de la sesión")
        for c in s.cookies:
            st.write(f"- Nombre: `{c.name}` | Secure: `{c.secure}` | Domain: `{c.domain}` | Path: `{c.path}`")

        if r2.status_code == 200:
            st.warning("⚠️ El login devolvió 200 (fallido). Buscando mensajes de error...")
            soup_err = BeautifulSoup(r2.text, "html.parser")
            errores = soup_err.find_all(string=lambda t: t and ("error" in t.lower() or "incorrect" in t.lower() or "usuario" in t.lower()))
            if errores:
                for err in errores[:5]:
                    st.write(f"- `{err.strip()}`")
            else:
                st.write("No se encontraron mensajes de error visibles. Puede ser bloqueo por IP o falta un campo.")
