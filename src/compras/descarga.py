"""Descarga de los archivos mensuales de órdenes de compra de ChileCompra.

Cada mes se descarga a un archivo temporal ``.part`` y solo se renombra a
``AAAA-M.zip`` cuando el zip está completo y es válido. Los archivos que ya
existen en ``data/raw/oc`` no se vuelven a descargar ni se modifican.

Cada archivo queda registrado en ``data/manifiesto_oc.csv`` (versionado en git)
con su URL, fecha de descarga, tamaño y SHA-256. Si un archivo ya registrado
cambió de contenido, la descarga se detiene con un error.

Uso desde PowerShell::

    uv run python -m compras.descarga --anio 2025
    uv run python -m compras.descarga --anio 2025 --meses 1 2 3
"""

import argparse
import csv
import datetime
import hashlib
import logging
import os
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Iterable
from pathlib import Path

from compras.rutas import CRUDOS_OC, MANIFIESTO_OC

URL_BASE = "https://transparenciachc.blob.core.windows.net/oc-da"
REINTENTOS = 3
ESPERA_SEGUNDOS = 10
TIEMPO_LIMITE_RED = 120  # segundos sin respuesta del servidor antes de abortar un intento
COLUMNAS_MANIFIESTO = ["archivo", "url", "fecha_descarga", "bytes", "sha256"]

log = logging.getLogger(__name__)


class ErrorDescarga(Exception):
    """No se pudo obtener un archivo mensual válido."""


class ErrorManifiesto(Exception):
    """Un archivo ya registrado no coincide con lo anotado en el manifiesto."""


def nombre_archivo(anio: int, mes: int) -> str:
    """Nombre del archivo mensual, con el mes sin cero a la izquierda (``2025-1.zip``)."""
    if not 1 <= mes <= 12:
        raise ValueError(f"Mes fuera de rango: {mes}")
    return f"{anio}-{mes}.zip"


def url_mes(anio: int, mes: int) -> str:
    """URL de descarga del archivo de un mes."""
    return f"{URL_BASE}/{nombre_archivo(anio, mes)}"


def sha256_archivo(ruta: Path) -> str:
    """SHA-256 del archivo, leído por bloques para no cargarlo entero en memoria."""
    digest = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            digest.update(bloque)
    return digest.hexdigest()


def leer_manifiesto(ruta: Path) -> dict[str, dict[str, str]]:
    """Filas del manifiesto indexadas por nombre de archivo; vacío si no existe."""
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return {fila["archivo"]: fila for fila in csv.DictReader(archivo)}


def _clave_orden(nombre: str) -> tuple[int, int]:
    anio, mes = nombre.removesuffix(".zip").split("-")
    return int(anio), int(mes)


