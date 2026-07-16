import html

import pandas as pd
import streamlit as st

from services.tmdb import IMG_URL
from services.storage import actualizar_favorito


def mostrar_favorito(row, id_drama_favorito, limpiar_estado_favorito):
    poster = row["poster"] if pd.notna(row["poster"]) else ""
    titulo = str(row["titulo"])
    titulo_seguro = html.escape(titulo)

    if poster:
        imagen = IMG_URL + poster
    else:
        imagen = "https://placehold.co/500x750/d8b4e2/4a044e.png?text=JulyVerse"

    recuerdo_html = ""

    if "recuerdo" in row and pd.notna(row["recuerdo"]) and str(row["recuerdo"]).strip():
        recuerdo = html.escape(str(row["recuerdo"]).strip())
        recuerdo_html = f'<div class="favorite-memory">💜 {recuerdo}</div>'

    calificacion_html = ""

    if "calificacion" in row and pd.notna(row["calificacion"]):
        calificacion = int(row["calificacion"])

        if calificacion > 0:
            calificacion_html = f'<div class="favorite-rating">⭐ {calificacion}/10</div>'

    tarjeta_html = (
        '<div class="favorite-card">'
        '<div class="favorite-poster-wrapper">'
        f'<img src="{imagen}" class="favorite-poster">'
        '</div>'
        '<div class="favorite-info">'
        f'<div class="favorite-title">⭐ {titulo_seguro}</div>'
        f'{calificacion_html}'
        f'{recuerdo_html}'
        '</div>'
        '</div>'
    )

    st.markdown(tarjeta_html, unsafe_allow_html=True)

    if st.button(
        "Quitar favorito",
        key=f"quitar_fav_{id_drama_favorito}",
        width="stretch"
    ):
        actualizar_favorito(id_drama_favorito, False)

        limpiar_estado_favorito(id_drama_favorito)

        st.session_state.mensaje_toast = f"Quitaste '{titulo}' de favoritos."
        st.session_state.pagina_pendiente = "⭐ Favoritos"
        st.rerun()