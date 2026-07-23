import streamlit as st


def calcular_logros(total_vistos, total_recuerdos):
    logros = []

    reglas = [
        {
            "condicion": total_vistos >= 1,
            "icono": "🌱",
            "titulo": "Primer paso",
            "descripcion": "Terminaste tu primer KDrama. JulyVerse acaba de comenzar."
        },
        {
            "condicion": total_vistos >= 5,
            "icono": "📺",
            "titulo": "Maratón inicial",
            "descripcion": "Ya terminaste 5 historias. Tu universo empieza a crecer."
        },
        {
            "condicion": total_vistos >= 10,
            "icono": "✨",
            "titulo": "Coleccionista de historias",
            "descripcion": "10 KDramas terminados. Cada historia ya tiene su lugar."
        },
        {
            "condicion": total_vistos >= 25,
            "icono": "💜",
            "titulo": "Habitante de JulyVerse",
            "descripcion": "25 historias terminadas. Este universo ya tiene mucha vida."
        },
        {
            "condicion": total_vistos >= 50,
            "icono": "🌌",
            "titulo": "Universo en expansión",
            "descripcion": "50 historias completadas. JulyVerse está lleno de recuerdos."
        },
        {
            "condicion": total_vistos >= 100,
            "icono": "👑",
            "titulo": "Reina del drama",
            "descripcion": "100 historias terminadas. Este logro es legendario."
        },
        {
            "condicion": total_recuerdos >= 1,
            "icono": "📖",
            "titulo": "Primer recuerdo",
            "descripcion": "Guardaste tu primer recuerdo de una historia."
        },
        {
            "condicion": total_recuerdos >= 5,
            "icono": "📝",
            "titulo": "Diario en crecimiento",
            "descripcion": "5 recuerdos guardados. Ya no solo ves historias, también las recuerdas."
        },
        {
            "condicion": total_recuerdos >= 10,
            "icono": "💫",
            "titulo": "Memorias de JulyVerse",
            "descripcion": "10 recuerdos guardados. Tu diario empieza a brillar."
        },
    ]

    for regla in reglas:
        if regla["condicion"]:
            logros.append(regla)

    return logros


def mostrar_logros(logros):
    st.markdown(
        '<div class="achievements-spacer" aria-hidden="true"></div>',
        unsafe_allow_html=True
    )

    with st.expander("🏆 Logros desbloqueados"):
        if not logros:
            st.info("Aún no hay logros desbloqueados. El primero llegará cuando termines tu primer KDrama.")
            return

        columnas = st.columns(3)

        for i, logro in enumerate(logros):
            with columnas[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(255,255,255,.45);
                        padding: 16px;
                        border-radius: 16px;
                        margin-bottom: 12px;
                        border: 1px solid rgba(255,255,255,.35);
                        backdrop-filter: blur(10px);
                        min-height: 150px;
                    ">
                        <h2 style="margin-bottom: 4px;">{logro["icono"]}</h2>
                        <strong>{logro["titulo"]}</strong>
                        <p style="margin-top: 8px; font-size: 14px;">
                            {logro["descripcion"]}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
