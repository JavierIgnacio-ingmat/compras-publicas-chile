# compras-publicas-chile
Análisis de dispersión de precios en compras públicas de Chile: cuánto varía lo que pagan los organismos del Estado por productos idénticos, qué lo explica y cuánto se podría ahorrar. Datos abiertos de ChileCompra · SQL (DuckDB) · Python.

## Cómo reproducir

Requisitos: Python 3.12 y [uv](https://docs.astral.sh/uv/). Los comandos funcionan en PowerShell.

```powershell
uv sync          # crea .venv con las versiones exactas de uv.lock
uv run pytest    # corre los tests
```

Los datos se descargan aparte: ver [`data/README.md`](data/README.md).

## Estructura

```
src/compras/       código Python: descarga, carga, orquestación y análisis
sql/               consultas DuckDB del modelo estrella y la limpieza
tests/             tests de datos y de funciones (pytest)
reports/figures/   gráficos generados por el código
docs/              diccionario de datos
data/              datos locales, no versionados
```
