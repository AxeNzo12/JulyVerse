import html

import streamlit as st

from components.drama_details import mostrar_detalles_kdrama
from components.drama_card import mostrar_tarjeta
from services.recommendation_preferences import agregar_no_interesa


def mostrar_recomendacion(
    drama,
    lista_vistos_ids,
    lista_por_ver_ids
):
    id_kdrama = int(drama.get("id", 0))
    titulo = drama.get("name", "Sin título")
    motivos = drama.get("_motivos", [])
    afinidad = drama.get("_afinidad", {})
    afinidad_texto = html.escape(
        str(afinidad.get("texto", "Buena opción"))
    )
    afinidad_icono = html.escape(str(afinidad.get("icono", "✨")))
    afinidad_clase = afinidad.get("clase", "medium")

    if afinidad_clase not in {"high", "medium", "soft"}:
        afinidad_clase = "medium"

    motivos_html = "".join(
        f'<span class="recommendation-reason">{html.escape(str(motivo))}</span>'
        for motivo in motivos
    )

    with st.container(key=f"recommendation_item_{id_kdrama}"):
        st.markdown(
            f"""
            <div class="recommendation-match">
                <div class="recommendation-affinity recommendation-affinity-{afinidad_clase}">
                    {afinidad_icono} {afinidad_texto}
                </div>
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

        columna_detalles, columna_ocultar = st.columns(2)

        with columna_detalles:
            if st.button(
                "🔎 Ver detalles",
                key=f"ver_detalles_recomendacion_{id_kdrama}",
                width="stretch"
            ):
                mostrar_detalles_kdrama(drama)

        with columna_ocultar:
            if st.button(
                "🙈 No me interesa",
                key=f"ocultar_recomendacion_{id_kdrama}",
                help="La oculta de futuras recomendaciones.",
                width="stretch"
            ):
                agregar_no_interesa(id_kdrama, titulo)
                st.session_state.mensaje_toast = (
                    f"Ocultaste '{titulo}' de las recomendaciones."
                )
                st.rerun()
