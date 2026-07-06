import streamlit as st
import requests
import pandas as pd
import os
from utils.paths import IMAGES, CSS
from utils.messages import obtener_bienvenida
from components.dashboard import mostrar_dashboard
from components.welcome import mostrar_bienvenida
from utils.special_dates import obtener_fecha_especial
from utils.recuerdos import (
    imagen_a_base64,
    obtener_recuerdo_por_indice,
)


st.set_page_config(
    page_title="JulyVerse",
    page_icon="💜",
    layout="wide"
)

# Muestra la notificación animada si hay un mensaje pendiente
if 'mensaje_toast' in st.session_state:
    st.toast(st.session_state.mensaje_toast, icon="✨")
    del st.session_state.mensaje_toast

def cargar_css():
    with open(CSS / "style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()


# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🐻 Tata")
    st.caption("Compañero oficial de JulyVerse 💜")
    st.write(
    "Estoy aquí para acompañarte mientras descubres nuevas historias."
    )
    try:
        st.image(IMAGES / "ui" / "tata.png")
    except:
        st.info("💡 Guarda una foto como 'taehyung.jpg' en tu carpeta para que aparezca aquí.")

if "bienvenida_actual" not in st.session_state:
    st.session_state.bienvenida_actual = obtener_bienvenida()

saludo, mensaje = st.session_state.bienvenida_actual

mostrar_bienvenida(
    saludo,
    mensaje
)

fecha_especial = obtener_fecha_especial()

if fecha_especial:
    titulo_fecha, mensaje_fecha = fecha_especial

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,.55);
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,.35);
            backdrop-filter: blur(10px);
        ">
            <h3>{titulo_fecha}</h3>
            <p style="font-size:17px;">{mensaje_fecha}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- MEMORIA DE LA APLICACIÓN (SESSION STATE) ---
if 'pagina_catalogo' not in st.session_state:
    st.session_state.pagina_catalogo = 1

# --- NUEVO: Memoria para las fotos personalizadas ---
if 'imagenes_asignadas' not in st.session_state:
    st.session_state.imagenes_asignadas = {}
if 'contador_fotos' not in st.session_state:
    st.session_state.contador_fotos = 0
# --- NUEVO: Memoria para guardar los resultados de búsqueda ---
if 'resultados_busqueda' not in st.session_state:
    st.session_state.resultados_busqueda = []

def reset_pagina():
    # Si ella cambia de género, regresamos a la página 1
    st.session_state.pagina_catalogo = 1

# Códigos oficiales de géneros de TV en TMDB
GENEROS_TMDB = {
    "Todos": "",
    "Drama / Romance": "18",
    "Comedia": "35",
    "Acción y Aventura": "10759",
    "Misterio": "9648",
    "Fantasía / Sci-Fi": "10765",
    "Crimen": "80"
}

# --- CONFIGURACIÓN DE LA API ---
API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"
IMG_URL_SMALL = "https://image.tmdb.org/t/p/w200" # URL para las miniaturas
ARCHIVO_CSV = "mis_kdramas.csv"

# --- MANEJO DE DATOS ---
def cargar_vistos():
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        # Parche de seguridad: si el archivo existe pero es la versión vieja,
        # le agrega la columna 'poster' vacía automáticamente para que no falle.
        if 'poster' not in df.columns:
            df['poster'] = ""
        return df
    
    # Si de plano no existe, crea la estructura desde cero con las 3 columnas
    return pd.DataFrame(columns=["id", "titulo", "poster"])
def actualizar_visto(id_kdrama, titulo, poster, visto):
    df = cargar_vistos()

    # Aseguramos que el ID siempre sea número
    id_kdrama = int(id_kdrama)

    if not df.empty:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)

    if visto:
        if id_kdrama not in df["id"].values:
            nuevo_registro = pd.DataFrame({
                "id": [id_kdrama],
                "titulo": [titulo],
                "poster": [poster]
            })

            df = pd.concat([df, nuevo_registro], ignore_index=True)

    else:
        df = df[df["id"] != id_kdrama]

        # Si ya no queda ningún KDrama, dejamos el CSV vacío pero con columnas
        if df.empty:
            df = pd.DataFrame(columns=["id", "titulo", "poster"])

    df.to_csv(ARCHIVO_CSV, index=False)
