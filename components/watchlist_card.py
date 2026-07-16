import html

import pandas as pd
import streamlit as st

from services.tmdb import IMG_URL_SMALL
from services.storage import actualizar_visto
from services.watchlist import eliminar_por_ver


def mostrar_por_ver_card(row, id_por_ver):
    titulo = str(row["titulo"])
    titulo_seguro = html.escape(titulo)

    poster = ""

    if "poster" in row and pd.notna(row["poster"]):
        poster = str(row["poster"])

    if poster:
        imagen_html = f'<img loading="lazy" src="{IMG_URL_SMALL + poster}" class="watchlist-poster">'
    else:
        imagen_html = '<div class="watchlist-placeholder">💜</div>'

    tarjeta_html = (
        '<div class="watchlist-card">'
        '<div class="watchlist-poster-wrapper">'
        f'{imagen_html}'
        '</div>'
        f'<div class="watchlist-title">{titulo_seguro}</div>'
        '<div class="watchlist-caption">Pendiente por ver</div>'
        '</div>'
    )

    st.markdown(tarjeta_html, unsafe_allow_html=True)

    if st.button(
        "Marcar como visto",
        key=f"por_ver_a_visto_{id_por_ver}",
        width="stretch"
    ):
        actualizar_visto(
            id_por_ver,
            titulo,
            poster,
            True
        )

        eliminar_por_ver(id_por_ver)

        st.session_state.mensaje_toast = f"Moviste '{titulo}' a vistos 💜"
        st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
        st.rerun()

    if st.button(
        "Quitar",
        key=f"quitar_por_ver_page_{id_por_ver}",
        width="stretch"
    ):
        eliminar_por_ver(id_por_ver)

        st.session_state.mensaje_toast = f"Quitaste '{titulo}' de Por Ver."
        st.session_state.pagina_pendiente = "💫 Por Ver"
        st.rerun()