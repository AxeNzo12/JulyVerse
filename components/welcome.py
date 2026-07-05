import streamlit as st

def mostrar_bienvenida(saludo, mensaje):

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,.45);
            padding:25px;
            border-radius:20px;
            margin-bottom:20px;
            backdrop-filter: blur(10px);
        ">

        <h1 style="margin-bottom:5px;">
            💜 JulyVerse
        </h1>

        <h3>{saludo}</h3>

        <p style="font-size:18px;">
            {mensaje}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )