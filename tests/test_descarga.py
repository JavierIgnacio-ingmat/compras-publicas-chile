"""Tests de la descarga de archivos mensuales y del manifiesto, sin acceso a internet."""

import csv
import hashlib
import io
import re
import urllib.error
import zipfile

import pytest

from compras import descarga


def _zip_valido(contenido: str = '"ID";"Codigo"\r\n1;"A-1-SE25"\r\n') -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("2025-1.csv", contenido)
    return buffer.getvalue()


class _Respuesta(io.BytesIO):
    """Imita la respuesta de urlopen: un archivo de bytes usable con ``with``."""


@pytest.fixture(autouse=True)
def rutas_temporales(tmp_path, monkeypatch):
    """Ningún test escribe en data/: las rutas por defecto apuntan a una carpeta temporal."""
    destino = tmp_path / "oc"
    manifiesto = tmp_path / "manifiesto_oc.csv"
    monkeypatch.setattr(descarga, "CRUDOS_OC", destino)
    monkeypatch.setattr(descarga, "MANIFIESTO_OC", manifiesto)
    return destino, manifiesto


@pytest.fixture
def respuestas(monkeypatch):
    """Reemplaza urlopen por una cola de respuestas; registra las URL pedidas."""
    cola = []
    pedidas = []

    def urlopen_falso(url, timeout=None):
        pedidas.append(url)
        siguiente = cola.pop(0)
        if isinstance(siguiente, Exception):
            raise siguiente
        return _Respuesta(siguiente)

    monkeypatch.setattr(descarga.urllib.request, "urlopen", urlopen_falso)
    return cola, pedidas


def _http_error(codigo):
    return urllib.error.HTTPError("https://ejemplo", codigo, "error", {}, None)


def _filas_manifiesto(ruta):
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


# --- Nombres y URL -----------------------------------------------------------


def test_nombre_y_url_usan_mes_sin_cero():
    assert descarga.nombre_archivo(2025, 1) == "2025-1.zip"
    assert descarga.nombre_archivo(2025, 10) == "2025-10.zip"
    assert descarga.url_mes(2025, 1) == (
        "https://transparenciachc.blob.core.windows.net/oc-da/2025-1.zip"
    )


@pytest.mark.parametrize("mes", [0, 13])
def test_mes_fuera_de_rango(mes):
    with pytest.raises(ValueError):
        descarga.nombre_archivo(2025, mes)


# --- Descarga ----------------------------------------------------------------


def test_descarga_exitosa_deja_solo_el_zip_final(rutas_temporales, respuestas):
    destino, _ = rutas_temporales
    cola, pedidas = respuestas
    cola.append(_zip_valido())

    ruta = descarga.descargar_mes(2025, 1, espera=0)

    assert ruta == destino / "2025-1.zip"
    assert zipfile.is_zipfile(ruta)
    assert [p.name for p in destino.iterdir()] == ["2025-1.zip"]
    assert pedidas == [descarga.url_mes(2025, 1)]


def test_archivo_existente_no_se_descarga_ni_se_modifica(rutas_temporales, respuestas):
    destino, _ = rutas_temporales
    _, pedidas = respuestas
    destino.mkdir()
    existente = destino / "2025-1.zip"
    existente.write_bytes(b"contenido original")

    ruta = descarga.descargar_mes(2025, 1, espera=0)

    assert ruta == existente
    assert existente.read_bytes() == b"contenido original"
    assert pedidas == []


def test_error_transitorio_se_reintenta(respuestas):
    cola, pedidas = respuestas
    cola.extend([urllib.error.URLError("sin conexión"), _http_error(503), _zip_valido()])

    ruta = descarga.descargar_mes(2025, 1, reintentos=3, espera=0)

    assert zipfile.is_zipfile(ruta)
    assert len(pedidas) == 3


def test_contenido_que_no_es_zip_falla_sin_dejar_archivos(rutas_temporales, respuestas):
    destino, manifiesto = rutas_temporales
    cola, pedidas = respuestas
    cola.extend([b"<html>error</html>"] * 3)

    with pytest.raises(descarga.ErrorDescarga):
        descarga.descargar_mes(2025, 1, reintentos=3, espera=0)

    assert len(pedidas) == 3
    assert list(destino.iterdir()) == []
    assert not manifiesto.exists()


