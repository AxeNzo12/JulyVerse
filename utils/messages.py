import random
from datetime import datetime

WELCOME_MESSAGES = [
    "Cada historia que terminas se convierte en un recuerdo.",
    "Hoy puede ser el día en que encuentres tu próximo drama favorito.",
    "Hay miles de historias esperando por ti.",
    "Disfruta cada episodio.",
    "Un episodio a la vez.",
    "Bienvenida a tu pequeño universo.",
    "Que hoy encuentres una historia que te haga sonreír.",
    "Siempre hay una nueva aventura esperando."
]

def obtener_bienvenida():

    hora = datetime.now().hour

    if 5 <= hora < 12:
        saludo = "🌅 Buenos días, July."

    elif 12 <= hora < 19:
        saludo = "☀️ Buenas tardes, July."

    else:
        saludo = "🌙 Buenas noches, July."

    mensaje = random.choice(WELCOME_MESSAGES)

    return saludo, mensaje