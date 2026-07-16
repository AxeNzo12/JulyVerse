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
    layout="wide"
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
                use_container_width=True
            )
    else:
        st.caption("Aún no hay datos para respaldar.")

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
    promedio=promedio_calificacion
)

mostrar_logros(logros_desbloqueados)


OPCIONES_PAGINA = [
    "📺 Catálogo",
    "🔍 Buscar Serie",
    "✨ Mis KDramas Vistos",
    "⭐ Favoritos"
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

# PESTAÑA 1: CATÁLOGO POPULAR
if pagina_actual == "📺 Catálogo":
    col_titulo, col_filtro = st.columns([2, 1])
    with col_titulo:
        st.subheader("Lo más popular del momento")
    with col_filtro:
        # Menú desplegable para los géneros
        genero_seleccionado = st.selectbox(
            "Filtrar por género:", 
            list(GENEROS_TMDB.keys()), 
            on_change=reset_pagina
        )
    
    # Traducimos el texto seleccionado a su ID numérico
    id_genero_filtro = GENEROS_TMDB[genero_seleccionado]
    
    # Llamamos a la API con la página actual y el género
    kdramas = obtener_kdramas_populares(st.session_state.pagina_catalogo, id_genero_filtro)
    
    columnas = st.columns(4) 
    for indice, drama in enumerate(kdramas):
        with columnas[indice % 4]:
            mostrar_tarjeta(drama, "cat", lista_vistos_ids)
            
    st.divider()
    
    # Botón mágico para cargar 20 más
    col_espacio1, col_boton, col_espacio2 = st.columns([1, 1, 1])
    with col_boton:
        if st.button("➕ Cargar más KDramas", use_container_width=True):
            st.session_state.pagina_catalogo += 1
            st.rerun()
# PESTAÑA 2: BUSCADOR
# PESTAÑA 2: BUSCADOR MEJORADO (CON FORMULARIO)
if pagina_actual == "🔍 Buscar Serie":
    st.subheader("Encuentra una serie específica")
    
    # Creamos un formulario que agrupa la caja de texto y el botón
    with st.form(key='formulario_busqueda', clear_on_submit=False):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            busqueda = st.text_input("Escribe el nombre de la serie:", label_visibility="collapsed")
        with col_btn:
            # Al estar dentro del form, el botón se activa automáticamente con Enter
            submit_button = st.form_submit_button(label="🔍 Buscar", use_container_width=True)
            
        if submit_button:
            if busqueda:
                st.session_state.resultados_busqueda = buscar_kdrama(busqueda)
            else:
                st.session_state.resultados_busqueda = []
                st.warning("Por favor, escribe un nombre.")

    # Mostramos los resultados
    if st.session_state.resultados_busqueda:
        cols_busqueda = st.columns(4)
        for idx, res in enumerate(st.session_state.resultados_busqueda):
            with cols_busqueda[idx % 4]:
                mostrar_tarjeta(res, "bus", lista_vistos_ids)
    elif not st.session_state.resultados_busqueda and "busqueda" in locals() and busqueda:
        st.info("No se encontraron resultados.")

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
                cols_top = st.columns(3)

                for indice, (_, drama_top) in enumerate(df_top.iterrows()):
                    with cols_top[indice]:
                        titulo_top = drama_top["titulo"]
                        calificacion_top = int(drama_top["calificacion"])

                        if pd.notna(drama_top["poster"]) and drama_top["poster"]:
                            st.image(IMG_URL_SMALL + drama_top["poster"], width=120)

                        st.markdown(f"**💜 {titulo_top}**")
                        st.caption(f"⭐ {calificacion_top}/10")

        filtro_vistos = st.radio(
            "Filtrar KDramas",
            [
                "Todos",
                "⭐ Favoritos",
                "📖 Con recuerdo",
                "📝 Sin recuerdo",
                "🌟 Calificados",
                "❔ Sin calificar",
                "🏆 Mejor calificados"
            ],
            horizontal=True,
            key="filtro_vistos"
        )
        col_buscar_vistos, col_orden_vistos = st.columns([2, 1])

        with col_buscar_vistos:
            busqueda_vistos = st.text_input(
                "Buscar en tus KDramas vistos",
                placeholder="Escribe el nombre de una serie...",
                key="busqueda_vistos"
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

        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_vistos_actualizado)} KDramas")

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