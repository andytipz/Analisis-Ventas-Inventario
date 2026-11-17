# Análisis de ventas e inventario | Dashboard comercial

Proyecto de análisis de datos con **Python, pandas y Matplotlib** que transforma registros de ventas e inventario de una empresa minorista en indicadores, visualizaciones y reportes para apoyar decisiones comerciales.

![Panel de ventas e inventario](output/dashboard_ventas_inventario.png)

## Objetivo

Explorar el rendimiento comercial de un conjunto de datos minoristas mediante el análisis de ventas netas, utilidad bruta, margen bruto, modalidades de venta, líneas de producto, tiendas y existencias disponibles estimadas.

## Resultados principales

| Indicador | Resultado aproximado |
|---|---:|
| Registros de ventas analizados | 125.751 |
| Ventas netas | 10,48 millones (unidades monetarias de origen) |
| Utilidad bruta | 4,63 millones (unidades monetarias de origen) |
| Margen bruto | 44,2 % |
| Existencias disponibles estimadas | 37.576 unidades |
| Período de ventas | 1 jun 2025 – 24 abr 2026 |

> **Importante:** El origen no especifica claramente la moneda utilizada ni confirma la naturaleza real o sintética de los registros. Por eso, las cifras monetarias no se etiquetan como dólares. Abril de 2026 es un mes parcial y no debe compararse sin ajustar por días disponibles.

## Análisis incluidos

El panel presenta seis visualizaciones: evolución mensual de ventas, ventas por modalidad, ventas frente a costos, ventas por línea de producto, tiendas con mayores ventas y existencias estimadas por línea de producto.

El programa también genera CSV de ventas mensuales, ventas por modalidad, categoría y tienda, inventario por categoría y tienda, devoluciones por categoría e indicadores generales.

## Tecnologías

- **Python 3.12**: procesamiento y ejecución del análisis.
- **pandas**: limpieza, validación, cálculos y agrupaciones.
- **Matplotlib**: creación y exportación de gráficos.

## Estructura del proyecto

```text
SALES_ANALYTICS_DASHBOARD/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── retail_sales_ml_apl.csv        # Descargar por separado
│   └── retail_inventory_ml_apl.csv    # Descargar por separado
└── output/
    ├── dashboard_ventas_inventario.png
    ├── notas_metodologicas.txt
    └── ...otros reportes CSV generados
```

Los archivos CSV de origen **no se incluyen en el repositorio** por su tamaño. El script crea la carpeta `output/` cuando se ejecuta.

## Instalación y ejecución

1. Descarga los dos archivos CSV de la fuente indicada más abajo.
2. Colócalos en la carpeta `data/` con sus nombres originales:
   - `retail_sales_ml_apl.csv`
   - `retail_inventory_ml_apl.csv`
3. Abre una terminal en la carpeta del proyecto e instala las dependencias:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. Ejecuta el análisis:

   ```bash
   python3 app.py
   ```

El panel se mostrará en pantalla y se guardará como `output/dashboard_ventas_inventario.png`. Los reportes CSV y las notas metodológicas se guardarán en `output/`.

## Metodología y criterios

- **Ventas netas:** suma de `Sales Amount`. Las devoluciones se mantienen con el signo registrado en el origen; no se descuentan por segunda vez.
- **Utilidad bruta:** ventas netas menos la suma de `Cogs`.
- **Margen bruto:** utilidad bruta dividida para ventas netas, multiplicada por 100.
- **Devoluciones:** se identifican usando `Is Return`; el porcentaje de registros con devolución no equivale necesariamente a una tasa de unidades devueltas.
- **Inventario disponible estimado:** suma de las cantidades no negativas de registros con `End Date = 9999-12-31` y `Start Date` anterior o igual a la fecha final del análisis. Los saldos negativos se registran como anomalías y solo se consideran cero para este indicador.
- **Integridad:** los archivos originales no se modifican; los nombres de categorías y modalidades se traducen únicamente para el análisis y la visualización.

## Limitaciones

El panel es **descriptivo**: no hace pronósticos, no presenta una auditoría contable y no constituye un sistema de inventario en tiempo real. Los valores de inventario son una estimación basada en la interpretación de los registros abiertos del archivo. Para uso comercial real haría falta validar el significado de esos intervalos y conciliarlos con las existencias físicas.

## Origen y licencia de los datos

**Retail Transactions and Stocks Data**, Jimmy Smith, Mendeley Data, versión 1, publicado el 27 de abril de 2026. [DOI: 10.17632/27x8mjm8k4.1](https://doi.org/10.17632/27x8mjm8k4.1). Licencia de los datos: **CC BY 4.0**.

Este repositorio es un ejercicio independiente de análisis y visualización; el conjunto de datos se atribuye a su autor original.
