import geopandas as gpd
import streamlit as st
from pathlib import Path

@st.cache_data(show_spinner="Cargando red de accesibilidad...")
def cargar_nodos() -> gpd.GeoDataFrame:
    """
    Carga el GeoJSON de nodos, proyecta las geometrías a WGS84
    y extrae sus coordenadas.
    
    La función se almacena en caché de Streamlit para evitar lecturas 
    repetitivas en disco durante la recarga interactiva de la app.

    Returns:
        gpd.GeoDataFrame: DataFrame espacial que contiene las esquinas 
        procesadas, incluyendo sus scores de tiempos y las nuevas 
        columnas 'lon' y 'lat' requeridas por PyDeck.
        
    Raises:
        FileNotFoundError: Si el archivo procesado no existe en el directorio de datos.
    
    """
    ruta = Path("data/processed/nodos_accesibilidad.geojson")
    
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo en: {ruta}.")
    
    # Leemos el archivo
    gdf = gpd.read_file(ruta)
    
    # Proyectamos a Lat/Lon (EPSG:4326) estándar de mapas web
    gdf = gdf.to_crs(epsg=4326)
    
    # Extraemos coordenadas para PyDeck
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y
    
    return gdf