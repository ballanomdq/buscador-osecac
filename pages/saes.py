import streamlit as st
import pandas as pd

# Configuración de página clara, sobria y accesible
st.set_page_config(page_title="Portal SAES - OSECAC", layout="wide")

st.markdown("""
<style>
/* Fondo claro e institucional */
.stApp { background-color: #f8fafc !important; color: #0f172a !important; }
.stMarkdown p, label, span { color: #0f172a !important; }

/* Contenedores sobrios */
.saes-card {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 16px;
    margin-top: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.box-logistica {
    background-color: #f1f5f9;
    border-left: 4px solid #0284c7;
    padding: 12px;
    margin-top: 10px;
    border-radius: 4px;
    font-size: 14px; /* Un poco más grande para tu vista */
}

/* Badges discretos */
.badge-verde { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
.badge-azul { background-color: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }
.badge-rojo { background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }

/* Mejoras de accesibilidad visual */
html, body, [class*="css"] { font-size: 17px; }
div[data-testid="stButton"] > button { font-size: 1.05rem; padding: 0.6rem 1.2rem; }
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

# Botón superior de retorno (Mantenemos tu lógica original)
if st.button("← Volver al Menú Principal"):
    # Si tenés un main.py, esto funcionará. Si no, comentalo.
    try:
        st.switch_page("main.py")
    except Exception:
        st.warning("Función de retorno al menú principal no disponible en este entorno.")

# --- CONTROL DE SESIÓN ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "saes_menu" not in st.session_state:
    st.session_state.saes_menu = "consultas"

# ================= 1. ACCESO AL SAES (LOGIN INICIAL) =================
if not st.session_state.saes_logueado:
    st.markdown("## 🔑 Acceso al SAES")
    st.markdown("Ingrese sus datos de usuario para ingresar al portal de OSECAC.")
    
    with st.form("form_login_saes"):
        c_usr, c_pwd = st.columns(2)
        with c_usr:
            usuario = st.text_input("Usuario:", value="rballano")
        with c_pwd:
            password = st.text_input("Contraseña:", type="password")
            
        btn_ingresar = st.form_submit_button("🚀 Entrar al SAES", use_container_width=True)
        
        if btn_ingresar:
            if usuario and password:
                st.session_state.saes_logueado = True
                st.success("✅ Acceso correcto.")
                st.rerun()
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")

# ================= 2. PORTAL DENTRO DEL SAES =================
else:
    # Encabezado con estado de sesión
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.markdown("### 🏥 Sistema para OSECAC — Portal SAES")
        st.caption("Sesión activa | Usuario: rballano")
    with head_col2:
        if st.button("🔒 Cerrar Sesión"):
            st.session_state.saes_logueado = False
            st.session_state.saes_menu = "consultas"
            st.rerun()

    st.markdown("<hr style='margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

    # Menú lateral con TODAS las opciones del sistema original
    menu_col, body_col = st.columns([1, 4])

    with menu_col:
        st.markdown("#### Menú Principal")
        if st.button("📁 Listados", use_container_width=True):
            st.session_state.saes_menu = "listados"
        if st.button("💊 Consultas (Medicamentos)", use_container_width=True):
            st.session_state.saes_menu = "consultas"
        if st.button("🌐 Consultas por delegación", use_container_width=True):
            st.session_state.saes_menu = "delegacion"
        if st.button("📋 Solicitudes de trámite", use_container_width=True):
            st.session_state.saes_menu = "solicitudes"

    with body_col:
        # SECCIÓN 1: CONSULTAS DE MEDICAMENTOS
        if st.session_state.saes_menu == "consultas":
            st.markdown("### Medicamentos - Consultas")
            
            with st.form("form_consulta_beneficiario"):
                col_orden, col_tipo, col_doc, col_check = st.columns([1, 1, 2, 2])
                with col_orden:
                    nro_orden = st.text_input("Nro. Orden:")
                with col_tipo:
                    tipo_doc = st.selectbox("Tipo Doc:", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
                with col_doc:
                    nro_doc = st.text_input("Nro. de Documento:", value="6705303")
                with col_check:
                    st.write("")
                    ver_solo_disp = st.checkbox("Ver sólo disposiciones")
                
                btn_buscar = st.form_submit_button("🔍 Consultar en SAES", use_container_width=True)

            # Carga automática de los datos cuando se consulta el número de prueba
            if btn_buscar or nro_doc == "6705303":
                if tipo_doc == "LC" and nro_doc == "6705303":
                    nombre_afiliado = "FERREYRA MARIA ISABEL"
                    
                    st.info(f"👤 **Nombre:** {nombre_afiliado} — **Documento:** {tipo_doc} {nro_doc}")
                    
                    # Lista completa de los 6 trámites reales (basados en tu captura de SAES)
                    tramites_reales = [
                        {
                            "id": 1, "aut": "2307424", "op": "3", "cant_op": "3",
                            "f_desde_aut": "25/10/2026", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "24/12/2026", "f_hasta_op": "22/01/2027",
                            "programa": "MACULOPATIA", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "En proceso de entrega", "badge": "rojo",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 1)"],
                            "remito": {"id_prov": "4187325", "ot": "4891011", "est_ot": "En Proceso", "tipo_remito": "COMUN", "nro_remito": "681200", "remito_imp": "R000600398122", "est_rem": "Generado", "fecha_despacho": "Pendiente de despacho"}
                        },
                        {
                            "id": 2, "aut": "2307424", "op": "2", "cant_op": "3",
                            "f_desde_aut": "25/10/2026", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "25/10/2026", "f_hasta_op": "23/11/2026",
                            "programa": "MACULOPATIA", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde",
                            "consideraciones": "OI / Sin coseguro.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 0)"],
                            "remito": {"id_prov": "4187325", "ot": "4891012", "est_ot": "Finalizado", "tipo_remito": "COMUN", "nro_remito": "681201", "remito_imp": "R000600398123", "est_rem": "Recibido", "fecha_despacho": "15/10/2026"}
                        },
                        {
                            "id": 3, "aut": "2307424", "op": "1", "cant_op": "3",
                            "f_desde_aut": "25/10/2026", "f_hasta_aut": "22/01/2027",
                            "f_desde_op": "25/10/2026", "f_hasta_op": "23/11/2026",
                            "programa": "MACULOPATIA", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde",
                            "consideraciones": "OD / Sin coseguro.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 0)"],
                            "remito": {"id_prov": "4187325", "ot": "4891013", "est_ot": "Finalizado", "tipo_remito": "COMUN", "nro_remito": "681202", "remito_imp": "R000600398124", "est_rem": "Recibido", "fecha_despacho": "12/09/2026"}
                        },
                        {
                            "id": 4, "aut": "2249655", "op": "3", "cant_op": "1",
                            "f_desde_aut": "30/08/2026", "f_hasta_aut": "28/11/2026",
                            "f_desde_op": "30/08/2026", "f_hasta_op": "26/02/2027",
                            "programa": "DBT TIPO II", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde",
                            "consideraciones": "Requiere refrigeración.",
                            "medicamentos": ["INSULINA GLARGINA - 100 UI/ml x 10 ml (Cant: 1 | Pendiente: 0)"],
                            "remito": {"id_prov": "4187326", "ot": "4891014", "est_ot": "Finalizado", "tipo_remito": "COMUN", "nro_remito": "681203", "remito_imp": "R000600398125", "est_rem": "Recibido", "fecha_despacho": "05/09/2026"}
                        },
                        {
                            "id": 5, "aut": "2249655", "op": "2", "cant_op": "1",
                            "f_desde_aut": "30/08/2026", "f_hasta_aut": "28/11/2026",
                            "f_desde_op": "30/08/2026", "f_hasta_op": "26/02/2027",
                            "programa": "DBT TIPO II", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde",
                            "consideraciones": "Requiere refrigeración.",
                            "medicamentos": ["INSULINA GLARGINA - 100 UI/ml x 10 ml (Cant: 1 | Pendiente: 0)"],
                            "remito": {"id_prov": "4187326", "ot": "4891015", "est_ot": "Finalizado", "tipo_remito": "COMUN", "nro_remito": "681204", "remito_imp": "R000600398126", "est_rem": "Recibido", "fecha_despacho": "05/09/2026"}
                        },
                        {
                            "id": 6, "aut": "212571", "op": "1", "cant_op": "1",
                            "f_desde_aut": "31/05/2026", "f_hasta_aut": "29/08/2026",
                            "f_desde_op": "31/05/2026", "f_hasta_op": "29/08/2026",
                            "programa": "DBT TIPO II", "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "estado": "Entregado", "badge": "verde",
                            "consideraciones": "Requiere refrigeración.",
                            "medicamentos": ["INSULINA GLARGINA - 100 UI/ml x 10 ml (Cant: 1 | Pendiente: 0)"],
                            "remito": {"id_prov": "4187327", "ot": "4891016", "est_ot": "Finalizado", "tipo_remito": "COMUN", "nro_remito": "681205", "remito_imp": "R000600398127", "est_rem": "Recibido", "fecha_despacho": "02/06/2026"}
                        }
                    ]

                    st.markdown("#### Trámites encontrados")
                    st.caption("👉 Hacé clic sobre una fila para ver el detalle completo del trámite.")

                    # Preparamos el DataFrame para la tabla interactiva
                    df = pd.DataFrame(tramites_reales)
                    df_vis = df[["aut", "op", "programa", "f_desde_aut", "f_hasta_aut", "farmacia", "estado"]].copy()
                    df_vis.columns = ["Nro. Autorización", "OP", "Programa", "AUT Desde", "AUT Hasta", "Farmacia", "Estado"]

                    # Mostramos la tabla con selección de fila
                    evento = st.dataframe(
                        df_vis,
                        use_container_width=True,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="single-row",
                        key="tabla_tramites_saes",
                    )

                    # Si el usuario hace clic en una fila, mostramos el detalle
                    if evento and evento.selection and evento.selection.rows:
                        idx = evento.selection.rows[0]
                        fila_dict = tramites_reales[idx]

                        # Usamos el modal (st.dialog) para mostrar el detalle de forma accesible
                        @st.dialog("📄 Detalle del trámite", width="large")
                        def mostrar_detalle(fila):
                            st.markdown(f"### Nro. Autorización: **{fila['aut']}** (OP {fila['op']})")
                            
                            # Badge de estado
                            clase_badge = "badge-rojo" if fila["badge"] == "rojo" else "badge-verde"
                            st.markdown(f'<span class="{clase_badge}">{fila["estado"]}</span>', unsafe_allow_html=True)
                            
                            st.divider()
                            
                            # Datos generales
                            st.markdown(f"""
                            <div class="saes-card">
                                <h4>Datos generales</h4>
                                <p><b>Programa:</b> {fila['programa']}</p>
                                <p><b>Farmacia:</b> {fila['farmacia']}</p>
                                <p><b>AUT:</b> {fila['f_desde_aut']} al {fila['f_hasta_aut']}</p>
                                <p><b>OP:</b> {fila['f_desde_op']} al {fila['f_hasta_op']}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Consideraciones médicas
                            st.markdown(f"""
                            <div class="saes-card">
                                <h4>🩺 Consideraciones médicas</h4>
                                <p>{fila['consideraciones']}</p>
                                <p><b>Medicamentos:</b></p>
                                <ul>
                                    {''.join([f'<li>{m}</li>' for m in fila['medicamentos']])}
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)

                            # Logística (Equivalente al "ojito")
                            remito = fila['remito']
                            st.markdown(f"""
                            <div class="box-logistica">
                                <h4>🚚 Trazabilidad logística</h4>
                                <p><b>ID Orden Provincial:</b> {remito['id_prov']}</p>
                                <p><b>Nro OT:</b> {remito['ot']} ({remito['est_ot']})</p>
                                <p><b>Tipo Remito:</b> {remito['tipo_remito']} - Nro: {remito['nro_remito']}</p>
                                <p><b>Remito Impreso:</b> {remito['remito_imp']}</p>
                                <p><b>Estado Recepción:</b> {remito['est_rem']}</p>
                                <p><b>Fecha Despacho:</b> {remito['fecha_despacho']}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            if st.button("Cerrar", use_container_width=True):
                                st.rerun()

                        # Llamamos al modal pasando la fila seleccionada
                        mostrar_detalle(fila_dict)

        # OTRAS SECCIONES (Mantenemos tu lógica original)
        elif st.session_state.saes_menu == "listados":
            st.markdown("### 📁 Listados")
            st.info("Módulo en construcción.")
        elif st.session_state.saes_menu == "delegacion":
            st.markdown("### 🌐 Consultas por delegación")
            st.info("Módulo en construcción.")
        elif st.session_state.saes_menu == "solicitudes":
            st.markdown("### 📋 Solicitudes de trámite")
            st.info("Módulo en construcción.")
