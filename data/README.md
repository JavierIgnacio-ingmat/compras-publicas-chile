# Datos

Esta carpeta **no se versiona** (salvo este archivo). Cada persona descarga los datos por su cuenta.

## Fuente

Datos abiertos de ChileCompra: <https://datos-abiertos.chilecompra.cl/descargas>

Se usa la pestaña **"Descarga masiva por URL"**, que entrega archivos con las órdenes de compra
de **todos los organismos**, un archivo por mes.
La pestaña "Descarga de reportes" **no sirve** para este proyecto: filtra por un organismo a la vez,
y el análisis necesita comparar entre organismos.

## Qué se descarga

| Conjunto | Periodo | Estado |
|---|---|---|
| Órdenes de compra (`oc-da`) | 12 archivos mensuales del año definido en la decisión D1 de `SPEC.md` | Necesario |
| Licitaciones (`lic-da`) | Mismo periodo | Opcional; solo si se analiza el número de oferentes |

## URL

`https://transparenciachc.blob.core.windows.net/oc-da/AAAA-M.zip`, con el mes sin cero a la izquierda.

Confirmada con la descarga de enero de 2025:
<https://transparenciachc.blob.core.windows.net/oc-da/2025-1.zip>. Para los demás meses se supone
el mismo patrón; se confirma al descargarlos.

## Cómo descargar

```powershell
uv run python -m compras.descarga --anio 2025                # los 12 meses
uv run python -m compras.descarga --anio 2025 --meses 1 2 3  # solo algunos meses
```

Los archivos quedan en `raw/oc/` con su nombre original (`AAAA-M.zip`). Los que ya existen no se
vuelven a descargar ni se modifican. Cada mes se baja primero a un archivo `.part` y solo se
renombra cuando el zip está completo y es válido. Si un mes falla tres veces seguidas, o no existe
(HTTP 404), el comando se detiene con un error y no deja archivos a medias.

### Registro de descargas

Cada archivo queda anotado en `manifiesto_oc.csv`, que **sí se versiona** en git:

| Columna | Contenido |
|---|---|
| `archivo` | Nombre del zip (`2025-1.zip`) |
| `url` | URL de descarga |
| `fecha_descarga` | Fecha y hora UTC de la descarga (`2026-11-18T21:03:00Z`); vacía si el archivo ya existía cuando se creó el registro |
| `bytes` | Tamaño del zip |
| `sha256` | Huella del zip, para comprobar que es el mismo archivo |

Los archivos que ya existen se registran con su huella sin volver a descargarlos. Si un archivo
registrado cambia de contenido, el comando se detiene con un error: los archivos de `raw/` no deben
modificarse. Lo mismo ocurre si otra persona descarga un mes que ChileCompra regeneró después del
registro: el error avisa que esos datos ya no son los mismos que se analizaron.

## Formato verificado

Verificado en la tarea T1 (2026-11-18) con `raw/oc/2025-1.zip` (enero de 2025), leyendo el CSV
directo desde el zip, sin descomprimirlo en disco. Los demás meses se suponen iguales; el código
de ingesta debe comprobar que el encabezado coincida.

Las 79 columnas, las columnas clave para el análisis y los valores observados están en el
diccionario de datos: [`docs/diccionario-oc.md`](../docs/diccionario-oc.md).

**Archivo.**

| Propiedad | Valor en `2025-1.zip` |
|---|---|
| Tamaño del zip | 85.454.921 bytes (≈ 81,5 MiB) |
| Contenido | Un solo archivo, `2025-1.csv`, en la raíz del zip (compresión deflate) |
| Tamaño del CSV | 85.454.787 bytes comprimido; 615.211.371 bytes descomprimido (≈ 587 MiB, 7,2 veces más) |
| Filas de datos | 360.196, más una fila de encabezado |
| Columnas | 79 |
| Granularidad | Una fila por ítem de OC. `IDItem` es único. Hay 139.431 OC distintas (`Codigo` e `ID` son equivalentes 1 a 1) |
| Duplicados | No hay filas idénticas |
| Periodo | Todas las filas tienen `FechaEnvio` en enero de 2025; `FechaCreacion` puede ser anterior (incluso de 2023) |

