import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Módulo SAES - Estilo Original", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }

/* Estilos de badges para estados */
.badge-verde { background-color: #15803d; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
.badge-azul { background-color: #1d4ed8; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
.badge-rojo { background-color: #b91c1c; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }

/* Tarjeta estilo SAES */
.saes-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 12px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 Portal SAES - Consulta por Programa y Fechas")
st.markdown("---")

if st.button("⬅️ Volver al Menú Principal"):
    st.switch_page("main.py")

# --- CONTROL DE SESIÓN ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False

# 1. LOGIN
if not st.session_state.saes_logueado:
    st.subheader("🔑 Acceso al Sistema SAES")
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario:", value="rballano")
    with col2:
        password = st.text_input("Contraseña:", type="password")
    
    if st.button("🚀 Ingresar"):
        if usuario and password:
            st.session_state.saes_logueado = True
            st.rerun()
        else:
            st.warning("⚠️ Ingresa usuario y contraseña.")

# 2. PANEL DE CONSULTA
else:
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.info("👤 Conectado a SAES | Estilo Clásico Organizado por Programas y Entregas")
    with col_logout:
        if st.button("🔒 Salir"):
            st.session_state.saes_logueado = False
            st.rerun()

    st.markdown("---")

    with st.form("form_consulta_saes"):
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            tipo_doc = st.selectbox("Tipo Doc:", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
        with c2:
            nro_doc = st.text_input("Nro. Documento:", value="6705303")
        with c3:
            st.write("")
            btn_buscar = st.form_submit_button("🔍 CONSULTAR", use_container_width=True)

    if btn_buscar:
        if nro_doc:
            with st.spinner("Consultando registros..."):
                
                if tipo_doc == "LC" and nro_doc == "6705303":
                    nombre_beneficiario = "FERREYRA MARIA ISABEL"
                    
                    # Trámites organizados tal cual las entregas de SAES
                    tramites = [
                        {
                            "id": 1, "aut": "2307424", "op": "3 / 3", "programa": "MACULOPATIA",
                            "f_desde": "24/12/2026", "f_hasta": "22/01/2027", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "En proceso", "badge": "rojo", "med": "BEVACIZUMAB (Cant: 1 | Pendiente: 1)",
                            "remito": "Común - 681200 | Estado: Generado | Despacho: Pendiente"
                        },
                        {
                            "id": 2, "aut": "2307424", "op": "2 / 3", "programa": "MACULOPATIA",
                            "f_desde": "24/11/2026", "f_hasta": "23/12/2026", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "En proceso", "badge": "rojo", "med": "BEVACIZUMAB (Cant: 1 | Pendiente: 1)",
                            "remito": "Común - 679912 | Estado: Generado | Despacho: Pendiente"
                        },
                        {
                            "id": 3, "aut": "2307424", "op": "1 / 3", "programa": "MACULOPATIA",
                            "f_desde": "25/10/2026", "f_hasta": "23/11/2026", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde", "med": "BEVACIZUMAB (Cant: 1 | Pendiente: 0)",
                            "remito": "Común - 677890 | Estado: Recepcionado | Despacho: 26/10/2026"
                        },
                        {
                            "id": 4, "aut": "2249653", "op": "1 / 1", "programa": "DBT TIPO II",
                            "f_desde": "28/11/2026", "f_hasta": "26/02/2027", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Pendiente", "badge": "rojo", "med": "METFORMINA y VILDAGLIPTIN (Pendientes)",
                            "remito": "Común - 670112 | Estado: Pendiente | Despacho: A programar"
                        },
                        {
                            "id": 5, "aut": "2125714", "op": "1 / 1", "programa": "DBT TIPO II",
                            "f_desde": "31/05/2026", "f_hasta": "29/08/2026", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde", "med": "METFORMINA y VILDAGLIPTIN (Entregados)",
                            "remito": "Común - 675467 | Estado: Recepcionado | Despacho: 01/06/2026"
                        }
                    ]

                    st.success(f"Afiliado: **{nombre_beneficiario}** (LC: {nro_doc})[cite: 12]")
                    
                    st.markdown("### 📋 Listado de Autorizaciones y Entregas")
                    st.caption("Seleccione el número de trámite abajo para ver su detalle específico de medicamentos y remito:")

                    # Mostramos una tabla resumen limpia (sin columna DNI repetida)
                    df_tabla = pd.DataFrame([
                        {
                            "Item": t["id"],
                            "Programa": t["programa"],
                            "Nro. Autoriz.": t["aut"],
                            "Entrega OP": t["op"],
                            "Vigencia Desde": t["f_desde"],
                            "Vigencia Hasta": t["f_hasta"],
                            "Estado": t["estado"]
                        } for t in tramites
                    ])
                    st.dataframe(df_tabla, use_container_width=True, hide_index=True)

                    # Selector limpio tipo menú desplegable de SAES para ver el detalle de un renglón puntual
                    st.markdown("---")
                    opcion_elegida = st.selectbox(
                        "📌 Seleccione el trámite para ver el detalle del remito y medicamentos:",
                        options=tramites,
                        format_func=lambda x: f"Trámite #{x['id']} — Programa: {x['programa']} (Autorización N° {x['aut']} - OP {x['op']})"
                    )

                    # Tarjeta compacta que muestra la información al hacer clic en el renglón
                    if opcion_elegida:
                        t = opcion_elegida
                        badge_html = f"<span class='badge-{t['badge']}'>{t['estado'].upper()}</span>"
                        
                        st.markdown(f"""
                        <div class="saes-card">
                            <h4 style="margin: 0; color: #60a5fa;">Detalle del Trámite #{t['id']} &nbsp;&nbsp; {badge_html}</h4>
                            <hr style="margin: 8px 0; border-color: #334155;">
                            <p style="margin: 4px 0;"><b>Programa:</b> {t['programa']} | <b>Farmacia:</b> {t['farmacia']}</p>
                            <p style="margin: 4px 0;"><b>Medicamento / Cantidad:</b> {t['med']}</p>
                            <p style="margin: 4px 0;"><b>📦 Datos de Logística / Remito:</b> {t['remito']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.warning("No se encontraron registros para este documento.")
        else:
            st.warning("⚠️ Ingrese un número de documento.")
