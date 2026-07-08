import pandas as pd
import streamlit as st

from services.tmdb import IMG_URL_SMALL
from services.storage import (
    actualizar_visto,
    actualizar_favorito,
    actualizar_calificacion,
)
from components.memory_box import mostrar_caja_recuerdo


def mostrar_kdrama_visto(
    row,
    id_drama_lista,
    obtener_key_favorito,
    limpiar_estado_favorito,
    limpiar_estado_drama,
):
    with st.container(border=True):
        col_img, col_txt, col_btn = st.columns([1, 7, 2])

        with col_img:
            if pd.notna(row["poster"]) and row["poster"]:
                st.image(IMG_URL_SMALL + row["poster"], width=90)
            else:
                st.markdown("💜")

        with col_txt:
            st.markdown(f"### 💜 {row['titulo']}")

            # --- FAVORITO ---
            favorito_actual = False

            if "favorito" in row and pd.notna(row["favorito"]):
                favorito_actual = bool(row["favorito"])

            favorito_nuevo = st.checkbox(
                "⭐ Favorito",
                value=favorito_actual,
                key=obtener_key_favorito(id_drama_lista)
            )

            if favorito_nuevo != favorito_actual:
                actualizar_favorito(id_drama_lista, favorito_nuevo)

                limpiar_estado_favorito(id_drama_lista)

                if favorito_nuevo:
                    st.session_state.mensaje_toast = f"Agregaste '{row['titulo']}' a favoritos ⭐"
                else:
                    st.session_state.mensaje_toast = f"Quitaste '{row['titulo']}' de favoritos."

                st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
                st.rerun()

            # --- CALIFICACIÓN PERSONAL ---
            calificacion_actual = 0

            if "calificacion" in row and pd.notna(row["calificacion"]):
                calificacion_actual = int(row["calificacion"])

            opciones_calificacion = ["Sin calificar"] + [str(i) for i in range(1, 11)]

            indice_calificacion = 0

            if calificacion_actual > 0:
                indice_calificacion = calificacion_actual

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
            mostrar_caja_recuerdo(row, id_drama_lista)

        with col_btn:
            st.write("")

            if st.button("Quitar", key=f"btn_quitar_{id_drama_lista}", use_container_width=True):
                actualizar_visto(id_drama_lista, row["titulo"], row["poster"], False)

                limpiar_estado_drama(id_drama_lista)
                limpiar_estado_favorito(id_drama_lista)

                st.session_state.resultados_busqueda = []
                st.session_state.mensaje_toast = f"Quitaste '{row['titulo']}' de tu lista."

                st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
                st.rerun()