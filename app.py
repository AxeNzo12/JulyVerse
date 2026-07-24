import html
import streamlit as st
import pandas as pd
from pathlib import Path
from utils.paths import IMAGES, CSS
from utils.messages import obtener_bienvenida
from components.dashboard import mostrar_dashboard
from components.welcome import mostrar_bienvenida
from utils.special_dates import obtener_fecha_especial
from components.drama_card import mostrar_tarjeta
from components.watched_card import mostrar_kdrama_visto
from components.memory_box import mostrar_caja_recuerdo
from components.stats_panel import mostrar_estadisticas
from services.watchlist import cargar_por_ver, eliminar_por_ver
from components.watchlist_card import mostrar_por_ver_card
from components.favorite_card import mostrar_favorito
from utils.recuerdos import (
    imagen_a_base64,
    obtener_recuerdo_por_indice,
)
from services.tmdb import (
    GENEROS_TMDB,
    IMG_URL,
    IMG_URL_SMALL,
    obtener_kdramas_populares,
    buscar_kdrama,
)
from services.storage import (
    cargar_vistos,
    actualizar_visto,
    actualizar_favorito,
    actualizar_calificacion,
)
from components.achievements import (
    calcular_logros,
    mostrar_logros,
)

st.set_page_config(
    page_title="JulyVerse",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="auto"
)

# Muestra la notificación animada si hay un mensaje pendiente
if 'mensaje_toast' in st.session_state:
    st.toast(st.session_state.mensaje_toast, icon="✨")
    del st.session_state.mensaje_toast

