import base64

from utils.paths import IMAGES

CARPETA_RECUERDOS = IMAGES / "recuerdos"

IMAGENES_RECUERDO = [
    CARPETA_RECUERDOS / "july1.jpeg",
    CARPETA_RECUERDOS / "july2.jpeg",
    CARPETA_RECUERDOS / "july3.jpeg",
    CARPETA_RECUERDOS / "july4.jpeg",
    CARPETA_RECUERDOS / "july5.jpeg",
]

def imagen_a_base64(ruta):
    try:
        with open(ruta, "rb") as img:
            return base64.b64encode(img.read()).decode("utf-8")
    except:
        return ""

def obtener_recuerdo_por_indice(indice):
    return IMAGENES_RECUERDO[indice % len(IMAGENES_RECUERDO)]