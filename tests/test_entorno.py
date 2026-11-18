"""Verifica que el entorno tenga lo necesario para correr el proyecto."""

import importlib

import pytest

DEPENDENCIAS = ["duckdb", "pandas", "statsmodels", "matplotlib"]


@pytest.mark.parametrize("modulo", DEPENDENCIAS)
def test_dependencia_importable(modulo):
    importlib.import_module(modulo)


def test_paquete_del_proyecto_importable():
    import compras

    assert compras.__doc__


def test_duckdb_ejecuta_consulta_y_entrega_pandas():
    import duckdb

    resultado = duckdb.sql("SELECT 2 + 2 AS suma").df()
    assert resultado["suma"].iloc[0] == 4
