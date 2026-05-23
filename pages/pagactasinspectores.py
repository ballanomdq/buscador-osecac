import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
import re
import tempfile
import os
from folium.plugins import Fullscreen, HeatMap

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
div[data-testid="stButton"] button[kind="secondary"] {
    background: #10b981 !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #059669 !important;
}
.stDataFrame { font-size: 0.75rem; }
.filtro-titulo { font-size: 0.65rem; color: #64748b; margin-bottom: 0.2rem; }
iframe {
    width: 100% !important;
    height: 60vh !important;
    min-height: 450px !important;
    border: none !important;
    border-radius: 8px !important;
}
.contacto-card {
    background: #1e293b;
    padding: 0.5rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #3b82f6;
}
.contacto-manual {
    border-left-color: #10b981;
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

# ── Funciones para agenda telefónica ─────────────────────────────────────────
def sincronizar_agenda_desde_padron(cuit, razon_social, telefono_legal, telefono_real, email):
    """Sincroniza los datos del padrón SIN pisar los agregados manualmente"""
    if not cuit:
        return
    
    telefonos_a_sincronizar = []
    if telefono_legal and str(telefono_legal).strip():
        telefonos_a_sincronizar.append(("legal", str(telefono_legal).strip()))
    if telefono_real and str(telefono_real).strip() and str(telefono_real).strip() != str(telefono_legal).strip():
        telefonos_a_sincronizar.append(("real", str(telefono_real).strip()))
    
    for fuente, telefono_str in telefonos_a_sincronizar:
        try:
            existente = supabase.table("agenda_telefonica").select("id").eq("cuit", str(cuit)).eq("telefono", telefono_str).eq("tipo", "sistema").execute()
            
            if not existente.data:
                supabase.table("agenda_telefonica").insert({
                    "cuit": str(cuit),
                    "razon_social": razon_social or "",
                    "telefono": telefono_str,
                    "email": email or "",
                    "tipo": "sistema",
                    "fuente": fuente,
                    "observaciones": f"Teléfono de {fuente} cargado desde el padrón"
                }).execute()
        except Exception as e:
            pass

def obtener_agenda_completa(cuit):
    """Obtiene TODOS los contactos de una empresa (sistema + manual)"""
    try:
        datos = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).order("tipo", desc=False).execute()
        return datos.data if datos.data else []
    except Exception as e:
        return []

def agregar_contacto_manual(cuit, razon_social, telefono, email, observaciones, legajo_inspector):
    """Agrega un contacto manual"""
    try:
        existente = supabase.table("agenda_telefonica").select("id").eq("cuit", str(cuit)).eq("telefono", telefono).execute()
        if existente.data:
            st.warning("⚠️ Este número ya existe")
            return False
        
        supabase.table("agenda_telefonica").insert({
            "cuit": str(cuit),
            "razon_social": razon_social,
            "telefono": telefono,
            "email": email or "",
            "tipo": "manual",
            "fuente": "inspector",
            "legajo_inspector": legajo_inspector,
            "observaciones": observaciones or ""
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def eliminar_contacto(contacto_id):
    """Elimina un contacto manual"""
    try:
        contacto = supabase.table("agenda_telefonica").select("*").eq("id", contacto_id).execute()
        if contacto.data and contacto.data[0]['tipo'] == 'manual':
            supabase.table("agenda_telefonica").delete().eq("id", contacto_id).execute()
            return True
        else:
            st.warning("No se pueden eliminar contactos del sistema")
            return False
    except Exception as e:
        return False

def editar_contacto_manual(contacto_id, nuevo_telefono, nuevo_email, nuevas_obs):
    """Edita un contacto manual"""
    try:
        supabase.table("agenda_telefonica").update({
            "telefono": nuevo_telefono,
            "email": nuevo_email,
            "observaciones": nuevas_obs,
            "fecha_actualizacion": "now()"
        }).eq("id", contacto_id).execute()
        return True
    except Exception as e:
        return False

def sincronizar_toda_agenda(df_empresas):
    """Sincroniza TODAS las empresas de una sola vez"""
    if df_empresas.empty:
        return 0
    
    contador = 0
    for _, row in df_empresas.iterrows():
        cuit = row.get('cuit')
        if not cuit:
            continue
        
        razon_social = row.get('razon_social', '')
        email = row.get('email', '')
        tel_legal = row.get('tel_dom_legal')
        tel_real = row.get('tel_dom_real')
        
        telefonos = []
        if tel_legal and str(tel_legal).strip():
            telefonos.append(("legal", str(tel_legal).strip()))
        if tel_real and str(tel_real).strip() and str(tel_real).strip() != str(tel_legal).strip():
            telefonos.append(("real", str(tel_real).strip()))
        
        for fuente, telefono_str in telefonos:
            existente = supabase.table("agenda_telefonica").select("id").eq("cuit", str(cuit)).eq("telefono", telefono_str).eq("tipo", "sistema").execute()
            if not existente.data:
                supabase.table("agenda_telefonica").insert({
                    "cuit": str(cuit),
                    "razon_social": razon_social,
                    "telefono": telefono_str,
                    "email": email,
                    "tipo": "sistema",
                    "fuente": fuente,
                    "observaciones": f"Teléfono de {fuente} cargado desde el padrón"
                }).execute()
                contador += 1
    return contador

def generar_informe_txt(df_empresas, nombre_inspector, legajo):
    """Genera informe TXT con fichas por empresa"""
    contenido = []
    contenido.append("=" * 80)
    contenido.append(f"                    INFORME DE EMPRESAS ASIGNADAS")
    contenido.append(f"                  Inspector: {nombre_inspector} (Legajo: {legajo})")
    contenido.append(f"                        Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    contenido.append(f"                        Total de empresas: {len(df_empresas)}")
    contenido.append("=" * 80)
    contenido.append("")
    
    for i, (_, row) in enumerate(df_empresas.iterrows(), 1):
        contenido.append("┌" + "─" * 78 + "┐")
        contenido.append(f"│ EMPRESA N° {i:<70}│")
        contenido.append("├" + "─" * 78 + "┤")
        contenido.append(f"│ CUIT:           {str(row.get('cuit', 'N/D')):<61}│")
        contenido.append(f"│ RAZÓN SOCIAL:   {str(row.get('razon_social', 'N/D')):<61}│")
        contenido.append(f"│ DOMICILIO:      {str(row.get('calle', 'N/D'))} {str(row.get('numero', '')):<61}│")
        contenido.append(f"│ LOCALIDAD:      {str(row.get('localidad', 'N/D')):<61}│")
        contenido.append(f"│ TELÉFONO LEGAL: {str(row.get('tel_dom_legal', 'N/D')):<61}│")
        contenido.append(f"│ TELÉFONO REAL:  {str(row.get('tel_dom_real', 'N/D')):<61}│")
        contenido.append(f"│ EMAIL:          {str(row.get('email', 'N/D')):<61}│")
        
        # Formatear fechas
        vto = row.get('vto', 'N/D')
        if hasattr(vto, 'strftime'):
            vto = vto.strftime('%d/%m/%Y')
        contenido.append(f"│ VENCIMIENTO:    {str(vto):<61}│")
        
        fecha_carga = row.get('fecha_carga', 'N/D')
        if hasattr(fecha_carga, 'strftime'):
            fecha_carga = fecha_carga.strftime('%d/%m/%Y')
        contenido.append(f"│ FECHA CARGA:    {str(fecha_carga):<61}│")
        
        contenido.append(f"│ ACTA:           {str(row.get('acta', 'N/D')):<61}│")
        contenido.append(f"│ MAIL ENVIADO:   {str(row.get('mail_enviado', 'N/D')):<61}│")
        contenido.append("└" + "─" * 78 + "┘")
        contenido.append("")
    
    contenido.append("=" * 80)
    contenido.append("                        FIN DEL INFORME")
    contenido.append("=" * 80)
    
    return "\n".join(contenido)

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
def cargar_empresas_por_inspector(legajo):
    datos = supabase.table("padron_deuda_presunta").select(
        "id", "cuit", "razon_social", "localidad", "calle", "numero", 
        "piso", "dpto", "cp", "vto", "acta", "mail_enviado", 
        "tel_dom_legal", "tel_dom_real", "email", "deuda_presunta",
        "desde", "hasta", "actividad", "situacion", "fecha_carga"
    ).eq("leg", legajo).execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

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
    df_empresas = cargar_empresas_por_inspector(legajo_seleccionado)
    coordenadas = cargar_coordenadas()

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
tab_lista, tab_mapa, tab_agenda, tab_informe = st.tabs([
    "📋 Listado de Empresas", 
    "🗺️ Mapa de Ubicaciones", 
    "📞 Agenda Telefónica",
    "📄 Generar Informe"
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
    
    columnas_mostrar = {
        'cuit': 'CUIT',
        'razon_social': 'RAZÓN SOCIAL',
        'localidad': 'LOCALIDAD',
        'calle': 'CALLE',
        'numero': 'NÚMERO',
        'tel_dom_legal': 'TEL. LEGAL',
        'tel_dom_real': 'TEL. REAL',
        'email': 'EMAIL',
        'vto': 'VTO',
        'fecha_carga': 'FECHA CARGA',
        'acta': 'ACTA'
    }
    
    df_tabla = pd.DataFrame()
    for col_orig, col_nuevo in columnas_mostrar.items():
        if col_orig in df_filtrado.columns:
            df_tabla[col_nuevo] = df_filtrado[col_orig]
    
    # Formatear fechas
    for col_fecha in ['VTO', 'FECHA CARGA']:
        if col_fecha in df_tabla.columns:
            df_tabla[col_fecha] = df_tabla[col_fecha].apply(
                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else "")
            )
    
    st.dataframe(df_tabla, use_container_width=True, height=500)

# ══════════════════════════════════════════════════════════════════
# TAB 2: MAPA DE UBICACIONES
# ══════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown("### 🗺️ Ubicación de sus empresas")
    st.caption("💡 Los puntos muestran la ubicación aproximada de cada empresa")
    
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
        telefono = row.get('tel_dom_legal') or row.get('tel_dom_real')
        
        coords = coordenadas.get(id_empresa)
        
        if not coords:
            total_sin_coords_mapa += 1
            continue
        
        lat, lon = coords
        
        popup_text = f"""
        <div style="min-width: 250px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b>Teléfono:</b> {telefono if telefono else 'No registrado'}
        </div>
        """
        
        datos_mapa.append({
            "coords": [lat, lon],
            "popup": popup_text,
            "razon_social": razon_social
        })
    
    if not datos_mapa:
        st.info(f"📌 No hay empresas con ubicación disponible para {nombre_inspector}.")
    else:
        st.info(f"📍 Mostrando {len(datos_mapa)} de {total_registros} empresas")
        
        centro_lat = sum(d["coords"][0] for d in datos_mapa) / len(datos_mapa)
        centro_lon = sum(d["coords"][1] for d in datos_mapa) / len(datos_mapa)
        
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="cartodbpositron")
        
        for dato in datos_mapa:
            folium.CircleMarker(
                location=dato["coords"],
                radius=8,
                popup=folium.Popup(dato["popup"], max_width=350),
                color=color_inspector,
                fill=True,
                fill_color=color_inspector,
                fill_opacity=0.7,
                tooltip=dato["razon_social"][:35]
            ).add_to(m)
        
        heat_data = [[d["coords"][0], d["coords"][1]] for d in datos_mapa]
        if len(heat_data) > 5:
            HeatMap(heat_data, radius=15, blur=10, max_zoom=13).add_to(m)
        
        Fullscreen(position="topleft").add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            m.save(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            os.unlink(tmp.name)
        
        st.components.v1.html(html_content, height=550, width=None)
        
        st.markdown("---")
        st.markdown("### 📊 Resumen de su zona")
        
        localidades_count = df_empresas['localidad'].value_counts().head(10)
        for loc, count in localidades_count.items():
            st.markdown(f"- {loc}: {count} empresas")
        
        if total_sin_coords_mapa > 0:
            st.warning(f"⚠️ {total_sin_coords_mapa} empresas sin coordenadas")

# ══════════════════════════════════════════════════════════════════
# TAB 3: AGENDA TELEFÓNICA (CON BOTÓN MANUAL)
# ══════════════════════════════════════════════════════════════════
with tab_agenda:
    st.markdown("### 📞 Agenda Telefónica - Gestión de Contactos")
    
    # Botón para actualizar agenda (SOLO cuando se presiona)
    st.markdown("#### 🔄 Sincronización con el padrón")
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("📥 ACTUALIZAR AGENDA", type="primary", use_container_width=True):
            with st.spinner("Sincronizando teléfonos del padrón..."):
                agregados = sincronizar_toda_agenda(df_empresas)
                if agregados > 0:
                    st.success(f"✅ Agenda actualizada: {agregados} teléfonos nuevos agregados")
                else:
                    st.info("📭 No se encontraron teléfonos nuevos para agregar")
                st.cache_data.clear()
                time.sleep(0.5)
                st.rerun()
    with col_btn2:
        st.caption("💡 Los teléfonos del padrón (tel_dom_legal y tel_dom_real) se cargan automáticamente sin duplicados")
    
    st.markdown("---")
    
    # Selector de empresa
    empresa_buscar = st.selectbox(
        "Seleccionar empresa para ver/editar contactos",
        options=[f"{row['razon_social']} (CUIT: {row['cuit']})" for _, row in df_empresas.iterrows()],
        key="selector_empresa_agenda"
    )
    
    if empresa_buscar:
        cuit_match = re.search(r'CUIT:\s*(\d+)', empresa_buscar)
        if cuit_match:
            cuit_seleccionado = cuit_match.group(1)
            empresa_data = df_empresas[df_empresas['cuit'].astype(str) == cuit_seleccionado].iloc[0]
            razon_social = empresa_data['razon_social']
            
            st.markdown(f"**Empresa:** {razon_social}")
            st.markdown(f"**CUIT:** {cuit_seleccionado}")
            st.markdown("---")
            
            contactos = obtener_agenda_completa(cuit_seleccionado)
            
            if contactos:
                st.markdown("#### 📋 Contactos registrados")
                for contacto in contactos:
                    es_manual = contacto['tipo'] == 'manual'
                    
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
                        
                        with col1:
                            st.markdown(f"**📞 {contacto['telefono']}**" if contacto['telefono'] else "Sin teléfono")
                        with col2:
                            st.markdown(f"✉️ {contacto['email']}" if contacto['email'] else "Sin email")
                        with col3:
                            if es_manual:
                                st.markdown("🟢 **Manual**")
                            else:
                                st.markdown("🔵 **Sistema (padrón)**")
                        with col4:
                            if es_manual:
                                if st.button("✏️", key=f"edit_btn_{contacto['id']}"):
                                    st.session_state[f"editando_{contacto['id']}"] = True
                                if st.button("🗑️", key=f"del_btn_{contacto['id']}"):
                                    if eliminar_contacto(contacto['id']):
                                        st.success("Contacto eliminado")
                                        st.cache_data.clear()
                                        time.sleep(0.5)
                                        st.rerun()
                        
                        if contacto.get('observaciones'):
                            st.caption(f"📝 Nota: {contacto['observaciones']}")
                        
                        if st.session_state.get(f"editando_{contacto['id']}"):
                            with st.expander(f"✏️ Editando contacto", expanded=True):
                                nuevo_tel = st.text_input("Teléfono", value=contacto['telefono'] or "", key=f"edit_tel_{contacto['id']}")
                                nuevo_email = st.text_input("Email", value=contacto['email'] or "", key=f"edit_email_{contacto['id']}")
                                nuevas_obs = st.text_area("Observaciones", value=contacto.get('observaciones') or "", key=f"edit_obs_{contacto['id']}")
                                
                                col_e1, col_e2 = st.columns(2)
                                with col_e1:
                                    if st.button("💾 Guardar", key=f"save_{contacto['id']}"):
                                        if editar_contacto_manual(contacto['id'], nuevo_tel, nuevo_email, nuevas_obs):
                                            st.success("Contacto actualizado")
                                            del st.session_state[f"editando_{contacto['id']}"]
                                            st.cache_data.clear()
                                            st.rerun()
                                with col_e2:
                                    if st.button("❌ Cancelar", key=f"cancel_{contacto['id']}"):
                                        del st.session_state[f"editando_{contacto['id']}"]
                                        st.rerun()
                        
                        st.markdown("---")
            else:
                st.info("No hay contactos registrados. Haga clic en 'ACTUALIZAR AGENDA' para cargar los teléfonos del padrón.")
            
            # Agregar nuevo contacto manual
            st.markdown("#### ➕ Agregar contacto manual")
            with st.form("form_nuevo_contacto"):
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    nuevo_telefono = st.text_input("Teléfono", placeholder="Ej: 2235551234")
                with col_n2:
                    nuevo_email = st.text_input("Email", placeholder="Ej: contacto@empresa.com")
                
                nuevas_obs = st.text_area("Observaciones / Notas", placeholder="Ej: Celular personal, Horario de atención, Contacto: Juan Pérez...", height=68)
                
                if st.form_submit_button("➕ AGREGAR CONTACTO"):
                    if nuevo_telefono:
                        if agregar_contacto_manual(cuit_seleccionado, razon_social, nuevo_telefono, nuevo_email, nuevas_obs, legajo_seleccionado):
                            st.success("✅ Contacto agregado correctamente")
                            st.cache_data.clear()
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.warning("Ingrese al menos un número de teléfono")

# ══════════════════════════════════════════════════════════════════
# TAB 4: GENERAR INFORME
# ══════════════════════════════════════════════════════════════════
with tab_informe:
    st.markdown("### 📄 Generar Informe de sus empresas")
    st.markdown("""
    <div style="background: #f1f5f9; padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.85rem;">📋 El informe se genera en formato TXT con una ficha detallada por cada empresa.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📊 Total empresas", len(df_empresas))
    with col_info2:
        st.metric("👤 Inspector", nombre_inspector)
    with col_info3:
        st.metric("📅 Fecha", datetime.now().strftime('%d/%m/%Y'))
    
    st.markdown("---")
    
    if st.button("📥 GENERAR Y DESCARGAR INFORME", type="primary", use_container_width=True):
        with st.spinner("Generando informe..."):
            contenido_txt = generar_informe_txt(df_empresas, nombre_inspector, legajo_seleccionado)
            st.download_button(
                label="✅ Hacer clic para descargar",
                data=contenido_txt.encode('utf-8'),
                file_name=f"INFORME_{nombre_inspector.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success("✅ Informe generado")

st.markdown("---")
st.caption(f"🔒 Acceso solo de consulta - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