def cargar_css():
    with open(CSS / "style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🐻 Tata")
    st.caption("Compañero oficial de JulyVerse 💜")
    st.write(
    "Estoy aquí para acompañarte mientras descubres nuevas historias."
    )
    try:
        st.image(IMAGES / "ui" / "tata.png")
    except:
        st.info("💡 Guarda una foto como 'taehyung.jpg' en tu carpeta para que aparezca aquí.")
    st.divider()

    st.subheader("💾 Respaldo")

    ruta_csv = Path("mis_kdramas.csv")

    if ruta_csv.exists():
        with open(ruta_csv, "rb") as archivo:
            st.download_button(
                label="Descargar respaldo",
                data=archivo,
                file_name="respaldo_julyverse.csv",
                mime="text/csv",
                width="stretch"
            )
        ruta_por_ver = Path("por_ver.csv")

    if ruta_por_ver.exists():
        with open(ruta_por_ver, "rb") as archivo_por_ver:
            st.download_button(
                label="Descargar Por Ver",
                data=archivo_por_ver,
                file_name="respaldo_por_ver_julyverse.csv",
                mime="text/csv",
                width="stretch"
            )
    else:
        st.caption("Aún no hay datos para respaldar.")

    st.markdown("#### 📤 Restaurar vistos")
    st.caption("Selecciona un respaldo de tus KDramas vistos.")

    archivo_respaldo = st.file_uploader(
        "Respaldo de KDramas vistos",
        type=["csv"],
        key="archivo_respaldo_julyverse",
        label_visibility="collapsed"
    )

    if archivo_respaldo is not None:
        try:
            df_importado = pd.read_csv(archivo_respaldo)

            columnas_obligatorias = {"id", "titulo"}

            if not columnas_obligatorias.issubset(df_importado.columns):
                st.error("Este archivo no parece ser un respaldo válido de JulyVerse.")
            else:
                st.caption(f"Se encontraron {len(df_importado)} KDramas en el respaldo.")

                st.warning("Restaurar este respaldo reemplazará los datos actuales.")

                if st.button("Restaurar respaldo", width="stretch"):
                    if "poster" not in df_importado.columns:
                        df_importado["poster"] = ""

                    if "recuerdo" not in df_importado.columns:
                        df_importado["recuerdo"] = ""

                    if "favorito" not in df_importado.columns:
                        df_importado["favorito"] = False

                    if "calificacion" not in df_importado.columns:
                        df_importado["calificacion"] = 0

                    df_importado = df_importado[
                        ["id", "titulo", "poster", "recuerdo", "favorito", "calificacion"]
                    ]

                    df_importado.to_csv("mis_kdramas.csv", index=False)

                    st.session_state.mensaje_toast = "Respaldo restaurado correctamente 💜"
                    st.session_state.pagina_pendiente = "✨ Mis KDramas Vistos"
                    st.rerun()

        except Exception as error:
            st.error("No pude leer el respaldo. Revisa que sea un archivo CSV válido.")
            st.caption(f"Detalle técnico: {error}")

    st.markdown("#### 💫 Restaurar Por Ver")
    st.caption("Selecciona un respaldo de tu lista Por Ver.")

    archivo_por_ver_respaldo = st.file_uploader(
        "Respaldo de la lista Por Ver",
        type=["csv"],
        key="archivo_respaldo_por_ver_julyverse",
        label_visibility="collapsed"
    )

    if archivo_por_ver_respaldo is not None:
        try:
            df_por_ver_importado = pd.read_csv(archivo_por_ver_respaldo)

            columnas_obligatorias_por_ver = {"id", "titulo"}

            if not columnas_obligatorias_por_ver.issubset(df_por_ver_importado.columns):
                st.error("Este archivo no parece ser un respaldo válido de Por Ver.")
            else:
                st.caption(f"Se encontraron {len(df_por_ver_importado)} KDramas por ver.")

                st.warning("Restaurar este respaldo reemplazará tu lista actual de Por Ver.")

                if st.button("Restaurar Por Ver", width="stretch"):
                    if "poster" not in df_por_ver_importado.columns:
                        df_por_ver_importado["poster"] = ""

                    df_por_ver_importado = df_por_ver_importado[
                        ["id", "titulo", "poster"]
                    ]

                    df_por_ver_importado["id"] = pd.to_numeric(
                        df_por_ver_importado["id"],
                        errors="coerce"
                    )

                    df_por_ver_importado = df_por_ver_importado.dropna(subset=["id"])
                    df_por_ver_importado["id"] = df_por_ver_importado["id"].astype(int)

                    df_por_ver_importado = df_por_ver_importado.drop_duplicates(
                        subset=["id"],
                        keep="first"
                    )

                    df_por_ver_importado.to_csv("por_ver.csv", index=False)

                    st.session_state.mensaje_toast = "Lista Por Ver restaurada correctamente 💫"
                    st.session_state.pagina_pendiente = "💫 Por Ver"
                    st.rerun()

        except Exception as error:
            st.error("No pude leer el respaldo de Por Ver. Revisa que sea un archivo CSV válido.")
            st.caption(f"Detalle técnico: {error}")
if "bienvenida_actual" not in st.session_state:
    st.session_state.bienvenida_actual = obtener_bienvenida()

saludo, mensaje = st.session_state.bienvenida_actual

mostrar_bienvenida(
    saludo,
    mensaje
)

fecha_especial = obtener_fecha_especial()

if fecha_especial:
    titulo_fecha, mensaje_fecha = fecha_especial

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,.55);
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,.35);
            backdrop-filter: blur(10px);
        ">
            <h3>{titulo_fecha}</h3>
            <p style="font-size:17px;">{mensaje_fecha}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


OPCIONES_PAGINA = [
    "📺 Catálogo",
    "🔍 Buscar Serie",
    "✨ Mis KDramas Vistos",
    "⭐ Favoritos",
    "💫 Por Ver",
    "📊 Estadísticas"
]

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "📺 Catálogo"

# Si alguna acción pidió cambiar de página, lo hacemos ANTES de crear el radio
if "pagina_pendiente" in st.session_state:
    st.session_state.pagina_actual = st.session_state.pagina_pendiente
    del st.session_state.pagina_pendiente

pagina_actual = st.radio(
    "Navegación",
    OPCIONES_PAGINA,
    horizontal=True,
    key="pagina_actual",
    label_visibility="collapsed"
)


