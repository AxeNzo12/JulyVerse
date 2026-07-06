import os
import pandas as pd

ARCHIVO_CSV = "mis_kdramas.csv"


def cargar_vistos():
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)

        if "poster" not in df.columns:
            df["poster"] = ""

        if "recuerdo" not in df.columns:
            df["recuerdo"] = ""

        df["recuerdo"] = df["recuerdo"].fillna("").astype(str)
        if not df.empty:
            df["id"] = pd.to_numeric(df["id"], errors="coerce")
            df = df.dropna(subset=["id"])
            df["id"] = df["id"].astype(int)

        return df

    return pd.DataFrame(columns=["id", "titulo", "poster", "recuerdo"])


def actualizar_visto(id_kdrama, titulo, poster, visto):
    df = cargar_vistos()

    id_kdrama = int(float(id_kdrama))

    if visto:
        if id_kdrama not in df["id"].values:
            nuevo_registro = pd.DataFrame({
                "id": [id_kdrama],
                "titulo": [titulo],
                "poster": [poster],
                "recuerdo": [""]
            })

            df = pd.concat([df, nuevo_registro], ignore_index=True)

    else:
        df = df[df["id"] != id_kdrama]

        if df.empty:
            df = pd.DataFrame(columns=["id", "titulo", "poster", "recuerdo"])

    df.to_csv(ARCHIVO_CSV, index=False)


def actualizar_recuerdo(id_kdrama, recuerdo):
    df = cargar_vistos()

    id_kdrama = int(float(id_kdrama))

    if not df.empty:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)
    
    # Aseguramos que la columna sea de texto
    df["recuerdo"] = df["recuerdo"].fillna("").astype(str)

    df.loc[df["id"] == id_kdrama, "recuerdo"] = recuerdo
    
    df.to_csv(ARCHIVO_CSV, index=False)