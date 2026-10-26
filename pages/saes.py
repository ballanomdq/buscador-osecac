import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Módulo SAES - OSECAC", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
.stApp { background-color: #0f172a !important; color: #e2e8f0 !important; }
.stMarkdown p, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔐 Portal SAES - Módulo de Gestión y Consultas")
st.markdown("---")

if st.button("⬅️ Volver al Menú Principal"):
    st.switch_page("main.py")

# --- CONTROL DE SESIÓN ---
if "saes_logueado" not in st.session_state:
    st.session_state.saes_logueado = False
if "menu_activo" not in st.session_state:
    st.session_state.menu_activo = "inicio"

# ================= PASO 1: LOGIN =================
if not st.session_state.saes_logueado:
    st.subheader("🔑 1. Acceso al SAES")
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario:", value="rballano")
    with col2:
        password = st.text_input("Contraseña:", type="password")
    
    if st.button("🚀 Entrar al SAES"):
        if usuario and password:
            st.session_state.saes_logueado = True
            st.success("✅ ¡Acceso correcto!")
            st.rerun()
        else:
            st.warning("⚠️ Ingrese usuario y contraseña.")

# ================= PASO 2: MENÚ PRINCIPAL Y SECCIONES =================
else:
    # Barra superior de navegación interna
    col_info, col_salir = st.columns([4, 1])
    with col_info:
        st.info(f"👤 Sesión activa en SAES | Menú actual: **{st.session_state.menu_activo.upper()}**")
    with col_salir:
        if st.button("🔒 Cerrar Sesión"):
            st.session_state.saes_logueado = False
            st.session_state.menu_activo = "inicio"
            st.rerun()

    st.markdown("---")

    # Si estamos en la portada interna, mostramos el menú principal tipo botones
    if st.session_state.menu_activo == "inicio":
        st.subheader("📁 Menú Principal SAES")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💊 Adm. de Medicamentos", use_container_width=True):
                st.session_state.menu_activo = "medicamentos"
                st.rerun()
        with c2:
            if st.button("📋 Autorizaciones / Prácticas", use_container_width=True):
                st.session_state.menu_activo = "practicas"
                st.rerun()

    # ================= PASO 3: MÓDULO MEDICAMENTOS =================
    elif st.session_state.menu_activo == "medicamentos":
        if st.button("⬅️ Volver al Menú SAES"):
            st.session_state.menu_activo = "inicio"
            st.rerun()
            
        st.subheader("💊 Administración de Medicamentos")
        
        # Submenú lateral o de botones internos
        sub_opcion = st.radio(
            "Seleccione una opción del menú:", 
            ["Listados", "Consultas", "Consultas por delegación", "Solicitudes de trámite"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # Si selecciona "Consultas" (el apartado del cronograma de entregas)
        if sub_opcion == "Consultas":
            st.markdown("### 🔍 Medicamentos - Consultas de Afiliado")
            
            with st.form("form_consulta_medicamentos"):
                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    nro_orden = st.text_input("Nro. Orden:")
                with col_b:
                    tipo_doc = st.selectbox("Tipo Doc:", ["DNI", "LC", "LE", "CI", "PAS", "S/D"])
                with col_c:
                    nro_doc = st.text_input("Nro. de Documento:")
                
                ver_disp = st.checkbox("Ver sólo disposiciones")
                
                btn_buscar_saes = st.form_submit_button("🔍 Consultar en SAES", use_container_width=True)
            
            if btn_buscar_saes:
                if nro_doc:
                    with st.spinner("Consultando en el sistema SAES..."):
                        # Simulación basada en tu prueba con LC 6705303 (FERREYRA MARIA ISABEL)
                        if tipo_doc == "LC" and nro_doc == "6705303":
                            st.success("✅ Beneficiario encontrado: FERREYRA MARIA ISABEL (LC 6705303)")
                            
                            data_resultado = {
                                "Nro. de Autortz.": ["2307424", "2307424", "2307424", "2249653", "2249653", "2125714"],
                                "F. Desde AUT.": ["25/10/2025", "25/10/2026", "25/10/2026", "26/02/2027", "30/08/2028", "31/05/2028"],
                                "F. Hasta AUT.": ["22/01/2027", "22/01/2027", "24/11/2026", "26/02/2027", "28/11/2028", "29/08/2028"],
                                "Programa": ["MACULOPATIA", "MACULOPATIA", "MACULOPATIA", "DBT TIPO II", "DBT TIPO II", "DBT TIPO II"],
                                "Farmacia": ["S.E.C. (MAR DEL PLATA)", "S.E.C. (MAR DEL PLATA)", "S.E.C. (MAR DEL PLATA)", "S.E.C. (MAR DEL PLATA)", "S.E.C. (MAR DEL PLATA)", "S.E.C. (MAR DEL PLATA)"],
                                "Nro Cant. DF OP": [3, 2, 1, 1, 1, 1]
                            }
                            df_res = pd.DataFrame(data_resultado)
                            st.dataframe(df_res, use_container_width=True)
                        else:
                            st.info(f"Búsqueda realizada para {tipo_doc} Nro: {nro_doc}. (Simulación de resultado exitoso)")
                else:
                    st.warning("⚠️ Debe ingresar un número de documento.")

        elif sub_opcion == "Solicitudes de trámite":
            st.info("📌 Apartado de Solicitudes de Trámite (En desarrollo según la estructura de SAES).")
        else:
            st.info(f"📌 Sección '{sub_opcion}' seleccionada.")

    elif st.session_state.menu_activo == "practicas":
        if st.button("⬅️ Volver al Menú SAES"):
            st.session_state.menu_activo = "inicio"
            st.rerun()
        st.subheader("📋 Autorizaciones / Prácticas")
        st.info("📌 Apartado de Prácticas de Autorización en configuración.")
