import os

import pandas as pd

from services.github_backup import respaldar_archivo

ARCHIVO_NO_INTERESAN = "no_me_interesan.csv"
COLUMNAS_NO_INTERESAN = ["id", "titulo"]


def cargar_no_interesan():
    if not os.path.exists(ARCHIVO_NO_INTERESAN):
        return pd.DataFrame(columns=COLUMNAS_NO_INTERESAN)

    try:
        df = pd.read_csv(ARCHIVO_NO_INTERESAN)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=COLUMNAS_NO_INTERESAN)

    if "id" not in df.columns:
        df["id"] = pd.NA

    if "titulo" not in df.columns:
        df["titulo"] = ""

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)
    df["titulo"] = df["titulo"].fillna("").astype(str)

    return (
        df[COLUMNAS_NO_INTERESAN]
        .drop_duplicates(subset=["id"], keep="first")
        .reset_index(drop=True)
    )


def agregar_no_interesa(id_kdrama, titulo):
    df = cargar_no_interesan()
    id_kdrama = int(float(id_kdrama))

    if id_kdrama not in df["id"].values:
        nuevo = pd.DataFrame({
            "id": [id_kdrama],
            "titulo": [str(titulo)],
        })
        df = pd.concat([df, nuevo], ignore_index=True)

    df.to_csv(ARCHIVO_NO_INTERESAN, index=False)
    respaldar_archivo(ARCHIVO_NO_INTERESAN)


def restaurar_recomendacion(id_kdrama):
    df = cargar_no_interesan()
    id_kdrama = int(float(id_kdrama))
    df = df[df["id"] != id_kdrama]
    df.to_csv(ARCHIVO_NO_INTERESAN, index=False)
    respaldar_archivo(ARCHIVO_NO_INTERESAN)
