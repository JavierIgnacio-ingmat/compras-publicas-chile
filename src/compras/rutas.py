"""Rutas del proyecto, calculadas desde la ubicación de este archivo."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "data"
CRUDOS_OC = DATOS / "raw" / "oc"
MANIFIESTO_OC = DATOS / "manifiesto_oc.csv"
