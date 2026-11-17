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

## Formato esperado (por verificar)

Según fuentes secundarias (no la documentación oficial):

- URL: `https://transparenciachc.blob.core.windows.net/oc-da/AAAA-M.zip` (por ejemplo, `2025-1.zip` para enero de 2025).
- Cada mes pesa entre 30 y 150 MB comprimido.
- Dentro hay un CSV con una fila por ítem de la orden de compra.
- Codificación `latin-1`, separador `;`, coma decimal y `NA` como valor vacío.

Todo esto se confirma con el primer archivo real. Si algo difiere, se corrige aquí.

## Estructura de carpetas

```
data/
├── README.md        este archivo (sí se versiona)
├── raw/             archivos tal como se descargan; solo lectura
│   └── oc/          AAAA-M.zip
└── interim/         archivos intermedios generados por el código
```

Los archivos de `raw/` no se modifican ni se renombran. Todo lo derivado se genera desde ellos con código.
