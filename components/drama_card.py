import html

import streamlit as st

from services.tmdb import IMG_URL_SMALL
from services.storage import actualizar_visto
from services.watchlist import agregar_por_ver, eliminar_por_ver
from utils.recuerdos import imagen_a_base64, obtener_recuerdo_por_indice


def obtener_imagen_fallback(id_kdrama):
    if "imagenes_asignadas" not in st.session_state:
        st.session_state.imagenes_asignadas = {}

    if "contador_fotos" not in st.session_state:
        st.session_state.contador_fotos = 0

    if id_kdrama not in st.session_state.imagenes_asignadas:
        st.session_state.imagenes_asignadas[id_kdrama] = st.session_state.contador_fotos
        st.session_state.contador_fotos += 1

    indice = st.session_state.imagenes_asignadas[id_kdrama]
    ruta_recuerdo = obtener_recuerdo_por_indice(indice)

    return imagen_a_base64(ruta_recuerdo)


def mostrar_tarjeta(drama, prefijo_key, lista_vistos_ids, lista_por_ver_ids=None):
    if lista_por_ver_ids is None:
        lista_por_ver_ids = []

    id_kdrama = int(drama.get("id", 0))
    titulo = drama.get("name", "Sin título")
    poster = drama.get("poster_path", "")
    descripcion = drama.get("overview", "")
    fecha = drama.get("first_air_date", "")
    promedio = drama.get("vote_average", 0)

    titulo_seguro = html.escape(titulo)
    descripcion_segura = html.escape(descripcion)

    visto_actual = id_kdrama in lista_vistos_ids
    en_por_ver = id_kdrama in lista_por_ver_ids

    if poster:
        imagen_html = f'<img loading="lazy" src="{IMG_URL_SMALL + poster}" class="catalog-poster">'
        fallback_texto = ""
    else:
        imagen_base64 = obtener_imagen_fallback(id_kdrama)
        imagen_html = f'<img src="data:image/jpeg;base64,{imagen_base64}" class="catalog-poster">'
        fallback_texto = '<div class="catalog-fallback">💜 No encontré el póster... Pero encontré un bonito recuerdo.</div>'

    if descripcion_segura:
        descripcion_corta = descripcion_segura[:130] + "..." if len(descripcion_segura) > 130 else descripcion_segura
    else:
        descripcion_corta = "Sin descripción disponible por ahora."

    if fecha:
        anio = fecha[:4]
    else:
        anio = "Sin año"

    tarjeta_html = (
        '<div class="catalog-card">'
        '<div class="catalog-poster-wrapper">'
        f'{imagen_html}'
        '</div>'
        '<div class="catalog-info">'
        f'<div class="catalog-title">{titulo_seguro}</div>'
        f'<div class="catalog-meta">📅 {anio} · ⭐ {round(promedio, 1)}</div>'
        f'<div class="catalog-description">{descripcion_corta}</div>'
        f'{fallback_texto}'
        '</div>'
        '</div>'
    )

    st.markdown(tarjeta_html, unsafe_allow_html=True)

    if visto_actual:
        st.button(
            "✅ Ya la viste",
            key=f"catalogo_estado_visto_{prefijo_key}_{id_kdrama}",
            width="stretch",
            disabled=True
        )

        if st.button(
            "↩ Quitar de vistos",
            key=f"catalogo_quitar_visto_{prefijo_key}_{id_kdrama}",
            help="Quita esta serie de Mis KDramas Vistos.",
            width="stretch"
        ):
            actualizar_visto(
                id_kdrama=id_kdrama,
                titulo=titulo,
                poster=poster,
                visto=False
            )

            st.session_state.mensaje_toast = f"Quitaste '{titulo}' de tus KDramas vistos."
            st.rerun()
    else:
        if st.button(
            "✓ Marcar como vista",
            key=f"catalogo_visto_{prefijo_key}_{id_kdrama}",
            help="Agrega esta serie a Mis KDramas Vistos.",
            width="stretch"
        ):
            actualizar_visto(
                id_kdrama=id_kdrama,
                titulo=titulo,
                poster=poster,
                visto=True
            )

            eliminar_por_ver(id_kdrama)
            st.session_state.mensaje_toast = f"Agregaste '{titulo}' a tus KDramas vistos 💜"
            st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
            st.rerun()

        if en_por_ver:
            if st.button(
                "Quitar de Por Ver",
                key=f"quitar_por_ver_{prefijo_key}_{id_kdrama}",
                width="stretch"
            ):
                eliminar_por_ver(id_kdrama)

                st.session_state.mensaje_toast = f"Quitaste '{titulo}' de Por Ver."
                st.rerun()
        else:
            if st.button(
                "💫 Quiero verla",
                key=f"agregar_por_ver_{prefijo_key}_{id_kdrama}",
                width="stretch"
            ):
                agregar_por_ver(id_kdrama, titulo, poster)

                st.session_state.mensaje_toast = f"Agregaste '{titulo}' a Por Ver 💫"
                st.rerun()
