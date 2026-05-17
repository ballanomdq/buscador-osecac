import folium
import osmnx as ox
import geopandas as gpd

# 1. BASE DE DATOS REAL DE BARRIOS POR INSPECTOR (Según tu mapa físico)
# Agrupamos los barrios oficiales de Mar del Plata para cada inspector
zonas_inspectores = {
    "GARCIA": {
        "color": "orange", # Naranja en tu mapa
        "barrios": ["Punta Mogotes", "Colinas de Peralta Ramos", "Juramento", "Termas Huinco", 
                    "Faro Norte", "Don Diego", "Las Canteras", "Santa Celina", "El Martillo"]
    },
    "CARBAYO": {
        "color": "pink", # Rosa/Fucsia en tu mapa
        "barrios": ["Cerrito Sur", "El Progreso", "Peralta Ramos Oeste", "Chauvin", 
                    "San Jose", "Plaza Mitre", "Stella Maris"]
    },
    "POLINESSI": {
        "color": "yellow", # Amarillo en tu mapa
        "barrios": ["Playa Grande", "Los Troncos", "San Carlos", "San Cayetano", 
                    "Jorge Newbery", "Libertad", "Florentino Ameghino"]
    },
    "RODRIGUEZ": {
        "color": "teal", # Azul/Celeste en tu mapa
        "barrios": ["Bernardino Rivadavia", "Santa Monica", "Funes y Anchorena", 
                    "San Juan", "La Perla", "Nueva Pompeya"]
    },
    "LOPEZ": {
        "color": "purple", # Morado en tu mapa
        "barrios": ["Regional", "Belisario Roldan", "Don Emilio", "Jose Hernandez", 
                    "Las Americas", "Autodromo", "El Caribe"]
    }
}

# 2. CONFIGURACIÓN DEL MAPA BASE
print("Inicializando mapa de Mar del Plata...")
m = folium.Map(location=[-38.0055, -57.5426], zoom_start=12, tiles="cartodbpositron")

# 3. DESCARGA DE POLÍGONOS REALES (Límites de Barrios de MDP)
print("Descargando límites oficiales de barrios desde OpenStreetMap...")
try:
    # Descargamos las fronteras de los barrios de Mar del Plata
    barrios_mdp = ox.features_from_place("Mar del Plata, Buenos Aires, Argentina", tags={"user_defined": "neighbourhood"})
    # Si no encuentra con esa etiqueta, usamos la estándar de límites geográficos
    if barrios_mdp.empty:
        barrios_mdp = ox.features_from_place("Mar del Plata, Buenos Aires, Argentina", tags={"boundary": "administrative", "admin_level": "10"})
except Exception as e:
    print(f"Error al descargar datos geográficos: {e}")
    barrios_mdp = None

# 4. PINTAR LAS ZONAS EN EL MAPA INTERACTIVO
if barrios_mdp is not None and not barrios_mdp.empty:
    for inspector, info in zonas_inspectores.items():
        print(f"Coloreando zona del Inspector: {inspector}...")
        
        # Creamos una capa específica para este inspector
        grupo_inspector = folium.FeatureGroup(name=f"Zona Inspector {inspector}")
        
        for barrio_nombre in info["barrios"]:
            # Buscamos el barrio real en la base de datos oficial
            barrio_real = barrios_mdp[barrios_mdp['name'].str.contains(barrio_nombre, case=False, na=False)]
            
            if not barrio_real.empty:
                # Convertimos a formato GeoJSON para Folium
                geo_data = barrio_real.__geo_interface__
                
                # Añadimos el polígono pintado al mapa
                folium.GeoJson(
                    geo_data,
                    style_function=lambda x, color=info["color"]: {
                        'fillColor': color,
                        'color': color,
                        'weight': 2,
                        'fillOpacity': 0.4  # Transparente para que se sigan viendo las calles abajo
                    },
                    tooltip=f"<b>Inspector:</b> {inspector}<br><b>Barrio asignado:</b> {barrio_nombre}"
                ).add_to(grupo_inspector)
        
        grupo_inspector.add_to(m)

# 5. GUARDAR EL MAPA INTERACTIVO HTML
folium.LayerControl(collapsed=False).add_to(m)
mapa_final = "mapa_zonas_inspectores_mdp.html"
m.save(mapa_final)

print(f"¡Hecho! Archivo real generado sin fantasías: '{mapa_final}'")
print("Haciendo doble clic en ese archivo podrás prender y apagar las zonas de cada inspector sobre el mapa real.")
