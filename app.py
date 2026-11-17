
"""Panel de ventas e inventario 2025–2026.

Datos: Retail Transactions and Stocks Data, Mendeley Data (CC BY 4.0).
La fuente no documenta la divisa. Los importes conservan sus unidades
originales y NO se etiquetan como USD. Tampoco se presupone su naturaleza
real o sintética. Los CSV originales no se alteran.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator

# ================================================================
# 1. RUTAS Y ESTILO
# ================================================================

BASE = Path(__file__).resolve().parent
DATOS = BASE / "data"
SALIDA = BASE / "output"

VENTAS_CSV = DATOS / "retail_sales_ml_apl.csv"
INVENTARIO_CSV = DATOS / "retail_inventory_ml_apl.csv"

FONDO = "#080F1E"
PANEL = "#152238"
BLANCO = "#F8FAFC"
GRIS = "#9CAEC4"
AZUL = "#38BDF8"
VERDE = "#34D399"
MORADO = "#A78BFA"
NARANJA = "#FB923C"
CUADRICULA = "#344358"

MESES = (
    "ene", "feb", "mar", "abr",
    "may", "jun", "jul", "ago",
    "sep", "oct", "nov", "dic"
)

CATEGORIAS = {
    "Scholar Footwear": "Calzado escolar",
    "Femme Footwear": "Calzado femenino",
    "Junior Apparel": "Ropa juvenil",
}

MODALIDADES = {
    "Full Price": "Precio regular",
    "Promo": "Promoción",
    "Markdown Tier 1": "Rebaja nivel 1",
    "Markdown Tier 2": "Rebaja nivel 2",
    "Clearance": "Liquidación",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "figure.facecolor": FONDO,
    "axes.facecolor": PANEL,
    "text.color": BLANCO,
    "axes.labelcolor": GRIS,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
    "axes.edgecolor": PANEL,
    "savefig.facecolor": FONDO,
})


# ================================================================
# 2. FUNCIONES DE FORMATO Y VALIDACIÓN
# ================================================================

def numero(valor, decimales=0):
    """Convierte 12345.67 a 12.345,67."""
    texto = f"{valor:,.{decimales}f}"

    return (
        texto.replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )


def corto(valor, _posicion=None):
    """Abrevia cifras para gráficos e indicadores."""
    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"{numero(valor / 1_000_000, 2)} M"

    if abs(valor) >= 1_000:
        return f"{numero(valor / 1_000, 0)} mil"

    return numero(valor)


def fecha_corta(fecha):
    return (
        f"{fecha.day:02d} "
        f"{MESES[fecha.month - 1]} "
        f"{fecha.year}"
    )


def comprobar_columnas(tabla, requeridas, nombre):
    faltantes = sorted(
        set(requeridas) - set(tabla.columns)
    )

    if faltantes:
        raise ValueError(
            f"Columnas ausentes en {nombre}: {faltantes}"
        )


def escribir_csv(tabla, nombre):
    tabla.to_csv(
        SALIDA / nombre,
        index=False,
        encoding="utf-8-sig",
    )


# ================================================================
# 3. CARGA Y VALIDACIÓN DE DATOS
# ================================================================

def cargar_datos():

    for archivo in (VENTAS_CSV, INVENTARIO_CSV):
        if not archivo.exists():
            raise FileNotFoundError(
                f"No se encuentra {archivo.name} "
                f"en la carpeta data/"
            )

    ventas = pd.read_csv(
        VENTAS_CSV,
        low_memory=False,
    )

    inventario = pd.read_csv(
        INVENTARIO_CSV,
        low_memory=False,
    )

    # Comprobar columnas originales.

    comprobar_columnas(
        ventas,
        [
            "Transaction Date",
            "Sales Type",
            "Is Return",
            "Sales Amount",
            "Cogs",
            "Qty Sold",
            "Product Division",
            "Store",
        ],
        "ventas",
    )

    comprobar_columnas(
        inventario,
        [
            "Start Date",
            "End Date",
            "Qty on hand",
            "Product Division",
            "Store",
            "Product No",
        ],
        "inventario",
    )

    # Limpiar ventas.

    originales = len(ventas)

    ventas["Transaction Date"] = pd.to_datetime(
        ventas["Transaction Date"],
        errors="coerce",
    )

    for columna in (
        "Sales Amount",
        "Cogs",
        "Qty Sold",
        "Is Return",
    ):
        ventas[columna] = pd.to_numeric(
            ventas[columna],
            errors="coerce",
        )

    ventas = ventas.dropna(
        subset=[
            "Transaction Date",
            "Sales Amount",
            "Cogs",
            "Is Return",
        ]
    ).copy()

    if ventas.empty:
        raise ValueError(
            "No hay ventas válidas para analizar."
        )

    # Traducir categorías y modalidades.

    ventas["categoria"] = (
        ventas["Product Division"]
        .fillna("Sin categoría")
        .replace(CATEGORIAS)
    )

    ventas["modalidad"] = (
        ventas["Sales Type"]
        .fillna("No especificada")
        .replace(MODALIDADES)
    )

    ventas["tienda"] = (
        ventas["Store"]
        .fillna("No identificada")
    )

    # Calcular utilidad bruta.

    ventas["utilidad_bruta"] = (
        ventas["Sales Amount"] - ventas["Cogs"]
    )

    ventas["mes"] = (
        ventas["Transaction Date"].dt.to_period("M")
    )

    # Preparar inventario.

    fecha_fin = ventas["Transaction Date"].max()

    inventario["Start Date"] = pd.to_datetime(
        inventario["Start Date"],
        errors="coerce",
    )

    inventario["Qty on hand"] = pd.to_numeric(
        inventario["Qty on hand"],
        errors="coerce",
    )

    # 9999-12-31 identifica registros abiertos.
    # Pandas no admite ese año como fecha Timestamp.

    abierto = (
        inventario["End Date"]
        .astype("string")
        .str.startswith("9999-12-31")
        .fillna(False)
    )

    vigente = inventario.loc[
        abierto
        & (inventario["Start Date"] <= fecha_fin)
        & inventario["Qty on hand"].notna()
    ].copy()

    if vigente.empty:
        raise ValueError(
            "No se encontraron registros abiertos de inventario."
        )

    vigente["categoria"] = (
        vigente["Product Division"]
        .fillna("Sin categoría")
        .replace(CATEGORIAS)
    )

    vigente["tienda"] = (
        vigente["Store"]
        .fillna("No identificada")
    )

    # Registrar los saldos negativos.
    # Para unidades disponibles se consideran cero.

    negativos = int(
        vigente["Qty on hand"].lt(0).sum()
    )

    vigente["disponibles"] = (
        vigente["Qty on hand"].clip(lower=0)
    )

    auditoria = {
        "registros_ventas_descartados": (
            originales - len(ventas)
        ),
        "registros_inventario_historico": len(inventario),
        "registros_inventario_abiertos": len(vigente),
        "registros_saldo_negativo": negativos,
    }

    return ventas, vigente, auditoria


# ================================================================
# 4. CÁLCULO DE INDICADORES
# ================================================================

def analizar(ventas, stock):

    ingresos = float(
        ventas["Sales Amount"].sum()
    )

    costos = float(
        ventas["Cogs"].sum()
    )

    utilidad = ingresos - costos

    devoluciones = (
        ventas["Is Return"].eq(1)
    )

    metricas = {
        "ventas_netas": ingresos,
        "costos_netos": costos,
        "utilidad_bruta": utilidad,
        "margen_bruto_pct": (
            utilidad / ingresos * 100
            if ingresos else 0.0
        ),
        "unidades_en_inventario": float(
            stock["disponibles"].sum()
        ),
        "registros_ventas": len(ventas),
        "registros_devolucion": int(
            devoluciones.sum()
        ),
        "porcentaje_registros_devolucion": float(
            devoluciones.mean() * 100
        ),
    }

    # Ventas mensuales.

    mensual = (
        ventas.groupby("mes")
        .agg(
            ventas_netas=("Sales Amount", "sum"),
            costos_netos=("Cogs", "sum"),
            utilidad_bruta=("utilidad_bruta", "sum"),
        )
        .reset_index()
        .sort_values("mes")
    )

    mensual["etiqueta"] = mensual["mes"].map(
        lambda mes: (
            f"{MESES[mes.month - 1]} "
            f"{str(mes.year)[-2:]}"
        )
    )

    mensual["mes"] = (
        mensual["mes"].astype(str)
    )

    # Ventas por modalidad.

    por_modalidad = (
        ventas.groupby("modalidad")["Sales Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # Ventas por categoría.

    por_categoria = (
        ventas.groupby("categoria")["Sales Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # Tiendas con mayores ventas.

    por_tienda = (
        ventas.groupby("tienda")["Sales Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(7)
    )

    # Inventario disponible por categoría.

    stock_categoria = (
        stock.groupby("categoria")["disponibles"]
        .sum()
        .sort_values(ascending=False)
    )

    # Inventario disponible por tienda.

    stock_tienda = (
        stock.groupby("tienda")["disponibles"]
        .sum()
        .sort_values(ascending=False)
    )

    # Resumen de devoluciones.

    reporte_devoluciones = (
        ventas.loc[devoluciones]
        .groupby("categoria")["Sales Amount"]
        .agg(
            registros="size",
            importe_neto="sum",
        )
        .reset_index()
    )

    reportes = {
        "mensual": mensual,
        "modalidad": por_modalidad,
        "categoria": por_categoria,
        "tienda": por_tienda,
        "stock_categoria": stock_categoria,
        "stock_tienda": stock_tienda,
        "devoluciones": reporte_devoluciones,
    }

    return metricas, reportes


# ================================================================
# 5. ESTILO DE LOS GRÁFICOS
# ================================================================

def estilo_grafico(ax, titulo, horizontal=False):

    ax.set_facecolor(PANEL)

    ax.set_title(
        titulo,
        loc="left",
        fontsize=12,
        fontweight="bold",
        color=BLANCO,
        pad=17,
    )

    for borde in ax.spines.values():
        borde.set_visible(False)

    ax.tick_params(
        axis="both",
        labelsize=9,
        length=0,
        pad=8,
    )

    ax.grid(
        axis="x" if horizontal else "y",
        color=CUADRICULA,
        alpha=0.28,
    )

    ax.set_axisbelow(True)


def tarjeta(
    figura,
    posicion,
    titulo,
    valor,
    detalle,
    color,
):

    ax = figura.add_axes(posicion)

    ax.set_facecolor(PANEL)

    for borde in ax.spines.values():
        borde.set_visible(False)

    ax.set_xticks([])
    ax.set_yticks([])

    ax.text(
        0.06, 0.76,
        titulo,
        transform=ax.transAxes,
        color=GRIS,
        fontsize=10,
    )

    ax.text(
        0.06, 0.38,
        valor,
        transform=ax.transAxes,
        color=color,
        fontsize=23,
        fontweight="bold",
    )

    ax.text(
        0.06, 0.12,
        detalle,
        transform=ax.transAxes,
        color=GRIS,
        fontsize=8.5,
    )


def grafico_barras(
    ax,
    serie,
    titulo,
    color,
    unidad="importe",
):

    estilo_grafico(
        ax,
        titulo,
        horizontal=True,
    )

    serie = (
        serie.sort_values().tail(7)
    )

    barras = ax.barh(
        serie.index.astype(str),
        serie.to_numpy(),
        height=0.53,
        color=color,
    )

    ax.xaxis.set_major_formatter(
        FuncFormatter(corto)
    )

    ax.xaxis.set_major_locator(
        MaxNLocator(nbins=5)
    )

    maximo = (
        float(serie.max())
        if len(serie) else 0.0
    )

    ax.set_xlim(
        0,
        max(maximo * 1.20, 1),
    )

    for barra in barras:
        ax.annotate(
            corto(barra.get_width()),
            (
                barra.get_width(),
                barra.get_y() + barra.get_height() / 2,
            ),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=BLANCO,
        )


# ================================================================
# 6. CREACIÓN DEL DASHBOARD
# ================================================================

def crear_panel(metricas, reportes, inicio, fin):

    fig = plt.figure(
        figsize=(20, 17),
        facecolor=FONDO,
    )

    # Encabezado principal.

    fig.text(
        0.055, 0.962,
        "VENTAS E INVENTARIO",
        fontsize=29,
        fontweight="bold",
        color=BLANCO,
    )

    fig.text(
        0.055, 0.940,
        "PANEL DE RENDIMIENTO COMERCIAL",
        fontsize=13,
        color=AZUL,
    )

    fig.text(
        0.055, 0.918,
        f"Período de análisis  ·  "
        f"{fecha_corta(inicio)} – {fecha_corta(fin)}",
        fontsize=10,
        color=GRIS,
    )

    fig.text(
        0.950, 0.957,
        "ANÁLISIS DE DATOS  /  2025–2026",
        fontsize=10,
        ha="right",
        color=MORADO,
    )

    # Indicadores principales.

    datos_tarjetas = [
        (
            [0.055, 0.814, 0.205, 0.078],
            "VENTAS NETAS",
            corto(metricas["ventas_netas"]),
            "Ventas menos devoluciones",
            AZUL,
        ),
        (
            [0.280, 0.814, 0.205, 0.078],
            "UTILIDAD BRUTA",
            corto(metricas["utilidad_bruta"]),
            "Ingresos menos costos",
            VERDE,
        ),
        (
            [0.505, 0.814, 0.205, 0.078],
            "MARGEN BRUTO",
            f"{numero(metricas['margen_bruto_pct'], 1)} %",
            "Rentabilidad sobre ventas",
            MORADO,
        ),
        (
            [0.730, 0.814, 0.220, 0.078],
            "UNIDADES EN INVENTARIO",
            numero(metricas["unidades_en_inventario"]),
            f"Corte: {fecha_corta(fin)}",
            NARANJA,
        ),
    ]

    for argumentos in datos_tarjetas:
        tarjeta(fig, *argumentos)

    # Distribución fija de los gráficos.

    ix = 0.085
    iw = 0.435

    dx = 0.675
    dw = 0.275

    alto = 0.145

    filas = (
        0.605,
        0.365,
        0.125,
    )

    mensual = reportes["mensual"]

    x = list(range(len(mensual)))

    # ------------------------------------------------------------
    # GRÁFICO 1: EVOLUCIÓN MENSUAL DE VENTAS
    # ------------------------------------------------------------

    ax1 = fig.add_axes([
        ix, filas[0], iw, alto
    ])

    estilo_grafico(
        ax1,
        "01  /  EVOLUCIÓN MENSUAL DE VENTAS",
    )

    ax1.plot(
        x,
        mensual["ventas_netas"],
        color=AZUL,
        linewidth=3,
        marker="o",
        markersize=6,
        markerfacecolor=FONDO,
        markeredgecolor=AZUL,
        markeredgewidth=2,
    )

    ax1.fill_between(
        x,
        mensual["ventas_netas"].to_numpy(),
        alpha=0.11,
        color=AZUL,
    )

    ax1.set_xticks(
        x,
        mensual["etiqueta"],
        fontsize=8,
    )

    ax1.yaxis.set_major_formatter(
        FuncFormatter(corto)
    )

    ax1.yaxis.set_major_locator(
        MaxNLocator(nbins=5)
    )

    ax1.set_ylim(
        0,
        max(
            float(mensual["ventas_netas"].max()) * 1.18,
            1,
        ),
    )

    # ------------------------------------------------------------
    # GRÁFICO 2: VENTAS POR MODALIDAD
    # ------------------------------------------------------------

    ax2 = fig.add_axes([
        dx, filas[0], dw, alto
    ])

    grafico_barras(
        ax2,
        reportes["modalidad"],
        "02  /  VENTAS POR MODALIDAD",
        MORADO,
    )

    # ------------------------------------------------------------
    # GRÁFICO 3: VENTAS Y COSTOS POR MES
    # ------------------------------------------------------------

    ax3 = fig.add_axes([
        ix, filas[1], iw, alto
    ])

    estilo_grafico(
        ax3,
        "03  /  VENTAS Y COSTOS POR MES",
    )

    ancho = 0.36

    ax3.bar(
        [i - ancho / 2 for i in x],
        mensual["ventas_netas"],
        width=ancho,
        color=AZUL,
        label="Ventas netas",
    )

    ax3.bar(
        [i + ancho / 2 for i in x],
        mensual["costos_netos"],
        width=ancho,
        color=NARANJA,
        label="Costos netos",
    )

    ax3.set_xticks(
        x,
        mensual["etiqueta"],
        fontsize=8,
    )

    ax3.yaxis.set_major_formatter(
        FuncFormatter(corto)
    )

    ax3.yaxis.set_major_locator(
        MaxNLocator(nbins=5)
    )

    ax3.set_ylim(
        0,
        max(
            float(
                mensual[
                    ["ventas_netas", "costos_netos"]
                ].max().max()
            ) * 1.22,
            1,
        ),
    )

    ax3.legend(
        loc="upper left",
        ncol=2,
        frameon=False,
        labelcolor=BLANCO,
        fontsize=9,
    )

    # ------------------------------------------------------------
    # GRÁFICO 4: VENTAS POR LÍNEA DE PRODUCTO
    # ------------------------------------------------------------

    ax4 = fig.add_axes([
        dx, filas[1], dw, alto
    ])

    grafico_barras(
        ax4,
        reportes["categoria"],
        "04  /  VENTAS POR LÍNEA DE PRODUCTO",
        VERDE,
    )

    # ------------------------------------------------------------
    # GRÁFICO 5: TIENDAS CON MAYORES VENTAS
    # ------------------------------------------------------------

    ax5 = fig.add_axes([
        ix, filas[2], iw, alto
    ])

    grafico_barras(
        ax5,
        reportes["tienda"],
        "05  /  TIENDAS CON MAYORES VENTAS",
        AZUL,
    )

    # ------------------------------------------------------------
    # GRÁFICO 6: EXISTENCIAS POR LÍNEA
    # ------------------------------------------------------------

    ax6 = fig.add_axes([
        dx, filas[2], dw, alto
    ])

    grafico_barras(
        ax6,
        reportes["stock_categoria"],
        "06  /  EXISTENCIAS POR LÍNEA",
        MORADO,
        unidad="unidades",
    )

    # Pie del dashboard.

    fig.text(
        0.055, 0.057,
        "FUENTE  /  Retail Transactions and Stocks Data · Mendeley Data",
        fontsize=9,
        color=GRIS,
    )

    fig.text(
        0.055, 0.038,
        f"Fecha de corte: {fecha_corta(fin)}   |   "
        f"Elaboración propia con Python",
        fontsize=8.5,
        color=GRIS,
    )

    fig.text(
        0.950, 0.038,
        "PANDAS  /  MATPLOTLIB",
        fontsize=9,
        ha="right",
        color=AZUL,
    )

    return fig


# ================================================================
# 7. EXPORTACIÓN DE RESULTADOS
# ================================================================

def exportar(
    metricas,
    reportes,
    auditoria,
    inicio,
    fin,
):

    SALIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Resumen mensual.

    escribir_csv(
        reportes["mensual"].drop(
            columns="etiqueta"
        ),
        "ventas_mensuales.csv",
    )

    # Reportes por categoría, tienda y modalidad.

    configuracion = [
        (
            "modalidad",
            "ventas_por_modalidad.csv",
            "ventas_netas",
            "modalidad",
        ),
        (
            "categoria",
            "ventas_por_categoria.csv",
            "ventas_netas",
            "categoria",
        ),
        (
            "tienda",
            "ventas_por_tienda.csv",
            "ventas_netas",
            "tienda",
        ),
        (
            "stock_categoria",
            "inventario_por_categoria.csv",
            "unidades",
            "categoria",
        ),
        (
            "stock_tienda",
            "inventario_por_tienda.csv",
            "unidades",
            "tienda",
        ),
    ]

    for (
        clave,
        nombre_archivo,
        nombre_valor,
        nombre_indice,
    ) in configuracion:

        tabla = (
            reportes[clave]
            .rename(nombre_valor)
            .rename_axis(nombre_indice)
        )

        escribir_csv(
            tabla.reset_index(),
            nombre_archivo,
        )

    # Resumen de devoluciones.

    escribir_csv(
        reportes["devoluciones"].rename(
            columns={
                "importe_neto": (
                    "importe_devoluciones_con_signo"
                )
            }
        ),
        "devoluciones_por_categoria.csv",
    )

    # Indicadores generales.

    resumen = {
        "inicio": inicio.date().isoformat(),
        "fin": fin.date().isoformat(),
        **metricas,
        **auditoria,
    }

    escribir_csv(
        pd.DataFrame([resumen]),
        "indicadores_generales.csv",
    )

    # Notas metodológicas fuera del dashboard.

    notas = (
        "NOTAS METODOLÓGICAS\n"
        "===================\n\n"
        "FUENTE: Retail Transactions and Stocks Data, "
        "Mendeley Data (2026).\n\n"
        "MONEDA:\n"
        "Los archivos no especifican claramente la divisa.\n"
        "Los importes se mantienen en sus unidades originales.\n"
        "No deben presentarse como USD sin confirmación.\n\n"
        "DEVOLUCIONES:\n"
        "Las devoluciones ya están incluidas como importes "
        "negativos en ventas y costos.\n"
        "No se restan una segunda vez.\n\n"
        "INVENTARIO:\n"
        "Las existencias se calculan a partir de registros "
        "con End Date=9999-12-31.\n"
        "La fecha de inicio debe ser anterior o igual "
        "al cierre del período de ventas.\n"
        "Los saldos negativos se identifican como anomalías.\n"
        "Se consideran cero solamente para calcular "
        "las unidades disponibles.\n\n"
        "PERÍODO:\n"
        "Abril de 2026 es un mes parcial: "
        "el último registro corresponde al día 24.\n\n"
        "PROCEDENCIA:\n"
        "La naturaleza real o sintética del conjunto "
        "de datos no está confirmada.\n"
    )

    (SALIDA / "notas_metodologicas.txt").write_text(
        notas,
        encoding="utf-8",
    )


# ================================================================
# 8. EJECUCIÓN PRINCIPAL
# ================================================================

def main():

    print(
        "Cargando información de ventas e inventario..."
    )

    ventas, stock, auditoria = cargar_datos()

    inicio = (
        ventas["Transaction Date"].min()
    )

    fin = (
        ventas["Transaction Date"].max()
    )

    metricas, reportes = analizar(
        ventas,
        stock,
    )

    # Exportar reportes.

    exportar(
        metricas,
        reportes,
        auditoria,
        inicio,
        fin,
    )

    # Crear dashboard.

    panel = crear_panel(
        metricas,
        reportes,
        inicio,
        fin,
    )

    imagen = (
        SALIDA / "dashboard_ventas_inventario.png"
    )

    panel.savefig(
        imagen,
        dpi=190,
        bbox_inches="tight",
        facecolor=FONDO,
    )

    # Resultados en la terminal.

    print("\nANÁLISIS COMPLETADO")
    print("-" * 45)

    print(
        f"Período: "
        f"{fecha_corta(inicio)} – {fecha_corta(fin)}"
    )

    print(
        f"Registros de ventas: "
        f"{numero(metricas['registros_ventas'])}"
    )

    print(
        f"Ventas netas: "
        f"{numero(metricas['ventas_netas'], 2)}"
    )

    print(
        f"Utilidad bruta: "
        f"{numero(metricas['utilidad_bruta'], 2)}"
    )

    print(
        f"Margen bruto: "
        f"{numero(metricas['margen_bruto_pct'], 2)} %"
    )

    print(
        f"Unidades en inventario: "
        f"{numero(metricas['unidades_en_inventario'])}"
    )

    print(
        f"Dashboard: {imagen}"
    )

    print(
        "Documentación metodológica: "
        "output/notas_metodologicas.txt"
    )

    plt.show()


if __name__ == "__main__":
    main()
