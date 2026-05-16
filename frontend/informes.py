import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import (
    fmt, gastos_por_categoria,
    calcular_trimestre, ingresos_por_mes, gastos_por_mes
)
from frontend.styles import (
    COLORS, CAT_LABELS, MESES, card, section_header, page_wrapper,
)
from frontend.charts import (
    bar_chart_ingresos_gastos, donut_chart_gastos, bar_chart_trimestral,
)

def InformesView(db: Database, navigate) -> ft.Container:
    year     = datetime.now().year
    ingresos = db.ingresos_by_year(year)
    gastos   = db.gastos_by_year(year)

    # ── Resumen anual ──────────────────────────────────────
    total_ingresos = sum(i.importe for i in ingresos)
    total_gastos_v = sum(g.importe for g in gastos)
    beneficio_neto = total_ingresos - total_gastos_v
    tasa_beneficio = (beneficio_neto / total_ingresos * 100) if total_ingresos else 0

    resumen_anual = card(
        ft.Column([
            ft.Text(f"Resumen Anual {year}", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            ft.Row([
                _kpi_mini("Total Ingresos",   fmt(total_ingresos), COLORS["stat1"]),
                _kpi_mini("Total Gastos",     fmt(total_gastos_v), COLORS["danger"]),
                _kpi_mini("Ahorro Neto",      fmt(beneficio_neto), COLORS["success"]),
                _kpi_mini("Margen",           f"{tasa_beneficio:.1f} %", COLORS["stat4"]),
                _kpi_mini("Nº Ingresos",      str(len(ingresos)),  COLORS["stat1"]),
                _kpi_mini("Nº Gastos",        str(len(gastos)),    COLORS["stat3"]),
            ], spacing=12),
        ], spacing=0),
    )

    # ── BarChart – Ingresos vs Gastos Mensuales ────────────────────
    ing_mes  = ingresos_por_mes(ingresos)
    gast_mes = gastos_por_mes(gastos)
    cl_b64 = bar_chart_ingresos_gastos(ing_mes, gast_mes, MESES, width_px=480, height_px=250)

    mensual_chart = card(
        ft.Column([
            ft.Text("Ingresos vs Gastos Mensuales", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=cl_b64, width=480, height=250,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        expand=True,
    )

    # ── PieChart (donut) – Gastos por categoría ────────────
    por_cat  = gastos_por_categoria(gastos)
    donut_b64 = donut_chart_gastos(por_cat, CAT_LABELS,
                                    width_px=360, height_px=250)

    gastos_chart = card(
        ft.Column([
            ft.Text("Gastos por Categoría", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=donut_b64, width=360, height=250,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        expand=True,
    )

    # ── BarChart agrupado – Comparativa trimestral ─────────
    trimestres = [calcular_trimestre(ingresos, gastos, t) for t in [1, 2, 3, 4]]
    trim_b64 = bar_chart_trimestral(trimestres, width_px=560, height_px=260)

    trimestral_chart = card(
        ft.Column([
            ft.Row([
                ft.Text("Comparativa Trimestral", size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"]),
                ft.Row([
                    ft.Container(width=12, height=12,
                                 bgcolor=COLORS["stat1"], border_radius=3),
                    ft.Text("Ingresos", size=11, color=COLORS["text_secondary"]),
                    ft.Container(width=12, height=12,
                                 bgcolor=COLORS["stat3"], border_radius=3),
                    ft.Text("Gastos", size=11, color=COLORS["text_secondary"]),
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Image(src=trim_b64, width=560, height=260,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
    )

    content = ft.Column([
        section_header("Informes", f"Análisis y estadísticas · {year}"),
        ft.Container(height=20),
        resumen_anual,
        ft.Container(height=16),
        ft.Row([mensual_chart, gastos_chart], spacing=20,
               vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=16),
        trimestral_chart,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)


def _kpi_mini(label: str, value: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=11, color="#64748B"),
            ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=color),
        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#F7F8FA",
        border_radius=12,
        padding=16,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )