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
.ficha-contacto {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;
}
.ficha-titulo {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>👤 Panel del Inspector</h2>
    <p>Consulta de empresas | Agenda telefónica independiente</p>
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

# ── FUNCIONES DE AGENDA (INDEPENDIENTE) ──────────────────────────────────────

def actualizar_agenda_desde_padron(cuit, razon_social, telefono_legal, telefono_real, email, direccion, localidad):
    """Actualiza o crea un registro en la agenda con los datos del padrón
    SOLO actualiza telefono_legal, telefono_real - NO toca los extras del inspector"""
    if not cuit:
        return
    
    # Verificar si ya existe en agenda
    existente = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).execute()
    
    if existente.data:
        # Actualizar solo los campos del sistema
        update_data = {
            "razon_social": razon_social or existente.data[0].get('razon_social'),
            "telefono_legal": telefono_legal or existente.data[0].get('telefono_legal'),
            "telefono_real": telefono_real or existente.data[0].get('telefono_real'),
            "email": email or existente.data[0].get('email'),
            "direccion": direccion or existente.data[0].get('direccion'),
            "localidad": localidad or existente.data[0].get('localidad'),
            "ultima_actualizacion": "now()"
        }
        supabase.table("agenda_telefonica").update(update_data).eq("cuit", str(cuit)).execute()
    else:
        # Crear nuevo registro
        supabase.table("agenda_telefonica").insert({
            "cuit": str(cuit),
            "razon_social": razon_social or "",
            "telefono_legal": telefono_legal or "",
            "telefono_real": telefono_real or "",
            "email": email or "",
            "direccion": direccion or "",
            "localidad": localidad or "",
            "fecha_creacion": "now()"
        }).execute()

def sincronizar_toda_agenda(df_empresas):
    """Sincroniza TODAS las empresas del inspector con la agenda"""
    if df_empresas.empty:
        return 0
    
    contador = 0
    for _, row in df_empresas.iterrows():
        cuit = row.get('cuit')
        if not cuit:
            continue
        
        razon_social = row.get('razon_social', '')
        email = row.get('email', '')
        tel_legal = row.get('tel_dom_legal', '')
        tel_real = row.get('tel_dom_real', '')
        direccion = f"{row.get('calle', '')} {row.get('numero', '')}".strip()
        localidad = row.get('localidad', '')
        
        # Verificar si ya existe
        existente = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).execute()
        
        if existente.data:
            # Solo actualizar si hay cambios en los campos del sistema
            cambios = False
            update_data = {}
            
            if razon_social and razon_social != existente.data[0].get('razon_social'):
                update_data["razon_social"] = razon_social
                cambios = True
            if tel_legal and tel_legal != existente.data[0].get('telefono_legal'):
                update_data["telefono_legal"] = tel_legal
                cambios = True
            if tel_real and tel_real != existente.data[0].get('telefono_real'):
                update_data["telefono_real"] = tel_real
                cambios = True
            if email and email != existente.data[0].get('email'):
                update_data["email"] = email
                cambios = True
            if direccion and direccion != existente.data[0].get('direccion'):
                update_data["direccion"] = direccion
                cambios = True
            if localidad and localidad != existente.data[0].get('localidad'):
                update_data["localidad"] = localidad
                cambios = True
            
            if cambios:
                update_data["ultima_actualizacion"] = "now()"
                supabase.table("agenda_telefonica").update(update_data).eq("cuit", str(cuit)).execute()
                contador += 1
        else:
            # Crear nuevo
            supabase.table("agenda_telefonica").insert({
                "cuit": str(cuit),
                "razon_social": razon_social,
                "telefono_legal": tel_legal or "",
                "telefono_real": tel_real or "",
                "email": email or "",
                "direccion": direccion,
                "localidad": localidad,
                "fecha_creacion": "now()"
            }).execute()
            contador += 1
    
    return contador

def obtener_todos_contactos_agenda():
    """Obtiene TODOS los contactos de la agenda (para el inspector actual)"""
    try:
        datos = supabase.table("agenda_telefonica").select("*").order("razon_social").execute()
        return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def agregar_telefono_extra(cuit, telefono, observacion, campo_num):
    """Agrega un teléfono extra en el campo especificado"""
    try:
        update_data = {
            campo_num: telefono,
            f"observaciones_{campo_num.replace('telefono_extra', 'observaciones_extra')}": observacion,
            "ultima_actualizacion": "now()"
        }
        supabase.table("agenda_telefonica").update(update_data).eq("cuit", str(cuit)).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def eliminar_telefono_extra(cuit, campo_num):
    """Elimina un teléfono extra"""
    try:
        update_data = {
            campo_num: None,
            f"observaciones_{campo_num.replace('telefono_extra', 'observaciones_extra')}": None,
            "ultima_actualizacion": "now()"
        }
        supabase.table("agenda_telefonica").update(update_data).eq("cuit", str(cuit)).execute()
        return True
    except Exception as e:
        return False

