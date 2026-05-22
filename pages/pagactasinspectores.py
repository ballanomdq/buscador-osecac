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
.anotacion-card, .contacto-card {
    background: #1e293b;
    padding: 0.5rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #3b82f6;
}
.contacto-manual {
    border-left-color: #10b981;
}
.btn-editar {
    background: #f59e0b !important;
}
.btn-eliminar {
    background: #ef4444 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>👤 Panel del Inspector</h2>
    <p>Visualice sus empresas asignadas - Gestión de contactos y anotaciones</p>
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

# ── Funciones para agenda telefónica (MEJORADA) ──────────────────────────────
def sincronizar_agenda_desde_padron(cuit, razon_social, telefono_sistema, email):
    """Sincroniza los datos del padrón SIN pisar los agregados manualmente"""
    # Solo actualizar si hay datos nuevos del padrón
    if telefono_sistema:
        # Verificar si ya existe este teléfono como 'sistema'
        existente = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).eq("telefono", telefono_sistema).eq("tipo", "sistema").execute()
        if not existente.data:
            # Insertar nuevo teléfono de sistema
            supabase.table("agenda_telefonica").insert({
                "cuit": str(cuit),
                "razon_social": razon_social,
                "telefono": telefono_sistema,
                "email": email,
                "tipo": "sistema",
                "fuente": "padron"
            }).execute()
    
    if email:
        pass  # Similar para email si se necesita

def obtener_agenda_completa(cuit):
    """Obtiene TODOS los contactos de una empresa (sistema + manual)"""
    datos = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).execute()
    return datos.data if datos.data else []

def agregar_contacto_manual(cuit, razon_social, telefono, email, legajo_inspector):
    """Agrega un contacto manual (no se pisa nunca)"""
    try:
        supabase.table("agenda_telefonica").insert({
            "cuit": str(cuit),
            "razon_social": razon_social,
            "telefono": telefono,
            "email": email,
            "tipo": "manual",
            "fuente": "inspector",
            "legajo_inspector": legajo_inspector
        }).execute()
        return True
    except Exception as e:
        if "duplicate" in str(e).lower():
            st.warning("Este número ya existe en la agenda")
        return False

def eliminar_contacto(contacto_id, legajo_inspector):
    """Elimina un contacto (solo si es manual o si es sistema con verificación)"""
    contacto = supabase.table("agenda_telefonica").select("*").eq("id", contacto_id).execute()
    if contacto.data:
        if contacto.data[0]['tipo'] == 'manual':
            supabase.table("agenda_telefonica").delete().eq("id", contacto_id).execute()
            return True
        else:
            st.warning("No se pueden eliminar contactos del sistema (solo ocultar)")
            return False
    return False

def editar_contacto_manual(contacto_id, nuevo_telefono, nuevo_email):
    """Edita un contacto manual"""
    supabase.table("agenda_telefonica").update({
        "telefono": nuevo_telefono,
        "email": nuevo_email,
        "fecha_actualizacion": "now()"
    }).eq("id", contacto_id).execute()
    return True

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
def cargar_anotaciones(legajo):
    datos = supabase.table("anotaciones_inspectores").select("*").eq("legajo_inspector", legajo).execute()
    if datos.data:
        return {d['id_empresa']: d['anotacion'] for d in datos.data}
    return {}

def guardar_anotacion(id_empresa, legajo, anotacion):
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
    
    # Sincronizar agenda (sin pisar manuales)
    if not df_empresas.empty:
        for _, row in df_empresas.iterrows():
            telefono = row.get('tel_dom_legal') or row.get('tel_dom_real')
            sincronizar_agenda_desde_padron(
                row.get('cuit'), 
                row.get('razon_social'),
                telefono,
                row.get('email')
            )
    
    coordenadas = cargar_coordenadas()
    anotaciones = cargar_anotaciones(legajo_seleccionado)

if df_empresas.empty:
    st.warning(f"No tiene empresas asignadas. {nombre_inspector} aún no tiene registros.")
    st.stop()

