import base64
import re
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st


GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2026-03-10"
PATRON_REPOSITORIO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RAMA_RESPALDO = "main"
CARPETA_REMOTA = "datos"
ARCHIVOS_RESPALDADOS = {
    "mis_kdramas.csv",
    "por_ver.csv",
    "no_me_interesan.csv",
}


def _obtener_configuracion():
    try:
        token = str(st.secrets.get("GITHUB_BACKUP_TOKEN", "")).strip()
        repositorio = str(st.secrets.get("GITHUB_BACKUP_REPO", "")).strip()
    except (FileNotFoundError, KeyError):
        return "", ""

    if not PATRON_REPOSITORIO.fullmatch(repositorio):
        return "", ""

    return token, repositorio


def _crear_headers(token):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }


def probar_conexion_github():
    """Comprueba el repositorio sin crear ni modificar archivos."""
    token, repositorio = _obtener_configuracion()

    if not token or not repositorio:
        return False, "Faltan los Secrets del respaldo."

    try:
        respuesta = requests.get(
            f"{GITHUB_API_URL}/repos/{repositorio}",
            headers=_crear_headers(token),
            timeout=10,
        )
    except requests.RequestException:
        return False, "No se pudo conectar con GitHub."

    if respuesta.status_code == 401:
        return False, "GitHub rechazó el token."

    if respuesta.status_code == 403:
        return False, "El token no tiene permiso para acceder al repositorio."

    if respuesta.status_code == 404:
        return False, "No se encontró el repositorio de respaldo."

    if not respuesta.ok:
        return False, f"GitHub respondió con el código {respuesta.status_code}."

    datos = respuesta.json()
    permisos = datos.get("permissions", {})

    if permisos.get("push") is False:
        return False, "El token puede leer el repositorio, pero no escribir en él."

    if not datos.get("private", False):
        return False, "El repositorio de respaldo debe ser privado."

    return True, f"Conexión segura con {repositorio}."


def _obtener_archivo_remoto(nombre_archivo, token, repositorio):
    ruta_remota = quote(
        f"{CARPETA_REMOTA}/{nombre_archivo}",
        safe="/",
    )
    return requests.get(
        f"{GITHUB_API_URL}/repos/{repositorio}/contents/{ruta_remota}",
        headers=_crear_headers(token),
        params={"ref": RAMA_RESPALDO},
        timeout=10,
    )


def sincronizar_archivo(nombre_archivo):
    """Crea o actualiza un CSV dentro del repositorio privado."""
    if nombre_archivo not in ARCHIVOS_RESPALDADOS:
        return False, "El archivo no pertenece a JulyVerse."

    ruta_local = Path(nombre_archivo)

    if not ruta_local.exists():
        return False, f"No existe {nombre_archivo} para respaldar."

    token, repositorio = _obtener_configuracion()

    if not token or not repositorio:
        return False, "Faltan los Secrets del respaldo."

    try:
        respuesta_actual = _obtener_archivo_remoto(
            nombre_archivo,
            token,
            repositorio,
        )

        if respuesta_actual.status_code == 200:
            sha_actual = respuesta_actual.json().get("sha")
        elif respuesta_actual.status_code == 404:
            sha_actual = None
        else:
            return (
                False,
                f"GitHub no pudo preparar {nombre_archivo} "
                f"(código {respuesta_actual.status_code}).",
            )

        contenido = base64.b64encode(ruta_local.read_bytes()).decode("ascii")
        datos = {
            "message": f"Actualiza {nombre_archivo} desde JulyVerse",
            "content": contenido,
            "branch": RAMA_RESPALDO,
        }

        if sha_actual:
            datos["sha"] = sha_actual

        ruta_remota = quote(
            f"{CARPETA_REMOTA}/{nombre_archivo}",
            safe="/",
        )
        respuesta_guardado = requests.put(
            f"{GITHUB_API_URL}/repos/{repositorio}/contents/{ruta_remota}",
            headers=_crear_headers(token),
            json=datos,
            timeout=15,
        )
    except (OSError, requests.RequestException):
        return False, f"No se pudo respaldar {nombre_archivo} en GitHub."

    if respuesta_guardado.status_code not in (200, 201):
        return (
            False,
            f"GitHub no pudo guardar {nombre_archivo} "
            f"(código {respuesta_guardado.status_code}).",
        )

    return True, f"{nombre_archivo} respaldado correctamente."


def respaldar_archivo(nombre_archivo):
    """Sincroniza un archivo y conserva un aviso seguro en la sesión."""
    correcto, mensaje = sincronizar_archivo(nombre_archivo)

    if correcto:
        st.session_state.pop("error_respaldo_github", None)
    else:
        st.session_state.error_respaldo_github = mensaje

    return correcto


def _descargar_archivo(respuesta, nombre_archivo):
    datos = respuesta.json()
    contenido_codificado = datos.get("content", "").replace("\n", "")

    if not contenido_codificado:
        return False

    try:
        contenido = base64.b64decode(
            contenido_codificado,
            validate=True,
        )
    except (ValueError, TypeError):
        return False

    ruta_local = Path(nombre_archivo)
    ruta_temporal = ruta_local.with_name(f".{ruta_local.name}.tmp")

    try:
        ruta_temporal.write_bytes(contenido)
        ruta_temporal.replace(ruta_local)
    except OSError:
        ruta_temporal.unlink(missing_ok=True)
        return False

    return True


def inicializar_datos_github():
    """Recupera los CSV remotos o crea el primer respaldo si aún no existen."""
    token, repositorio = _obtener_configuracion()

    if not token or not repositorio:
        return False, "Faltan los Secrets del respaldo."

    for nombre_archivo in sorted(ARCHIVOS_RESPALDADOS):
        try:
            respuesta = _obtener_archivo_remoto(
                nombre_archivo,
                token,
                repositorio,
            )
        except requests.RequestException:
            return False, "No se pudieron recuperar los datos desde GitHub."

        if respuesta.status_code == 200:
            if not _descargar_archivo(respuesta, nombre_archivo):
                return False, f"No se pudo recuperar {nombre_archivo}."
            continue

        if respuesta.status_code == 404:
            if Path(nombre_archivo).exists():
                correcto, mensaje = sincronizar_archivo(nombre_archivo)
                if not correcto:
                    return False, mensaje
            continue

        return (
            False,
            f"GitHub no pudo recuperar {nombre_archivo} "
            f"(código {respuesta.status_code}).",
        )

    return True, "Datos privados sincronizados correctamente."
