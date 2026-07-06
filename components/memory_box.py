import html

import pandas as pd
import streamlit as st

from services.storage import actualizar_recuerdo


def mostrar_caja_recuerdo(row, id_drama_lista):
    recuerdo_actual = ""

    if "recuerdo" in row and pd.notna(row["recuerdo"]):
        recuerdo_actual = str(row["recuerdo"]).strip()

    editando_key = f"editando_recuerdo_{id_drama_lista}"
    texto_key = f"texto_recuerdo_{id_drama_lista}"

    if editando_key not in st.session_state:
        st.session_state[editando_key] = False

    esta_editando = st.session_state[editando_key]

    # Si no hay recuerdo, mostramos directamente el editor
    if not recuerdo_actual:
        st.markdown("✨ **Guardar recuerdo**")

        nuevo_recuerdo = st.text_area(
            "¿Qué te dejó esta historia?",
            value="",
            key=texto_key,
            placeholder="Escribe aquí tu opinión, emoción o recuerdo..."
        )

        if st.button("Guardar recuerdo", key=f"guardar_recuerdo_{id_drama_lista}"):
            actualizar_recuerdo(id_drama_lista, nuevo_recuerdo.strip())
            st.session_state.mensaje_toast = f"Guardaste un recuerdo de '{row['titulo']}' 💜"

            if texto_key in st.session_state:
                del st.session_state[texto_key]
            st.session_state.pagina_actual = "✨ Mis KDramas Vistos"
            st.rerun()

        return

    # Si está editando, mostramos solo el editor
    if esta_editando:
        st.markdown("✨ **Editando recuerdo**")

        nuevo_recuerdo = st.text_area(
            "¿Qué te dejó esta historia?",
            value=recuerdo_actual,
            key=texto_key,
            placeholder="Escribe aquí tu opinión, emoción o recuerdo..."
        )

        col_guardar, col_cancelar, _ = st.columns([1, 1, 4])

        with col_guardar:
            if st.button("Guardar", key=f"guardar_recuerdo_{id_drama_lista}"):
                actualizar_recuerdo(id_drama_lista, nuevo_recuerdo.strip())
                st.session_state[editando_key] = False
                st.session_state.mensaje_toast = f"Actualizaste el recuerdo de '{row['titulo']}' 💜"

                if texto_key in st.session_state:
                    del st.session_state[texto_key]

                st.rerun()

        with col_cancelar:
            if st.button("Cancelar", key=f"cancelar_recuerdo_{id_drama_lista}"):
                st.session_state[editando_key] = False

                if texto_key in st.session_state:
                    del st.session_state[texto_key]

                st.rerun()

        return

    # Si ya hay recuerdo y no está editando, mostramos solo la tarjeta bonita
    recuerdo_seguro = html.escape(recuerdo_actual).replace("\n", "<br>")

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,.45);
            padding: 15px;
            border-radius: 15px;
            margin-top: 8px;
            margin-bottom: 8px;
            border: 1px solid rgba(255,255,255,.35);
            backdrop-filter: blur(10px);
        ">
            <strong>💜 Tu recuerdo:</strong>
            <p style="margin-top:8px;">{recuerdo_seguro}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Editar recuerdo", key=f"editar_recuerdo_{id_drama_lista}"):
        st.session_state[editando_key] = True

        if texto_key in st.session_state:
            del st.session_state[texto_key]

        st.rerun()