def limpiar_estado_drama(id_kdrama):
    id_kdrama = int(float(id_kdrama))

    version_key = f"version_drama_{id_kdrama}"

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    st.session_state[version_key] += 1

def obtener_key_checkbox(prefijo_key, id_kdrama):
    id_kdrama = int(float(id_kdrama))
    version = st.session_state.get(f"version_drama_{id_kdrama}", 0)

    return f"{prefijo_key}_{id_kdrama}_{version}"


df_vistos = cargar_vistos()
lista_vistos_ids = df_vistos['id'].tolist() if not df_vistos.empty else []
mostrar_dashboard(
    vistos=len(lista_vistos_ids)
)

# --- CONSULTAS A TMDB ---
@st.cache_data(show_spinner=False)
def obtener_kdramas_populares(limite_paginas, id_genero):
    resultados_totales = []

    for p in range(1, limite_paginas + 1):
        url = f"{BASE_URL}/discover/tv"

        parametros = {
            "api_key": API_KEY,
            "with_origin_country": "KR",
            "sort_by": "popularity.desc",
            "language": "es-MX",
            "page": p
        }

        if id_genero:
            parametros["with_genres"] = id_genero

        try:
            respuesta = requests.get(url, params=parametros, timeout=10)
            respuesta.raise_for_status()

            datos = respuesta.json()
            resultados_totales.extend(datos.get("results", []))

        except requests.exceptions.RequestException as error:
            st.error("No pude conectar con TMDB. Revisa tu internet o intenta de nuevo en unos minutos.")
            st.caption(f"Detalle técnico: {error}")
            return []

    return resultados_totales

def buscar_kdrama(query):
    url = f"{BASE_URL}/search/tv"

    parametros = {
        "api_key": API_KEY,
        "query": query,
        "language": "es-MX"
    }

    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status()

        return respuesta.json().get("results", [])

    except requests.exceptions.RequestException as error:
        st.error("No pude realizar la búsqueda en TMDB. Intenta de nuevo en unos minutos.")
        st.caption(f"Detalle técnico: {error}")
        return []

# Lista de tus fotos personalizadas


def mostrar_tarjeta(drama, prefijo_key):
    poster_path = drama.get('poster_path') or ''
    id_drama = int(drama["id"])
    
    if poster_path:
        url_imagen = IMG_URL + poster_path
    else:
        # LÓGICA DE ROTACIÓN SEGURA:
        # Si esta serie no tiene foto asignada en la memoria, le damos la siguiente en la lista
        if id_drama not in st.session_state.imagenes_asignadas:
            foto_elegida = obtener_recuerdo_por_indice(
                st.session_state.contador_fotos
            )
            st.session_state.imagenes_asignadas[id_drama] = foto_elegida
            st.session_state.contador_fotos += 1 # Avanzamos el contador para la próxima serie sin póster
            
        # Recuperamos la foto que se le asignó para que no cambie de golpe al hacer clic
        foto_definitiva = st.session_state.imagenes_asignadas[id_drama]
        
        img_b64 = imagen_a_base64(foto_definitiva)
        url_imagen = (
            f"data:image/jpeg;base64,{img_b64}"
            if img_b64
            else "https://placehold.co/500x750/d8b4e2/4a044e.png?text=JulyVerse"
        )   

    # HTML con altura fija de 450px y object-fit: contain
    st.markdown(f'''
        <div style="height: 450px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <img src="{url_imagen}"
                style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;">
        </div>
    ''', unsafe_allow_html=True)
    if not poster_path:
        st.caption("💜 No encontré el póster... Pero encontré un bonito recuerdo.")
    titulo = drama.get('name', 'Sin título')
    st.write(f"**{titulo}**")
    
    ya_visto = id_drama in lista_vistos_ids
    key_checkbox = obtener_key_checkbox(prefijo_key, id_drama)

    visto_ahora = st.checkbox(
        "Ya lo vi",
        value=ya_visto,
        key=key_checkbox
    )
    
    if visto_ahora != ya_visto:
        actualizar_visto(id_drama, titulo, poster_path, visto_ahora)
        if visto_ahora:
            st.session_state.mensaje_toast = f"¡Guardaste '{titulo}' en tu lista! 💜"
        st.rerun()
