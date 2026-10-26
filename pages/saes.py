import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Diagnóstico SAES v3", layout="wide")
st.title("🔍 Diagnóstico de Página Principal")

BASE = "http://portal.gmssa.com.ar/saes/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

if st.button("Ejecutar Diagnóstico Completo"):
    with st.spinner("Conectando y analizando..."):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})

        # 1. LOGIN
        r = s.get(BASE + "Login.aspx", timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        data = {i["name"]: i.get("value", "") for i in soup.find_all("input", {"type": "hidden"}) if i.get("name")}
        data.update({"txtUser": "rballano", "txtPassword": "654321", "imgbtnSend.x": "10", "imgbtnSend.y": "10"})
        s.post(BASE + "Login.aspx", data=data, headers={"Referer": BASE + "Login.aspx"}, allow_redirects=False, timeout=30)
        
        st.success("✅ Login completado (cookies obtenidas).")

        # 2. INSPECCIONAR welcome.aspx (Paso 1 de Claude)
        st.write("### Paso 1: Inspeccionando welcome.aspx")
        r3 = s.get(BASE + "welcome.aspx", allow_redirects=False, headers={"Referer": BASE + "Login.aspx"}, timeout=30)
        soup3 = BeautifulSoup(r3.text, "html.parser")
        
        st.write(f"**Largo del HTML:** `{len(r3.text)}` caracteres")
        st.write(f"**Título de la página:** `{soup3.title.string if soup3.title else 'Sin título'}`")
        st.write(f"**¿Contiene 'txtUser' (es el login)?:** `{'txtUser' in r3.text}`")
        st.write(f"**¿Contiene 'frameset' en el texto?:** `{'frameset' in r3.text.lower()}`")
        st.write(f"**¿Contiene 'document.write'?:** `{'document.write' in r3.text.lower()}`")
        
        st.write("**Scripts con src:**")
        scripts = [x.get("src") for x in soup3.find_all("script") if x.get("src")]
        if scripts:
            for src in scripts:
                st.code(src)
        else:
            st.write("No se encontraron scripts externos.")
            
        st.write("**Primeros 2500 caracteres del body:**")
        st.code(r3.text[:2500])

        # 3. PROBAR CANDIDATAS (Paso 3 de Claude)
        st.write("### Paso 3: Probando URLs candidatas a página principal")
        candidatas = ["welcome.aspx", "Default.aspx", "Main.aspx", "Index.aspx", "Home.aspx", "frmMain.aspx", "Principal.aspx", "Menu.aspx", "MenuPrincipal.aspx", "frmPrincipal.aspx"]
        
        resultados = []
        for p in candidatas:
            try:
                r_test = s.get(BASE + p, allow_redirects=False, timeout=15)
                t = r_test.text
                es_login = "txtUser" in t
                tiene_frames = t.lower().count("<frame")
                resultados.append({
                    "URL": p,
                    "Status": r_test.status_code,
                    "Largo": len(t),
                    "Es Login?": "❌ Sí" if es_login else "✅ No",
                    "Frames": tiene_frames
                })
            except Exception as e:
                resultados.append({"URL": p, "Status": "Error", "Largo": 0, "Es Login?": "?", "Frames": 0})
        
        st.dataframe(resultados, use_container_width=True, hide_index=True)

        # 4. VEREDICTO
        st.write("### Veredicto")
        exitos = [r for r in resultados if r["Es Login?"] == "✅ No" and r["Frames"] >= 2]
        if exitos:
            st.success(f"🎉 ¡Encontramos la página principal! Es: `{exitos[0]['URL']}`")
        else:
            st.warning("Ninguna URL candidata tiene frames. Puede que el login no esté funcionando realmente o que la página principal use JavaScript para cargar los frames.")
