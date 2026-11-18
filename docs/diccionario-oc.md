# Diccionario de datos: órdenes de compra (`oc-da`)

Construido en la tarea T1 a partir de `data/raw/oc/2025-1.zip` (enero de 2025). La sintaxis del
archivo (codificación, separador, decimales, valores vacíos) está en
[`data/README.md`](../data/README.md).

Para no identificar una OC ni un organismo concreto, los ejemplos de las columnas que lo permitirían
muestran solo el formato. `N` es un dígito, `A` un dígito del año, `D` el dígito verificador del RUT
y `<n>` un número de largo variable.

## Columnas

79 columnas, en este orden. Los nombres se copian tal cual, incluidas las erratas
(`Descripcion/Obervaciones`, `NombreroductoGenerico`) y el espacio de `Forma de Pago`.
Las columnas 1 a 60 y la 79 describen la OC y se repiten en cada ítem; las 61 a 78 describen el ítem.

| # | Columna | Ejemplo o formato | Notas |
|---|---|---|---|
| 1 | `ID` | entero de 8 dígitos | Identificador numérico de la OC |
| 2 | `Codigo` | `<n>-<n>-<letras>AA` (hasta 18 caracteres) | Código de la OC |
| 3 | `Link` | `http://www.mercadopublico.cl/PurchaseOrder/Modules/PO/DetailsPurchaseOrder.aspx?codigoOC=<Codigo>` | Ficha de la OC |
| 4 | `Nombre` | texto libre, hasta 255 caracteres | Nombre de la OC |
| 5 | `Descripcion/Obervaciones` | texto libre multilínea, hasta 1.061 caracteres | `NA` en 172 filas y `""` en 298 |
| 6 | `Tipo` | `SE` | Tipo de OC: `SE`, `AG`, `CM`, `TD`, `CC`, `CT` |
| 7 | `ProcedenciaOC` | `Proveniente de licitación pública` | 31 valores; incluye la causal del trato directo |
| 8 | `EsTratoDirecto` | `No` | `Si` / `No`; `NA` en 6 filas |
| 9 | `EsCompraAgil` | `No` | `Si` / `No` |
| 10 | `CodigoTipo` | `8` | Código de `Tipo` (8 = SE, 13 = AG, 9 = CM, 16 = TD, 14 = CC, 17 = CT) |
| 11 | `CodigoAbreviadoTipoOC` | `SE` | Igual a `Tipo` |
| 12 | `DescripcionTipoOC` | `Sin emisión automática` | Nombre de `Tipo` |
| 13 | `CodigoProyectoPlanAnualCompras` | `<n>-<n>-<letras>AA` | `NA` en el 70 % |
| 14 | `codigoEstado` | `12` | Código de `Estado` |
| 15 | `Estado` | `Recepcion Conforme` | Estado de la OC; 5 valores (ver abajo) |
| 16 | `codigoEstadoProveedor` | `7` | Código de `EstadoProveedor` |
| 17 | `EstadoProveedor` | `Aceptada` | 6 valores |
| 18 | `FechaCreacion` | `2023-04-18` | |
| 19 | `FechaEnvio` | `2025-01-14` | Define el mes del archivo |
| 20 | `FechaSolicitudCancelacion` | `2025-01-14` | Llena en casi todas las filas: **no indica** que se haya pedido cancelar |
| 21 | `fechaUltimaModificacion` | `2025-01-14` | |
| 22 | `FechaAceptacion` | `2025-01-15` | `NA` en 2.912 filas |
| 23 | `FechaCancelacion` | `2025-01-15` | `NA` salvo en 3 filas |
| 24 | `tieneItems` | `1` | Constante |
| 25 | `PromedioCalificacion` | `5` | Calificación del proveedor; decimales con coma |
| 26 | `CantidadEvaluacion` | `1` | |
| 27 | `MontoTotalOC` | `169646400` | Total de la OC en `TipoMonedaOC` |
| 28 | `TipoMonedaOC` | `CLP` | `CLP`, `CLF` (UF), `USD`, `UTM`, `EUR` |
| 29 | `MontoTotalOC_PesosChilenos` | `169646400` | Total de la OC convertido a pesos (solo a nivel de OC) |
| 30 | `Impuestos` | `27086400` | |
| 31 | `TipoImpuesto` | `IVA` | `IVA`, `Exento`, `Honorarios (14,5%)` y otros 3 |
| 32 | `Descuentos` | `0` | |
| 33 | `Cargos` | `0` | |
| 34 | `TotalNetoOC` | `142560000` | |
| 35 | `CodigoUnidadCompra` | entero | Unidad de compra dentro del organismo |
| 36 | `RutUnidadCompra` | `NN.NNN.NNN-D` | RUT con puntos y guion |
| 37 | `UnidadCompra` | texto en mayúsculas | Nombre de la unidad de compra |
| 38 | `CodigoOrganismoPublico` | entero | |
| 39 | `OrganismoPublico` | texto en mayúsculas | Nombre del organismo |
| 40 | `sector` | `Salud` | 7 valores; `NA` en 4.947 filas |
| 41 | `ActividadComprador` | `GOBIERNO CENTRAL Y ADMINISTRACION PUBLICA` | `""` en 70.138 filas |
| 42 | `CiudadUnidadCompra` | `Valdivia` | |
| 43 | `RegionUnidadCompra` | `Región de Los Ríos` | Región del comprador; 32 valores (ver abajo) |
| 44 | `PaisUnidadCompra` | `CL` | `CL`, `Extranjero`, `"  "` o `NA`. No es confiable: 138.596 filas dicen `Extranjero` |
| 45 | `CodigoSucursal` | entero | Sucursal del proveedor |
| 46 | `RutSucursal` | `NN.NNN.NNN-D` | RUT del proveedor |
| 47 | `Sucursal` | texto | Nombre de la sucursal |
| 48 | `CodigoProveedor` | entero | |
| 49 | `NombreProveedor` | texto | Puede ser una persona natural |
| 50 | `ActividadProveedor` | `OBRAS MENORES EN CONSTRUCCION (CONTRATISTAS, ALBAN` | Texto truncado |
| 51 | `ComunaProveedor` | `Valdivia` | `""` en 64.779 filas |
| 52 | `RegionProveedor` | `Región de Los Ríos` | `NA` en 61.857 filas |
| 53 | `PaisProveedor` | `Chile` | `Chile` o `CL`, entre otros; `NA` en 144.609 filas |
| 54 | `Financiamiento` | texto libre, a veces un código presupuestario con guiones | `""` en el 49 % |
| 55 | `PorcentajeIva` | `19` | `19`, `0`, `14,5`, `13,75` y otros |
| 56 | `Pais` | `CL` | Mismo dominio que `PaisUnidadCompra` |
| 57 | `TipoDespacho` | `7` | Código sin diccionario en el archivo; 7 valores |
| 58 | `FormaPago` | `2` | Código; su texto está en `Forma de Pago` |
| 59 | `CodigoLicitacion` | `<n>-<n>-<letras>AA` | `""` si la OC no viene de licitación |
| 60 | `Codigo_ConvenioMarco` | `2239-<n>-LRAA` | Solo en OC de convenio marco (17 convenios); `NA` en el resto |
| 61 | `IDItem` | entero de 9 dígitos | Identificador del ítem; único |
| 62 | `codigoCategoria` | `76111500` | `NA` en convenio marco |
| 63 | `Categoria` | `Servicios de limpieza industrial / Servicios de limpieza / …` | Rubros N1 / N2 / N3 unidos; `""` en convenio marco |
| 64 | `codigoProductoONU` | `76111501` | Código de producto ONU (UNSPSC), 8 dígitos; siempre lleno |
| 65 | `NombreroductoGenerico` | `Servicios de limpieza de edificios` | Nombre del código ONU; siempre lleno |
| 66 | `RubroN1` | `Equipamiento y suministros médicos` | 58 valores; `NA` en convenio marco |
| 67 | `RubroN2` | `Servicios de limpieza` | `NA` en convenio marco |
| 68 | `RubroN3` | `Servicios de limpieza de edificios y oficinas en general` | `NA` en convenio marco |
| 69 | `EspecificacionComprador` | texto libre multilínea, hasta 5.408 caracteres | Descripción del ítem escrita por el comprador |
| 70 | `EspecificacionProveedor` | texto libre, hasta 278 caracteres | Descripción del proveedor; `NA` en 59.077 filas y `""` en 34.450 |
| 71 | `cantidad` | `36` | Puede traer decimales y notación científica; 29 filas en 0 |
| 72 | `UnidadMedida` | `Unidad` | 94 valores; `NA` en convenio marco (ver abajo) |
| 73 | `monedaItem` | `CLP` | Moneda del ítem; mismos valores que `TipoMonedaOC` |
| 74 | `precioNeto` | `3960000` | Precio unitario neto, en `monedaItem`; 29 filas en 0 |
| 75 | `totalCargos` | `0` | |
| 76 | `totalDescuentos` | `0` | |
| 77 | `totalImpuestos` | `0` | Solo `0`, `51` o `NA`: no sirve |
| 78 | `totalLineaNeto` | `142560000` | Igual a `cantidad × precioNeto` salvo en 189 filas |
| 79 | `Forma de Pago` | `30 dias contra la recepcion conforme de la factura` | Texto de `FormaPago`; 3 valores |

