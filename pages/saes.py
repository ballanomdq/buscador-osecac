import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Diagnóstico SAES v2", layout="wide")
st.title("🔍 Diagnóstico de Login v2")

BASE = "http://portal.gmssa.com.ar/saes/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

if st.button("Ejecutar Diagnóstico"):
    with st.spinner("Conectando..."):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})

        # 1. GET y datos del login
        r = s.get(BASE + "Login.aspx", timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        data = {i["name"]: i.get("value", "") for i in soup.find_all("input", {"type": "hidden"}) if i.get("name")}
        data.update({
            "txtUser": "rballano",
            "txtPassword": "654321",
            "imgbtnSend.x": "10",
            "imgbtnSend.y": "10",
        })

        # 2. POST login
        r2 = s.post(BASE + "Login.aspx", data=data, headers={"Referer": BASE + "Login.aspx"}, allow_redirects=False, timeout=30)
        
        st.write("### 1. Cookies después del login")
        for c in s.cookies:
            st.write(f"- `{c.name}`")

        # 3. Buscar redirecciones por JS
        st.write("### 2. Buscando redirecciones (window.location, meta refresh, etc.)")
        redirecciones = []
        for pat in [r"window\.location\s*=\s*['\"]([^'\"]+)['\"]", r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r"<meta[^>]*refresh[^>]*url=([^'\" >]+)"]:
            matches = re.findall(pat, r2.text, flags=re.I)
            redirecciones.extend(matches)
        
        if redirecciones:
            st.success(f"¡Se encontraron {len(redirecciones)} redirecciones!")
            for url in set(redirecciones):
                st.code(url)
        else:
            st.warning("No se encontraron redirecciones por JS.")

        # 4. Intentar ir a welcome.aspx
        st.write("### 3. Probando ir a welcome.aspx")
        r3 = s.get(BASE + "welcome.aspx", allow_redirects=False, headers={"Referer": BASE + "Login.aspx"}, timeout=30)
        st.write(f"**Status:** `{r3.status_code}`")
        st.write(f"**Location:** `{r3.headers.get('Location')}`")
        
        if r3.status_code == 200:
            soup3 = BeautifulSoup(r3.text, "html.parser")
            frames = soup3.find_all("frame")
            st.write(f"**Frames encontrados:** `{len(frames)}`")
            for f in frames:
                st.write(f"- `{f.get('name')}` → `{f.get('src')}`")
                
            if len(frames) > 0:
                st.success("¡Tenemos frames! Podemos continuar.")
            else:
                st.warning("No hay frames. La página de welcome no cargó bien.")
        else:
            st.error("No se pudo cargar welcome.aspx.")
            st.write(r3.text[:500])
