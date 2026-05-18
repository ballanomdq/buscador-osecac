import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# Creamos el mapa directamente con código HTML y Leaflet estándar de internet
# Esto corre en el navegador del usuario, el servidor de Streamlit ni se entera
html_mapa = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com" />
    <script src="https://unpkg.com"></script>
    <style>
        #map { height: 550px; width: 100%; margin: 0; padding: 0; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Centrar en Mar del Plata
        var map = L.map('map').setView([-38.0055, -57.5426], 12);
        
        L.tileLayer('https://{s}://{z}/{x}/{y}{r}.png', {
            attribution: 'OpenStreetMap'
        }).addTo(map);

        // 1. ZONA GARCIA (Naranja)
        var garcia = L.polygon([
            [-38.0315, -57.5450], [-38.0550, -57.5350], [-38.0850, -57.5450], 
            [-38.0750, -57.5850], [-38.0450, -57.5950]
        ], {color: '#ff7f0e', fillColor: '#ff7f0e', fillOpacity: 0.4, weight: 3}).addTo(map);
        garcia.bindPopup("<b>Inspector:</b> GARCIA<br><b>Zonas:</b> Punta Mogotes, Colinas, Juramento, Faro Norte.");

        // 2. ZONA CARBAYO (Rosa)
        var carbayo = L.polygon([
            [-38.0050, -57.5420], [-38.0250, -57.5300], [-38.0450, -57.5500], 
            [-38.0350, -57.5750], [-38.0100, -57.5650]
        ], {color: '#e377c2', fillColor: '#e377c2', fillOpacity: 0.4, weight: 3}).addTo(map);
        carbayo.bindPopup("<b>Inspector:</b> CARBAYO<br><b>Zonas:</b> Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris.");

        // 3. ZONA POLINESSI (Amarillo)
        var polinessi = L.polygon([
            [-37.9750, -57.5450], [-38.0050, -57.5350], [-38.0150, -57.5750], 
            [-37.9850, -57.5950], [-37.9650, -57.5750]
        ], {color: '#bcbd22', fillColor: '#bcbd22', fillOpacity: 0.4, weight: 3}).addTo(map);
        polinessi.bindPopup("<b>Inspector:</b> POLINESSI<br><b>Zonas:</b> Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad.");

        // 4. ZONA RODRIGUEZ (Azul)
        var rodriguez = L.polygon([
            [-37.9950, -57.5550], [-38.0150, -57.5500], [-38.0250, -57.5850], 
            [-38.0050, -57.5990]
        ], {color: '#1f77b4', fillColor: '#1f77b4', fillOpacity: 0.4, weight: 3}).addTo(map);
        rodriguez.bindPopup("<b>Inspector:</b> RODRIGUEZ<br><b>Zonas:</b> Bernardino Rivadavia, Santa Mónica, San Juan, La Perla.");

        // 5. ZONA LOPEZ (Morado)
        var lopez = L.polygon([
            [-38.0150, -57.5850], [-38.0350, -57.5750], [-38.0550, -57.6150], 
            [-38.0250, -57.6350]
        ], {color: '#9467bd', fillColor: '#9467bd', fillOpacity: 0.4, weight: 3}).addTo(map);
        lopez.bindPopup("<b>Inspector:</b> LOPEZ<br><b>Zonas:</b> Regional, Belisario Roldán, Don Emilio, Las Américas.");

    </script>
</body>
</html>
"""

# Renderizamos el mapa usando el componente nativo de Streamlit
components.html(html_mapa, height=570)

# Panel de información complementario
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
st.markdown("🟢 **Inspector GARCIA**: Punta Mogotes, Colinas, Juramento, Faro Norte.")
st.markdown("🟢 **Inspector CARBAYO**: Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris.")
st.markdown("🟢 **Inspector POLINESSI**: Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad.")
st.markdown("🟢 **Inspector RODRIGUEZ**: Bernardino Rivadavia, Santa Mónica, San Juan, La Perla.")
st.markdown("🟢 **Inspector LOPEZ**: Regional, Belisario Roldán, Don Emilio, Las Américas.")
