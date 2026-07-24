import streamlit as st

from utils.auth import cerrar_sesion, mostrar_acceso
from utils.paths import CSS


st.set_page_config(
    page_title="AnimeVerse",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="auto",
)


def cargar_estilos():
    for nombre_archivo in ("style.css", "anime_style.css"):
        ruta_css = CSS / nombre_archivo
        with open(ruta_css, encoding="utf-8") as archivo_css:
            st.markdown(
                f"<style>{archivo_css.read()}</style>",
                unsafe_allow_html=True,
            )


cargar_estilos()

if not mostrar_acceso():
    st.stop()

with st.sidebar:
    st.markdown(
        """
        <div class="anime-sidebar-brand">
            <span>🧭</span>
            <strong>AnimeVerse</strong>
            <small>El océano de historias de July</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "app.py",
        label="Volver a JulyVerse",
        icon="💜",
        width="stretch",
    )
    if st.button(
        "Cerrar sesión",
        icon=":material/logout:",
        width="stretch",
        key="cerrar_sesion_animeverse",
    ):
        cerrar_sesion()

    st.divider()
    st.caption(
        "Los animes tendrán listas y estadísticas independientes de los KDramas."
    )

st.markdown(
    """
    <div class="anime-hero">
        <div class="anime-hero-compass">✦</div>
        <span class="anime-hero-eyebrow">UN NUEVO RUMBO PARA JULY</span>
        <h1>AnimeVerse</h1>
        <p>
            Un océano de aventuras, personajes inolvidables y nuevas historias
            por descubrir.
        </p>
        <div class="anime-hero-badges">
            <span>🌊 Catálogo propio</span>
            <span>🗺️ Historial separado</span>
            <span>⭐ Favoritos de July</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="anime-section-heading">
        <span>PRIMER MAPA DE NAVEGACIÓN</span>
        <h2>El viaje apenas comienza</h2>
        <p>
            Construiremos este universo por etapas para conservar intacto todo
            lo que ya funciona en JulyVerse.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="anime-roadmap">
        <article>
            <div class="anime-roadmap-icon">🔭</div>
            <strong>Catálogo y búsqueda</strong>
            <p>Explorar anime con información obtenida desde Jikan.</p>
            <span class="anime-roadmap-status active">SIGUIENTE ETAPA</span>
        </article>
        <article>
            <div class="anime-roadmap-icon">📜</div>
            <strong>El diario de July</strong>
            <p>Vistos, Por Ver, recuerdos, favoritos y calificaciones.</p>
            <span class="anime-roadmap-status">DATOS SEPARADOS</span>
        </article>
        <article>
            <div class="anime-roadmap-icon">🏴‍☠️</div>
            <strong>Su propia tripulación</strong>
            <p>Estadísticas y recomendaciones según sus animes favoritos.</p>
            <span class="anime-roadmap-status">MÁS ADELANTE</span>
        </article>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "La entrada a AnimeVerse ya está lista. "
    "El siguiente bloque agregará el catálogo y el buscador."
)
