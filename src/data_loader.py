import geopandas as gpd
import streamlit as st
from pathlib import Path

def extract_coords(geom) -> list:
    """
    Convierte geometrías lineales de Shapely al formato de lista anidada requerido por PyDeck.

    Args:
        geom (shapely.geometry.base.BaseGeometry): Geometría espacial de la calle.

    Returns:
        list: Lista anidada de coordenadas [[lon1, lat1], [lon2, lat2], ...]. 
              Retorna una lista vacía si la geometría no es lineal o es inválida.
    """
    if geom.geom_type == 'LineString':
        return [list(c) for c in geom.coords]
    elif geom.geom_type == 'MultiLineString':
        return [list(c) for c in geom.geoms[0].coords]
    
    return []

@st.cache_data(show_spinner="Cargando red de accesibilidad...")
def cargar_calles() -> gpd.GeoDataFrame:
    """
    Carga la red de calles, proyecta las geometrías a WGS84
    y prepara la estructura de datos para el frontend.
    
    La función se almacena en caché de Streamlit para evitar lecturas 
    repetitivas en disco durante la recarga interactiva de la app.

    Returns:
        gpd.GeoDataFrame: Dataframe espacial de las calles con sus respectivos 
        scores de accesibilidad y una nueva columna 'path' lista para ser consumida
        por el PathLayer de PyDeck.
        
    Raises:
        FileNotFoundError: Si el archivo procesado no existe en el directorio de datos.
    
    """
    ruta = Path("data/processed/calles.geojson")
    
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo en: {ruta}.")
    
    # Leemos el archivo y lo proyectamos a EPSG:4326 estándar de mapas web
    gdf = gpd.read_file(ruta)
    gdf = gdf.to_crs(epsg=4326)
    
    # Extraemos geometría en formato de lista para el PathLayer de PyDeck
    gdf['path'] = gdf.geometry.apply(extract_coords)
    
    return gdf