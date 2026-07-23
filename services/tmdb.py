import requests
import streamlit as st

BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"
IMG_URL_SMALL = "https://image.tmdb.org/t/p/w200"

GENEROS_TMDB = {
    "Todos": "",
    "Drama / Romance": "18",
    "Comedia": "35",
    "Acción y Aventura": "10759",
    "Misterio": "9648",
    "Fantasía / Sci-Fi": "10765",
    "Crimen": "80"
}

def obtener_api_key():
    return st.secrets["TMDB_API_KEY"]

@st.cache_data(show_spinner=False, ttl=3600)
def obtener_kdramas_populares(pagina, id_genero):
    url = f"{BASE_URL}/discover/tv"

    parametros = {
        "api_key": obtener_api_key(),
        "with_origin_country": "KR",
        "sort_by": "popularity.desc",
        "language": "es-MX",
        "page": pagina
    }

    if id_genero:
        parametros["with_genres"] = id_genero

    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status()

        datos = respuesta.json()
        return datos.get("results", [])

    except requests.exceptions.RequestException as error:
        st.error("No pude conectar con TMDB. Revisa tu internet o intenta de nuevo en unos minutos.")
        st.caption(f"Detalle técnico: {error}")
        return []

def buscar_kdrama(query):
    url = f"{BASE_URL}/search/tv"

    parametros = {
        "api_key": obtener_api_key(),
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