## Columnas clave para el análisis

| Concepto | Columna principal | Complementarias |
|---|---|---|
| Producto | `codigoProductoONU` | `NombreroductoGenerico`; `codigoCategoria`, `Categoria`, `RubroN1` a `RubroN3` (vacías en convenio marco) |
| Descripción | `EspecificacionComprador` | `EspecificacionProveedor`; a nivel de OC, `Nombre` y `Descripcion/Obervaciones` |
| Cantidad | `cantidad` | `UnidadMedida` |
| Precio unitario | `precioNeto` | `totalLineaNeto` |
| Moneda | `monedaItem` | `TipoMonedaOC` (distinta de `monedaItem` en 29 filas) |
| Modalidad de compra | `Tipo` | `EsTratoDirecto`, `EsCompraAgil`, `ProcedenciaOC`, `CodigoLicitacion`, `Codigo_ConvenioMarco` |
| Organismo | `CodigoOrganismoPublico`, `OrganismoPublico` | `CodigoUnidadCompra`, `UnidadCompra`; tipo de organismo en `sector` |
| Región | `RegionUnidadCompra` | `CiudadUnidadCompra`; del proveedor, `RegionProveedor` |
| Estado de la orden | `Estado` (`codigoEstado`) | `EstadoProveedor` (`codigoEstadoProveedor`) |

