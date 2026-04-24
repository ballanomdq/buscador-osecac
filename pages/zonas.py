import folium
import webbrowser
import os

# ============================================================
# COORDENADAS REALES (LAS QUE ME DISTE)
# ============================================================

# Eje Av. Colón
colon_jbjusto = [-38.0068, -57.6083]   # [lat, lon]
colon_güemes  = [-38.0076, -57.5451]
colon_indep   = [-38.0066, -57.5562]
colon_sanluis = [-38.0063, -57.5518]

# Eje Av. Juan B. Justo
jbjusto_catamarca      = [-38.0201, -57.5753]
jbjusto_güemes         = [-38.0315, -57.5471]
jbjusto_polonia        = [-38.0163, -57.5956]
jbjusto_peraltaramos   = [-38.0211, -57.5768]

# Puntos adicionales que me diste antes
punto_centro      = [-38.00093862744996, -57.54161484586379]  # Centro/Costa
punto_champagnat  = [-37.980243861788324, -57.58254961283819] # Rotonda Champagnat

# ============================================================
# CREAR MAPA BASE - USANDO CARTODB (NO SE VE EN BLANCO)
# ============================================================
lat_centro = (colon_güemes[0] + punto_centro[0]) / 2
lon_centro = (colon_güemes[1] + punto_centro[1]) / 2

# USO 'CartoDB positron' en lugar de OpenStreetMap para evitar pantalla en blanco
mapa = folium.Map(
    location=[lat_centro, lon_centro],
    zoom_start=13,
    tiles='CartoDB positron',  # <--- ESTO SOLUCIONA EL MAPA EN BLANCO
    control_scale=True
)

# ============================================================
# FUNCIÓN PARA DIBUJAR ZONAS (POLÍGONOS)
# ============================================================
def agregar_zona(mapa, vertices, inspector, zona, color, opacidad=0.4):
    """vertices: lista de [lat, lon]"""
    folium.Polygon(
        locations=vertices,
        color=color,
        weight=2,
        fill=True,
        fill_opacity=opacidad,
        popup=f"<b>{inspector}</b><br>{zona}",
        tooltip=f"{inspector} - {zona}"
    ).add_to(mapa)

# ============================================================
# DEFINIR POLÍGONOS - USANDO TUS COORDENADAS COMO REFERENCIA
# ============================================================

# RODRIGUEZ - Zona Güemes (Este, cerca del mar)
rodriguez_zona1 = [
    colon_güemes,           # Noroeste
    [-38.0076, -57.5400],   # Noreste (hacia el mar)
    [-38.0200, -57.5400],   # Sureste
    [-38.0200, -57.5471],   # Suroeste (cerca J.B. Justo)
    colon_güemes
]

# GARCÍA - Zona Microcentro
garcia_zona3 = [
    colon_indep,            # Noroeste
    colon_sanluis,          # Noreste
    [-38.0120, -57.5518],   # Sureste
    [-38.0120, -57.5562],   # Suroeste
    colon_indep
]

# CARBAYO - Zona Microcentro (Independencia)
carbayo_zona2 = [
    colon_indep,            # Noreste
    [-38.0066, -57.5620],   # Noroeste
    [-38.0130, -57.5620],   # Suroeste
    [-38.0130, -57.5562],   # Sureste
    colon_indep
]

# LOPEZ - Zona Centro (Plaza Mitre)
lopez_zona1 = [
    colon_sanluis,          # Noreste
    [-38.0063, -57.5580],   # Noroeste
    [-38.0140, -57.5580],   # Suroeste
    [-38.0140, -57.5518],   # Sureste
    colon_sanluis
]

# POLINESSI - Zona Champagnat (Noroeste)
polinessi_zona1 = [
    punto_champagnat,                       # Centro de la zona
    [punto_champagnat[0] + 0.015, punto_champagnat[1] - 0.015],
    [punto_champagnat[0] - 0.005, punto_champagnat[1] + 0.010],
    [punto_champagnat[0] - 0.008, punto_champagnat[1] - 0.008],
    punto_champagnat
]

# ============================================================
# AGREGAR TODAS LAS ZONAS AL MAPA
# ============================================================
agregar_zona(mapa, rodriguez_zona1, 
             "RODRIGUEZ, Maximiliano (Leg. 7713)", 
             "Zona 1 - Sector Güemes", "red", 0.35)

agregar_zona(mapa, garcia_zona3,
             "GARCÍA, Juan Paulo (Leg. 7852)",
             "Zona 3 - Microcentro / San Juan", "orange", 0.35)

agregar_zona(mapa, carbayo_zona2,
             "CARBAYO, Víctor Hugo (Leg. 9220)",
             "Zona 2 - Microcentro (Independencia)", "yellow", 0.35)

agregar_zona(mapa, lopez_zona1,
             "LOPEZ, Martín Leonardo (Leg. 9983)",
             "Zona 1 - Centro (Plaza Mitre)", "green", 0.35)

agregar_zona(mapa, polinessi_zona1,
             "POLINESSI, Juan José (Leg. 9513)",
             "Zona 1 - Noroeste (Champagnat)", "blue", 0.35)

# ============================================================
# MARCAR TODAS LAS INTERSECCIONES DE REFERENCIA
# ============================================================
puntos = {
    "Colón + J.B. Justo": colon_jbjusto,
    "Colón + Güemes": colon_güemes,
    "Colón + Independencia": colon_indep,
    "Colón + San Luis": colon_sanluis,
    "J.B. Justo + Catamarca": jbjusto_catamarca,
    "J.B. Justo + Güemes": jbjusto_güemes,
    "J.B. Justo + Polonia": jbjusto_polonia,
    "J.B. Justo + Peralta Ramos": jbjusto_peraltaramos,
    "Centro/Costa (ref)": punto_centro,
    "Champagnat (ref)": punto_champagnat
}

for nombre, coord in puntos.items():
    folium.Marker(
        coord,
        popup=nombre,
        icon=folium.Icon(color='gray', icon='info-sign', prefix='fa')
    ).add_to(mapa)

# ============================================================
# AGREGAR CAPAS DE CONTROL (para activar/desactivar zonas)
# ============================================================
folium.LayerControl().add_to(mapa)

# ============================================================
# GUARDAR Y ABRIR
# ============================================================
archivo = "mar_del_plata_inspectores.html"
mapa.save(archivo)
webbrowser.open('file://' + os.path.realpath(archivo))

print("=" * 60)
print("✅ MAPA GENERADO EXITOSAMENTE")
print("=" * 60)
print(f"📂 Archivo guardado: {archivo}")
print("🌐 Se abrió automáticamente en tu navegador")
print("\n📌 INSTRUCCIONES:")
print("   - Podés hacer zoom y moverte por el mapa")
print("   - Las zonas tienen diferentes colores por inspector")
print("   - Hacé clic en una zona para ver detalles")
print("   - Usá el control de capas (esquina superior derecha)")
print("=" * 60)
