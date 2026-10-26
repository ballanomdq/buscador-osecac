import streamlit as st
import pandas as pd

# Configuración de la página con diseño limpio y sobrio (Fondo claro institucional)
st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
/* Estilo general minimalista y sobrio (Fondo claro / corporativo) */
.stApp { background-color: #f8fafc !important; color: #1e293b !important; }
.stMarkdown p, label, span { color: #1e293b !important; }

/* Contenedores y tarjetas limpias */
.saes-container {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.detalle-box {
    background-color: #f1f5f9;
    border-left: 4px solid #0284c7;
    padding: 15px;
    margin-top: 15px;
    border-radius: 4px;
}

/* Estilos de badges discretos */
.badge-verde { background-color: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }
.badge-azul { background-color: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }
.badge-rojo { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# Barra superior de navegación simple
if st.button("← Volver al Inicio"):
    st.switch_page("main.py")

# --- CONTROL DE SESIÓN ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "saes_menu" not in st.session_state:
    st.session_state.saes_menu = "home"

# ================= 1. LOGIN SOBRIO Y DIRECTO =================
if not st.session_state.saes_logueado:
    st.markdown("## Acceso al Sistema SAES")
    st.markdown("Por favor, ingrese sus credenciales institucionales.")
    
    with st.form("form_login_sobrio"):
        usuario = st.text_input("Usuario", value="")
        password = st.text_input("Contraseña", type="password", value="")
        btn_entrar = st.form_submit_button("Ingresar")
        
        if btn_entrar:
            if usuario and password:
                st.session_state.saes_logueado = True
                st.rerun()
            else:
                st.warning("Ingrese usuario y contraseña para continuar.")

# ================= 2. PANTALLA PRINCIPAL DENTRO DEL SAES =================
else:
    # Encabezado institucional
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.markdown("### 🏥 Sistema para OSECAC — Portal SAES")
    with col_h2:
        if st.button("Cerrar Sesión"):
            st.session_state.saes_logueado = False
            st.session_state.saes_menu = "home"
            st.rerun()

    st.markdown("<hr style='margin: 5px 0 20px 0;'>", unsafe_allow_html=True)

    # Menú estilo SAES (Navegación lateral sobria)
    menu_col, content_col = st.columns([1, 4])

    with menu_col:
        st.markdown("#### Menú SAES")
        if st.button("📁 Listados", use_container_width=True):
            st.session_state.saes_menu = "listados"
        if st.button("🔍 Consultas (Medicamentos)", use_container_width=True):
            st.session_state.saes_menu = "consultas"
        if st.button("📋 Solicitudes de Trámite", use_container_width=True):
            st.session_state.saes_menu = "solicitudes"

    with content_col:
        # SECCIÓN: CONSULTA DE MEDICAMENTOS (La que usás habitualmente)
        if st.session_state.saes_menu in ["home", "consultas"]:
            st.markdown("#### Medicamentos - Consultas")
            
            # Formulario de búsqueda limpio (sin columna DNI repetida abajo)
            with st.form("form_busqueda_saes"):
                c1, c2, c3 = st.columns([1, 2, 2])
                with c1:
                    tipo_doc = st.selectbox("Tipo Doc", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
                with c2:
                    nro_doc = st.text_input("Nro. de Documento", value="6705303")
                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_buscar = st.form_submit_button("Consultar Trámites")

            # Al realizar la búsqueda o mantener el estado
            if btn_buscar or nro_doc == "6705303":
                if nro_doc == "6705303":
                    nombre_afiliado = "FERREYRA MARIA ISABEL"
                    
                    st.markdown(f"**Nombre:** {nombre_afiliado} — **Documento:** {tipo_doc} {nro_doc}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Base de datos de trámites simulada idéntica al SAES
                    tramites = [
                        {
                            "index": 0, "aut": "2307424", "op": "3 / 3", "f_desde_aut": "25/10/2025", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "24/12/2026", "f_hasta_op": "22/01/2027", "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)", "estado": "En proceso de entrega", "badge": "rojo",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 1)"],
                            "remito": "Común - 681200 | Estado: Generado | Despacho: Pendiente de despacho"
                        },
                        {
                            "index": 1, "aut": "2307424", "op": "2 / 3", "f_desde_aut": "25/10/2026", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "24/11/2026", "f_hasta_op": "23/12/2026", "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)", "estado": "En proceso de entrega", "badge": "rojo",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 1)"],
                            "remito": "Común - 679912 | Estado: Generado | Despacho: Pendiente de despacho"
                        },
                        {
                            "index": 2, "aut": "2307424", "op": "1 / 3", "f_desde_aut": "25/10/2026", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "25/10/2026", "f_hasta_op": "23/11/2026", "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)", "estado": "Entrega Total", "badge": "verde",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 0)"],
                            "remito": "Común - 677890 | Estado: Recepcionado | Despacho: 26/10/2026"
                        },
                        {
                            "index": 3, "aut": "2249653", "op": "1 / 1", "f_desde_aut": "28/11/2026", "f_hasta_aut": "26/02/2027",
                            "f_desde_op": "28/11/2026", "f_hasta_op": "26/02/2027", "programa": "DBT TIPO II",
                            "farmacia": "S.E.C. (MAR DEL PLATA)", "estado": "Pendiente", "badge": "rojo",
                            "consideraciones": "Sin observaciones especiales.",
                            "medicamentos": ["METFORMINA - 850 mg comp.x 60 (Cant: 1 | Pendiente: 1)", "VILDAGLIPTIN - 50 MG COMP.X 60 (Cant: 1 | Pendiente: 1)"],
                            "remito": "Común - 670112 | Estado: Pendiente | Despacho: A programar"
                        },
                        {
                            "index": 4, "aut": "2125714", "op": "1 / 1", "f_desde_aut": "31/05/2026", "f_hasta_aut": "29/08/2026",
                            "f_desde_op": "31/05/2026", "f_hasta_op": "29/08/2026", "programa": "DBT TIPO II",
                            "farmacia": "S.E.C. (MAR DEL PLATA)", "estado": "Entrega Total", "badge": "verde",
                            "consideraciones": "Entrega completada correctamente.",
                            "medicamentos": ["METFORMINA - 850 mg comp.x 60 (Cant: 1 | Pendiente: 0)", "VILDAGLIPTIN - 50 MG COMP.X 60 (Cant: 1 | Pendiente: 0)"],
                            "remito": "Común - 675467 | Estado: Recepcionado | Despacho: 01/06/2026"
                        }
                    ]

                    # Tabla principal idéntica a SAES
                    df_view = pd.DataFrame([
                        {
                            "Nro. Aut.": t["aut"],
                            "OP": t["op"],
                            "Programa": t["programa"],
                            "F. Desde OP": t["f_desde_op"],
                            "F. Hasta OP": t["f_hasta_op"],
                            "Farmacia": t["farmacia"],
                            "Estado": t["estado"]
                        } for t in tramites
                    ])
                    
                    st.dataframe(df_view, use_container_width=True, hide_index=True)
                    
                    # Selector minimalista de fila para ver el detalle exacto sin recargas bruscas
                    st.markdown("---")
                    seleccion = st.selectbox(
                        "🔍 Seleccione un trámite de la lista para ver el detalle completo (Ojito / Logística):",
                        options=tramites,
                        format_func=lambda x: f"Trámite N° {x['index']+1} — Autorización: {x['aut']} | Programa: {x['programa']} ({x['estado']})"
                    )

                    if seleccion:
                        t = seleccion
                        badge_html = f"<span class='badge-{t['badge']}'>{t['estado'].upper()}</span>"
                        
                        st.markdown(f"""
                        <div class="detalle-box">
                            <h4 style="margin-top:0; color:#0369a1;">Detalle de la Autorización N° {t['aut']} &nbsp;&nbsp; {badge_html}</h4>
                            <p><b>Programa:</b> {t['programa']} | <b>Farmacia:</b> {t['farmacia']}</p>
                            <p><b>Vigencia OP:</b> Desde {t['f_desde_op']} hasta {t['f_hasta_op']}</p>
                            <p><b>Consideraciones Médicas:</b> <em>{t['consideraciones']}</em></p>
                            <hr style="border-color:#cbd5e1; margin: 10px 0;">
                            <p><b>💊 Medicamentos:</b></p>
                            {''.join([f"<li>{m}</li>" for m in t['medicamentos']])}
                            <p style="margin-top: 10px;"><b>📦 Datos Logísticos (Remito / Despacho):</b> {t['remito']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.info("Ingrese un documento válido para consultar.")

        elif st.session_state.saes_menu == "listados":
            st.markdown("#### Listados del Sistema")
            st.info("Apartado de listados generales en desarrollo.")

        elif st.session_state.saes_menu == "solicitudes":
            st.markdown("#### Solicitudes de Trámite")
            st.info("Apartado de carga de solicitudes en desarrollo.")
