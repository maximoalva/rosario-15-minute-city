import streamlit as st
import geopandas as gpd
from pathlib import Path
from src import cargar_nodos

# Configuración de la página
st.set_page_config(
    page_title="Rosario 15 Minute City",
    layout="wide"
)

# Carga de datos con caché
nodos = cargar_nodos()