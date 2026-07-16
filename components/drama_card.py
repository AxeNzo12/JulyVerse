import html

import streamlit as st

from services.tmdb import IMG_URL
from services.storage import actualizar_visto
from services.watchlist import agregar_por_ver, eliminar_por_ver
from utils.recuerdos import imagen_a_base64, obtener_recuerdo_por_indice


def obtener_key_checkbox(prefijo_key, id_kdrama):
    id_kdrama = int(float(id_kdrama))
    version = st.session_state.get(f"version_drama_{id_kdrama}", 0)

    return f"{prefijo_key}_visto_{id_kdrama}_{version}"


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
        imagen_html = f'<img src="{IMG_URL + poster}" class="catalog-poster">'
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

    visto_nuevo = st.checkbox(
        "Ya lo vi",
        value=visto_actual,
        key=obtener_key_checkbox(prefijo_key, id_kdrama)
    )

    if visto_nuevo != visto_actual:
        actualizar_visto(
            id_kdrama=id_kdrama,
            titulo=titulo,
            poster=poster,
            visto=visto_nuevo
        )

        if visto_nuevo:
            eliminar_por_ver(id_kdrama)
            st.session_state.mensaje_toast = f"Agregaste '{titulo}' a tus KDramas vistos 💜"
            st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
        else:
            st.session_state.mensaje_toast = f"Quitaste '{titulo}' de tus KDramas vistos."

        st.rerun()

    if not visto_actual:
        if en_por_ver:
            if st.button(
                "Quitar de Por Ver",
                key=f"quitar_por_ver_{prefijo_key}_{id_kdrama}",
                use_container_width=True
            ):
                eliminar_por_ver(id_kdrama)

                st.session_state.mensaje_toast = f"Quitaste '{titulo}' de Por Ver."
                st.rerun()
        else:
            if st.button(
                "💫 Quiero verla",
                key=f"agregar_por_ver_{prefijo_key}_{id_kdrama}",
                use_container_width=True
            ):
                agregar_por_ver(id_kdrama, titulo, poster)

                st.session_state.mensaje_toast = f"Agregaste '{titulo}' a Por Ver 💫"
                st.rerun()