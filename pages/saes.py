import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="Diagnóstico SAES", layout="wide")

st.title("🔍 Diagnóstico de Navegación SAES")

if "diagnostico" not in st.session_state:
    st.session_state.diagnostico = ""

if st.button("Iniciar Diagnóstico"):
    with st.spinner("Analizando SAES..."):
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            # 1. LOGIN
            login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
            r = session.get(login_url, headers=headers, timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
            
            payload = {
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": viewstate,
                "txtUser": "rballano",
                "txtPassword": "654321",
                "imgbtnSend.x": "0",
                "imgbtnSend.y": "0"
            }
            r_post = session.post(login_url, data=payload, headers=headers, timeout=30, allow_redirects=True)
            
            # 2. VERIFICAR URL REAL (¿hay sesión cookieless?)
            st.write("### 1. URL después del login")
            st.code(r_post.url)
            
            # 3. OBTENER EL FRAMESET Y SUS FRAMES
            r_main = session.get("http://portal.gmssa.com.ar/saes/welcome.aspx", headers=headers, allow_redirects=True)
            soup_main = BeautifulSoup(r_main.text, 'html.parser')
            
            st.write("### 2. URL real de welcome.aspx")
            st.code(r_main.url)
            
            st.write("### 3. Frames encontrados")
            frames = {}
            for f in soup_main.find_all("frame"):
                src = f.get("src")
                if src:
                    url_completa = urljoin(r_main.url, src)
                    frames[f.get("name")] = url_completa
                    st.write(f"**{f.get('name')}:** `{src}`")
                    st.write(f"URL completa: `{url_completa}`")
            
            # 4. NAVEGAR AL FRAME DEL MENÚ
            if "NavigBar" in frames:
                st.write("### 4. Analizando el menú NavigBar")
                nav_url = frames["NavigBar"]
                nav = session.get(nav_url, headers=headers)
                nav_soup = BeautifulSoup(nav.text, 'html.parser')
                
                # Ver links y botones
                st.write("Links y botones encontrados:")
                for a in nav_soup.find_all(["a", "input"]):
                    onclick = a.get("onclick")
                    href = a.get("href")
                    name = a.get("name")
                    id_val = a.get("id")
                    texto = a.text.strip()
                    if any([onclick, href, name]):
                        st.write(f"- **Texto:** `{texto}` | **Href:** `{href}` | **OnClick:** `{onclick}` | **Name:** `{name}`")
                
                st.write("### 5. Buscando '__doPostBack' en el código")
                if "__doPostBack" in nav.text:
                    st.success("¡Se encontró __doPostBack! (El menú usa postbacks de JavaScript)")
                    # Buscamos el EVENTTARGET del link de Consultas
                    consultas_link = nav_soup.find("a", string=lambda t: t and "Consultas" in t)
                    if consultas_link:
                        href = consultas_link.get("href", "")
                        st.write(f"Link 'Consultas' encontrado: `{href}`")
                        # Extraer el EVENTTARGET
                        import re
                        match = re.search(r"__doPostBack\('([^']+)'", href)
                        if match:
                            st.session_state.diagnostico = match.group(1)
                            st.success(f"__EVENTTARGET detectado: **{match.group(1)}**")
                else:
                    st.warning("No se encontró __doPostBack. El menú puede usar redirecciones directas.")
                
        except Exception as e:
            st.error(f"Error: {e}")

# Mostrar resultados de diagnóstico si los hay
if st.session_state.diagnostico:
    st.write("---")
    st.write("### 📌 Diagnóstico Final")
    st.write(f"El botón de Consultas se maneja con el __EVENTTARGET: **{st.session_state.diagnostico}**")
