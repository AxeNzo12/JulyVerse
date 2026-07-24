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

    except requests.exceptions.RequestException:
        st.error("No pude conectar con TMDB. Revisa tu internet o intenta de nuevo en unos minutos.")
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

        resultados = respuesta.json().get("results", [])

        return [
            serie
            for serie in resultados
            if "KR" in serie.get("origin_country", [])
        ]

    except requests.exceptions.RequestException:
        st.error("No pude realizar la búsqueda en TMDB. Intenta de nuevo en unos minutos.")
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def _consultar_perfil_kdrama(id_kdrama):
    url = f"{BASE_URL}/tv/{int(id_kdrama)}"

    parametros = {
        "api_key": obtener_api_key(),
        "language": "es-MX",
        "append_to_response": "similar,aggregate_credits"
    }

    respuesta = requests.get(url, params=parametros, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_perfil_kdrama(id_kdrama):
    """Obtiene detalles, similares y reparto completo en una sola consulta."""
    try:
        return _consultar_perfil_kdrama(id_kdrama)

    except requests.exceptions.RequestException:
        return {}


@st.cache_data(show_spinner=False, ttl=3600)
def _consultar_trabajos_actor(id_actor):
    url = f"{BASE_URL}/person/{int(id_actor)}/combined_credits"

    parametros = {
        "api_key": obtener_api_key(),
        "language": "es-MX"
    }

    respuesta = requests.get(url, params=parametros, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_trabajos_actor(id_actor):
    """Obtiene películas y series relacionadas con una persona."""
    try:
        return _consultar_trabajos_actor(id_actor)

    except requests.exceptions.RequestException:
        return {}


@st.cache_data(show_spinner=False, ttl=3600)
def _consultar_kdramas_por_generos(ids_generos):
    ids_generos = tuple(int(id_genero) for id_genero in ids_generos)

    url = f"{BASE_URL}/discover/tv"

    parametros = {
        "api_key": obtener_api_key(),
        "with_origin_country": "KR",
        "with_genres": "|".join(str(id_genero) for id_genero in ids_generos),
        "sort_by": "popularity.desc",
        "vote_count.gte": 20,
        "include_adult": False,
        "language": "es-MX",
        "page": 1
    }

    respuesta = requests.get(url, params=parametros, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json().get("results", [])


def obtener_kdramas_por_generos(ids_generos):
    """Busca series coreanas relacionadas con los géneros preferidos."""
    ids_generos = tuple(int(id_genero) for id_genero in ids_generos)

    if not ids_generos:
        return []

    try:
        return _consultar_kdramas_por_generos(ids_generos)

    except requests.exceptions.RequestException:
        return []
