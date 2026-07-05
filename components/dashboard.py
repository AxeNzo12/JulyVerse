import streamlit as st

def mostrar_dashboard(vistos, recuerdos=0, favoritos=0, logros=0):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📺 Vistos", vistos)

    with c2:
        st.metric("⭐ Favoritos", favoritos)

    with c3:
        st.metric("📖 Recuerdos", recuerdos)

    with c4:
        st.metric("🏆 Logros", logros)