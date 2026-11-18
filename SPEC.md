# Especificación: dispersión de precios en compras públicas de Chile

> Estado: **borrador**. Las decisiones marcadas como `PENDIENTE` las toma Javier antes de
> implementar las tareas que dependen de ellas.

## 1. Contexto

Los organismos del Estado de Chile (ministerios, servicios de salud, municipios, Fuerzas Armadas,
universidades estatales, entre otros) compran bienes y servicios a través de la plataforma
**Mercado Público**, administrada por la Dirección ChileCompra, según la Ley 19.886 de Compras Públicas.

Cada compra genera una **orden de compra (OC)** que registra quién compra, a quién, qué producto,
cuántas unidades, a qué precio y por qué modalidad. Las modalidades principales son:

| Modalidad | Descripción |
|---|---|
| Licitación | Concurso donde varios proveedores ofertan |
| Convenio marco | Catálogo con precios negociados de antemano por ChileCompra |
| Trato directo | Compra a un proveedor sin concurso; es una excepción que debe justificarse |
| Compra ágil | Procedimiento simplificado para montos pequeños |

En los datos, la modalidad de cada orden se deriva con la regla de la decisión D9 (sección 7).

ChileCompra publica estas órdenes como datos abiertos.

**Por qué importa.** Si dos organismos compran el mismo producto y uno paga bastante más, la
diferencia es gasto público que podría evitarse. La literatura distingue el **desperdicio activo**
(beneficio para quien decide, como la corrupción) del **desperdicio pasivo** (ineficiencia sin
beneficio para nadie: poca escala, poca competencia, poca información). Bandiera, Prat y Valletti
(2009, *American Economic Review*) encontraron con datos de Italia que la mayor parte del
sobreprecio era pasivo. Este proyecto mide la dispersión con datos chilenos y **no intenta
distinguir ni atribuir corrupción**.

## 2. Pregunta y objetivos

**Pregunta:** ¿Cuánto varía el precio que pagan los organismos públicos chilenos por productos
idénticos, qué factores se asocian a pagar más y cuánto se podría ahorrar?

**Objetivo general.** Cuantificar la dispersión de precios unitarios para una canasta de productos
homogéneos, identificar los factores asociados a precios más altos y estimar el ahorro potencial.

**Objetivos específicos**

1. Construir una base de datos analítica limpia con las órdenes de compra de un año.
2. Definir y validar una canasta de 5 a 10 productos homogéneos.
3. Medir la dispersión de precios de cada producto.
4. Estimar la asociación del precio con la modalidad de compra, la cantidad, la región y el tipo de organismo.
5. Estimar el ahorro potencial bajo distintos precios de referencia.
6. Comunicar los resultados en un reporte reproducible con una recomendación concreta.

## 3. Alcance

**Incluye**
- Órdenes de compra del año definido en D1, de todos los organismos y todas las modalidades.
- Solo los productos de la canasta (D2) entran al análisis de precios. El resto de la base se usa
  para describir el contexto (montos totales, participación por modalidad).

**No incluye**
- Servicios ni obras: su precio no es comparable entre compras.
- Juicios sobre organismos, funcionarios o proveedores específicos.
- Calidad del producto o costos de despacho: no están en los datos (ver limitaciones).

## 4. Datos

Fuente, formato verificado e instrucciones de descarga en [`data/README.md`](data/README.md).

**Problema central:** los datos no dicen **cuánto contiene cada unidad comprada**. Una orden puede
registrar "1 resma" y otra "1 caja de 10 resmas" bajo el mismo código de producto. Existe la columna
`UnidadMedida`, pero no resuelve el problema: en enero de 2025 vale `Unidad` en la mitad de los ítems
y `Unidad no definida` en el 14 %, está vacía en todas las compras por convenio marco (17 %), y cuando
dice `Caja` no indica cuántas unidades trae. Por eso el análisis se restringe a productos donde la
unidad puede determinarse con confianza (etapa 4).

## 5. Metodología

**Etapa 1. Ingesta.** Descargar los archivos mensuales y cargarlos en DuckDB sin modificarlos (tabla cruda).

**Etapa 2. Modelado.** Construir un modelo estrella en SQL:
- `fact_item_oc`: una fila por ítem comprado (cantidad, precio neto unitario, total, moneda, fecha).
- Dimensiones: `dim_organismo`, `dim_proveedor`, `dim_producto`, `dim_modalidad`, `dim_fecha`.
- `dim_modalidad` guarda cada combinación observada de `Tipo`, `EsTratoDirecto` y `ProcedenciaOC`
  junto con la modalidad derivada según D9, para que la regla se pueda auditar.

**Etapa 3. Limpieza.** Reglas documentadas y con tests:
- Conservar solo los ítems de órdenes en estado `Aceptada` o `Recepcion Conforme` (D10). La regla es
  una lista blanca: si aparece un estado que no está en la lista, la limpieza se detiene con un error.
- Eliminar duplicados.
- Tratar la moneda según D7.
- Detectar precios unitarios imposibles (por ejemplo, el total anotado como precio unitario) y
  registrarlos en una tabla aparte en vez de borrarlos.

