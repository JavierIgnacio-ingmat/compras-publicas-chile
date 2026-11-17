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

Fuente, formato esperado e instrucciones de descarga en [`data/README.md`](data/README.md).

**Problema central:** los datos no traen un campo de **unidad de medida**. Una orden puede registrar
"1 resma" y otra "1 caja de 10 resmas" bajo el mismo código de producto. Por eso el análisis se
restringe a productos donde la unidad puede determinarse con confianza (etapa 4).

## 5. Metodología

**Etapa 1. Ingesta.** Descargar los archivos mensuales y cargarlos en DuckDB sin modificarlos (tabla cruda).

**Etapa 2. Modelado.** Construir un modelo estrella en SQL:
- `fact_item_oc`: una fila por ítem comprado (cantidad, precio neto unitario, total, moneda, fecha).
- Dimensiones: `dim_organismo`, `dim_proveedor`, `dim_producto`, `dim_modalidad`, `dim_fecha`.

**Etapa 3. Limpieza.** Reglas documentadas y con tests:
- Excluir órdenes en estado anulado, rechazado o equivalente (los estados exactos se ven en los datos).
- Eliminar duplicados.
- Tratar la moneda según D7.
- Detectar precios unitarios imposibles (por ejemplo, el total anotado como precio unitario) y
  registrarlos en una tabla aparte en vez de borrarlos.

**Etapa 4. Canasta.** Seleccionar productos candidatos y clasificar sus ítems con el código de
producto y patrones de texto sobre la descripción. Validar a mano una muestra aleatoria y reportar
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
| Git / GitHub | Versionado con un PR por tarea |

## 7. Decisiones

| ID | Decisión | Opciones | Recomendación de Claude | Estado |
|---|---|---|---|---|
| D1 | Año a analizar | 2025 (último completo) / 2024 / varios años | 2025: un año basta y mantiene el volumen manejable | `PENDIENTE` |
| D2 | Productos de la canasta | Se eligen después de explorar los datos (tarea T6) | Productos estandarizados y comprados por muchos organismos, como resma de papel carta o medicamentos con dosis definida | `PENDIENTE` |
| D3 | Precio de referencia para el ahorro | Mediana / P25 / precio de convenio marco | Reportar mediana y P25 como rango | `PENDIENTE` |
| D4 | Nivel de detalle de los resultados publicados | Por tipo de organismo y región / por organismo individual | Por tipo de organismo y región, para no exponer a nadie sin pruebas suficientes | `PENDIENTE` |
| D5 | Incluir la compra ágil | Sí / No | Sí: es una modalidad más y puede explicar precios | `PENDIENTE` |
| D6 | Idioma del código | Inglés / español | Nombres de código en inglés y documentación en español | `PENDIENTE` |
| D7 | Ítems en UF o dólares | Convertir a pesos con datos del Banco Central / excluirlos | Excluirlos si son menos del 1 % de los ítems de la canasta; verificarlo primero | `PENDIENTE` |
| D8 | Precio con o sin impuestos | Neto / con IVA | Neto: evita diferencias por régimen tributario | `PENDIENTE` |

## 8. Tareas

| ID | Tarea | Depende de |
|---|---|---|
| T0 | Documentación inicial: `CLAUDE.md`, `SPEC.md`, `data/README.md`, `.gitignore` | — |
| T1 | Descargar un mes y verificar el formato real; actualizar `data/README.md` | — |
| T2 | Entorno: dependencias y estructura de carpetas del código | — |
| T3 | Ingesta: script de descarga y carga cruda en DuckDB | T1, D1 |
| T4 | Modelo estrella en SQL | T3 |
| T5 | Limpieza con tests | T4, D5, D7, D8 |
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
- Sin unidad de medida, parte de la dispersión puede ser error de clasificación. La validación manual lo acota.
- El ahorro potencial es un contrafactual que asume que el precio de referencia era alcanzable.
- La regresión muestra asociaciones, no efectos causales.
