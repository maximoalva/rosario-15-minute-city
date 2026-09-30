import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
from pathlib import Path
from src import cargar_calles

# Configuración de la página
st.set_page_config(page_title="Rosario 15 Minute City", page_icon="🏙️", layout="wide")

# Carga de datos con caché
calles = cargar_calles()

# Barra lateral
st.sidebar.title("Filtros de accesibilidad")

# Lista de opciones (radio)
opciones = ["Todos los servicios"]

columnas_time = [c for c in calles.columns if c.startswith("time_")]
for col in columnas_time:
    opciones.append(f"{col.replace("time_", "").replace("_", " ").capitalize()}")

seleccion = st.sidebar.radio("¿Qué querés visualizar?", opciones)