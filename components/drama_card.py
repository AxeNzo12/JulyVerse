import streamlit as st

from services.tmdb import IMG_URL
from services.storage import actualizar_visto
from utils.recuerdos import (
    imagen_a_base64,
    obtener_recuerdo_por_indice,
)


def obtener_key_checkbox(prefijo_key, id_kdrama):
    id_kdrama = int(float(id_kdrama))
    version = st.session_state.get(f"version_drama_{id_kdrama}", 0)

    return f"{prefijo_key}_{id_kdrama}_{version}"


def mostrar_tarjeta(drama, prefijo_key, lista_vistos_ids):
    poster_path = drama.get("poster_path") or ""
    id_drama = int(drama["id"])

    if poster_path:
        url_imagen = IMG_URL + poster_path

    else:
        if id_drama not in st.session_state.imagenes_asignadas:
            foto_elegida = obtener_recuerdo_por_indice(
                st.session_state.contador_fotos
            )

            st.session_state.imagenes_asignadas[id_drama] = foto_elegida
            st.session_state.contador_fotos += 1

        foto_definitiva = st.session_state.imagenes_asignadas[id_drama]

        img_b64 = imagen_a_base64(foto_definitiva)

        url_imagen = (
            f"data:image/jpeg;base64,{img_b64}"
            if img_b64
            else "https://placehold.co/500x750/d8b4e2/4a044e.png?text=JulyVerse"
        )

    st.markdown(
        f"""
        <div style="
            height: 450px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        ">
            <img src="{url_imagen}"
                style="
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                    border-radius: 8px;
                ">
        </div>
        """,
        unsafe_allow_html=True
    )

    if not poster_path:
        st.caption("💜 No encontré el póster... Pero encontré un bonito recuerdo.")

    titulo = drama.get("name", "Sin título")
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