# --- MEMORIA DE LA APLICACIÓN (SESSION STATE) ---
if 'pagina_catalogo' not in st.session_state:
    st.session_state.pagina_catalogo = 1

# --- NUEVO: Memoria para las fotos personalizadas ---
if 'imagenes_asignadas' not in st.session_state:
    st.session_state.imagenes_asignadas = {}
if 'contador_fotos' not in st.session_state:
    st.session_state.contador_fotos = 0
# --- NUEVO: Memoria para guardar los resultados de búsqueda ---
if 'resultados_busqueda' not in st.session_state:
    st.session_state.resultados_busqueda = []

def reset_pagina():
    # Si ella cambia de género, regresamos a la página 1
    st.session_state.pagina_catalogo = 1


def mostrar_paginacion_catalogo(posicion):
    col_anterior, col_pagina, col_siguiente = st.columns([1, 1, 1])

    with col_anterior:
        if st.button(
            "⬅️ Anterior",
            key=f"catalogo_anterior_{posicion}",
            width="stretch",
            disabled=st.session_state.pagina_catalogo <= 1
        ):
            st.session_state.pagina_catalogo -= 1
            st.session_state.subir_catalogo = True
            st.rerun()

    with col_pagina:
        st.markdown(
            f"""
            <div style="text-align:center; font-weight:700; color:#4a044e; padding-top:8px;">
                Página {st.session_state.pagina_catalogo}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_siguiente:
        if st.button(
            "Siguiente ➡️",
            key=f"catalogo_siguiente_{posicion}",
            width="stretch"
        ):
            st.session_state.pagina_catalogo += 1
            st.session_state.subir_catalogo = True
            st.rerun()


def limpiar_estado_drama(id_kdrama):
    id_kdrama = int(float(id_kdrama))

    version_key = f"version_drama_{id_kdrama}"

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    st.session_state[version_key] += 1

def obtener_key_checkbox(prefijo_key, id_kdrama):
    id_kdrama = int(float(id_kdrama))
    version = st.session_state.get(f"version_drama_{id_kdrama}", 0)

    return f"{prefijo_key}_{id_kdrama}_{version}"

def limpiar_estado_favorito(id_kdrama):
    id_kdrama = int(float(id_kdrama))

    version_key = f"version_favorito_{id_kdrama}"

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    st.session_state[version_key] += 1


def obtener_key_favorito(id_kdrama):
    id_kdrama = int(float(id_kdrama))
    version = st.session_state.get(f"version_favorito_{id_kdrama}", 0)

    return f"favorito_{id_kdrama}_{version}"

df_vistos = cargar_vistos()
lista_vistos_ids = df_vistos['id'].tolist() if not df_vistos.empty else []
df_por_ver = cargar_por_ver()
lista_por_ver_ids = df_por_ver["id"].tolist() if not df_por_ver.empty else []
total_por_ver = len(lista_por_ver_ids)


total_recuerdos = 0

if not df_vistos.empty and "recuerdo" in df_vistos.columns:
    total_recuerdos = df_vistos["recuerdo"].fillna("").astype(str).str.strip().ne("").sum()

logros_desbloqueados = calcular_logros(
    total_vistos=len(lista_vistos_ids),
    total_recuerdos=total_recuerdos
)
total_favoritos = 0

if not df_vistos.empty and "favorito" in df_vistos.columns:
    total_favoritos = df_vistos["favorito"].sum()

promedio_calificacion = 0

if not df_vistos.empty and "calificacion" in df_vistos.columns:
    calificaciones_validas = df_vistos[df_vistos["calificacion"] > 0]["calificacion"]

    if not calificaciones_validas.empty:
        promedio_calificacion = round(calificaciones_validas.mean(), 1)

mostrar_dashboard(
    vistos=len(lista_vistos_ids),
    recuerdos=total_recuerdos,
    favoritos=total_favoritos,
    logros=len(logros_desbloqueados),
    promedio=promedio_calificacion,
    por_ver=total_por_ver
)

mostrar_logros(logros_desbloqueados)


# PESTAÑA 1: CATÁLOGO POPULAR
if pagina_actual == "📺 Catálogo":
    if st.session_state.pop("subir_catalogo", False):
        id_inicio_catalogo = f"catalogo-inicio-{st.session_state.pagina_catalogo}"

        st.html(
            f"""
            <div id="{id_inicio_catalogo}"></div>
            <script>
                setTimeout(function() {{
                    document.getElementById("{id_inicio_catalogo}")?.scrollIntoView({{
                        behavior: "smooth",
                        block: "start"
                    }});
                }}, 150);
            </script>
            """,
            unsafe_allow_javascript=True
        )

    col_titulo, col_filtro = st.columns([2, 1])
    with col_titulo:
        st.subheader("Lo más popular del momento")
    with col_filtro:
        # Menú desplegable para los géneros
        genero_seleccionado = st.selectbox(
            "🎭 Género",
            list(GENEROS_TMDB.keys()),
            on_change=reset_pagina,
            key="filtro_genero_catalogo"
        )
    
    # Traducimos el texto seleccionado a su ID numérico
    id_genero_filtro = GENEROS_TMDB[genero_seleccionado]

    mostrar_paginacion_catalogo("superior")

    # Llamamos a la API con la página actual y el género
    kdramas = obtener_kdramas_populares(st.session_state.pagina_catalogo, id_genero_filtro)
    
    columnas = st.columns(4) 
    for indice, drama in enumerate(kdramas):
        with columnas[indice % 4]:
            mostrar_tarjeta(drama, "cat", lista_vistos_ids, lista_por_ver_ids)
            
    st.divider()

    mostrar_paginacion_catalogo("inferior")
    
# PESTAÑA 2: BUSCADOR MEJORADO (CON FORMULARIO)
if pagina_actual == "🔍 Buscar Serie":
    st.subheader("Encuentra una serie específica")
    st.caption("Busca por título y explora los resultados disponibles en TMDB.")
    
    # Creamos un formulario que agrupa la caja de texto y el botón
    with st.form(key='formulario_busqueda', clear_on_submit=False):
        busqueda = st.text_input(
            "Escribe el nombre de la serie:",
            placeholder="Escribe el nombre de un KDrama...",
            label_visibility="collapsed"
        )

        # Al estar dentro del form, el botón se activa automáticamente con Enter.
        # Mantenerlo como hijo directo evita un aviso fugaz de Streamlit.
        submit_button = st.form_submit_button(
            label="🔍 Buscar en TMDB",
            width="content"
        )
            
        if submit_button:
            if busqueda:
                st.session_state.resultados_busqueda = buscar_kdrama(busqueda)
            else:
                st.session_state.resultados_busqueda = []
                st.warning("Por favor, escribe un nombre.")

    # Mostramos los resultados
    if st.session_state.resultados_busqueda:
        cantidad_resultados = len(st.session_state.resultados_busqueda)
        texto_resultados = (
            "resultado encontrado"
            if cantidad_resultados == 1
            else "resultados encontrados"
        )

        st.markdown(
            f"""
            <div class="search-results-count">
                <span>✨</span>
                <strong>{cantidad_resultados}</strong> {texto_resultados}
            </div>
            """,
            unsafe_allow_html=True
        )

        cols_busqueda = st.columns(4)
        for idx, res in enumerate(st.session_state.resultados_busqueda):
            with cols_busqueda[idx % 4]:
                mostrar_tarjeta(res, "bus", lista_vistos_ids, lista_por_ver_ids)
    elif not st.session_state.resultados_busqueda and "busqueda" in locals() and busqueda:
        busqueda_segura = html.escape(busqueda.strip())

        st.markdown(
            f"""
            <div class="search-empty-state">
                <div class="search-empty-icon">🔎</div>
                <strong>No encontramos “{busqueda_segura}”</strong>
                <span>Prueba con otro título o revisa cómo está escrito.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# PESTAÑA 3: LISTA PERSONAL CON MINIATURAS Y BOTÓN PARA QUITAR
if pagina_actual == "✨ Mis KDramas Vistos":
    st.subheader("Tu historial de series terminadas")

    df_vistos_actualizado = cargar_vistos()
    
    if not df_vistos_actualizado.empty:
        # --- TOP DE JULY ---
        df_top = df_vistos_actualizado.copy()

        if "calificacion" not in df_top.columns:
            df_top["calificacion"] = 0

        df_top["calificacion"] = pd.to_numeric(
            df_top["calificacion"],
            errors="coerce"
        ).fillna(0).astype(int)

        df_top = df_top[df_top["calificacion"] > 0]
        df_top = df_top.sort_values("calificacion", ascending=False).head(3)

        if not df_top.empty:
            with st.expander("👑 Top de July"):
                st.markdown(
                    """
                    <div class="top-july-intro">
                        <span class="top-july-intro-icon">✨</span>
                        <div>
                            <strong>El podio personal de July</strong>
                            <small>Sus historias mejor calificadas del historial</small>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                cols_top = st.columns(3)
                posiciones_top = [
                    ("🥇", "Primer lugar"),
                    ("🥈", "Segundo lugar"),
                    ("🥉", "Tercer lugar"),
                ]

                for indice, (_, drama_top) in enumerate(df_top.iterrows()):
                    with cols_top[indice]:
                        titulo_top = html.escape(str(drama_top["titulo"]))
                        calificacion_top = int(drama_top["calificacion"])
                        medalla_top, posicion_top = posiciones_top[indice]

                        if pd.notna(drama_top["poster"]) and drama_top["poster"]:
                            poster_top = (
                                f'<img src="{IMG_URL_SMALL + drama_top["poster"]}" '
                                'class="top-july-poster" loading="lazy">'
                            )
                        else:
                            poster_top = '<div class="top-july-poster-fallback">💜</div>'

                        st.markdown(
                            f"""
                            <div class="top-july-card top-july-card-{indice + 1}">
                                <div class="top-july-medal">{medalla_top}</div>
                                {poster_top}
                                <div class="top-july-info">
                                    <div class="top-july-place">{posicion_top}</div>
                                    <div class="top-july-title">{titulo_top}</div>
                                    <div class="top-july-score">⭐ {calificacion_top}/10</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        col_buscar_vistos, col_filtro_vistos, col_orden_vistos = st.columns([2, 1, 1])

        with col_buscar_vistos:
            busqueda_vistos = st.text_input(
                "Buscar en tus KDramas vistos",
                placeholder="Escribe el nombre de una serie...",
                key="busqueda_vistos"
            )

        with col_filtro_vistos:
            filtro_vistos = st.selectbox(
                "Filtrar por",
                [
                    "Todos",
                    "⭐ Favoritos",
                    "📖 Con recuerdo",
                    "📝 Sin recuerdo",
                    "🌟 Calificados",
                    "❔ Sin calificar",
                    "🏆 Mejor calificados"
                ],
                key="filtro_vistos"
            )

        with col_orden_vistos:
            orden_vistos = st.selectbox(
                "Ordenar por",
                [
                    "Más recientes",
                    "A-Z",
                    "Z-A",
                    "Mejor calificación",
                    "Menor calificación"
                ],
                key="orden_vistos"
            )
        df_filtrado = df_vistos_actualizado.copy()

        # Aseguramos columnas por si algún dato viejo no las tiene
        if "favorito" not in df_filtrado.columns:
            df_filtrado["favorito"] = False

        if "recuerdo" not in df_filtrado.columns:
            df_filtrado["recuerdo"] = ""

        if "calificacion" not in df_filtrado.columns:
            df_filtrado["calificacion"] = 0

        df_filtrado["recuerdo"] = df_filtrado["recuerdo"].fillna("").astype(str)
        df_filtrado["calificacion"] = pd.to_numeric(
            df_filtrado["calificacion"],
            errors="coerce"
        ).fillna(0).astype(int)

        if filtro_vistos == "⭐ Favoritos":
            df_filtrado = df_filtrado[df_filtrado["favorito"] == True]

        elif filtro_vistos == "📖 Con recuerdo":
            df_filtrado = df_filtrado[
                df_filtrado["recuerdo"].str.strip() != ""
            ]

        elif filtro_vistos == "📝 Sin recuerdo":
            df_filtrado = df_filtrado[
                df_filtrado["recuerdo"].str.strip() == ""
            ]

        elif filtro_vistos == "🌟 Calificados":
            df_filtrado = df_filtrado[
                df_filtrado["calificacion"] > 0
            ].sort_values("calificacion", ascending=False)

        elif filtro_vistos == "❔ Sin calificar":
            df_filtrado = df_filtrado[
                df_filtrado["calificacion"] == 0
            ]

        elif filtro_vistos == "🏆 Mejor calificados":
            df_filtrado = df_filtrado[
                df_filtrado["calificacion"] >= 8
            ].sort_values("calificacion", ascending=False)
        # --- BÚSQUEDA EN VISTOS ---
        if busqueda_vistos.strip():
            df_filtrado = df_filtrado[
                df_filtrado["titulo"]
                .fillna("")
                .astype(str)
                .str.contains(busqueda_vistos.strip(), case=False, na=False)
            ]

        # --- ORDENAMIENTO ---
        if orden_vistos == "Más recientes":
            df_filtrado = df_filtrado.iloc[::-1]

        elif orden_vistos == "A-Z":
            df_filtrado = df_filtrado.sort_values("titulo", ascending=True)

        elif orden_vistos == "Z-A":
            df_filtrado = df_filtrado.sort_values("titulo", ascending=False)

        elif orden_vistos == "Mejor calificación":
            df_filtrado = df_filtrado.sort_values("calificacion", ascending=False)

        elif orden_vistos == "Menor calificación":
            df_filtrado = df_filtrado.sort_values("calificacion", ascending=True)

        cantidad_filtrada = len(df_filtrado)
        cantidad_total = len(df_vistos_actualizado)
        texto_historias = "historia terminada" if cantidad_total == 1 else "historias terminadas"

        st.markdown(
            f"""
            <div class="watched-results-count">
                <span class="watched-results-icon">✓</span>
                Mostrando <strong>{cantidad_filtrada}</strong> de
                <strong>{cantidad_total}</strong> {texto_historias}
            </div>
            """,
            unsafe_allow_html=True
        )

        if not df_filtrado.empty:
            for i, row in df_filtrado.iterrows():
                id_drama_lista = int(row["id"])

                mostrar_kdrama_visto(
                    row=row,
                    id_drama_lista=id_drama_lista,
                    obtener_key_favorito=obtener_key_favorito,
                    limpiar_estado_favorito=limpiar_estado_favorito,
                    limpiar_estado_drama=limpiar_estado_drama,
                )

                st.write("")

        else:
            st.info("No hay KDramas que coincidan con este filtro.")

    else:
        st.info("Aún no has marcado ningún KDrama como visto. ¡Explora el catálogo o usa el buscador!")

# PESTAÑA 4: FAVORITOS
if pagina_actual == "⭐ Favoritos":
    st.subheader("⭐ Tus KDramas favoritos")

    df_favoritos = cargar_vistos()

    if not df_favoritos.empty and "favorito" in df_favoritos.columns:
        df_favoritos = df_favoritos[df_favoritos["favorito"] == True]

    if not df_favoritos.empty:
        columnas_favoritos = st.columns(3)

        for i, row in df_favoritos.iterrows():
            id_drama_favorito = int(row["id"])

            with columnas_favoritos[i % 3]:
                mostrar_favorito(
                    row,
                    id_drama_favorito,
                    limpiar_estado_favorito
                )

    else:
        st.info("Aún no has marcado ningún KDrama como favorito.")

# PESTAÑA 5: POR VER
if pagina_actual == "💫 Por Ver":
    st.subheader("💫 KDramas por ver")

    df_por_ver_actualizado = cargar_por_ver()

    if not df_por_ver_actualizado.empty:
        col_buscar_por_ver, col_orden_por_ver = st.columns([2, 1])

        with col_buscar_por_ver:
            busqueda_por_ver = st.text_input(
                "Buscar en Por Ver",
                placeholder="Escribe el nombre de una serie...",
                key="busqueda_por_ver"
            )

        with col_orden_por_ver:
            orden_por_ver = st.selectbox(
                "Ordenar Por Ver",
                [
                    "Más recientes",
                    "A-Z",
                    "Z-A"
                ],
                key="orden_por_ver"
            )

        df_por_ver_filtrado = df_por_ver_actualizado.copy()

        if busqueda_por_ver.strip():
            df_por_ver_filtrado = df_por_ver_filtrado[
                df_por_ver_filtrado["titulo"]
                .fillna("")
                .astype(str)
                .str.contains(busqueda_por_ver.strip(), case=False, na=False)
            ]

        if orden_por_ver == "Más recientes":
            df_por_ver_filtrado = df_por_ver_filtrado.iloc[::-1]

        elif orden_por_ver == "A-Z":
            df_por_ver_filtrado = df_por_ver_filtrado.sort_values("titulo", ascending=True)

        elif orden_por_ver == "Z-A":
            df_por_ver_filtrado = df_por_ver_filtrado.sort_values("titulo", ascending=False)

        df_por_ver_filtrado = df_por_ver_filtrado.reset_index(drop=True)

        cantidad_por_ver_filtrada = len(df_por_ver_filtrado)
        cantidad_por_ver_total = len(df_por_ver_actualizado)
        texto_pendientes = (
            "historia pendiente"
            if cantidad_por_ver_total == 1
            else "historias pendientes"
        )

        st.markdown(
            f"""
            <div class="watchlist-results-count">
                <span class="watchlist-results-icon">💫</span>
                Mostrando <strong>{cantidad_por_ver_filtrada}</strong> de
                <strong>{cantidad_por_ver_total}</strong> {texto_pendientes}
            </div>
            """,
            unsafe_allow_html=True
        )

        if not df_por_ver_filtrado.empty:
            for inicio_fila in range(0, len(df_por_ver_filtrado), 3):
                fila_por_ver = df_por_ver_filtrado.iloc[inicio_fila:inicio_fila + 3]
                cantidad_en_fila = len(fila_por_ver)

                if cantidad_en_fila == 1:
                    columnas_por_ver = st.columns([1, 1, 1])
                    posiciones_columnas = [1]

                elif cantidad_en_fila == 2:
                    columnas_por_ver = st.columns([0.5, 1, 1, 0.5])
                    posiciones_columnas = [1, 2]

                else:
                    columnas_por_ver = st.columns(3)
                    posiciones_columnas = [0, 1, 2]

                for posicion, (_, row) in enumerate(fila_por_ver.iterrows()):
                    id_por_ver = int(row["id"])

                    with columnas_por_ver[posiciones_columnas[posicion]]:
                        mostrar_por_ver_card(row, id_por_ver)
        else:
            st.markdown(
                """
                <div class="watchlist-empty-state">
                    <div class="watchlist-empty-icon">🔎</div>
                    <strong>No encontramos esa historia</strong>
                    <span>Prueba con otro título o limpia la búsqueda.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.markdown(
            """
            <div class="watchlist-empty-state">
                <div class="watchlist-empty-icon">💫</div>
                <strong>Tu lista Por Ver está esperando</strong>
                <span>
                    Explora el catálogo y guarda aquí las historias
                    que quieras descubrir después.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

# PESTAÑA 6: ESTADÍSTICAS
if pagina_actual == "📊 Estadísticas":
    st.subheader("📊 Estadísticas de JulyVerse")

    df_estadisticas = cargar_vistos()

    mostrar_estadisticas(df_estadisticas)