def _escribir_manifiesto(ruta: Path, filas: dict[str, dict[str, str]]) -> None:
    """Escribe el manifiesto ordenado por año y mes, reemplazándolo de una vez."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    with open(temporal, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_MANIFIESTO, lineterminator="\n")
        escritor.writeheader()
        for nombre in sorted(filas, key=_clave_orden):
            escritor.writerow(filas[nombre])
    os.replace(temporal, ruta)


def registrar_en_manifiesto(
    ruta_zip: Path, url: str, manifiesto: Path, fecha_descarga: str = ""
) -> dict[str, str]:
    """Anota un archivo en el manifiesto o verifica que coincida con su registro.

    Un archivo nuevo se agrega con su tamaño y SHA-256; ``fecha_descarga`` queda
    vacía si no se conoce (archivos descargados antes de existir el manifiesto).
    Si el archivo ya estaba registrado con otro SHA-256, lanza ``ErrorManifiesto``
    y no cambia nada: los archivos de ``data/raw`` no deben modificarse.
    """
    filas = leer_manifiesto(manifiesto)
    sha = sha256_archivo(ruta_zip)
    registrada = filas.get(ruta_zip.name)
    if registrada is not None:
        if registrada["sha256"] != sha:
            raise ErrorManifiesto(
                f"{ruta_zip.name} no coincide con el manifiesto: "
                f"SHA-256 registrado {registrada['sha256']}, actual {sha}"
            )
        return registrada
    fila = {
        "archivo": ruta_zip.name,
        "url": url,
        "fecha_descarga": fecha_descarga,
        "bytes": str(ruta_zip.stat().st_size),
        "sha256": sha,
    }
    filas[ruta_zip.name] = fila
    _escribir_manifiesto(manifiesto, filas)
    log.info("%s registrado en %s", ruta_zip.name, manifiesto.name)
    return fila


def _bajar_a(url: str, destino: Path) -> None:
    with urllib.request.urlopen(url, timeout=TIEMPO_LIMITE_RED) as respuesta:
        with open(destino, "wb") as archivo:
            shutil.copyfileobj(respuesta, archivo, length=1 << 20)


def _validar_zip(ruta: Path) -> None:
    if not zipfile.is_zipfile(ruta):
        raise ErrorDescarga(f"{ruta.name} no es un archivo zip")
    with zipfile.ZipFile(ruta) as z:
        danado = z.testzip()
        if danado is not None:
            raise ErrorDescarga(f"{ruta.name}: el archivo interno {danado} está dañado")


def _ahora_utc() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bajar_con_reintentos(url: str, final: Path, reintentos: int, espera: float) -> None:
    parcial = final.with_name(final.name + ".part")
    ultimo_error: Exception | None = None
    for intento in range(1, reintentos + 1):
        try:
            log.info("Descargando %s (intento %d de %d)", url, intento, reintentos)
            _bajar_a(url, parcial)
            _validar_zip(parcial)
            os.replace(parcial, final)
            log.info("%s descargado (%d bytes)", final.name, final.stat().st_size)
            return
        except urllib.error.HTTPError as error:
            parcial.unlink(missing_ok=True)
            if error.code == 404:
                raise ErrorDescarga(f"{url} no existe (HTTP 404)") from error
            ultimo_error = error
        except (urllib.error.URLError, OSError, ErrorDescarga) as error:
            parcial.unlink(missing_ok=True)
            ultimo_error = error
        log.warning("Falló el intento %d: %s", intento, ultimo_error)
        if intento < reintentos:
            time.sleep(espera)
    raise ErrorDescarga(
        f"No se pudo descargar {url} después de {reintentos} intentos: {ultimo_error}"
    ) from ultimo_error


def descargar_mes(
    anio: int,
    mes: int,
    destino: Path | None = None,
    manifiesto: Path | None = None,
    reintentos: int = REINTENTOS,
    espera: float = ESPERA_SEGUNDOS,
) -> Path:
    """Descarga el archivo de un mes, lo registra en el manifiesto y devuelve su ruta.

    Si el archivo ya existe, no lo descarga: solo lo registra (con fecha vacía) o
    verifica que coincida con su registro. Reintenta ante errores de red o zips
    inválidos; un error HTTP 404 se informa de inmediato, porque reintentar no lo
    arregla. Si todos los intentos fallan, lanza ``ErrorDescarga`` y no deja
    archivos a medias ni filas en el manifiesto.
    """
    destino = CRUDOS_OC if destino is None else destino
    manifiesto = MANIFIESTO_OC if manifiesto is None else manifiesto
    destino.mkdir(parents=True, exist_ok=True)
    final = destino / nombre_archivo(anio, mes)
    url = url_mes(anio, mes)

    if final.exists():
        log.info("%s ya existe; no se descarga de nuevo", final.name)
        registrar_en_manifiesto(final, url, manifiesto)
        return final

    _bajar_con_reintentos(url, final, reintentos, espera)
    registrar_en_manifiesto(final, url, manifiesto, fecha_descarga=_ahora_utc())
    return final


def descargar_meses(
    anio: int,
    meses: Iterable[int] = range(1, 13),
    destino: Path | None = None,
    manifiesto: Path | None = None,
    reintentos: int = REINTENTOS,
    espera: float = ESPERA_SEGUNDOS,
) -> list[Path]:
    """Descarga varios meses en orden y se detiene en el primero que falle."""
    return [descargar_mes(anio, mes, destino, manifiesto, reintentos, espera) for mes in meses]


def main(argumentos: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--anio", type=int, required=True, help="Año a descargar, por ejemplo 2025")
    parser.add_argument(
        "--meses", type=int, nargs="+", default=list(range(1, 13)), help="Meses (1 a 12); por defecto, todos"
    )
    opciones = parser.parse_args(argumentos)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    descargar_meses(opciones.anio, opciones.meses)


if __name__ == "__main__":
    main()
