import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; margin-bottom: 5px; width: 100%; text-align: left;}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🏥 Portal SAES - Extraer Medicamentos")

st.markdown("""
### Paso 1: Abrí SAES y buscá el DNI
1. Hacé clic en el botón de abajo para abrir SAES en una pestaña nueva.
2. Logueate con tu usuario y contraseña.
3. Andá a **Adm. de Medicamentos → Consultas**.
4. Escribí el DNI y apretá **Enter**.
5. Cuando veas la tabla de trámites, **hacé clic en el ojito (👁️) de un trámite** para abrir el detalle.
6. **Copiá todo el HTML de esa página** (Ctrl + U, Ctrl + A, Ctrl + C).
7. Pegalo en el cuadro de abajo.
""")

if st.button("🌐 Abrir SAES en pestaña nueva"):
    st.markdown('<meta http-equiv="refresh" content="0; url=http://portal.gmssa.com.ar/SAES/Login.aspx">', unsafe_allow_html=True)
    st.info("Si no se abre automáticamente, hacé clic acá: [Abrir SAES](http://portal.gmssa.com.ar/SAES/Login.aspx)")

st.markdown("### Paso 2: Pegá el HTML del detalle")
html_input = st.text_area("Pegá acá el HTML de la página de detalle (Ctrl + U, Ctrl + A, Ctrl + C):", height=300)

if html_input:
    try:
        soup = BeautifulSoup(html_input, 'html.parser')
        
        # Extraer datos del beneficiario
        nombre = soup.find(id="lblNombre")
        documento = soup.find(id="lblNroDocumento")
        delegacion = soup.find(id="lblDelegacion")
        
        st.markdown("### 👤 Datos del beneficiario")
        if nombre: st.write(f"**Nombre:** {nombre.text.strip()}")
        if documento: st.write(f"**Documento:** {documento.text.strip()}")
        if delegacion: st.write(f"**Delegación:** {delegacion.text.strip()}")
        
        # Extraer tabla de medicamentos
        tabla = soup.find('table', {'id': 'grdDetalles__ctl2_gvDetallesOP'})
        if tabla:
            filas = tabla.find_all('tr')
            medicamentos = []
            for f in filas[1:]:  # Saltar encabezado
                celdas = f.find_all('td')
                if len(celdas) >= 4:
                    medicamentos.append({
                        "Droga": celdas[0].text.strip(),
                        "Presentación": celdas[1].text.strip(),
                        "Autorizado": celdas[2].text.strip(),
                        "Despachado": celdas[3].text.strip(),
                    })
            
            if medicamentos:
                st.markdown("### 💊 Medicamentos")
                st.dataframe(pd.DataFrame(medicamentos), use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron medicamentos en la tabla.")
        else:
            st.warning("No se encontró la tabla de medicamentos. Asegurate de haber copiado el HTML del detalle (con el ojito abierto).")
            
        # Extraer datos de la orden (opcional)
        tabla_orden = soup.find('table', {'id': 'grdDetalles'})
        if tabla_orden:
            filas = tabla_orden.find_all('tr')
            orden = []
            for f in filas[1:]:
                celdas = f.find_all('td')
                if len(celdas) >= 18:
                    orden.append({
                        "Nro Autorización": celdas[0].text.strip(),
                        "Estado": celdas[1].text.strip(),
                        "F. Desde OP": celdas[3].text.strip(),
                        "F. Hasta OP": celdas[4].text.strip(),
                        "Farmacia": celdas[9].text.strip(),
                        "Nro Remito": celdas[13].text.strip(),
                    })
            if orden:
                st.markdown("### 📋 Datos de la orden")
                st.dataframe(pd.DataFrame(orden), use_container_width=True, hide_index=True)
                
    except Exception as e:
        st.error(f"Error al parsear el HTML: {e}")
