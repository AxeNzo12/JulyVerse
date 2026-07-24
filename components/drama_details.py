import html

import streamlit as st

from services.tmdb import (
    IMG_URL_SMALL,
    PROFILE_IMG_URL_SMALL,
    obtener_perfil_kdrama,
)


ESTADOS_TMDB = {
    "Ended": "Finalizada",
    "Returning Series": "En emisión",
    "Canceled": "Cancelada",
    "In Production": "En producción",
    "Planned": "Planeada",
    "Pilot": "Piloto",
}


def _texto_seguro(valor, predeterminado="Sin información"):
    if valor in (None, ""):
        valor = predeterminado

    return html.escape(str(valor))


@st.dialog("✨ Detalles del KDrama", width="large")
def mostrar_detalles_kdrama(drama):
    id_kdrama = int(drama.get("id", 0))

    with st.spinner("Abriendo esta historia..."):
        perfil = obtener_perfil_kdrama(id_kdrama)

    if not perfil:
        st.warning(
            "No pude cargar los detalles desde TMDB. "
            "Inténtalo nuevamente en unos minutos."
        )
        return

    titulo = perfil.get("name") or drama.get("name") or "Sin título"
    titulo_original = perfil.get("original_name", "")
    poster = perfil.get("poster_path") or drama.get("poster_path", "")
    descripcion = (
        perfil.get("overview")
        or drama.get("overview")
        or "TMDB todavía no tiene una descripción disponible."
    )
    fecha = perfil.get("first_air_date", "")
    estado = ESTADOS_TMDB.get(
        perfil.get("status", ""),
        perfil.get("status", "Sin información")
    )
    temporadas = perfil.get("number_of_seasons", 0)
    episodios = perfil.get("number_of_episodes", 0)
    promedio = round(float(perfil.get("vote_average", 0) or 0), 1)
    generos = [
        genero.get("name", "")
        for genero in perfil.get("genres", [])
        if genero.get("name")
    ]

    columna_poster, columna_info = st.columns([1, 2])

    with columna_poster:
        if poster:
            st.image(
                IMG_URL_SMALL + poster,
                caption=titulo,
                width=240
            )
        else:
            st.markdown(
                '<div class="details-poster-placeholder">🌙</div>',
                unsafe_allow_html=True
            )

    with columna_info:
        st.markdown(
            f"""
            <div class="details-heading">
                <strong>{_texto_seguro(titulo)}</strong>
                <span>{_texto_seguro(titulo_original, "")}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        generos_html = "".join(
            f'<span class="details-genre">{_texto_seguro(genero)}</span>'
            for genero in generos
        )

        if generos_html:
            st.markdown(
                f'<div class="details-genres">{generos_html}</div>',
                unsafe_allow_html=True
            )

        datos_html = "".join([
            (
                '<div class="details-data-item">'
                f'<strong>{_texto_seguro(fecha[:4] if fecha else "—")}</strong>'
                "<span>Estreno</span></div>"
            ),
            (
                '<div class="details-data-item">'
                f'<strong>{_texto_seguro(episodios or "—")}</strong>'
                "<span>Episodios</span></div>"
            ),
            (
                '<div class="details-data-item">'
                f'<strong>{_texto_seguro(temporadas or "—")}</strong>'
                "<span>Temporadas</span></div>"
            ),
            (
                '<div class="details-data-item">'
                f'<strong>⭐ {_texto_seguro(promedio)}</strong>'
                "<span>TMDB</span></div>"
            ),
        ])

        st.markdown(
            f'<div class="details-data-grid">{datos_html}</div>',
            unsafe_allow_html=True
        )
        st.caption(f"Estado: {estado}")
        st.markdown("#### La historia")
        st.write(descripcion)

    reparto = perfil.get("aggregate_credits", {}).get("cast", [])[:4]

    if reparto:
        reparto_html = ""

        for persona in reparto:
            nombre = persona.get("name", "Sin nombre")
            foto = persona.get("profile_path", "")
            roles = persona.get("roles", []) or []
            personaje = roles[0].get("character", "") if roles else ""
            nombre_seguro = _texto_seguro(nombre)
            foto_html = (
                '<img loading="lazy" class="details-cast-photo" '
                f'src="{_texto_seguro(PROFILE_IMG_URL_SMALL + foto)}" '
                f'alt="{nombre_seguro}">'
                if foto
                else '<div class="details-cast-placeholder">🎭</div>'
            )
            texto_personaje = (
                f"<span>{_texto_seguro(personaje)}</span>"
                if personaje
                else ""
            )
            reparto_html += (
                '<div class="details-cast-item">'
                f"{foto_html}"
                f'<strong>{nombre_seguro}</strong>'
                f"{texto_personaje}</div>"
            )

        st.markdown("#### Reparto principal")
        st.markdown(
            f'<div class="details-cast-grid">{reparto_html}</div>',
            unsafe_allow_html=True
        )