**Etapa 4. Canasta.** Seleccionar productos candidatos y clasificar sus ítems con el código de
producto, patrones de texto sobre la descripción y la columna `UnidadMedida`. Esta última es una señal
más, no una fuente de verdad (ver sección 4). Validar a mano una muestra aleatoria y reportar
la precisión de la clasificación.

**Etapa 5. Análisis.**
- *Descriptivo:* distribución del precio unitario por producto; cociente P90/P10 y coeficiente de
  variación como medidas de dispersión.
- *Explicativo:* regresión del logaritmo del precio unitario sobre la modalidad, el logaritmo de la
  cantidad, la región, el tipo de organismo y el mes, con efectos fijos por producto. Errores
  estándar agrupados por organismo. Los coeficientes se interpretan como diferencias porcentuales
  aproximadas a igual producto, no como efectos causales.
- *Opcional:* detección de compras con precios anómalos (por ejemplo, Isolation Forest) y
  comparación con la regla simple P90/P10.

**Etapa 6. Ahorro potencial.** Para cada ítem pagado sobre el precio de referencia (D3), el ahorro es
(precio pagado − precio de referencia) × cantidad. Se reporta como rango, usando más de una referencia.
Supuesto declarado: que el precio de referencia era alcanzable para todos los compradores.

**Etapa 7. Comunicación.** README que responde la pregunta en el primer párrafo, gráficos, limitaciones y recomendación.

## 6. Herramientas

| Herramienta | Uso |
|---|---|
| DuckDB (SQL) | Almacenamiento, modelo estrella, limpieza, indicadores |
| Python + pandas | Orquestación, análisis de resultados agregados |
| statsmodels | Regresión |
| matplotlib | Gráficos |
| pytest | Tests de calidad de datos y de funciones |
| uv | Entorno de Python y dependencias con versiones fijas (`uv.lock`) |
| Git / GitHub | Versionado con un PR por tarea |

## 7. Decisiones

| ID | Decisión | Opciones | Recomendación de Claude | Estado |
|---|---|---|---|---|
| D1 | Año a analizar | 2025 (último completo) / 2024 / varios años | 2025: un año basta y mantiene el volumen manejable | `DECIDIDA`: 2025 |
| D2 | Productos de la canasta | Se eligen después de explorar los datos (tarea T6) | Productos estandarizados y comprados por muchos organismos, como resma de papel carta o medicamentos con dosis definida | `PENDIENTE` |
| D3 | Precio de referencia para el ahorro | Mediana / P25 / precio de convenio marco | Reportar mediana y P25 como rango | `PENDIENTE` |
| D4 | Nivel de detalle de los resultados publicados | Por tipo de organismo y región / por organismo individual | Por tipo de organismo y región, para no exponer a nadie sin pruebas suficientes | `PENDIENTE` |
| D5 | Incluir la compra ágil | Sí / No | Sí: es una modalidad más y puede explicar precios | `PENDIENTE` |
| D6 | Idioma del código | Inglés / español | Nombres de código en inglés y documentación en español | `DECIDIDA`: español, en código y documentación |
| D7 | Ítems en UF o dólares | Convertir a pesos con datos del Banco Central / excluirlos | Excluirlos si son menos del 1 % de los ítems de la canasta; verificarlo primero | `PENDIENTE` |
| D8 | Precio con o sin impuestos | Neto / con IVA | Neto: evita diferencias por régimen tributario | `PENDIENTE` |
| D9 | Cómo derivar la modalidad de compra | `Tipo` tal cual / 4 modalidades + otra / 4 modalidades con compra coordinada aparte | 4 modalidades + otra | `DECIDIDA`: 4 modalidades + otra (regla abajo) |
| D10 | Qué estados de la orden entran al análisis | Solo `Aceptada` y `Recepcion Conforme` / excluir solo `Cancelacion solicitada` / todos | Solo `Aceptada` y `Recepcion Conforme` | `DECIDIDA`: solo `Aceptada` y `Recepcion Conforme` |

### D9. Regla de modalidad

Se aplica en orden; cada ítem toma la primera fila que cumple. Las comparaciones son por valor exacto:
por ejemplo, `licitación pública previa sin ofertas, o con ofertas inadmisibles` es una causal de
trato directo, no una licitación. Las columnas están descritas en
[`docs/diccionario-oc.md`](docs/diccionario-oc.md). Los conteos son de enero de 2025, antes de filtrar estados.

| Orden | Condición | Modalidad | Ítems |
|---|---|---|---|
| 1 | `ProcedenciaOC` es `Orden de Compra para informar` o `NA` | Otra | 5.325 |
| 2 | `Tipo` = `AG` | Compra ágil | 122.329 |
| 3 | `Tipo` = `CM`, o `ProcedenciaOC` = `Proveniente de convenio marco` | Convenio marco | 62.164 |
| 4 | `Tipo` = `TD` o `CT`, o `EsTratoDirecto` = `Si` | Trato directo | 21.449 |
| 5 | `ProcedenciaOC` = `Proveniente de licitación pública` o `Proveniente de licitación privada` | Licitación | 148.929 |

