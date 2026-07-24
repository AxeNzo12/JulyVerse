import html

import pandas as pd
import streamlit as st

from services.tmdb import IMG_URL_SMALL
from services.storage import (
    actualizar_visto,
    actualizar_favorito,
    actualizar_calificacion,
)
from components.memory_box import mostrar_caja_recuerdo


def guardar_favorito_desde_interruptor(id_drama, titulo, key_interruptor):
    favorito_nuevo = bool(st.session_state.get(key_interruptor, False))

    actualizar_favorito(id_drama, favorito_nuevo)

    if favorito_nuevo:
        mensaje = f"Agregaste '{titulo}' a favoritos ⭐"
    else:
        mensaje = f"Quitaste '{titulo}' de favoritos."

    st.session_state[f"toast_favorito_{id_drama}"] = mensaje


@st.fragment
def mostrar_interruptor_favorito(
    id_drama,
    titulo,
    favorito_actual,
    key_interruptor,
):
    favorito_mostrado = bool(
        st.session_state.get(key_interruptor, favorito_actual)
    )
    etiqueta_favorito = (
        "⭐ Favorita de July"
        if favorito_mostrado
        else "☆ Marcar como favorita"
    )

    st.toggle(
        etiqueta_favorito,
        value=favorito_actual,
        key=key_interruptor,
        on_change=guardar_favorito_desde_interruptor,
        args=(id_drama, titulo, key_interruptor)
    )

    key_toast = f"toast_favorito_{id_drama}"

    if key_toast in st.session_state:
        st.toast(st.session_state.pop(key_toast), icon="✨")


def mostrar_kdrama_visto(
    row,
    id_drama_lista,
    obtener_key_favorito,
    limpiar_estado_favorito,
    limpiar_estado_drama,
):
    titulo = str(row["titulo"])
    titulo_seguro = html.escape(titulo)

    with st.container(border=True, key=f"watched_card_{id_drama_lista}"):
        col_img, col_txt, col_btn = st.columns([1.2, 6.9, 1.9])

        with col_img:
            if pd.notna(row["poster"]) and row["poster"]:
                poster_html = (
                    f'<img src="{IMG_URL_SMALL + row["poster"]}" '
                    'class="watched-poster" loading="lazy">'
                )
            else:
                poster_html = '<div class="watched-poster-fallback">💜</div>'

            st.markdown(
                f'<div class="watched-poster-wrapper">{poster_html}</div>',
                unsafe_allow_html=True
            )

        with col_txt:
            st.markdown(
                f"""
                <div class="watched-heading">
                    <div class="watched-complete-icon">✓</div>
                    <div>
                        <div class="watched-eyebrow">HISTORIA TERMINADA</div>
                        <div class="watched-title">{titulo_seguro}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_favorito, col_calificacion, _ = st.columns([2.1, 1.6, 1.3])

            # --- FAVORITO ---
            favorito_actual = False

            if "favorito" in row and pd.notna(row["favorito"]):
                favorito_actual = bool(row["favorito"])

            with col_favorito:
                key_favorito = obtener_key_favorito(id_drama_lista)

                mostrar_interruptor_favorito(
                    id_drama=id_drama_lista,
                    titulo=titulo,
                    favorito_actual=favorito_actual,
                    key_interruptor=key_favorito,
                )

            # --- CALIFICACIÓN PERSONAL ---
            calificacion_actual = 0

            if "calificacion" in row and pd.notna(row["calificacion"]):
                calificacion_actual = int(row["calificacion"])

            opciones_calificacion = ["Sin calificar"] + [str(i) for i in range(1, 11)]

            indice_calificacion = 0

            if calificacion_actual > 0:
                indice_calificacion = calificacion_actual

            with col_calificacion:
                calificacion_seleccionada = st.selectbox(
                    "⭐ Calificación",
                    options=opciones_calificacion,
                    index=indice_calificacion,
                    key=f"calificacion_{id_drama_lista}"
                )

            nueva_calificacion = (
                0
                if calificacion_seleccionada == "Sin calificar"
                else int(calificacion_seleccionada)
            )

            if nueva_calificacion != calificacion_actual:
                actualizar_calificacion(id_drama_lista, nueva_calificacion)

                if nueva_calificacion > 0:
                    st.session_state.mensaje_toast = f"Calificaste '{row['titulo']}' con {nueva_calificacion}/10 ⭐"
                else:
                    st.session_state.mensaje_toast = f"Quitaste la calificación de '{row['titulo']}'."

                st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
                st.rerun()

            # --- RECUERDO ---
            recuerdo_actual = ""

            if "recuerdo" in row and pd.notna(row["recuerdo"]):
                recuerdo_actual = str(row["recuerdo"]).strip()

            editando_recuerdo = st.session_state.get(
                f"editando_recuerdo_{id_drama_lista}",
                False
            )
            etiqueta_recuerdo = (
                "💜 Ver recuerdo"
                if recuerdo_actual
                else "💭 Agregar recuerdo"
            )

            with st.expander(
                etiqueta_recuerdo,
                expanded=editando_recuerdo
            ):
                mostrar_caja_recuerdo(row, id_drama_lista)

        with col_btn:
            if st.button(
                "↩ Quitar del historial",
                key=f"btn_quitar_{id_drama_lista}",
                width="stretch"
            ):
                actualizar_visto(id_drama_lista, row["titulo"], row["poster"], False)

                limpiar_estado_drama(id_drama_lista)
                limpiar_estado_favorito(id_drama_lista)

                st.session_state.resultados_busqueda = []
                st.session_state.mensaje_toast = f"Quitaste '{row['titulo']}' de tu lista."

                st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
                st.rerun()
