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
# Semántica: azul=ingresos, violeta=gastos, esmeralda=beneficio, ámbar=fiscal
C_INDIGO  = "#3B82F6"   # azul     → Ingresos
C_EMERALD = "#10B981"   # esmeralda
C_ROSE    = "#8B5CF6"   # violeta  → Gastos
C_SKY     = "#06B6D4"   # cyan
C_AMBER   = "#F59E0B"   # ámbar
C_PURPLE  = "#EC4899"   # rosa
C_TEAL    = "#14B8A6"   # teal
C_ORANGE  = "#F97316"   # naranja
C_RED     = "#DC2626"   # rojo profundo

CHART_PALETTE = [C_INDIGO, C_EMERALD, C_AMBER,
                 C_RED,    C_TEAL,    C_ROSE,
                 C_SKY,    C_ORANGE]

BG_COLOR  = "#FFFFFF"
GRID_CLR  = "#F3F4F6"
TEXT_CLR  = "#6B7280"
TEXT_DARK = "#111827"

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


# ── 3. BarChart – Ingresos vs Gastos Mensuales ──────────────
def bar_chart_ingresos_gastos(ing_mes: list, gast_mes: list, meses: list,
                              width_px=480, height_px=240) -> str:
    if not any(ing_mes) and not any(gast_mes):
        fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_CLR)
        ax.axis("off")
        return _to_b64(fig)

    fig, ax = plt.subplots(figsize=(width_px / 130, height_px / 130))
    import numpy as np
    x = np.arange(len(meses))
    width = 0.35

    ax.bar(x - width/2, ing_mes, width, label='Ingresos', color=CHART_PALETTE[0], zorder=2)
    ax.bar(x + width/2, gast_mes, width, label='Gastos', color=CHART_PALETTE[3], zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([m[:3] for m in meses], fontsize=8, color=TEXT_CLR)
    ax.tick_params(axis="y", labelsize=8, colors=TEXT_CLR, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color=GRID_CLR, linestyle="--", linewidth=0.5, zorder=0)
    
    ax.legend(fontsize=8, frameon=False, labelcolor=TEXT_CLR, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
    
    fig.tight_layout()
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