**Sintaxis del CSV.**

| Aspecto | Valor observado |
|---|---|
| Codificación | Windows-1252 (`cp1252`), sin BOM. **No** es UTF-8. Ver "Codificación" más abajo |
| Separador | `;` |
| Comillas | Los textos y fechas van entre `"`; los números y `NA` van sin comillas |
| Fin de registro | `\r\n` (CRLF) |
| Saltos de línea dentro de campos | Sí, en campos de texto entre comillas (sobre todo como `\r\r\n`). El archivo tiene unos 2 millones de líneas físicas para 360 mil registros: **no se pueden contar filas contando líneas** |
| Decimales | Coma (`14,5`). No hay separador de miles |
| Notación científica | Sí, en columnas numéricas: `6e+05`, `1,1e+07`, `1e-04`. El lector debe aceptar mantisa con coma y exponente. Aparece en más de 4.900 valores de `precioNeto` y unos 120 de `cantidad`. Ver "Notación científica" más abajo |
| Fechas | `AAAA-MM-DD`, sin hora |
| Valores vacíos | Tres formas: `NA` sin comillas (la principal, en números y textos), cadena vacía `""` (sobre todo en textos: `CodigoLicitacion`, `Categoria`, `ActividadComprador`, `Financiamiento`) y, en `Pais` y `PaisUnidadCompra`, dos espacios `"  "`. No aparece `"NA"` entre comillas |

**Codificación.** Casi todo el texto es Windows-1252: aparecen comillas tipográficas, viñetas y
guiones de ese juego de caracteres (bytes `0x93`, `0x94`, `0x95` y `0x96`, unas 150 mil veces).
Pero hay unos 1.700 fragmentos de texto que venían en UTF-8 y quedaron mezclados (por ejemplo,
`ISOFÃNICA` por `ISOFÁNICA`, `DiseÃ±o` por `Diseño`). Esos fragmentos traen bytes que no existen en
`cp1252` (`0x81`, `0x8D`, `0x9D`), por lo que decodificar con `cp1252` estricto **falla**.
Decodificar como `latin-1` nunca falla, pero convierte esos símbolos tipográficos en caracteres de
control. Afecta sobre todo a las descripciones de ítems, que se usan para clasificar la canasta (T7).

**Notación científica.** En todos los casos comparables, la notación científica no pierde dígitos: las mantisas tienen a lo
sumo 4 dígitos significativos (`6e+05`, `1,1e+07`) y, cuando se comparan con montos de la misma
fila u OC escritos sin notación científica, cuadran exactamente:

- `cantidad × precioNeto = totalLineaNeto` en los 484 ítems en que `precioNeto` usa notación
  científica, `cantidad` y `totalLineaNeto` no la usan, y no hay cargos ni descuentos.
- `TotalNetoOC` es igual a la suma de `totalLineaNeto` de sus ítems en 277 de las 278 OC en que
  `TotalNetoOC` usa notación científica y sus ítems no. La excepción (`5e+05` contra una suma de
  415.205) es una inconsistencia del dato, no un redondeo.

**Hipótesis no verificada:** la combinación de `;`, coma decimal, `NA` y notación científica
coincide con la salida de `write.csv2` del lenguaje R. ChileCompra no documenta cómo genera el archivo.

## Estructura de carpetas

```
data/
├── README.md        este archivo (sí se versiona)
├── raw/             archivos tal como se descargan; solo lectura
│   └── oc/          AAAA-M.zip
└── interim/         archivos intermedios generados por el código
```

Los archivos de `raw/` no se modifican ni se renombran. Todo lo derivado se genera desde ellos con código.
