import streamlit as st


def mostrar_dashboard(vistos, recuerdos=0, favoritos=0, logros=0, promedio=0):
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("📺 Vistos", vistos)

    with c2:
        st.metric("⭐ Favoritos", favoritos)

    with c3:
        st.metric("📖 Recuerdos", recuerdos)

    with c4:
        st.metric("🏆 Logros", logros)

    with c5:
        if promedio > 0:
            st.metric("🌟 Promedio", f"{promedio}/10")
        else:
            st.metric("🌟 Promedio", "-")