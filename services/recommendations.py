from collections import defaultdict

import pandas as pd

from services.tmdb import (
    obtener_kdramas_por_generos,
    obtener_perfil_kdrama,
    obtener_trabajos_actor,
)


LIMITE_SEMILLAS = 3
LIMITE_ACTORES = 4


def _normalizar_vistos(df_vistos):
    df = df_vistos.copy()

    if "favorito" not in df.columns:
        df["favorito"] = False

    if "calificacion" not in df.columns:
        df["calificacion"] = 0

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

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)
    df["_orden"] = range(len(df))

    return df


def _seleccionar_semillas(df_vistos):
    df = _normalizar_vistos(df_vistos)

    if df.empty:
        return []

    df["_prioridad"] = (
        df["calificacion"].where(df["calificacion"] > 0, 5)
        + df["favorito"].astype(int) * 2
    )

    df = df.sort_values(
        ["_prioridad", "_orden"],
        ascending=[False, False]
    )

    return df.head(LIMITE_SEMILLAS).to_dict("records")


def _es_serie_coreana(drama):
    paises = drama.get("origin_country", []) or []
    idioma_original = drama.get("original_language", "")

    return "KR" in paises or idioma_original == "ko"


def _obtener_id(drama):
    try:
        return int(drama.get("id", 0))
    except (TypeError, ValueError):
        return 0


def _agregar_candidato(
    candidatos,
    drama,
    ids_excluidos,
    puntos_origen=0,
    semilla="",
    actor=""
):
    id_drama = _obtener_id(drama)

    if (
        not id_drama
        or id_drama in ids_excluidos
        or not _es_serie_coreana(drama)
    ):
        return

    if id_drama not in candidatos:
        candidatos[id_drama] = {
            "drama": dict(drama),
            "puntos_origen": 0.0,
            "semillas": set(),
            "actores": set(),
        }

    candidato = candidatos[id_drama]
    candidato["puntos_origen"] += float(puntos_origen)

    if semilla:
        candidato["semillas"].add(str(semilla))

    if actor:
        candidato["actores"].add(str(actor))

    # Algunas fuentes de TMDB traen menos campos. Conservamos los más completos.
    for campo, valor in drama.items():
        if valor and not candidato["drama"].get(campo):
            candidato["drama"][campo] = valor


def _obtener_generos_drama(drama):
    ids_generos = drama.get("genre_ids", []) or []

    if not ids_generos and drama.get("genres"):
        ids_generos = [
            genero.get("id")
            for genero in drama["genres"]
            if genero.get("id")
        ]

    return [int(id_genero) for id_genero in ids_generos]


def _obtener_nivel_afinidad(puntuacion):
    if puntuacion >= 12:
        return {
            "texto": "Muy compatible",
            "icono": "💜",
            "clase": "high",
        }

    if puntuacion >= 10:
        return {
            "texto": "Buena opción",
            "icono": "✨",
            "clase": "medium",
        }

    return {
        "texto": "Podría gustarle",
        "icono": "🌙",
        "clase": "soft",
    }


