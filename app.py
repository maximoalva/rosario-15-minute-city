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

# --- CONFIGURACIÓN DE LA VISTA ACTUAL ---
if seleccion == "Todos los servicios":
    columna_activa = "score_15min"
    es_global = True
else:
    # Reconstruimos el nombre de la columna (ej: "Minutos a: Salud" -> "time_salud")
    nombre_cat = seleccion.replace("Minutos a: ", "").lower().replace(" ", "_")
    columna_activa = f"time_{nombre_cat}"
    es_global = False

# --- LÓGICA DEL HEATMAP (GRADIENTES DE COLOR) ---
def calcular_color(val, es_score_global):
    # Si es NaN o está a más de media hora, lo pintamos Rojo Oscuro
    if pd.isna(val) or val > 30: 
        return [215, 48, 39, 255] 
        
    if es_score_global:
        # GLOBAL (0 a 8): Interpolamos de Rojo (0) a Verde (8)
        factor = val / 8
        r = int(215 - factor * (215 - 26))
        g = int(48 + factor * (152 - 48))
        b = int(39 + factor * (80 - 39))
        return [r, g, b, 255]
    else:
        # INDIVIDUAL: 0 min (Verde) -> 15 min (Blanco) -> >15 min (Rojo)
        if val <= 15:
            # Interpolamos de Verde a Blanco
            factor = val / 15
            r = int(26 + factor * (255 - 26))
            g = int(152 + factor * (255 - 152))
            b = int(80 + factor * (255 - 80))
            return [r, g, b, 255]
        else:
            # Interpolamos de Blanco a Rojo
            factor = min((val - 15) / 15, 1.0) # Tope en 30 min (factor 1.0)
            r = int(255 - factor * (255 - 215))
            g = int(255 - factor * (255 - 48))
            b = int(255 - factor * (255 - 39))
            return [r, g, b, 255]

# Trabajamos sobre una copia para no ensuciar la caché
df_mapa = calles.copy()

# Aplicamos los colores al vuelo
df_mapa['color'] = df_mapa[columna_activa].apply(lambda x: calcular_color(x, es_global))

# TRUCO VITAL PARA PYDECK: Tiramos la columna 'geometry' nativa y lo pasamos a un DataFrame estándar 
# (PyDeck usa nuestra nueva columna 'path', la geometría de GeoPandas lo confunde)
df_mapa = pd.DataFrame(df_mapa.drop(columns=['geometry']))

# --- INTERFAZ PRINCIPAL ---
st.title("🏙️ La Ciudad de 15 Minutos - Rosario")

if es_global:
    st.markdown(f"**Visualizando:** Puntaje Global (Calles Verdes = Tienen acceso a todos los servicios en <15 min)")
else:
    st.markdown(f"**Visualizando:** {seleccion} (Verde = Cerca, Blanco = 15 min, Rojo = Lejos)")

# --- MAPA 2D PYDECK ---
capa_calles = pdk.Layer(
    "PathLayer",
    data=df_mapa,
    get_path="path",
    get_color="color",
    get_width=15,          # Ancho de la calle en metros (importante para que se vea)
    width_min_pixels=2,    # Ancho mínimo en píxeles (para que no desaparezca al alejar)
    pickable=True,
    auto_highlight=True    # Brilla al pasar el mouse
)

vista_inicial = pdk.ViewState(
    latitude=-32.9468,
    longitude=-60.6393,
    zoom=12.5,
    pitch=0
)

# Tooltip dinámico que muestra el valor exacto de la calle que tocás
etiqueta = "Categorías cubiertas" if es_global else "Minutos de caminata"
mapa = pdk.Deck(
    layers=[capa_calles],
    initial_view_state=vista_inicial,
    map_style='road',
    tooltip={"text": f"{etiqueta}: {{{columna_activa}}}"},
    height=700
)

st.pydeck_chart(mapa)