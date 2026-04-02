import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import time
import re

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Fiscalización OSECAC", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS PROFESIONALES ---
st.markdown("""
<style>
    /* Estilo para los títulos de los Expanders */
    .stExpander { border: 1px solid #d1d5db; border-radius: 10px; margin-bottom: 10px; transition: 0.3s; }
    .stExpander:hover { border-color: #3b82f6; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05); }
    
    /* Badge de Alerta */
    .badge { padding: 4px 8px; border-radius: 6px; color: white; font-weight: bold; font-size: 0.8rem; margin-right: 10px; }
    .badge-roja { background-color: #ef4444; }
    .badge-amarilla { background-color: #f59e0b; }
    .badge-gris { background-color: #6b7280; }
    .badge-verde { background-color: #10b981; }

    /* Estilo de la fuente */
    .texto-edicto { font-family: 'Inter', sans-serif; line-height: 1.6; color: #1f2937; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA DE NEGOCIO ---

def extraer_datos_inteligente(texto, sujetos_db, cuits_db):
    """Extrae nombre y DNI del texto si la base de datos viene vacía."""
    texto_upper = texto.upper()
    
    # 1. Prioridad: Quiebras
    if "QUIEBRA" in texto_upper:
        match = re.search(r"(?:QUIEBRA DE|FALLIDO:|SOLICITANTE:)\s*([A-ZÁÉÍÓÚÑ\s]{5,60})", texto_upper)
        nombre = match.group(1).split(",")[0].strip() if match else (sujetos_db if sujetos_db else "Sujeto no identificado")
        dni = re.search(r"DNI\s*(\d[\d\s\.]{6,})", texto_upper)
        return f"🚨 QUIEBRA: {nombre}", dni.group(0) if dni else "S/D"

    # 2. Búsqueda de nombres en mayúsculas (General)
    nombres = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{4,}(?:\s+[A-ZÁÉÍÓÚÑ]{3,})+\b', texto)
    blacklist = ["JUZGADO", "SECRETARIA", "BOLETIN", "PROVINCIA", "BUENOS", "AIRES"]
    nombre_limpio = next((n for n in nombres if not any(b in n for b in blacklist)), None)
    
    if nombre_limpio:
        return nombre_limpio, cuits_db if cuits_db else "Ver en texto"
    
    return "Aviso Informativo", ""

def renderizar_titulo_profesional(row):
    """Genera el HTML para el título del expander antes de abrirlo."""
    texto = row["texto_completo"]
    nombre, doc = extraer_datos_inteligente(texto, row.get("sujetos"), row.get("cuit_detectados"))
    
    # Determinar color de badge
    es_quiebra = "QUIEBRA" in texto.upper() or "CONCURSO" in texto.upper()
    clase = "badge-roja" if es_quiebra else "badge-gris"
    label = "QUIEBRA" if es_quiebra else "INFORMATIVO"
    
    # Check de revisado
    revisado = st.session_state.get(f"rev_{row['id']}", False)
    check = "✅" if revisado else "⬜"
    
    return f"{check} <span class='badge {clase}'>{label}</span> <b>{nombre}</b> | {row['localidad']} | <small>{doc}</small>"

# --- CONEXIÓN Y CARGA (Resumida para brevedad) ---
# [Aquí va tu código de conexión a Supabase igual al anterior]
SUPABASE_URL, SUPABASE_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INTERFAZ PRINCIPAL ---
st.title("⚖️ Portal de Fiscalización OSECAC")

# Sidebar con filtros y estadísticas
with st.sidebar:
    st.image("https://www.osecac.org.ar/images/logo-osecac.png", width=150) # Ejemplo
    st.header("Control de Gestión")
    localidad_filtro = st.multiselect("Filtrar Localidad", sorted(LOCALIDADES), default=None)
    st.divider()
    if st.button("🔄 Actualizar Base de Datos", use_container_width=True):
        st.rerun()

# Query con red de seguridad para Quiebras
query = supabase.table("edictos").select("*").order("fecha", desc=True)
response = query.execute()
datos = response.data

if datos:
    df = pd.DataFrame(datos)
    # Filtrado lógico en el DataFrame (más rápido que en query)
    if localidad_filtro:
        # IMPORTANTE: Siempre dejamos las quiebras visibles aunque no sean de la localidad
        df = df[(df['localidad'].isin(localidad_filtro)) | (df['texto_completo'].str.contains('quiebra', case=False))]

    # Agrupar por Boletín
    for (fecha, num), grupo in df.groupby([df['fecha'], 'boletin_numero']):
        st.subheader(f"📅 Boletín N° {num} - {fecha[:10]}")
        
        for _, row in grupo.iterrows():
            eid = row["id"]
            
            # El "Mini Título" profesional
            with st.expander(renderizar_titulo_profesional(row), expanded=False):
                col_txt, col_btn = st.columns([0.8, 0.2])
                
                with col_txt:
                    st.markdown(f"<div class='texto-edicto'>{row['texto_completo']}</div>", unsafe_allow_html=True)
                
                with col_btn:
                    st.write("---")
                    # Botón Revisado
                    if st.checkbox("Marcar Revisado", key=f"rev_{eid}"):
                        st.session_state[f"rev_{eid}"] = True
                    
                    # Botón Eliminar con Doble Validación
                    if st.button("🗑️ Eliminar", key=f"del_{eid}", type="secondary"):
                        st.warning("¿Confirmar?")
                        if st.button("SÍ, ELIMINAR", key=f"conf_{eid}", type="primary"):
                            supabase.table("edictos").delete().eq("id", eid).execute()
                            st.success("Eliminado.")
                            st.rerun()

else:
    st.info("No hay edictos para mostrar con los filtros actuales.")
