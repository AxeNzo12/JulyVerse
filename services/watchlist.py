import os
import pandas as pd

from services.github_backup import respaldar_archivo

ARCHIVO_POR_VER = "por_ver.csv"


def cargar_por_ver():
    if os.path.exists(ARCHIVO_POR_VER):
        df = pd.read_csv(ARCHIVO_POR_VER)

        if "id" not in df.columns:
            df["id"] = []

        if "titulo" not in df.columns:
            df["titulo"] = ""

        if "poster" not in df.columns:
            df["poster"] = ""

        if not df.empty:
            df["id"] = pd.to_numeric(df["id"], errors="coerce")
            df = df.dropna(subset=["id"])
            df["id"] = df["id"].astype(int)

        return df

    return pd.DataFrame(columns=["id", "titulo", "poster"])


def agregar_por_ver(id_kdrama, titulo, poster):
    df = cargar_por_ver()

    id_kdrama = int(float(id_kdrama))

    if id_kdrama not in df["id"].values:
        nuevo = pd.DataFrame({
            "id": [id_kdrama],
            "titulo": [titulo],
            "poster": [poster]
        })

        df = pd.concat([df, nuevo], ignore_index=True)

    df.to_csv(ARCHIVO_POR_VER, index=False)
    respaldar_archivo(ARCHIVO_POR_VER)


def eliminar_por_ver(id_kdrama):
    df = cargar_por_ver()

    id_kdrama = int(float(id_kdrama))

    if not df.empty:
        df = df[df["id"] != id_kdrama]

    df.to_csv(ARCHIVO_POR_VER, index=False)
    respaldar_archivo(ARCHIVO_POR_VER)
