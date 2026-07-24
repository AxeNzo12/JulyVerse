import hmac

import streamlit as st


CLAVE_SESION = "acceso_julyverse"


def mostrar_acceso():
    """Muestra el acceso privado y devuelve True cuando la sesión está autorizada."""
    if st.session_state.get(CLAVE_SESION, False):
        return True

    _, columna_acceso, _ = st.columns([1, 1.15, 1])

    with columna_acceso:
        with st.container(key="login_julyverse"):
            st.markdown(
                """
                <div class="login-julyverse-header">
                    <span class="login-julyverse-star">✦</span>
                    <h1>JulyVerse</h1>
                    <p>Un pequeño universo hecho especialmente para July.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("formulario_acceso"):
                contrasena = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="Escribe la contraseña",
                )
                entrar = st.form_submit_button(
                    "Entrar a JulyVerse 💜",
                    width="stretch",
                )

            if entrar:
                contrasena_guardada = st.secrets.get("APP_PASSWORD", "")

                if not contrasena_guardada:
                    st.error(
                        "Falta configurar APP_PASSWORD en los Secrets de la app."
                    )
                elif hmac.compare_digest(
                    contrasena,
                    str(contrasena_guardada),
                ):
                    st.session_state[CLAVE_SESION] = True
                    st.rerun()
                else:
                    st.error("La contraseña no es correcta. Inténtalo de nuevo.")

    return False


def cerrar_sesion():
    """Cierra únicamente la sesión actual del navegador."""
    st.session_state.pop(CLAVE_SESION, None)
    st.rerun()