# ── Contadores ───────────────────────────────────────────────────────────────
total_registros = len(df_empresas)
con_coordenadas = sum(1 for _, row in df_empresas.iterrows() if coordenadas.get(row['id']) is not None)

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.metric("📋 Total de empresas", total_registros)
with col_c2:
    st.metric("📍 Con ubicación", con_coordenadas)
with col_c3:
    st.metric("⚠️ Sin ubicación", total_registros - con_coordenadas)

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
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_cuit = st.text_input("CUIT", key="filtro_cuit_lista", placeholder="Ej: 30707685243")
    with col_f2:
        filtro_razon = st.text_input("Razón Social", key="filtro_razon_lista", placeholder="Razón social")
    with col_f3:
        filtro_calle = st.text_input("Calle", key="filtro_calle_lista", placeholder="Ej: San Luis")
    
    df_filtrado = df_empresas.copy()
    if filtro_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if filtro_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    if filtro_calle:
        df_filtrado = df_filtrado[df_filtrado['calle'].astype(str).str.contains(filtro_calle, case=False, na=False)]
    
    st.markdown(f"**📊 Mostrando {len(df_filtrado)} de {total_registros} registros**")
    
    columnas_mostrar = ['cuit', 'razon_social', 'localidad', 'calle', 'numero', 'vto', 'acta']
    df_tabla = df_filtrado[[c for c in columnas_mostrar if c in df_filtrado.columns]].copy()
    
    if 'vto' in df_tabla.columns:
        df_tabla['vto'] = df_tabla['vto'].apply(lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else ""))
    
    st.dataframe(df_tabla, use_container_width=True, height=500)
    
    if st.button("📥 Descargar listado (CSV)"):
        csv_data = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="✅ Hacer clic para descargar",
            data=csv_data,
            file_name=f"empresas_{nombre_inspector.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ══════════════════════════════════════════════════════════════════