# --- SISTEMA DE PESTAÑAS (TABS) ---
tab_catalogo, tab_buscar, tab_lista = st.tabs(["📺 Catálogo", "🔍 Buscar Serie", "✨ Mis KDramas Vistos"])

# PESTAÑA 1: CATÁLOGO POPULAR
with tab_catalogo:
    col_titulo, col_filtro = st.columns([2, 1])
    with col_titulo:
        st.subheader("Lo más popular del momento")
    with col_filtro:
        # Menú desplegable para los géneros
        genero_seleccionado = st.selectbox(
            "Filtrar por género:", 
            list(GENEROS_TMDB.keys()), 
            on_change=reset_pagina
        )
    
    # Traducimos el texto seleccionado a su ID numérico
    id_genero_filtro = GENEROS_TMDB[genero_seleccionado]
    
    # Llamamos a la API con la página actual y el género
    kdramas = obtener_kdramas_populares(st.session_state.pagina_catalogo, id_genero_filtro)
    
    columnas = st.columns(4) 
    for indice, drama in enumerate(kdramas):
        with columnas[indice % 4]:
            mostrar_tarjeta(drama, "cat")
            
    st.divider()
    
    # Botón mágico para cargar 20 más
    col_espacio1, col_boton, col_espacio2 = st.columns([1, 1, 1])
    with col_boton:
        if st.button("➕ Cargar más KDramas", use_container_width=True):
            st.session_state.pagina_catalogo += 1
            st.rerun()
# PESTAÑA 2: BUSCADOR
# PESTAÑA 2: BUSCADOR MEJORADO (CON FORMULARIO)
with tab_buscar:
    st.subheader("Encuentra una serie específica")
    
    # Creamos un formulario que agrupa la caja de texto y el botón
    with st.form(key='formulario_busqueda', clear_on_submit=False):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            busqueda = st.text_input("Escribe el nombre de la serie:", label_visibility="collapsed")
        with col_btn:
            # Al estar dentro del form, el botón se activa automáticamente con Enter
            submit_button = st.form_submit_button(label="🔍 Buscar", use_container_width=True)
            
        if submit_button:
            if busqueda:
                st.session_state.resultados_busqueda = buscar_kdrama(busqueda)
            else:
                st.session_state.resultados_busqueda = []
                st.warning("Por favor, escribe un nombre.")

    # Mostramos los resultados
    if st.session_state.resultados_busqueda:
        cols_busqueda = st.columns(4)
        for idx, res in enumerate(st.session_state.resultados_busqueda):
            with cols_busqueda[idx % 4]:
                mostrar_tarjeta(res, "bus")
    elif not st.session_state.resultados_busqueda and "busqueda" in locals() and busqueda:
        st.info("No se encontraron resultados.")

# PESTAÑA 3: LISTA PERSONAL CON MINIATURAS Y BOTÓN PARA QUITAR
with tab_lista:
    st.subheader("Tu historial de series terminadas")
    
    # Recargamos los datos para tener la información fresca
    df_vistos_actualizado = cargar_vistos()
    
    if not df_vistos_actualizado.empty:
        for i, row in df_vistos_actualizado.iterrows():
            # Dividimos en 3 espacios: Imagen, Texto, Casilla
            id_drama_lista = int(row["id"])
            col_img, col_txt, col_check = st.columns([1, 8, 2])
            
            with col_img:
                if pd.notna(row['poster']) and row['poster']:
                    st.image(IMG_URL_SMALL + row['poster'], width=60)
            
            with col_txt:
                st.write("") # Espaciador
                st.write(f"💜 **{row['titulo']}**")
                
            with col_check:
                st.write("")

                if st.button("Quitar", key=f"btn_quitar_{id_drama_lista}", use_container_width=True):
                    actualizar_visto(id_drama_lista, row["titulo"], row["poster"], False)

                    limpiar_estado_drama(id_drama_lista)

                    st.session_state.resultados_busqueda = []
                    st.session_state.mensaje_toast = f"Quitaste '{row['titulo']}' de tu lista."

                    st.rerun()
                                    
            st.divider() # Línea de separación
    else:
        st.info("Aún no has marcado ningún KDrama como visto. ¡Explora el catálogo o usa el buscador!")