## Valores observados en enero de 2025

**`Tipo`** (filas de ítem):

| `Tipo` | `DescripcionTipoOC` | Filas | `EsTratoDirecto` | `EsCompraAgil` |
|---|---|---|---|---|
| `SE` | Sin emisión automática | 155.517 | `No` 152.404; `Si` 3.107; `NA` 6 | `No` |
| `AG` | Compra ágil | 122.329 | `Si` | `Si` |
| `CM` | Convenio Marco | 61.787 | `No` | `No` |
| `TD` | Proveniente de Ficha de Trato Directo | 18.377 | `Si` 18.324; `No` 53 | `No` |
| `CC` | Compra Coordinada | 2.168 | `No` | `No` |
| `CT` | Proveniente de compra por Cotización | 18 | `Si` | `No` |

`SE` mezcla procedimientos: 146.024 ítems vienen de licitación pública, 5.266 son "Orden de Compra
para informar", 739 vienen de licitación privada, 375 de convenio marco y el resto son causales de
trato directo (según `ProcedenciaOC`). Las compras ágiles figuran también como trato directo
(`EsTratoDirecto = Si`).

**`Estado`**: `Recepcion Conforme` 266.633, `Aceptada` 90.314, `Enviada a proveedor` 2.695,
`Cancelacion solicitada` 322, `En proceso` 232. No aparecen estados "anulada", "rechazada" ni
"cancelada"; `EstadoProveedor` tiene un solo `Cancelada`.

**Moneda del ítem (`monedaItem`)**: `CLP` 357.870, `CLF` 1.404, `USD` 795, `UTM` 120, `EUR` 7.
Los ítems en otra moneda que no es el peso son el 0,65 % del total.

**`RegionUnidadCompra`**: las 16 regiones vienen escritas de dos formas, una larga
(`Región de Valparaíso `, a veces con espacios al final) y una corta (`Valparaíso`). La forma corta
aparece en 7.787 filas. Hay que normalizarlas.

**`UnidadMedida`**: `Unidad` 181.308, `NA` 61.824 (todo convenio marco), `Unidad no definida` 49.450,
`Global` 9.779, `Caja` 8.865, `kilogramo` 7.074, y otros 88 valores.
