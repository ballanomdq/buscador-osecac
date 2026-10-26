# app.py — Módulo SAES (OSECAC Miramar) — versión unificada accesible
# Reemplaza todo tu archivo actual por este.

import streamlit as st
import pandas as pd

# ============================================================
# CONFIGURACIÓN GENERAL (accesibilidad visual)
# ============================================================
st.set_page_config(
    page_title="SAES · OSECAC Miramar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS: fondo claro, tipografía grande, botones amplios, badges legibles
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 18px; }
    .stApp { background-color: #f8fafc; }
    h1 { font-size: 2.2rem !important; color: #0f172a; }
    h2 { font-size: 1.7rem !important; color: #0f172a; }
    h3 { font-size: 1.35rem !important; color: #0f172a; }
    div[data-testid="stButton"] > button {
        font-size: 1.1rem; padding: 0.7rem 1.4rem; border-radius: 10px;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        font-size: 1.1rem; padding: 0.5rem;
    }
    .badge {
        display: inline-block; padding: 0.25rem 0.7rem; border-radius: 8px;
        font-weight: 600; font-size: 0.95rem;
    }
    .badge-ok   { background:#dcfce7; color:#166534; }
    .badge-warn { background:#fef9c3; color:#854d0e; }
    .badge-bad  { background:#fee2e2; color:#991b1b; }
    .badge-info { background:#dbeafe; color:#1e40af; }
    .detalle-card {
        background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
        padding:1.2rem 1.4rem; margin-bottom:1rem;
    }
    .detalle-card h4 { margin-top:0; font-size:1.2rem; color:#0f172a; }
    .detalle-row { font-size:1.05rem; margin:0.25rem 0; color:#1e293b; }
    .detalle-row b { color:#0f172a; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "menu" not in st.session_state:
    st.session_state.menu = "Listados"

# ============================================================
# 🔴 ACÁ VA TU CÓDIGO REAL DE EXTRACCIÓN 🔴
# ============================================================
def buscar_en_saes(tipo_doc: str, nro_doc: str) -> list[dict]:
    """
    REEMPLAZAR ESTE BLOQUE POR TU CÓDIGO DE SCRAPING/CONSULTA.
    Debe devolver una LISTA DE DICCIONARIOS, donde cada diccionario
    es un trámite con las siguientes claves exactas:
    """
    
    # --- BORRAR ESTO (es el mock que solo devuelve 1) ---
    # resultados_reales = []
    # return resultados_reales
    # ----------------------------------------------------

    # --- EJEMPLO DE CÓMO DEBERÍA LLEGAR TU DATA REAL ---
    # (Simulo que acá traés 3 trámites de la base de datos)
    resultados_reales = [
        {
            "Nro. Autorización": "AUT-2024-000123", "OP": "OP-77812", "Programa": "Maculopatía",
            "AUT Desde": "2024-03-01", "AUT Hasta": "2024-09-01", "OP Desde": "2024-03-05", "OP Hasta": "2024-08-30",
            "Farmacia": "Farmacia Central Miramar", "Estado": "Autorizado",
            "Medicamento": "Ranibizumab 10 mg/mL", "Dosis": "0.5 mg intravítrea mensual", "Cant. solicitada": 3, "Cant. pendiente entrega": 1, "Consideraciones médicas": "Paciente con antecedente de HTA.",
            "IdOrdenProv": "IP-2024-5591", "Nro. OT": "OT-33421", "Tipo Remito": "COMUN", "Nro. Remito": "675467", "Estado Recepción": "Recibido", "Fecha Despacho": "2024-03-06",
        },
        {
            "Nro. Autorización": "AUT-2024-000124", "OP": "OP-77813", "Programa": "DBT Tipo II",
            "AUT Desde": "2024-04-10", "AUT Hasta": "2024-10-10", "OP Desde": "2024-04-12", "OP Hasta": "2024-09-30",
            "Farmacia": "Farmacia del Pueblo", "Estado": "Pendiente",
            "Medicamento": "Insulina Glargina", "Dosis": "20 UI diarias", "Cant. solicitada": 5, "Cant. pendiente entrega": 5, "Consideraciones médicas": "Requiere refrigeración.",
            "IdOrdenProv": "IP-2024-5592", "Nro. OT": "OT-33422", "Tipo Remito": "COMUN", "Nro. Remito": "675468", "Estado Recepción": "En tránsito", "Fecha Despacho": "2024-04-13",
        },
        {
            "Nro. Autorización": "AUT-2024-000125", "OP": "OP-77814", "Programa": "Oncología",
            "AUT Desde": "2024-05-01", "AUT Hasta": "2024-11-01", "OP Desde": "2024-05-02", "OP Hasta": "2024-10-15",
            "Farmacia": "Farmacia Hospitalaria", "Estado": "Rechazado",
            "Medicamento": "Trastuzumab", "Dosis": "8 mg/kg", "Cant. solicitada": 1, "Cant. pendiente entrega": 0, "Consideraciones médicas": "Revisar historia clínica.",
            "IdOrdenProv": "IP-2024-5593", "Nro. OT": "OT-33423", "Tipo Remito": "ESPECIAL", "Nro. Remito": "675469", "Estado Recepción": "Rechazado", "Fecha Despacho": "2024-05-03",
        }
    ]

    # (Opcional) Acá podés ordenar la lista como en SAES antes de retornarla.
    # Por ejemplo, ordenado por Nro de Autorización:
    # resultados_reales = sorted(resultados_reales, key=lambda x: x["Nro. Autorización"], reverse=True)
    
    return resultados_reales


# ============================================================
# PANTALLA LOGIN
# ============================================================
def pantalla_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🏥 Portal SAES · OSECAC Miramar")
        st.caption("Acceso institucional")
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
            clave = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            ingresar = st.form_submit_button("Ingresar", use_container_width=True)
        if ingresar:
            if usuario and clave:
                st.session_state.logueado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Complete usuario y contraseña.")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
def menu_principal():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario}")
        st.divider()
        st.session_state.menu = st.radio(
            "Menú",
            ["Listados", "Consultas de Medicamentos", "Solicitudes de Trámite"],
            index=["Listados", "Consultas de Medicamentos", "Solicitudes de Trámite"].index(st.session_state.menu),
        )
        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.logueado = False
            st.session_state.usuario = ""
            st.rerun()


# ============================================================
# UTILIDADES DE PRESENTACIÓN
# ============================================================
def badge_estado(estado: str) -> str:
    e = estado.lower()
    if "autoriz" in e and "no" not in e:
        cls, txt = "badge-ok", estado
    elif "pend" in e or "revis" in e:
        cls, txt = "badge-warn", estado
    elif "rechaz" in e or "anul" in e:
        cls, txt = "badge-bad", estado
    else:
        cls, txt = "badge-info", estado
    return f'<span class="badge {cls}">{txt}</span>'


def card_detalle(titulo: str, filas: list[tuple[str, str]]):
    html = f'<div class="detalle-card"><h4>{titulo}</h4>'
    for k, v in filas:
        html += f'<div class="detalle-row"><b>{k}:</b> {v}</div>'
    html += "</div>"
    return html


@st.dialog("📄 Detalle del trámite", width="large")
def mostrar_detalle(fila: dict):
    st.markdown(f"### Nro. Autorización: **{fila.get('Nro. Autorización', 'N/A')}**")
    estado = fila.get('Estado', 'Desconocido')
    st.markdown(f"Estado: {badge_estado(estado)}", unsafe_allow_html=True)
    st.divider()

    st.markdown(card_detalle("Datos generales", [
        ("OP", fila.get("OP", "")),
        ("Programa", fila.get("Programa", "")),
        ("AUT Desde", fila.get("AUT Desde", "")),
        ("AUT Hasta", fila.get("AUT Hasta", "")),
        ("OP Desde", fila.get("OP Desde", "")),
        ("OP Hasta", fila.get("OP Hasta", "")),
        ("Farmacia", fila.get("Farmacia", "")),
    ]), unsafe_allow_html=True)

    st.markdown(card_detalle("🩺 Consideraciones médicas y medicamentos", [
        ("Medicamento", fila.get("Medicamento", "")),
        ("Dosis", fila.get("Dosis", "")),
        ("Cant. solicitada", str(fila.get("Cant. solicitada", ""))),
        ("Cant. pendiente entrega", str(fila.get("Cant. pendiente entrega", ""))),
        ("Consideraciones", fila.get("Consideraciones médicas", "")),
    ]), unsafe_allow_html=True)

    st.markdown(card_detalle("🚚 Trazabilidad logística", [
        ("IdOrdenProv", fila.get("IdOrdenProv", "")),
        ("Nro. OT", fila.get("Nro. OT", "")),
        ("Tipo Remito", fila.get("Tipo Remito", "")),
        ("Nro. Remito", fila.get("Nro. Remito", "")),
        ("Estado Recepción", fila.get("Estado Recepción", "")),
        ("Fecha Despacho", fila.get("Fecha Despacho", "")),
    ]), unsafe_allow_html=True)

    if st.button("Cerrar", use_container_width=True):
        st.rerun()


# ============================================================
# PANTALLA DE CONSULTA / LISTADOS
# ============================================================
def pantalla_consulta():
    st.markdown("## 🔎 Consulta de trámites")
    st.caption("Busque por tipo y número de documento del beneficiario.")

    col1, col2, col3 = st.columns([1, 1.2, 0.8])
    with col1:
        tipo_doc = st.selectbox("Tipo de documento", ["DNI", "LC", "LE", "CI", "PAS"])
    with col2:
        nro_doc = st.text_input("Número de documento", placeholder="Ej: 30123456")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        buscar = st.button("🔍 Buscar", use_container_width=True)

    if buscar:
        if not nro_doc.strip():
            st.warning("Ingrese un número de documento.")
            return
        
        # Acá se llama a tu función real que trae TODOS los trámites
        with st.spinner("Buscando trámites en SAES..."):
            st.session_state["resultados"] = buscar_en_saes(tipo_doc, nro_doc.strip())

    resultados = st.session_state.get("resultados")
    if not resultados:
        return

    st.divider()
    st.markdown(f"### Resultados ({len(resultados)})")
    st.caption("👉 Hacé clic sobre una fila para ver el detalle completo del trámite.")

    df = pd.DataFrame(resultados)
    columnas_visibles = [
        "Nro. Autorización", "OP", "Programa",
        "AUT Desde", "AUT Hasta", "Farmacia", "Estado",
    ]
    
    # Aseguramos que las columnas existan para que no rompa
    columnas_existentes = [c for c in columnas_visibles if c in df.columns]
    df_vis = df[columnas_existentes].copy()

    evento = st.dataframe(
        df_vis,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="tabla_tramites",
    )

    if evento and evento.selection and evento.selection.rows:
        idx = evento.selection.rows[0]
        fila_dict = resultados[idx]
        mostrar_detalle(fila_dict)


# ============================================================
# ROUTER PRINCIPAL
# ============================================================
if not st.session_state.logueado:
    pantalla_login()
else:
    menu_principal()
    m = st.session_state.menu
    if m == "Listados":
        pantalla_consulta()
    elif m == "Consultas de Medicamentos":
        st.markdown("## 💊 Consultas de Medicamentos")
        st.info("Módulo en construcción. Se conectará con la capa médica del trámite.")
    elif m == "Solicitudes de Trámite":
        st.markdown("## 📝 Solicitudes de Trámite")
        st.info("Módulo en construcción.")
