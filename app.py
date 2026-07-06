import streamlit as st
import pandas as pd
from utils.paths import IMAGES, CSS
from utils.messages import obtener_bienvenida
from components.dashboard import mostrar_dashboard
from components.welcome import mostrar_bienvenida
from utils.special_dates import obtener_fecha_especial
from components.drama_card import mostrar_tarjeta
from components.memory_box import mostrar_caja_recuerdo
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
    actualizar_recuerdo,
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


df_vistos = cargar_vistos()
lista_vistos_ids = df_vistos['id'].tolist() if not df_vistos.empty else []


total_recuerdos = 0

if not df_vistos.empty and "recuerdo" in df_vistos.columns:
    total_recuerdos = df_vistos["recuerdo"].fillna("").astype(str).str.strip().ne("").sum()

logros_desbloqueados = calcular_logros(
    total_vistos=len(lista_vistos_ids),
    total_recuerdos=total_recuerdos
)

mostrar_dashboard(
    vistos=len(lista_vistos_ids),
    recuerdos=total_recuerdos,
    logros=len(logros_desbloqueados)
)

mostrar_logros(logros_desbloqueados)

# --- SISTEMA DE PESTAÑAS (TABS) ---
tab_catalogo, tab_buscar, tab_lista = st.tabs(["📺 Catálogo", "🔍 Buscar Serie", "✨ Mis KDramas Vistos"])

# PESTAÑA 1: CATÁLOGO POPULAR
with tab_catalogo:
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
with tab_buscar:
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
with tab_lista:
    st.subheader("Tu historial de series terminadas")
    
    # Recargamos los datos para tener la información fresca
    df_vistos_actualizado = cargar_vistos()
    
    if not df_vistos_actualizado.empty:
        for i, row in df_vistos_actualizado.iterrows():
            # Dividimos en 3 espacios: Imagen, Texto, Casilla
            id_drama_lista = int(row["id"])
            col_img, col_txt, col_check = st.columns([1, 8, 2])
            
            with col_img:
                if pd.notna(row['poster']) and row['poster']:
                    st.image(IMG_URL_SMALL + row['poster'], width=60)
            
            with col_txt:
                st.write("") # Espaciador
                st.write(f"💜 **{row['titulo']}**")
                mostrar_caja_recuerdo(row, id_drama_lista)

            with col_check:
                st.write("")

                if st.button("Quitar", key=f"btn_quitar_{id_drama_lista}", use_container_width=True):
                    actualizar_visto(id_drama_lista, row["titulo"], row["poster"], False)

                    limpiar_estado_drama(id_drama_lista)

                    st.session_state.resultados_busqueda = []
                    st.session_state.mensaje_toast = f"Quitaste '{row['titulo']}' de tu lista."

                    st.rerun()
                                    
            st.divider() # Línea de separación
    else:
        st.info("Aún no has marcado ningún KDrama como visto. ¡Explora el catálogo o usa el buscador!")