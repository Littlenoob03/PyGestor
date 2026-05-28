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

    #RESUMEN ANUAL
    total_ingresos = sum(i.importe for i in ingresos)
    total_gastos_v = sum(g.importe for g in gastos)
    beneficio_neto = total_ingresos - total_gastos_v
    tasa_beneficio = (beneficio_neto / total_ingresos * 100) if total_ingresos else 0

    resumen_anual = card(
        ft.Column([
            ft.Text(f"Resumen Anual {year}", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            ft.ResponsiveRow([
                ft.Container(content=_kpi_mini("Total Ingresos",   fmt(total_ingresos), COLORS["stat1"]), col={"xs": 6, "sm": 4, "lg": 2}),
                ft.Container(content=_kpi_mini("Total Gastos",     fmt(total_gastos_v), COLORS["danger"]), col={"xs": 6, "sm": 4, "lg": 2}),
                ft.Container(content=_kpi_mini("Ahorro Neto",      fmt(beneficio_neto), COLORS["success"]), col={"xs": 6, "sm": 4, "lg": 2}),
                ft.Container(content=_kpi_mini("Margen",           f"{tasa_beneficio:.1f} %", COLORS["stat4"]), col={"xs": 6, "sm": 4, "lg": 2}),
                ft.Container(content=_kpi_mini("Nº Ingresos",      str(len(ingresos)),  COLORS["stat1"]), col={"xs": 6, "sm": 4, "lg": 2}),
                ft.Container(content=_kpi_mini("Nº Gastos",        str(len(gastos)),    COLORS["stat3"]), col={"xs": 6, "sm": 4, "lg": 2}),
            ], spacing=12),
        ], spacing=0),
    )

    #GRAFICO INGRESOS VS GASTOS ( BARRAS )
    ing_mes  = ingresos_por_mes(ingresos)
    gast_mes = gastos_por_mes(gastos)
    cl_b64 = bar_chart_ingresos_gastos(ing_mes, gast_mes, MESES, width_px=1000, height_px=350)

    mensual_chart = card(
        ft.Column([
            ft.Text("Ingresos vs Gastos Mensuales", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=cl_b64, height=280,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        expand=True,
    )

    #GRAFICO GASTOS POR CATEGORIA (DONUT)
    por_cat  = gastos_por_categoria(gastos)
    donut_b64 = donut_chart_gastos(por_cat, CAT_LABELS,
                                    width_px=600, height_px=350)

    gastos_chart = card(
        ft.Column([
            ft.Text("Gastos por Categoría", size=15,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=donut_b64, height=280,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        expand=True,
    )

    #GRAFICO COMPARATIVA TRIMESTRAL (BARRAS)
    trimestres = [calcular_trimestre(ingresos, gastos, t) for t in [1, 2, 3, 4]]
    trim_b64 = bar_chart_trimestral(trimestres, width_px=1200, height_px=400)

    def trim_table():
        rows = [
            ft.Container(
                content=ft.Row([
                    ft.Text("Período", size=11, weight=ft.FontWeight.BOLD, color=COLORS["text_muted"], width=50),
                    ft.Text("Ingresos", size=11, weight=ft.FontWeight.BOLD, color=COLORS["text_muted"], expand=True, text_align=ft.TextAlign.RIGHT),
                    ft.Text("Gastos", size=11, weight=ft.FontWeight.BOLD, color=COLORS["text_muted"], expand=True, text_align=ft.TextAlign.RIGHT),
                ]),
                padding=ft.Padding.symmetric(vertical=8, horizontal=12),
                border=ft.border.only(bottom=ft.border.BorderSide(1, COLORS["border"]))
            )
        ]
        for t in trimestres:
            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"T{t['trimestre']}", weight=ft.FontWeight.BOLD, size=13, color=COLORS["text_primary"], width=50),
                        ft.Text(fmt(t["base_ingresos"]), size=13, weight=ft.FontWeight.W_600, color=COLORS["stat1"], expand=True, text_align=ft.TextAlign.RIGHT),
                        ft.Text(fmt(t["base_gastos"]), size=13, weight=ft.FontWeight.W_600, color=COLORS["stat3"], expand=True, text_align=ft.TextAlign.RIGHT),
                    ]),
                    padding=ft.Padding.symmetric(vertical=10, horizontal=12),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, COLORS["border"])) if t["trimestre"] < 4 else None
                )
            )
        return ft.Container(
            content=ft.Column(rows, spacing=0),
            bgcolor="#F7F8FA",
            border_radius=12,
            padding=4
        )

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
            ft.Container(height=16),
            ft.ResponsiveRow([
                ft.Container(
                    content=ft.Image(src=trim_b64, height=320, fit=ft.BoxFit.CONTAIN),
                    col={"xs": 12, "lg": 7}
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Detalle Acumulado", weight=ft.FontWeight.BOLD, size=13, color=COLORS["text_primary"]),
                        trim_table()
                    ], spacing=12),
                    col={"xs": 12, "lg": 5},
                    padding=ft.Padding.only(top=20)
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
    )

    content = ft.Column([
        section_header("Informes", f"Análisis y estadísticas · {year}"),
        ft.Container(height=20),
        resumen_anual,
        ft.Container(height=16),
        ft.ResponsiveRow([
            ft.Container(content=mensual_chart, col={"xs": 12, "lg": 7}),
            ft.Container(content=gastos_chart, col={"xs": 12, "lg": 5})
        ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=16),
        trimestral_chart,
    ], spacing=0, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

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
        alignment=ft.Alignment(0, 0),
    )