def guardar_nota_inspector(cuit, nota):
    """Guarda la nota del inspector para la empresa"""
    try:
        supabase.table("agenda_telefonica").update({
            "nota_inspector": nota,
            "ultima_actualizacion": "now()"
        }).eq("cuit", str(cuit)).execute()
        return True
    except Exception as e:
        return False

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

st.success(f"✅ Bienvenido/a {nombre_inspector}")

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
    st.metric("📋 Total de empresas asignadas", total_registros)
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
# TAB 1: LISTADO DE EMPRESAS (SOLO LECTURA)
# ══════════════════════════════════════════════════════════════════
with tab_lista:
    st.markdown("### 📋 Listado de sus empresas")
    st.caption("🔒 Modo solo consulta - Datos del padrón")
    
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
        
        popup_text = f"""
        <div style="min-width: 250px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}
        </div>
        """
        
        datos_mapa.append({
            "coords": [lat, lon],
            "popup": popup_text,
            "razon_social": razon_social
        })
    
    if not datos_mapa:
        st.info(f"📌 No hay empresas con ubicación disponible.")
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
        
        if total_sin_coords_mapa > 0:
            st.warning(f"⚠️ {total_sin_coords_mapa} empresas sin coordenadas")

# ══════════════════════════════════════════════════════════════════
# TAB 3: AGENDA TELEFÓNICA (INDEPENDIENTE)
# ══════════════════════════════════════════════════════════════════
with tab_agenda:
    st.markdown("### 📞 Agenda Telefónica - Contactos de sus empresas")
    st.markdown("""
    <div style="background: #f1f5f9; padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.85rem;">
        📌 Esta agenda es <strong>INDEPENDIENTE</strong> del padrón. Los datos se actualizan desde sus empresas asignadas,<br>
        pero si mañana se borran todos los registros, la agenda conserva la información.<br>
        ✏️ Usted puede agregar hasta 3 teléfonos adicionales y notas personales que NO se pierden al actualizar.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón para sincronizar agenda
    col_sync1, col_sync2 = st.columns([1, 3])
    with col_sync1:
        if st.button("🔄 ACTUALIZAR AGENDA", type="primary", use_container_width=True):
            with st.spinner("Sincronizando con sus empresas asignadas..."):
                agregados = sincronizar_toda_agenda(df_empresas)
                if agregados > 0:
                    st.success(f"✅ Agenda actualizada: {agregados} empresas sincronizadas")
                else:
                    st.info("📭 La agenda ya está al día")
                st.cache_data.clear()
                time.sleep(0.5)
                st.rerun()
    with col_sync2:
        st.caption("💡 Actualiza los teléfonos legal/real desde el padrón. No modifica sus teléfonos adicionales.")
    
    st.markdown("---")
    
    # Buscador de agenda
    st.markdown("#### 🔎 Buscar en la agenda")
    col_bus1, col_bus2 = st.columns(2)
    with col_bus1:
        buscar_cuit = st.text_input("CUIT", placeholder="Ej: 30707685243", key="buscar_agenda_cuit")
    with col_bus2:
        buscar_razon = st.text_input("Razón Social", placeholder="Ej: PEPSICO", key="buscar_agenda_razon")
    
    # Obtener agenda completa
    df_agenda = obtener_todos_contactos_agenda()
    
    if df_agenda.empty:
        st.info("📭 La agenda está vacía. Presione 'ACTUALIZAR AGENDA' para cargar sus empresas.")
    else:
        # Filtrar agenda
        df_agenda_filtrada = df_agenda.copy()
        if buscar_cuit:
            df_agenda_filtrada = df_agenda_filtrada[df_agenda_filtrada['cuit'].astype(str).str.contains(buscar_cuit, case=False, na=False)]
        if buscar_razon:
            df_agenda_filtrada = df_agenda_filtrada[df_agenda_filtrada['razon_social'].astype(str).str.contains(buscar_razon, case=False, na=False)]
        
        st.markdown(f"**📊 Mostrando {len(df_agenda_filtrada)} contactos**")
        
        # Mostrar cada empresa como ficha
        for _, row in df_agenda_filtrada.iterrows():
            with st.expander(f"🏢 {row.get('razon_social', 'Sin nombre')} (CUIT: {row.get('cuit', 'N/D')})", expanded=False):
                col_dat1, col_dat2 = st.columns(2)
                
                with col_dat1:
                    st.markdown("**📞 Teléfonos del sistema:**")
                    st.markdown(f"- Legal: {row.get('telefono_legal', 'No registrado')}")
                    st.markdown(f"- Real: {row.get('telefono_real', 'No registrado')}")
                    st.markdown(f"✉️ Email: {row.get('email', 'No registrado')}")
                    st.markdown(f"📍 Dirección: {row.get('direccion', 'No registrada')}")
                    st.markdown(f"🏘️ Localidad: {row.get('localidad', 'No registrada')}")
                
                with col_dat2:
                    st.markdown("**📝 Teléfonos adicionales (usted los gestiona):**")
                    
                    # Teléfono extra 1
                    extra1 = row.get('telefono_extra1')
                    obs1 = row.get('observaciones_extra1', '')
                    if extra1:
                        st.markdown(f"- {extra1} {f'({obs1})' if obs1 else ''}")
                        if st.button("🗑️ Eliminar", key=f"del_extra1_{row['cuit']}"):
                            if eliminar_telefono_extra(row['cuit'], 'telefono_extra1'):
                                st.success("Eliminado")
                                st.rerun()
                    else:
                        with st.form(key=f"form_extra1_{row['cuit']}"):
                            nuevo_tel = st.text_input("Nuevo teléfono", key=f"tel1_{row['cuit']}", placeholder="Ej: 2235551234")
                            nueva_obs = st.text_input("Observación", key=f"obs1_{row['cuit']}", placeholder="Ej: Celular personal")
                            if st.form_submit_button("➕ Agregar"):
                                if nuevo_tel:
                                    if agregar_telefono_extra(row['cuit'], nuevo_tel, nueva_obs, 'telefono_extra1'):
                                        st.success("Teléfono agregado")
                                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Teléfono extra 2
                    extra2 = row.get('telefono_extra2')
                    obs2 = row.get('observaciones_extra2', '')
                    if extra2:
                        st.markdown(f"- {extra2} {f'({obs2})' if obs2 else ''}")
                        if st.button("🗑️ Eliminar", key=f"del_extra2_{row['cuit']}"):
                            if eliminar_telefono_extra(row['cuit'], 'telefono_extra2'):
                                st.success("Eliminado")
                                st.rerun()
                    else:
                        with st.form(key=f"form_extra2_{row['cuit']}"):
                            nuevo_tel = st.text_input("Nuevo teléfono", key=f"tel2_{row['cuit']}", placeholder="Ej: 2235551234")
                            nueva_obs = st.text_input("Observación", key=f"obs2_{row['cuit']}", placeholder="Ej: Teléfono fijo alternativo")
                            if st.form_submit_button("➕ Agregar"):
                                if nuevo_tel:
                                    if agregar_telefono_extra(row['cuit'], nuevo_tel, nueva_obs, 'telefono_extra2'):
                                        st.success("Teléfono agregado")
                                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Teléfono extra 3
                    extra3 = row.get('telefono_extra3')
                    obs3 = row.get('observaciones_extra3', '')
                    if extra3:
                        st.markdown(f"- {extra3} {f'({obs3})' if obs3 else ''}")
                        if st.button("🗑️ Eliminar", key=f"del_extra3_{row['cuit']}"):
                            if eliminar_telefono_extra(row['cuit'], 'telefono_extra3'):
                                st.success("Eliminado")
                                st.rerun()
                    else:
                        with st.form(key=f"form_extra3_{row['cuit']}"):
                            nuevo_tel = st.text_input("Nuevo teléfono", key=f"tel3_{row['cuit']}", placeholder="Ej: 2235551234")
                            nueva_obs = st.text_input("Observación", key=f"obs3_{row['cuit']}", placeholder="Ej: Contacto emergencia")
                            if st.form_submit_button("➕ Agregar"):
                                if nuevo_tel:
                                    if agregar_telefono_extra(row['cuit'], nuevo_tel, nueva_obs, 'telefono_extra3'):
                                        st.success("Teléfono agregado")
                                        st.rerun()
                
                # Nota del inspector
                st.markdown("---")
                st.markdown("**📝 Nota personal (solo para usted):**")
                nota_actual = row.get('nota_inspector', '')
                nueva_nota = st.text_area("", value=nota_actual if nota_actual else "", height=68, key=f"nota_{row['cuit']}", 
                                         placeholder="Ej: Atiende mejor por la tarde, es el hijo el que maneja los pagos...")
                if st.button("💾 Guardar nota", key=f"guardar_nota_{row['cuit']}"):
                    if guardar_nota_inspector(row['cuit'], nueva_nota):
                        st.success("Nota guardada")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 4: GENERAR INFORME
# ══════════════════════════════════════════════════════════════════
with tab_informe:
    st.markdown("### 📄 Generar Informe de sus empresas")
    
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
