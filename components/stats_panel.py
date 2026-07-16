import pandas as pd
import streamlit as st

from services.tmdb import IMG_URL_SMALL


def preparar_datos(df):
    df = df.copy()

    if "favorito" not in df.columns:
        df["favorito"] = False

    if "recuerdo" not in df.columns:
        df["recuerdo"] = ""

    if "calificacion" not in df.columns:
        df["calificacion"] = 0

    df["recuerdo"] = df["recuerdo"].fillna("").astype(str)

    df["favorito"] = (
        df["favorito"]
        .fillna(False)
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes", "si", "sí"])
    )

    df["calificacion"] = (
        pd.to_numeric(df["calificacion"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return df


def mostrar_estadisticas(df_vistos):
    if df_vistos.empty:
        st.info("Aún no hay datos suficientes para mostrar estadísticas.")
        return

    df = preparar_datos(df_vistos)

    total_vistos = len(df)
    total_favoritos = int(df["favorito"].sum())
    total_recuerdos = int(df["recuerdo"].str.strip().ne("").sum())

    calificados = df[df["calificacion"] > 0]

    promedio = 0
    if not calificados.empty:
        promedio = round(calificados["calificacion"].mean(), 1)

    porcentaje_recuerdos = round((total_recuerdos / total_vistos) * 100, 1)
    porcentaje_favoritos = round((total_favoritos / total_vistos) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📺 Total vistos", total_vistos)

    with c2:
        st.metric("⭐ Favoritos", f"{porcentaje_favoritos}%")

    with c3:
        st.metric("📖 Con recuerdo", f"{porcentaje_recuerdos}%")

    with c4:
        if promedio > 0:
            st.metric("🌟 Promedio", f"{promedio}/10")
        else:
            st.metric("🌟 Promedio", "-")

    st.divider()

    if not calificados.empty:
        st.subheader("👑 Mejor calificado")

        mejor = calificados.sort_values("calificacion", ascending=False).iloc[0]

        col_img, col_info = st.columns([1, 4])

        with col_img:
            if pd.notna(mejor["poster"]) and mejor["poster"]:
                st.image(IMG_URL_SMALL + mejor["poster"], width=120)
            else:
                st.markdown("💜")

        with col_info:
            st.markdown(f"### 💜 {mejor['titulo']}")
            st.markdown(f"⭐ **{int(mejor['calificacion'])}/10**")

            if str(mejor["recuerdo"]).strip():
                st.caption(f"📖 {mejor['recuerdo']}")

        st.divider()

        st.subheader("📊 Distribución de calificaciones")

        distribucion = (
            calificados["calificacion"]
            .value_counts()
            .reindex(range(1, 11), fill_value=0)
            .sort_index()
        )

        st.bar_chart(distribucion)

        st.divider()

        st.subheader("🏆 Top 5 de July")

        top_5 = calificados.sort_values("calificacion", ascending=False).head(5)

        tabla_top = top_5[["titulo", "calificacion", "favorito"]].copy()
        tabla_top["favorito"] = tabla_top["favorito"].apply(lambda x: "⭐" if x else "")

        tabla_top = tabla_top.rename(
            columns={
                "titulo": "KDrama",
                "calificacion": "Calificación",
                "favorito": "Favorito"
            }
        )

        st.dataframe(tabla_top, hide_index=True, width="stretch")

    else:
        st.info("Todavía no hay KDramas calificados. Cuando califiques alguno, aquí aparecerán las estadísticas.")