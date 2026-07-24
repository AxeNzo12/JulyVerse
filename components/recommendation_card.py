import html

import streamlit as st

from components.drama_card import mostrar_tarjeta


def mostrar_recomendacion(
    drama,
    lista_vistos_ids,
    lista_por_ver_ids
):
    id_kdrama = int(drama.get("id", 0))
    motivos = drama.get("_motivos", [])

    motivos_html = "".join(
        f'<span class="recommendation-reason">{html.escape(str(motivo))}</span>'
        for motivo in motivos
    )

    with st.container(key=f"recommendation_item_{id_kdrama}"):
        st.markdown(
            f"""
            <div class="recommendation-match">
                <div class="recommendation-match-title">✨ Elegida para July</div>
                <div class="recommendation-reasons">{motivos_html}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        mostrar_tarjeta(
            drama,
            "recomendacion",
            lista_vistos_ids,
            lista_por_ver_ids
        )
