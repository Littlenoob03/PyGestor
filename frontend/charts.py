"""
charts.py – Generación de gráficos con matplotlib para GestorPro.
Devuelve las imágenes en base64 para usarlas con ft.Image(src_base64=...).
"""
import io
import base64
import matplotlib
matplotlib.use("Agg")   # Backend sin ventana
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter

# ── Paleta coherente con el diseño de GestorPro ───────────
C_INDIGO  = "#6366F1"
C_EMERALD = "#10B981"
C_ROSE    = "#F43F5E"
C_SKY     = "#0EA5E9"
C_AMBER   = "#F59E0B"
C_PURPLE  = "#A855F7"
C_TEAL    = "#14B8A6"
C_ORANGE  = "#F97316"

CHART_PALETTE = [C_INDIGO, C_EMERALD, C_AMBER,
                 C_ROSE,   C_TEAL,    C_PURPLE,
                 C_SKY,    C_ORANGE]

BG_COLOR  = "#FFFFFF"
GRID_CLR  = "#F1F5F9"
TEXT_CLR  = "#475569"
TEXT_DARK = "#0F172A"

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.spines.left": False,
    "axes.spines.bottom": False,
    "axes.facecolor":   BG_COLOR,
    "figure.facecolor": BG_COLOR,
    "axes.grid":        True,
    "grid.color":       GRID_CLR,
    "grid.linewidth":   1,
    "axes.labelcolor":  TEXT_CLR,
    "xtick.color":      TEXT_CLR,
    "ytick.color":      TEXT_CLR,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
})


def _to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130,
                bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def euro_fmt(x, pos):
    if x >= 1000:
        return f"{x/1000:.0f}k€"
    return f"{x:.0f}€"


# ── 1. LineChart – Evolución mensual ──────────────────────
def line_chart_mensual(ing_mes: list, gast_mes: list,
                       meses: list, width_px=560, height_px=220) -> str:
    fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))

    x = range(12)
    ax.plot(x, ing_mes,  color=C_INDIGO,  linewidth=2.5,
            marker="o", markersize=4, label="Ingresos")
    ax.fill_between(x, ing_mes,  alpha=0.08, color=C_INDIGO)

    ax.plot(x, gast_mes, color=C_ROSE,    linewidth=2.5,
            marker="o", markersize=4, label="Gastos")
    ax.fill_between(x, gast_mes, alpha=0.06, color=C_ROSE)

    ax.set_xticks(range(12))
    ax.set_xticklabels(meses, fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9, frameon=False,
              labelcolor=TEXT_CLR, loc="upper left")
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", color=GRID_CLR, linewidth=1)
    ax.grid(axis="x", visible=False)

    return _to_b64(fig)


# ── 2. PieChart (donut) – Distribución de gastos ─────────
def donut_chart_gastos(por_cat: dict, labels_map: dict,
                       width_px=260, height_px=220) -> str:
    if not por_cat:
        fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_CLR)
        ax.axis("off")
        return _to_b64(fig)

    sorted_cat = sorted(por_cat.items(), key=lambda x: -x[1])
    valores = [v for _, v in sorted_cat]
    etiquetas = [labels_map.get(k, ("📦","Otros"))[1] for k, _ in sorted_cat]
    colores   = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(sorted_cat))]
    total     = sum(valores)

    fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
    wedges, texts = ax.pie(
        valores,
        colors=colores,
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )

    # Texto central
    ax.text(0, 0, f"{total:.0f}€", ha="center", va="center",
            fontsize=11, fontweight="bold", color=TEXT_DARK)

    # Leyenda lateral
    legend_patches = [
        mpatches.Patch(color=c, label=f"{l}  {v/total*100:.0f}%")
        for c, l, v in zip(colores, etiquetas, valores)
    ]
    ax.legend(handles=legend_patches, loc="center left",
              bbox_to_anchor=(1, 0.5), fontsize=8,
              frameon=False, labelcolor=TEXT_CLR)
    ax.axis("equal")

    return _to_b64(fig)


# ── 3. BarChart – Ingresos por cliente ────────────────────
def bar_chart_clientes(por_cliente: dict,
                       width_px=480, height_px=240) -> str:
    if not por_cliente:
        fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_CLR)
        ax.axis("off")
        return _to_b64(fig)

    sorted_cl = sorted(por_cliente.items(), key=lambda x: -x[1])
    nombres = [n[:15] + "…" if len(n) > 15 else n for n, _ in sorted_cl]
    valores = [v for _, v in sorted_cl]
    colores = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(sorted_cl))]

    fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
    bars = ax.bar(nombres, valores, color=colores, width=0.5,
                  zorder=2)

    # Etiquetas sobre barras
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(valores) * 0.02,
                f"{val:.0f}€", ha="center", va="bottom",
                fontsize=8, color=TEXT_DARK, fontweight="bold")

    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.set_ylim(bottom=0, top=max(valores) * 1.22)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", color=GRID_CLR, linewidth=1, zorder=0)
    ax.grid(axis="x", visible=False)

    # Bordes redondeados (simular con rects)
    for bar in bars:
        bar.set_linewidth(0)

    return _to_b64(fig)


# ── 4. BarChart agrupado – Comparativa trimestral ─────────
def bar_chart_trimestral(trimestres: list,
                         width_px=560, height_px=240) -> str:
    import numpy as np

    t_names = ["T1", "T2", "T3", "T4"]
    ing  = [d["base_ingresos"] for d in trimestres]
    gast = [d["base_gastos"]   for d in trimestres]
    x    = np.arange(len(t_names))
    w    = 0.35

    fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
    b1 = ax.bar(x - w / 2, ing,  w, color=C_INDIGO, label="Ingresos",
                zorder=2, linewidth=0)
    b2 = ax.bar(x + w / 2, gast, w, color=C_ROSE,   label="Gastos",
                zorder=2, linewidth=0)

    ax.set_xticks(x)
    ax.set_xticklabels(t_names)
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9, frameon=False, labelcolor=TEXT_CLR)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", color=GRID_CLR, linewidth=1, zorder=0)
    ax.grid(axis="x", visible=False)

    return _to_b64(fig)