# TAB 2: MAPA DE UBICACIONES (MEJORADO - TODAS LAS EMPRESAS)
# ══════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown("### 🗺️ Ubicación de sus empresas")
    st.caption("💡 Mapa de calor: zonas rojas/amarillas = mayor concentración de empresas")
    
    # Ver localidades asignadas
    localidades_inspector = supabase.table("inspectores_localidad").select("localidad").eq("legajo", legajo_seleccionado).execute()
    tiene_localidades = localidades_inspector.data and len(localidades_inspector.data) > 0
    
    if tiene_localidades:
        st.info(f"📍 Este inspector tiene asignadas localidades fuera de Mar del Plata.")
    
    # PREPARAR DATOS PARA EL MAPA (todas las empresas)
    datos_mapa = []  # Para puntos con coordenadas
    empresas_sin_coords = []  # Para mostrar lista
    
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
        vto = row.get('vto', '')
        
        coords = coordenadas.get(id_empresa)
        
        if coords:
            lat, lon = coords
            
            # Obtener contactos para el popup
            contactos = obtener_agenda_completa(cuit)
            telefonos = [c['telefono'] for c in contactos if c.get('telefono')]
            emails = [c['email'] for c in contactos if c.get('email')]
            
            popup_text = f"""
            <div style="min-width: 280px; max-width: 350px;">
                <b>{razon_social}</b><br>
                <b>CUIT:</b> {cuit}<br>
                <b>Dirección:</b> {calle} {numero}<br>
                <b>Localidad:</b> {localidad}<br>
                <b>Vencimiento:</b> {vto if vto else 'N/A'}<br>
                <b>Teléfonos:</b> {', '.join(telefonos) if telefonos else 'No registrado'}<br>
                <b>Emails:</b> {', '.join(emails) if emails else 'No registrado'}
            </div>
            """
            
            datos_mapa.append({
                "coords": [lat, lon],
                "popup": popup_text,
                "razon_social": razon_social,
                "localidad": localidad
            })
        else:
            empresas_sin_coords.append({
                "Razón Social": razon_social,
                "CUIT": cuit,
                "Dirección": f"{calle} {numero}",
                "Localidad": localidad
            })
    
    # Mostrar mapa si hay datos
    if datos_mapa:
        st.info(f"📍 Mostrando {len(datos_mapa)} empresas con ubicación. {len(empresas_sin_coords)} sin geolocalizar.")
        
        # Calcular centro
        centro_lat = sum(d["coords"][0] for d in datos_mapa) / len(datos_mapa)
        centro_lon = sum(d["coords"][1] for d in datos_mapa) / len(datos_mapa)
        
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles="cartodbpositron")
        
        # Agregar marcadores
        for dato in datos_mapa:
            icon_color = color_inspector
            if "MAR DEL PLATA" not in dato["localidad"].upper():
                icon_color = "#ffaa00"
            
            folium.CircleMarker(
                location=dato["coords"],
                radius=7,
                popup=folium.Popup(dato["popup"], max_width=400),
                color=icon_color,
                fill=True,
                fill_color=icon_color,
                fill_opacity=0.7,
                tooltip=f"{dato['razon_social'][:35]}"
            ).add_to(m)
        
        # MAPA DE CALOR (todas las empresas del inspector)
        if len(datos_mapa) > 3:
            heat_data = [[d["coords"][0], d["coords"][1]] for d in datos_mapa]
            HeatMap(heat_data, radius=25, blur=15, min_opacity=0.3, max_zoom=13).add_to(m)
        
        Fullscreen(position="topleft").add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            m.save(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            os.unlink(tmp.name)
        
        st.components.v1.html(html_content, height=550, width=None)
        
        # Resumen por localidad
        st.markdown("---")
        st.markdown("### 📊 Distribución por localidad")
        localidades_count = df_empresas['localidad'].value_counts().head(15)
        
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            for loc, count in localidades_count.items():
                st.markdown(f"- **{loc}**: {count} empresas")
        
        with col_loc2:
            st.metric("Total empresas", total_registros)
            st.metric("Con ubicación", len(datos_mapa))
            st.metric("Sin ubicación", len(empresas_sin_coords))
    
    else:
        st.warning(f"⚠️ No hay empresas con ubicación para {nombre_inspector}.")
    
    # Mostrar empresas sin coordenadas
    if empresas_sin_coords:
        with st.expander(f"📌 Ver {len(empresas_sin_coords)} empresas sin ubicación en el mapa"):
            st.dataframe(pd.DataFrame(empresas_sin_coords), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 3: AGENDA TELEFÓNICA (EDITABLE)
# ══════════════════════════════════════════════════════════════════
with tab_agenda:
    st.markdown("### 📞 Agenda Telefónica - Gestión de Contactos")
    st.caption("""
    - 📞 **Teléfonos azules**: Vienen del padrón (solo lectura)
    - ✏️ **Teléfonos verdes**: Agregados por usted (puede editar/eliminar)
    - ➕ **Agregar contacto**: Puede añadir teléfonos adicionales manualmente
    """)
    
    # Buscar empresa
    empresa_buscar = st.selectbox(
        "Seleccionar empresa",
        options=[f"{row['razon_social']} (CUIT: {row['cuit']})" for _, row in df_empresas.iterrows()],
        key="selector_empresa_agenda"
    )
    
    if empresa_buscar:
        # Extraer CUIT
        cuit_match = re.search(r'CUIT:\s*(\d+)', empresa_buscar)
        if cuit_match:
            cuit_seleccionado = cuit_match.group(1)
            empresa_data = df_empresas[df_empresas['cuit'].astype(str) == cuit_seleccionado].iloc[0]
            razon_social = empresa_data['razon_social']
            
            st.markdown(f"**Empresa:** {razon_social}")
            st.markdown(f"**CUIT:** {cuit_seleccionado}")
            st.markdown("---")
            
            # Obtener todos los contactos
            contactos = obtener_agenda_completa(cuit_seleccionado)
            
            # Mostrar contactos existentes
            if contactos:
                for contacto in contactos:
                    es_manual = contacto['tipo'] == 'manual'
                    
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**📞 {contacto['telefono']}**" if contacto['telefono'] else "Sin teléfono")
                    with col2:
                        st.markdown(f"✉️ {contacto['email']}" if contacto['email'] else "Sin email")
                    with col3:
                        if es_manual:
                            st.markdown("🟢 **Manual**")
                        else:
                            st.markdown("🔵 **Sistema**")
                    with col4:
                        if es_manual:
                            if st.button("✏️", key=f"edit_btn_{contacto['id']}"):
                                st.session_state[f"editando_contacto_{contacto['id']}"] = True
                            if st.button("🗑️", key=f"del_btn_{contacto['id']}"):
                                if eliminar_contacto(contacto['id'], legajo_seleccionado):
                                    st.success("Contacto eliminado")
                                    st.cache_data.clear()
                                    time.sleep(0.5)
                                    st.rerun()
                        else:
                            st.markdown("*(solo lectura)*")
                    
                    # Edición de contacto manual
                    if st.session_state.get(f"editando_contacto_{contacto['id']}"):
                        with st.expander(f"✏️ Editando {contacto['telefono']}", expanded=True):
                            nuevo_tel = st.text_input("Nuevo teléfono", value=contacto['telefono'] or "", key=f"edit_tel_{contacto['id']}")
                            nuevo_email = st.text_input("Nuevo email", value=contacto['email'] or "", key=f"edit_email_{contacto['id']}")
                            col_edit1, col_edit2 = st.columns(2)
                            with col_edit1:
                                if st.button("💾 Guardar", key=f"save_{contacto['id']}"):
                                    editar_contacto_manual(contacto['id'], nuevo_tel, nuevo_email)
                                    st.success("Contacto actualizado")
                                    del st.session_state[f"editando_contacto_{contacto['id']}"]
                                    st.cache_data.clear()
                                    st.rerun()
                            with col_edit2:
                                if st.button("❌ Cancelar", key=f"cancel_{contacto['id']}"):
                                    del st.session_state[f"editando_contacto_{contacto['id']}"]
                                    st.rerun()
                    
                    st.markdown("---")
            else:
                st.info("No hay contactos registrados para esta empresa")
            
            # Agregar nuevo contacto manual
            st.markdown("### ➕ Agregar nuevo contacto")
            with st.form("form_nuevo_contacto"):
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    nuevo_telefono = st.text_input("Teléfono", placeholder="Ej: 2235551234")
                with col_n2:
                    nuevo_email = st.text_input("Email", placeholder="Ej: contacto@empresa.com")
                
                if st.form_submit_button("➕ AGREGAR CONTACTO"):
                    if nuevo_telefono or nuevo_email:
                        if agregar_contacto_manual(cuit_seleccionado, razon_social, nuevo_telefono, nuevo_email, legajo_seleccionado):
                            st.success("✅ Contacto agregado correctamente")
                            st.cache_data.clear()
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.warning("Ingrese al menos un teléfono o email")

# ══════════════════════════════════════════════════════════════════
# TAB 4: ANOTACIONES
# ══════════════════════════════════════════════════════════════════
with tab_anotaciones:
    st.markdown("### 📝 Mis Anotaciones")
    st.caption("Aquí puede guardar notas sobre sus gestiones con cada empresa")
    
    empresas_opciones = {f"{row['razon_social']} (CUIT: {row['cuit']})": row['id'] for _, row in df_empresas.iterrows()}
    
    if empresas_opciones:
        empresa_seleccionada = st.selectbox("Seleccionar empresa", options=list(empresas_opciones.keys()), key="selector_empresa_anotacion")
        id_empresa_sel = empresas_opciones[empresa_seleccionada]
        
        anotacion_actual = anotaciones.get(id_empresa_sel, "")
        
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