Si un ítem no cumple ninguna regla, la construcción de `dim_modalidad` (T4) se detiene con un error,
igual que la lista blanca de D10. En enero de 2025 todos los ítems cumplen alguna.

`Tipo` no basta por sí solo porque `SE` mezcla licitaciones, tratos directos y otros casos;
`EsTratoDirecto` y `ProcedenciaOC` los separan. Resultado para cada caso:

| Caso | Ítems | Modalidad | Por qué |
|---|---|---|---|
| `AG` (compra ágil) | 122.329 | Compra ágil | Es la modalidad misma. Viene marcada con `EsTratoDirecto` = `Si`, por eso la regla 2 va antes que la 4 |
| `CM` (convenio marco) | 61.787 | Convenio marco | Compra desde el catálogo de convenio marco |
| `SE` de licitación pública o privada | 146.763 | Licitación | La orden proviene de un concurso (146.024 pública, 739 privada) |
| `SE` con `EsTratoDirecto` = `Si` | 3.107 | Trato directo | `ProcedenciaOC` trae una causal de trato directo |
| `SE` con `ProcedenciaOC` = `Proveniente de convenio marco` | 375 | Convenio marco | La procedencia indica que el precio viene de un convenio marco |
| `SE` con `ProcedenciaOC` = `Orden de Compra para informar` | 5.266 | Otra | La procedencia no indica el procedimiento de compra |
| `SE` con `EsTratoDirecto` = `NA` | 6 | Otra | También tienen `ProcedenciaOC` = `NA`: no hay dato para saber cómo se compró |
| `TD` con `EsTratoDirecto` = `Si` | 18.324 | Trato directo | Ficha de trato directo con su causal |
| `TD` con `EsTratoDirecto` = `No` | 53 | Otra | Todos tienen `ProcedenciaOC` = `Orden de Compra para informar`; se tratan igual que los 5.266 de `SE` |
| `CT` (cotización) | 18 | Trato directo | Marcadas con `EsTratoDirecto` = `Si`; su causal es una excepción de trato directo (remanente de contrato, con 3 cotizaciones) |
| `CC` (compra coordinada) de licitación pública o privada | 2.166 | Licitación | La orden proviene de una licitación (2.160 pública, 6 privada) |
| `CC` con `ProcedenciaOC` = `Proveniente de convenio marco` | 2 | Convenio marco | Misma razón que en `SE`: manda la procedencia |

Si los ítems "Otra" entran o no a la regresión se decide en T9.

El test de T4 debe verificar que ninguna compra ágil (`Tipo` = `AG` o `EsCompraAgil` = `Si`) quede
en "Otra" por la regla 1. En enero de 2025 no hay ninguna.

### D10. Estados incluidos

Solo `Aceptada` y `Recepcion Conforme`: son órdenes que el proveedor aceptó, con precio confirmado.
En enero de 2025 quedan fuera 3.249 ítems (0,9 %): `Enviada a proveedor` 2.695,
`Cancelacion solicitada` 322 y `En proceso` 232. Los estados anulada o rechazada no aparecen en los datos.

## 8. Tareas

| ID | Tarea | Depende de |
|---|---|---|
| T0 | Documentación inicial: `CLAUDE.md`, `SPEC.md`, `data/README.md`, `.gitignore` | — |
| T1 | Descargar un mes y verificar el formato real; actualizar `data/README.md` | — |
| T2 | Entorno: dependencias y estructura de carpetas del código | — |
| T3 | Ingesta: script de descarga y carga cruda en DuckDB | T1, D1 |
| T4 | Modelo estrella en SQL | T3, D9 |
| T5 | Limpieza con tests | T4, D5, D7, D8, D9, D10 |
| T6 | Exploración de productos candidatos | T5 |
| T7 | Clasificación de la canasta y validación manual | T6, D2 |
| T8 | Análisis descriptivo | T7 |
| T9 | Regresión | T8 |
| T10 | Ahorro potencial | T8, D3 |
| T11 | (Opcional) Detección de anomalías | T8 |
| T12 | README final con resultados | T9, T10, D4 |

## 9. Criterios de aceptación

- Todo el análisis se reproduce desde cero con los comandos documentados en el README.
- Los tests pasan.
- La clasificación de la canasta tiene una precisión de al menos 95 % en una muestra validada a mano
  de al menos 200 ítems. *(Umbral propuesto; Javier puede ajustarlo.)*
- El README responde la pregunta en el primer párrafo y declara las limitaciones.
- Ningún dato crudo ni credencial queda en el repositorio.

## 10. Limitaciones conocidas

- **Precio distinto no significa irregularidad.** Puede reflejar despacho a zonas remotas, urgencia,
  calidad o cantidades mínimas.
- Sin una unidad de medida confiable, parte de la dispersión puede ser error de clasificación. La validación manual lo acota.
- El ahorro potencial es un contrafactual que asume que el precio de referencia era alcanzable.
- La regresión muestra asociaciones, no efectos causales.
