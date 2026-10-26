import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Módulo SAES - Vista Integral y Logística", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }

/* Estilos de badges para estados */
.badge-verde { background-color: #15803d; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
.badge-azul { background-color: #1d4ed8; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
.badge-rojo { background-color: #b91c1c; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }

/* Tarjeta para desglosar trámites */
.card-tramite {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
}
.box-remito {
    background-color: #0f172a;
    border-left: 4px solid #3b82f6;
    padding: 10px;
    margin-top: 10px;
    font-size: 13px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 Módulo SAES - Resumen Integral y Logística de Envíos")
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

# 2. PANEL DE CONSULTA INTEGRAL
else:
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.info("👤 Conectado a SAES | Consulta Unificada con Trazabilidad Logística")
    with col_logout:
        if st.button("🔒 Salir"):
            st.session_state.saes_logueado = False
            st.rerun()

    st.markdown("---")

    with st.form("form_consulta_integral"):
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            tipo_doc = st.selectbox("Tipo Doc:", ["DNI", "LC", "LE", "CI", "PAS", "S/D"], index=1)
        with c2:
            nro_doc = st.text_input("Nro. Documento:", value="6705303")
        with c3:
            st.write("") # Espaciador
            btn_buscar = st.form_submit_button("🔍 BUSCAR Y VER DETALLE COMPLETO", use_container_width=True)

    if btn_buscar:
        if nro_doc:
            with st.spinner("Procesando historial y datos logísticos de remitos..."):
                
                if tipo_doc == "LC" and nro_doc == "6705303":
                    nombre_beneficiario = "FERREYRA MARIA ISABEL"
                    
                    # Trámites incorporando la información exacta del "ojito" (Remitos, OT y Despachos)
                    tramites = [
                        {
                            "aut": "2307424",
                            "op": "3 / 3",
                            "estado_aut": "En proceso de entrega",
                            "badge_color": "rojo",
                            "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "f_desde_op": "24/12/2026",
                            "f_hasta_op": "22/01/2027",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 1)"],
                            "tiene_remito": False
                        },
                        {
                            "aut": "2307424",
                            "op": "2 / 3",
                            "estado_aut": "En proceso de entrega",
                            "badge_color": "rojo",
                            "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "f_desde_op": "24/11/2026",
                            "f_hasta_op": "23/12/2026",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 1)"],
                            "tiene_remito": False
                        },
                        {
                            "aut": "2307424",
                            "op": "1 / 3",
                            "estado_aut": "Entrega Total",
                            "badge_color": "verde",
                            "programa": "MACULOPATIA",
                            "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "f_desde_op": "25/10/2026",
                            "f_hasta_op": "23/11/2026",
                            "consideraciones": "OD / Abona coseguro vía App Mi Osecac.",
                            "medicamentos": ["BEVACIZUMAB - 0.2 ml/5 mg vial x 1 (Cant: 1 | Pendiente: 0)"],
                            "tiene_remito": False
                        },
                        {
                            "aut": "2249653",
                            "op": "1 / 1",
                            "estado_aut": "Pendiente",
                            "badge_color": "rojo",
                            "programa": "DBT TIPO II",
                            "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "f_desde_op": "28/11/2026",
                            "f_hasta_op": "26/02/2027",
                            "consideraciones": "Sin observaciones especiales.",
                            "medicamentos": [
                                "METFORMINA - 850 mg comp.x 60 (Cant: 1 | Pendiente: 1)",
                                "VILDAGLIPTIN - 50 MG COMP.X 60 (Cant: 1 | Pendiente: 1)"
                            ],
                            "tiene_remito": False
                        },
                        {
                            "aut": "2125714",
                            "op": "1 / 1",
                            "estado_aut": "Entrega Total",
                            "badge_color": "verde",
                            "programa": "DBT TIPO II",
                            "farmacia": "S.E.C. (MAR DEL PLATA)",
                            "f_desde_op": "31/05/2026",
                            "f_hasta_op": "29/08/2026",
                            "consideraciones": "Entrega completada correctamente.",
                            "medicamentos": [
                                "METFORMINA - 850 mg comp.x 60 (Cant: 1 | Pendiente: 0)",
                                "VILDAGLIPTIN - 50 MG COMP.X 60 (Cant: 1 | Pendiente: 0)"
                            ],
                            "tiene_remito": True,
                            "remito_info": {
                                "id_orden_prov": "3812981",
                                "nro_ot": "4818004",
                                "est_ot": "Con Remito",
                                "tipo_remito": "COMUN",
                                "nro_remito": "675467",
                                "nro_remito_imp": "R000600354626",
                                "est_rem": "Recepcionado",
                                "fecha_despacho": "01/06/2026"
                            }
                        }
                    ]

                    st.success(f"👤 Beneficiario: **{nombre_beneficiario}** | Doc: **{tipo_doc} {nro_doc}**")
                    
                    # 1. TABLA RESUMEN
                    st.subheader("📊 1. Resumen General de Autorizaciones")
                    df_resumen = pd.DataFrame([
                        {
                            "Nro. Autorización": t["aut"],
                            "Nro OP": t["op"],
                            "Programa": t["programa"],
                            "Estado": t["estado_aut"],
                            "Vigencia OP": f"{t['f_desde_op']} al {t['f_hasta_op']}",
                            "Farmacia": t["farmacia"]
                        } for t in tramites
                    ])
                    st.dataframe(df_resumen, use_container_width=True)

                    st.markdown("---")

                    # 2. DESGLOSE DETALLADO + DATOS DEL "OJITO" (REMITOS Y DESPACHOS)
                    st.subheader("📋 2. Detalle de Trámites, Medicamentos y Trazabilidad de Remitos")
                    st.caption("Aquí se incluye la información detallada de medicamentos y los datos logísticos de despacho (equivalente a hacer clic en el ojito 👁️):")

                    for i, t in enumerate(tramites, 1):
                        badge_html = f"<span class='badge-{t['badge_color']}'>{t['estado_aut'].upper()}</span>"
                        
                        # Renderizamos la tarjeta principal del trámite
                        with st.container():
                            st.markdown(f"""
                            <div class="card-tramite">
                                <h4>Trámite #{i} - Autorización N° {t['aut']} (OP {t['op']}) &nbsp;&nbsp; {badge_html}</h4>
                                <p><strong>Programa:</strong> {t['programa']} | <strong>Farmacia:</strong> {t['farmacia']}</p>
                                <p><strong>Vigencia OP:</strong> Desde {t['f_desde_op']} hasta {t['f_hasta_op']}</p>
                                <p><strong>Consideraciones Médicas:</strong> <em>{t['consideraciones']}</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.write("💊 **Medicamentos solicitados / estado:**")
                            for med in t["medicamentos"]:
                                st.markdown(f"- {med}")

                            # Si el trámite tiene datos de remito (como el de la orden 2125714), los mostramos en un cuadro destacado
                            if t.get("tiene_remito"):
                                r = t["remito_info"]
                                st.markdown(f"""
                                <div class="box-remito">
                                    📦 <b>DETALLE LOGÍSTICO (Datos del Remito / Ojito):</b><br>
                                    • <b>ID Orden Prov:</b> {r['id_orden_prov']} | <b>Nro. OT:</b> {r['nro_ot']} ({r['est_ot']})<br>
                                    • <b>Tipo / Nro Remito:</b> {r['tipo_remito']} - {r['nro_remito']} (Imp: {r['nro_remito_imp']})<br>
                                    • <b>Estado Remito:</b> {r['est_rem']} | <b>Fecha de Despacho:</b> {r['fecha_despacho']}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.warning(f"No se encontraron registros de prueba para el documento {nro_doc}.")
        else:
            st.warning("⚠️ Ingresa un número de documento.")
