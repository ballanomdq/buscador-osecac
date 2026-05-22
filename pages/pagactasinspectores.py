import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
import re
import tempfile
import os
from folium.plugins import Fullscreen, HeatMap
import time
import hashlib

st.set_page_config(page_title="Panel de Inspector - OSECAC", layout="wide")

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid #3b82f6;
}
.main-header h2 { color: white; margin: 0; font-size: 1.3rem; }
.main-header p { color: #94a3b8; margin: 0; font-size: 0.8rem; }
div[data-testid="stButton"] button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    padding: 0.3rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
}
div[data-testid="stButton"] button:hover { background: #2563eb !important; }
.stDataFrame { font-size: 0.75rem; }
.filtro-titulo { font-size: 0.65rem; color: #64748b; margin-bottom: 0.2rem; }
iframe {
    width: 100% !important;
    height: 60vh !important;
    min-height: 450px !important;
    border: none !important;
    border-radius: 8px !important;
}
.anotacion-card {
    background: #1e293b;
    padding: 0.5rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>👤 Panel del Inspector</h2>
    <p>Visualice sus empresas asignadas - Acceso solo de consulta</p>
</div>
""", unsafe_allow_html=True)

col_volver, _ = st.columns([1, 11])
with col_volver:
    if st.button("← Volver al portal"):
        st.switch_page("main.py")

st.markdown("---")

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Funciones para agenda telefónica ─────────────────────────────────────────
def actualizar_agenda_telefonica(empresas_df):
    """Actualiza la agenda telefónica con los datos actuales de las empresas"""
    for _, row in empresas_df.iterrows():
        cuit = row.get('cuit')
        razon_social = row.get('razon_social')
        telefono = row.get('tel_dom_legal') or row.get('tel_dom_real')
        email = row.get('email')
        
        if cuit:
            # Verificar si ya existe
            existente = supabase.table("agenda_telefonica").select("*").eq("cuit", cuit).execute()
            
            if existente.data:
                # Actualizar si cambió algo
                if (existente.data[0].get('razon_social') != razon_social or
                    existente.data[0].get('telefono') != telefono or
                    existente.data[0].get('email') != email):
                    supabase.table("agenda_telefonica").update({
                        "razon_social": razon_social,
                        "telefono": telefono,
                        "email": email,
                        "ultima_actualizacion": "now()"
                    }).eq("cuit", cuit).execute()
            else:
                # Insertar nuevo
                supabase.table("agenda_telefonica").insert({
                    "cuit": cuit,
                    "razon_social": razon_social,
                    "telefono": telefono,
                    "email": email,
                    "ultima_actualizacion": "now()"
                }).execute()

# ── Cargar datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

@st.cache_data(ttl=300)
def cargar_coordenadas():
    datos = supabase.table("coordenadas_empresas").select("id_empresa, lat, lon").execute()
    if datos.data:
        return {d['id_empresa']: (d['lat'], d['lon']) for d in datos.data if d['lat'] is not None}
    return {}

@st.cache_data(ttl=300)
def cargar_agenda():
    datos = supabase.table("agenda_telefonica").select("*").execute()
    if datos.data:
        return {d['cuit']: {'telefono': d.get('telefono', ''), 'email': d.get('email', ''), 'razon_social': d.get('razon_social', '')} for d in datos.data}
    return {}

@st.cache_data(ttl=300)
def cargar_anotaciones(legajo):
    datos = supabase.table("anotaciones_inspectores").select("*").eq("legajo_inspector", legajo).execute()
    if datos.data:
        return {d['id_empresa']: d['anotacion'] for d in datos.data}
    return {}

def guardar_anotacion(id_empresa, legajo, anotacion):
    """Guarda o actualiza una anotación"""
    existente = supabase.table("anotaciones_inspectores").select("*").eq("id_empresa", id_empresa).eq("legajo_inspector", legajo).execute()
    
    if existente.data:
        supabase.table("anotaciones_inspectores").update({
            "anotacion": anotacion,
            "fecha_anotacion": "now()"
        }).eq("id", existente.data[0]['id']).execute()
    else:
        supabase.table("anotaciones_inspectores").insert({
            "id_empresa": id_empresa,
            "legajo_inspector": legajo,
            "anotacion": anotacion,
            "fecha_anotacion": "now()"
        }).execute()

# ── Cargar inspectores ───────────────────────────────────────────────────────
inspectores = cargar_inspectores()

if not inspectores:
    st.warning("No hay inspectores cargados en el sistema.")
    st.stop()

# ── Selector de inspector ────────────────────────────────────────────────────
st.markdown("### 🔑 Seleccione su inspector")

opciones_inspectores = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores}

col_insp1, col_insp2 = st.columns([2, 1])
with col_insp1:
    inspector_seleccionado = st.selectbox(
        "Inspector",
        options=list(opciones_inspectores.keys()),
        key="selector_inspector"
    )

legajo_seleccionado = opciones_inspectores[inspector_seleccionado]
nombre_inspector = inspector_seleccionado.split(" (Legajo")[0]

st.success(f"✅ Bienvenido/a {nombre_inspector} - Visualizando sus empresas asignadas")

st.markdown("---")

# ── Cargar datos del inspector ───────────────────────────────────────────────
with st.spinner("Cargando sus empresas..."):
    df_empresas = supabase.table("padron_deuda_presunta").select("*").eq("leg", legajo_seleccionado).execute()
    df_empresas = pd.DataFrame(df_empresas.data) if df_empresas.data else pd.DataFrame()
    
    # Actualizar agenda telefónica automáticamente
    if not df_empresas.empty:
        actualizar_agenda_telefonica(df_empresas)
    
    coordenadas = cargar_coordenadas()
    agenda = cargar_agenda()
    anotaciones = cargar_anotaciones(legajo_seleccionado)

if df_empresas.empty:
    st.warning(f"No tiene empresas asignadas. {nombre_inspector} aún no tiene registros.")
    st.stop()

# ── Contadores ───────────────────────────────────────────────────────────────
total_registros = len(df_empresas)
con_coordenadas = 0
sin_coordenadas = 0
for _, row in df_empresas.iterrows():
    if coordenadas.get(row['id']) is not None:
        con_coordenadas += 1
    else:
        sin_coordenadas += 1

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.metric("📋 Total de empresas", total_registros)
with col_c2:
    st.metric("📍 Con ubicación", con_coordenadas)
with col_c3:
    st.metric("⚠️ Sin ubicación", sin_coordenadas)

st.markdown("---")

# ── Pestañas ─────────────────────────────────────────────────────────────────
tab_lista, tab_mapa, tab_agenda, tab_anotaciones = st.tabs([
    "📋 Listado de Empresas",
    "🗺️ Mapa de Ubicaciones",
    "📞 Agenda Telefónica",
    "📝 Mis Anotaciones"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: LISTADO DE EMPRESAS
# ══════════════════════════════════════════════════════════════════
with tab_lista:
    st.markdown("### 📋 Listado de sus empresas")
    st.caption("🔒 Modo solo consulta - No se pueden editar datos")
    
    # Filtros
    st.markdown("#### 🔎 Filtros de búsqueda")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown('<p class="filtro-titulo">CUIT</p>', unsafe_allow_html=True)
        filtro_cuit = st.text_input("CUIT", key="filtro_cuit_lista", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with col_f2:
        st.markdown('<p class="filtro-titulo">RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon = st.text_input("Razón Social", key="filtro_razon_lista", placeholder="Razón social", label_visibility="collapsed")
    with col_f3:
        st.markdown('<p class="filtro-titulo">CALLE</p>', unsafe_allow_html=True)
        filtro_calle = st.text_input("Calle", key="filtro_calle_lista", placeholder="Ej: San Luis", label_visibility="collapsed")
    
    # Aplicar filtros
    df_filtrado = df_empresas.copy()
    
    if filtro_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if filtro_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    if filtro_calle:
        df_filtrado = df_filtrado[df_filtrado['calle'].astype(str).str.contains(filtro_calle, case=False, na=False)]
    
    st.markdown(f"**📊 Mostrando {len(df_filtrado)} de {total_registros} registros**")
    
    # Preparar datos para mostrar
    df_mostrar = df_filtrado.copy()
    
    # Agregar teléfono y email desde la agenda
    df_mostrar['telefono'] = df_mostrar['cuit'].apply(lambda x: agenda.get(str(x), {}).get('telefono', '') if x else '')
    df_mostrar['email'] = df_mostrar['cuit'].apply(lambda x: agenda.get(str(x), {}).get('email', '') if x else '')
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = {
        'cuit': 'CUIT',
        'razon_social': 'RAZÓN SOCIAL',
        'localidad': 'LOCALIDAD',
        'calle': 'CALLE',
        'numero': 'NÚMERO',
        'telefono': 'TELÉFONO',
        'email': 'EMAIL',
        'vto': 'VENCIMIENTO',
        'acta': 'ACTA'
    }
    
    df_tabla = pd.DataFrame()
    for col_orig, col_nuevo in columnas_mostrar.items():
        if col_orig in df_mostrar.columns:
            df_tabla[col_nuevo] = df_mostrar[col_orig]
    
    # Formatear fechas
    if 'VENCIMIENTO' in df_tabla.columns:
        df_tabla['VENCIMIENTO'] = df_tabla['VENCIMIENTO'].apply(
            lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else "")
        )
    
    # Paginación
    RPP = 200
    total_paginas = max(1, (len(df_tabla) + RPP - 1) // RPP)
    
    if 'pagina_lista' not in st.session_state:
        st.session_state.pagina_lista = 1
    st.session_state.pagina_lista = max(1, min(st.session_state.pagina_lista, total_paginas))
    
    off = (st.session_state.pagina_lista - 1) * RPP
    df_paginado = df_tabla.iloc[off:off+RPP]
    
    col_pag1, col_pag2, col_pag3 = st.columns([1, 3, 1])
    with col_pag1:
        if st.button("◀ Anterior", key="btn_ant_lista") and st.session_state.pagina_lista > 1:
            st.session_state.pagina_lista -= 1
            st.rerun()
    with col_pag2:
        st.caption(f"Página {st.session_state.pagina_lista} de {total_paginas}")
    with col_pag3:
        if st.button("Siguiente ▶", key="btn_sig_lista") and st.session_state.pagina_lista < total_paginas:
            st.session_state.pagina_lista += 1
            st.rerun()
    
    st.dataframe(df_paginado, use_container_width=True, height=500)
    
    # Botón para descargar CSV
    if st.button("📥 Descargar listado (CSV)", key="btn_descargar_csv"):
        csv_data = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="✅ Hacer clic para descargar",
            data=csv_data,
            file_name=f"empresas_{nombre_inspector.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ══════════════════════════════════════════════════════════════════
# TAB 2: MAPA DE UBICACIONES
# ══════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown("### 🗺️ Ubicación de sus empresas")
    st.caption("💡 Los puntos muestran la ubicación de cada empresa. El mapa de calor muestra las zonas con mayor concentración.")
    
    # Detectar si el inspector tiene localidades fuera de MDP
    localidades_inspector = supabase.table("inspectores_localidad").select("localidad").eq("legajo", legajo_seleccionado).execute()
    tiene_localidades = localidades_inspector.data and len(localidades_inspector.data) > 0
    
    if tiene_localidades:
        st.info(f"📍 Este inspector tiene asignadas localidades fuera de Mar del Plata. El mapa muestra también esas ubicaciones.")
    
    # Preparar datos para el mapa
    datos_mapa = []
    total_sin_coords_mapa = 0
    
    colores_inspectores = {
        "RODRIGUEZ": "#2563eb",
        "POLINESSI": "#10b981",
        "LOPEZ": "#f59e0b",
        "CARBAYO": "#8b5cf6",
        "GARCIA": "#fcd34d",
    }
    nombre_corto = nombre_inspector.split(',')[0].upper()
    color_inspector = colores_inspectores.get(nombre_corto, "#3b82f6")
    
    for _, row in df_empresas.iterrows():
        id_empresa = row['id']
        razon_social = row.get('razon_social', 'Sin nombre')
        calle = row.get('calle', '')
        numero = row.get('numero', '')
        localidad = row.get('localidad', '')
        cuit = row.get('cuit', '')
        
        coords = coordenadas.get(id_empresa)
        
        if not coords:
            total_sin_coords_mapa += 1
            continue
        
        lat, lon = coords
        
        telefono = agenda.get(str(cuit), {}).get('telefono', '') if cuit else ''
        email = agenda.get(str(cuit), {}).get('email', '') if cuit else ''
        
        popup_text = f"""
        <div style="min-width: 250px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b>Teléfono:</b> {telefono}<br>
            <b>Email:</b> {email}
        </div>
        """
        
        datos_mapa.append({
            "coords": [lat, lon],
            "popup": popup_text,
            "razon_social": razon_social,
            "localidad": localidad
        })
    
    if not datos_mapa:
        st.info(f"📌 No hay empresas con ubicación disponible para {nombre_inspector}. Use el botón 'ACTUALIZAR COORDENADAS' en el mapa general para geocodificar las direcciones.")
    else:
        st.info(f"📍 Mostrando {len(datos_mapa)} de {total_registros} empresas (las que tienen coordenadas cargadas)")
        
        # Calcular centro
        centro_lat = sum(d["coords"][0] for d in datos_mapa) / len(datos_mapa)
        centro_lon = sum(d["coords"][1] for d in datos_mapa) / len(datos_mapa)
        
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles="cartodbpositron")
        
        # Agregar marcadores por localidad (diferentes íconos para MDP vs otras)
        for dato in datos_mapa:
            if "MAR DEL PLATA" in dato["localidad"].upper():
                icon_color = color_inspector
                icon_type = "circle"
            else:
                icon_color = "#ffaa00"
                icon_type = "circle"
            
            folium.CircleMarker(
                location=dato["coords"],
                radius=8,
                popup=folium.Popup(dato["popup"], max_width=350),
                color=icon_color,
                fill=True,
                fill_color=icon_color,
                fill_opacity=0.7,
                tooltip=f"{dato['razon_social'][:35]} - {dato['localidad']}"
            ).add_to(m)
        
        # Mapa de calor
        heat_data = [[d["coords"][0], d["coords"][1]] for d in datos_mapa]
        if len(heat_data) > 5:
            HeatMap(heat_data, radius=20, blur=15, max_zoom=13, min_opacity=0.3).add_to(m)
        
        Fullscreen(position="topleft", title="Pantalla completa", title_cancel="Salir").add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            m.save(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            os.unlink(tmp.name)
        
        st.components.v1.html(html_content, height=550, width=None)
        
        # Resumen
        st.markdown("---")
        st.markdown("### 📊 Resumen de su zona")
        
        localidades_count = df_empresas['localidad'].value_counts().head(10)
        st.markdown("**Distribución por localidad:**")
        for loc, count in localidades_count.items():
            st.markdown(f"- {loc}: {count} empresas")
        
        if total_sin_coords_mapa > 0:
            st.warning(f"⚠️ {total_sin_coords_mapa} empresas no tienen coordenadas cargadas.")

# ══════════════════════════════════════════════════════════════════
# TAB 3: AGENDA TELEFÓNICA
# ══════════════════════════════════════════════════════════════════
with tab_agenda:
    st.markdown("### 📞 Agenda Telefónica")
    st.caption("Todos los contactos de sus empresas asignadas")
    
    # Buscar en agenda por CUIT o Razón Social
    col_bus1, col_bus2 = st.columns(2)
    with col_bus1:
        buscar_cuit = st.text_input("Buscar por CUIT", placeholder="Ej: 30707685243", key="buscar_cuit_agenda")
    with col_bus2:
        buscar_razon = st.text_input("Buscar por Razón Social", placeholder="Ej: PEPSICO", key="buscar_razon_agenda")
    
    # Filtrar agenda
    agenda_filtrada = []
    for cuit, datos in agenda.items():
        # Verificar si esta empresa está asignada a este inspector
        empresa_asignada = df_empresas[df_empresas['cuit'].astype(str) == str(cuit)]
        if not empresa_asignada.empty:
            if buscar_cuit and str(cuit) != buscar_cuit:
                continue
            if buscar_razon and buscar_razon.lower() not in datos.get('razon_social', '').lower():
                continue
            agenda_filtrada.append({
                "CUIT": cuit,
                "RAZÓN SOCIAL": datos.get('razon_social', ''),
                "TELÉFONO": datos.get('telefono', ''),
                "EMAIL": datos.get('email', '')
            })
    
    if agenda_filtrada:
        df_agenda = pd.DataFrame(agenda_filtrada)
        st.dataframe(df_agenda, use_container_width=True, height=500)
        
        # Botón para descargar agenda
        if st.button("📥 Descargar agenda (CSV)", key="btn_descargar_agenda"):
            csv_data = df_agenda.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="✅ Hacer clic para descargar",
                data=csv_data,
                file_name=f"agenda_{nombre_inspector.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No hay contactos en la agenda para sus empresas asignadas")

# ══════════════════════════════════════════════════════════════════
# TAB 4: ANOTACIONES
# ══════════════════════════════════════════════════════════════════
with tab_anotaciones:
    st.markdown("### 📝 Mis Anotaciones")
    st.caption("Aquí puede guardar notas sobre sus gestiones con cada empresa")
    
    # Selector de empresa para anotar
    empresas_opciones = {f"{row['razon_social']} (CUIT: {row['cuit']})": row['id'] for _, row in df_empresas.iterrows()}
    
    if empresas_opciones:
        empresa_seleccionada = st.selectbox("Seleccionar empresa", options=list(empresas_opciones.keys()), key="selector_empresa_anotacion")
        id_empresa_sel = empresas_opciones[empresa_seleccionada]
        
        # Obtener anotación existente
        anotacion_actual = anotaciones.get(id_empresa_sel, "")
        
        # Textarea para anotación
        nueva_anotacion = st.text_area("Anotación", value=anotacion_actual, height=150, 
                                       placeholder="Ej: 15/05/2025 - Llamé al Sr. Pérez, quedó en enviar documentación...")
        
        col_guardar, _ = st.columns([1, 3])
        with col_guardar:
            if st.button("💾 Guardar anotación", type="primary", use_container_width=True):
                guardar_anotacion(id_empresa_sel, legajo_seleccionado, nueva_anotacion)
                st.success("✅ Anotación guardada correctamente")
                st.cache_data.clear()
                st.rerun()
        
        st.markdown("---")
        
        # Mostrar todas las anotaciones del inspector
        st.markdown("### 📋 Todas sus anotaciones")
        
        if anotaciones:
            for id_emp, anotacion in anotaciones.items():
                empresa_data = df_empresas[df_empresas['id'] == id_emp]
                if not empresa_data.empty:
                    razon = empresa_data.iloc[0].get('razon_social', 'Sin nombre')
                    cuit = empresa_data.iloc[0].get('cuit', '')
                    st.markdown(f"""
                    <div class="anotacion-card">
                        <b>{razon}</b> (CUIT: {cuit})<br>
                        <small style="color: #94a3b8;">📝 {anotacion}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No tiene anotaciones guardadas aún.")
    else:
        st.info("No hay empresas asignadas para anotar")

st.markdown("---")
st.caption(f"🔒 Acceso solo de consulta - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