def generar_recomendaciones(df_vistos, limite=6, ids_ocultos=None):
    semillas = _seleccionar_semillas(df_vistos)
    ids_ocultos = [] if ids_ocultos is None else ids_ocultos

    if not semillas:
        return {
            "recomendaciones": [],
            "semillas": [],
            "generos": [],
            "actores": [],
        }

    ids_vistos = {
        int(id_kdrama)
        for id_kdrama in _normalizar_vistos(df_vistos)["id"].tolist()
    }
    ids_excluidos = ids_vistos | {
        int(id_kdrama)
        for id_kdrama in ids_ocultos
    }

    candidatos = {}
    preferencias_genero = defaultdict(float)
    nombres_generos = {}
    perfiles_semillas = []
    actores_preferidos = {}

    for semilla in semillas:
        perfil = obtener_perfil_kdrama(semilla["id"])

        if not perfil:
            continue

        titulo_semilla = semilla.get("titulo", perfil.get("name", ""))
        calificacion = int(semilla.get("calificacion", 0))
        favorito = bool(semilla.get("favorito", False))
        peso_semilla = max(calificacion, 6) + (2 if favorito else 0)

        perfiles_semillas.append((semilla, perfil))

        for genero in perfil.get("genres", []):
            id_genero = genero.get("id")
            nombre_genero = genero.get("name")

            if not id_genero:
                continue

            preferencias_genero[int(id_genero)] += peso_semilla

            if nombre_genero:
                nombres_generos[int(id_genero)] = str(nombre_genero)

        similares = perfil.get("similar", {}).get("results", [])
        bonus_similar = 3 + max(calificacion - 7, 0) * 0.5

        if favorito:
            bonus_similar += 0.75

        for drama in similares[:12]:
            _agregar_candidato(
                candidatos,
                drama,
                ids_excluidos,
                puntos_origen=bonus_similar,
                semilla=titulo_semilla,
            )

        reparto = perfil.get("aggregate_credits", {}).get("cast", [])

        # Tomamos pocos actores de cada semilla para que una sola serie
        # no ocupe todo el perfil de recomendaciones.
        for actor in reparto[:2]:
            id_actor = actor.get("id")
            nombre_actor = actor.get("name")

            if (
                id_actor
                and nombre_actor
                and int(id_actor) not in actores_preferidos
                and len(actores_preferidos) < LIMITE_ACTORES
            ):
                actores_preferidos[int(id_actor)] = str(nombre_actor)

    generos_principales = [
        id_genero
        for id_genero, _ in sorted(
            preferencias_genero.items(),
            key=lambda item: item[1],
            reverse=True
        )[:3]
    ]

    for drama in obtener_kdramas_por_generos(tuple(generos_principales)):
        _agregar_candidato(
            candidatos,
            drama,
            ids_excluidos,
            puntos_origen=1.25,
        )

    for id_actor, nombre_actor in actores_preferidos.items():
        trabajos = obtener_trabajos_actor(id_actor)

        for drama in trabajos.get("cast", []):
            if drama.get("media_type") != "tv":
                continue

            _agregar_candidato(
                candidatos,
                drama,
                ids_excluidos,
                puntos_origen=3.5,
                actor=nombre_actor,
            )

    if preferencias_genero:
        peso_genero_maximo = max(preferencias_genero.values())
    else:
        peso_genero_maximo = 1

    recomendaciones = []

    for candidato in candidatos.values():
        drama = candidato["drama"]
        ids_generos = _obtener_generos_drama(drama)
        generos_coincidentes = [
            id_genero
            for id_genero in ids_generos
            if id_genero in preferencias_genero
        ]

        puntos_genero = sum(
            (preferencias_genero[id_genero] / peso_genero_maximo) * 2.2
            for id_genero in generos_coincidentes[:3]
        )

        promedio_tmdb = float(drama.get("vote_average", 0) or 0)
        votos_tmdb = int(drama.get("vote_count", 0) or 0)
        puntos_calidad = min(promedio_tmdb, 10) * 0.2
        puntos_calidad += min(votos_tmdb / 100, 1) * 0.5

        puntuacion = (
            candidato["puntos_origen"]
            + puntos_genero
            + puntos_calidad
        )

        nombres_generos_coincidentes = [
            nombres_generos[id_genero]
            for id_genero in generos_coincidentes
            if id_genero in nombres_generos
        ]

        actores_comunes = sorted(candidato["actores"])
        semillas_comunes = sorted(candidato["semillas"])
        motivos = []

        if actores_comunes:
            motivos.append(f"Con {', '.join(actores_comunes[:2])}")

        if nombres_generos_coincidentes:
            motivos.append(
                f"Coincide en {', '.join(nombres_generos_coincidentes[:2])}"
            )

        if semillas_comunes:
            motivos.append(f"Porque a July le gustó {semillas_comunes[0]}")

        if not motivos and promedio_tmdb >= 7.5:
            motivos.append("Tiene una buena valoración en TMDB")

        if not motivos:
            motivos.append("Encaja con el perfil de July")

        drama["_motivos"] = motivos[:2]
        drama["_puntuacion_recomendacion"] = round(puntuacion, 2)
        drama["_afinidad"] = _obtener_nivel_afinidad(puntuacion)
        recomendaciones.append(drama)

    recomendaciones.sort(
        key=lambda drama: (
            drama.get("_puntuacion_recomendacion", 0),
            float(drama.get("vote_average", 0) or 0),
            int(drama.get("vote_count", 0) or 0),
        ),
        reverse=True
    )

    generos_resumen = [
        nombres_generos[id_genero]
        for id_genero in generos_principales
        if id_genero in nombres_generos
    ]

    return {
        "recomendaciones": recomendaciones[:int(limite)],
        "semillas": [
            str(semilla.get("titulo", ""))
            for semilla, _ in perfiles_semillas
            if semilla.get("titulo")
        ],
        "generos": generos_resumen,
        "actores": list(actores_preferidos.values()),
    }