def test_http_404_falla_sin_reintentar(rutas_temporales, respuestas):
    destino, _ = rutas_temporales
    cola, pedidas = respuestas
    cola.append(_http_error(404))

    with pytest.raises(descarga.ErrorDescarga, match="404"):
        descarga.descargar_mes(2025, 1, reintentos=3, espera=0)

    assert len(pedidas) == 1
    assert list(destino.iterdir()) == []


def test_varios_meses_se_detiene_en_el_primero_que_falla(rutas_temporales, respuestas):
    destino, manifiesto = rutas_temporales
    cola, pedidas = respuestas
    cola.extend([_zip_valido(), _http_error(404), _zip_valido()])

    with pytest.raises(descarga.ErrorDescarga):
        descarga.descargar_meses(2025, [1, 2, 3], espera=0)

    assert [p.name for p in destino.iterdir()] == ["2025-1.zip"]
    assert len(pedidas) == 2
    assert [f["archivo"] for f in _filas_manifiesto(manifiesto)] == ["2025-1.zip"]


# --- Manifiesto --------------------------------------------------------------


def test_descarga_nueva_queda_registrada_con_fecha_tamano_y_hash(rutas_temporales, respuestas):
    _, manifiesto = rutas_temporales
    cola, _ = respuestas
    contenido = _zip_valido()
    cola.append(contenido)

    descarga.descargar_mes(2025, 1, espera=0)

    filas = _filas_manifiesto(manifiesto)
    assert len(filas) == 1
    fila = filas[0]
    assert list(fila) == descarga.COLUMNAS_MANIFIESTO
    assert fila["archivo"] == "2025-1.zip"
    assert fila["url"] == descarga.url_mes(2025, 1)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", fila["fecha_descarga"])
    assert fila["bytes"] == str(len(contenido))
    assert fila["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_archivo_existente_se_registra_con_fecha_vacia_sin_descargar(rutas_temporales, respuestas):
    destino, manifiesto = rutas_temporales
    _, pedidas = respuestas
    destino.mkdir()
    contenido = _zip_valido()
    (destino / "2025-1.zip").write_bytes(contenido)

    descarga.descargar_mes(2025, 1, espera=0)

    assert pedidas == []
    [fila] = _filas_manifiesto(manifiesto)
    assert fila["fecha_descarga"] == ""
    assert fila["bytes"] == str(len(contenido))
    assert fila["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_segunda_ejecucion_no_duplica_ni_cambia_el_registro(rutas_temporales, respuestas):
    _, manifiesto = rutas_temporales
    cola, _ = respuestas
    cola.append(_zip_valido())

    descarga.descargar_mes(2025, 1, espera=0)
    antes = manifiesto.read_bytes()
    descarga.descargar_mes(2025, 1, espera=0)

    assert manifiesto.read_bytes() == antes
    assert len(_filas_manifiesto(manifiesto)) == 1


def test_archivo_modificado_detiene_la_descarga_sin_tocar_el_manifiesto(rutas_temporales, respuestas):
    destino, manifiesto = rutas_temporales
    cola, _ = respuestas
    cola.append(_zip_valido())
    ruta = descarga.descargar_mes(2025, 1, espera=0)
    antes = manifiesto.read_bytes()

    ruta.write_bytes(_zip_valido("contenido distinto"))

    with pytest.raises(descarga.ErrorManifiesto, match="2025-1.zip"):
        descarga.descargar_mes(2025, 1, espera=0)
    assert manifiesto.read_bytes() == antes


def test_manifiesto_ordenado_por_anio_y_mes(rutas_temporales, respuestas):
    _, manifiesto = rutas_temporales
    cola, _ = respuestas
    cola.extend([_zip_valido(), _zip_valido(), _zip_valido()])

    descarga.descargar_meses(2025, [10, 2, 1], espera=0)

    assert [f["archivo"] for f in _filas_manifiesto(manifiesto)] == [
        "2025-1.zip",
        "2025-2.zip",
        "2025-10.zip",
    ]
