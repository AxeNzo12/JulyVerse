import os
import pandas as pd

ARCHIVO_CSV = "mis_kdramas.csv"


def cargar_vistos():
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)

        if "poster" not in df.columns:
            df["poster"] = ""

        if not df.empty:
            df["id"] = pd.to_numeric(df["id"], errors="coerce")
            df = df.dropna(subset=["id"])
            df["id"] = df["id"].astype(int)

        return df

    return pd.DataFrame(columns=["id", "titulo", "poster"])


def actualizar_visto(id_kdrama, titulo, poster, visto):
    df = cargar_vistos()

    id_kdrama = int(float(id_kdrama))

    if visto:
        if id_kdrama not in df["id"].values:
            nuevo_registro = pd.DataFrame({
                "id": [id_kdrama],
                "titulo": [titulo],
                "poster": [poster]
            })

            df = pd.concat([df, nuevo_registro], ignore_index=True)

    else:
        df = df[df["id"] != id_kdrama]

        if df.empty:
            df = pd.DataFrame(columns=["id", "titulo", "poster"])

    df.to_csv(ARCHIVO_CSV, index=False)