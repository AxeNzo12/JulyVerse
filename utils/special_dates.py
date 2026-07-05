from datetime import datetime

SPECIAL_DATES = {
    "01-01": (
        "🎆 Feliz Año Nuevo, July.",
        "Nuevo año, nuevas historias y nuevos recuerdos para JulyVerse."
    ),
    "02-14": (
        "💜 Feliz San Valentín, July.",
        "Gracias por compartir este pequeño universo conmigo."
    ),
    "12-24": (
        "🎄 Feliz Navidad, July.",
        "Espero que hoy encuentres una historia tan bonita como esta fecha."
    ),
    "12-25": (
        "🎁 Feliz Navidad, July.",
        "Que este día también se convierta en un recuerdo especial."
    ),
    "01-07": (
        "🎉Te amo preciosa feliz cumpleaños",
        "Pasala hermoso mi reina"
    )
}

def obtener_fecha_especial():
    hoy = datetime.now().strftime("%m-%d")
    return SPECIAL_DATES.get(hoy)