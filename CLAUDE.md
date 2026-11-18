# Instrucciones para Claude en este repositorio

## El proyecto

Análisis de dispersión de precios en compras públicas de Chile con datos abiertos de ChileCompra.
La especificación completa está en [`SPEC.md`](SPEC.md). Léela antes de proponer cualquier cambio.

## Quién decide

- **El autor del proyecto es Javier.** Claude asiste: propone, redacta, implementa y revisa.
- Las decisiones de método y alcance son de Javier. Si una tarea depende de una decisión marcada
  como `PENDIENTE` en `SPEC.md`, **no la tomes**: presenta las opciones con sus consecuencias y
  una recomendación, y espera su respuesta.
- Si algo no está cubierto por `SPEC.md`, pregunta antes de inventar alcance.
- Cuestiona las ideas de Javier cuando creas que están equivocadas. No busques complacerlo.

## Forma de trabajo (SDD)

1. Una tarea por vez, tomada de la lista de tareas de `SPEC.md`.
2. Cada tarea va en su propia rama (`tipo/descripcion-corta`, por ejemplo `feat/ingesta-oc`)
   y termina en un pull request.
3. **Muestra el diff antes de aplicar cambios** a archivos existentes y espera la aprobación.
   Después de aplicarlos, confirma que los archivos quedaron íntegros (sin cortes ni contenido perdido).
4. Cambios pequeños y revisables. Mejor tres PR chicos que uno grande.
5. Cada PR explica **qué** hace y **por qué** se eligió ese enfoque, de modo que Javier pueda
   defenderlo en una entrevista sin haber escrito cada línea.
6. Toda regla de limpieza de datos queda documentada y tiene al menos un test.

## Prohibido

- Subir datos al repositorio (`data/` está excluida en `.gitignore`, salvo `data/README.md`).
- Subir credenciales, tokens o el archivo `.env`.
- Modificar los archivos de `data/raw/`: son la copia original de la fuente y se tratan como solo lectura.
- Borrar ramas, hacer `force push` o reescribir historia publicada. Eso lo hace Javier.
- Publicar resultados que identifiquen a un organismo o funcionario específico mientras la
  decisión D4 de `SPEC.md` siga pendiente.

## Entorno

- Javier trabaja en **Windows**. Usa `pathlib` para las rutas y evita comandos que solo existan
  en bash. Si das un comando de terminal, que funcione en PowerShell.
- Entorno con `uv`: `uv sync` instala las versiones exactas de `uv.lock` y `uv run <comando>` ejecuta
  dentro del entorno (por ejemplo, `uv run pytest`). Las dependencias se agregan con `uv add`, no con
  `pip install`.
- Nombres de código en español (decisión D6): módulos, funciones, variables y tablas SQL. Van sin
  tildes ni ñ (por ejemplo, `anio`, `categoria`, `region`). Las columnas crudas de la fuente
  conservan su nombre original.
- Base de datos analítica: DuckDB, en un archivo local excluido de git.
- Los datos crudos son pesados (varios GB). No los cargues completos en pandas: procesa con
  DuckDB y trae a Python solo resultados agregados o muestras.

## Datos

Ver [`data/README.md`](data/README.md) para la fuente, el formato y cómo descargarlos.
Lo que se sabe del formato viene de fuentes secundarias y **debe verificarse** con el archivo real
antes de escribir el código de ingesta.
