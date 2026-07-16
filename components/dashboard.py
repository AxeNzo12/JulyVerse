import streamlit as st


def mostrar_metric_card(icono, titulo, valor, descripcion):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icono}</div>
            <div class="metric-content">
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">{valor}</div>
                <div class="metric-description">{descripcion}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mostrar_dashboard(vistos, recuerdos=0, favoritos=0, logros=0, promedio=0, por_ver=0):
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        mostrar_metric_card(
            "📺",
            "Vistos",
            vistos,
            "Historias terminadas"
        )

    with c2:
        mostrar_metric_card(
            "💫",
            "Por Ver",
            por_ver,
            "Historias pendientes"
        )

    with c3:
        mostrar_metric_card(
            "⭐",
            "Favoritos",
            favoritos,
            "Historias especiales"
        )

    with c4:
        mostrar_metric_card(
            "📖",
            "Recuerdos",
            recuerdos,
            "Opiniones guardadas"
        )

    with c5:
        mostrar_metric_card(
            "🏆",
            "Logros",
            logros,
            "Metas desbloqueadas"
        )

    with c6:
        valor_promedio = f"{promedio}/10" if promedio > 0 else "-"

        mostrar_metric_card(
            "🌟",
            "Promedio",
            valor_promedio,
            "Calificación media"
        )