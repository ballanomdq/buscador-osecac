import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import time
import re

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS PROFESIONALES
st.set_page_config(page_title="Fiscalización OSECAC", layout="wide")

st.markdown("""
<style>
    /* Contenedor del edicto */
    .stExpander { border: 1px solid #d1d5db; border-radius: 10px; margin-bottom: 10px; transition: 0.3s; }
    .stExpander:hover { border-color: #3b82f6; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05); }
    
    /* Badges de alerta */
    .badge { padding: 4px 10px; border-radius: 6px; color: white; font-weight: bold; font-size: 0.75rem; margin-right: 10px; text-transform: uppercase; }
    .badge-roja { background-color: #ef4444; } /* Quiebras */
    .badge-gris { background-color: #6b7280; } /* Informativos */
    
    /* Texto del edicto */
    .texto-edicto { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        font-size: 1.1rem; 
        line-height: 1.6; 
        color: #1f2937; 
        background: #ffffff; 
        padding: 20px; 
        border-radius: 8px;
        border: 1px solid #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

# 2. LISTA DE LOCALIDADES (Para evitar el NameError)
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

# 3. CONEXIÓN A SUPABASE
def conectar_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Error: No se encontraron las credenciales 'SUPABASE_URL' y 'SUPABASE_KEY' en los Secrets.")
        st.stop()

supabase = conectar_supabase()

# 4. CEREBRO DE EXTRACCIÓN (Detecta nombres y quiebras en el texto)
def extraer_info_titulo(texto, sujetos_db):
    texto_upper = texto.upper()
    
    # Prioridad 1: Quiebras/Concursos
    if any(p in texto_upper for p in ["QUIEBRA", "CONCURSO"]):
        # Intentar extraer nombre del fallido
        match = re.search(r"(?:QUIEBRA DE|FALLIDO:|DECLARED THE BANKRUPTCY OF|CONTRA)\s*([A-ZÁÉÍÓÚÑ\s]{5,60})", texto_upper)
        nombre = match.group(1).split(",")[0].strip() if match else (sujetos_db if sujetos_db else "SUJETO NO IDENTIFICADO")
        # Intentar extraer DNI
        dni = re.search(r"DNI\s*(\d[\d\s\.]{6,})", texto_upper)
        doc = f" | DNI: {dni.group(1).strip()}" if dni else ""
        return f"🚨 QUIEBRA: {nombre}{doc}", "badge-roja"

    # Prioridad 2: Nombres genéricos (Sucesiones, Citaciones)
    nombres_mayus = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{4,}(?:\s+[A-ZÁÉÍÓÚÑ]{3,})+\b', texto)
    blacklist = ["JUZGADO", "SECRETARIA", "BOLETIN", "PROVINCIA", "BUENOS", "AIRES", "DEPARTAMENTO", "JUDICIAL"]
    nombre_limpio = next((n for n in nombres_mayus if not any(b in n for b in blacklist)), "Aviso Informativo")
    
    return nombre_limpio, "badge-gris"

# 5. INTERFAZ Y FILTROS
st.title("⚖️ Fiscalización Profesional OSECAC")

with st.sidebar:
    st.header("Configuración")
    localidad_filtro = st.multiselect("Filtrar por Localidad", sorted(LOCALIDADES), default=None)
    st.divider()
    st.info("💡 Las quiebras detectadas aparecerán siempre en tu lista, aunque no selecciones su localidad.")

# 6. CARGA Y PROCESAMIENTO DE DATOS
response = supabase.table("edictos").select("*").order("fecha", desc=True).execute()
datos = response.data

if datos:
    df = pd.DataFrame(datos)
    
    # Filtro Inteligente: Localidades elegidas + Cualquier cosa que diga "quiebra"
    if localidad_filtro:
        mask = (df['localidad'].isin(localidad_filtro)) | (df['texto_completo'].str.contains('quiebra', case=False))
        df = df[mask]

    # Agrupar por Boletín para organizar la vista
    for (fecha, num), grupo in df.groupby([df['fecha'], 'boletin_numero']):
        st.subheader(f"📅 Boletín N° {num} — {fecha[:10]}")
        
        for _, row in grupo.iterrows():
            eid = row["id"]
            texto = row["texto_completo"]
            sujetos = row.get("sujetos")
            
            # Generar título dinámico
            nombre_display, clase_badge = extraer_info_titulo(texto, sujetos)
            label_localidad = row["localidad"]
            
            # Renderizar el expander con el título profesional
            titulo_html = f"<span class='badge {clase_alerta}'>{label_localidad}</span> <b>{nombre_display}</b>"
            
            # Fallback si falla la variable por algún motivo en el bucle
            clase_alerta = clase_badge 

            with st.expander(f"{label_localidad} | {nombre_display}", expanded=False):
                col_texto, col_acciones = st.columns([0.8, 0.2])
                
                with col_texto:
                    st.markdown(f"<div class='texto-edicto'>{texto}</div>", unsafe_allow_html=True)
                
                with col_acciones:
                    st.write("**Gestión**")
                    revisado = st.checkbox("Revisado", key=f"rev_{eid}")
                    
                    if st.button("🗑️ Eliminar", key=f"del_{eid}"):
                        st.error("¿Confirmar eliminación?")
                        if st.button("SÍ, BORRAR DEFINITIVAMENTE", key=f"conf_{eid}"):
                            supabase.table("edictos").delete().eq("id", eid).execute()
                            st.success("Eliminado")
                            st.rerun()
else:
    st.warning("No se encontraron edictos en la base de datos.")
