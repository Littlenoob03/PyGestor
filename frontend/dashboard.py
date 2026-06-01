import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import (
    formatear_moneda, calcular_resumen, ingresos_por_mes, gastos_por_mes,
    gastos_por_categoria,
)
from frontend.styles import (
    COLORS, GRADIENTS, MESES, CAT_LABELS,
    tarjetas_informativas, tarjeta, cabecera,
    separador, etiqueta, vista_adaptable,
)
from frontend.graficos import (
    grafico_mensual_lineas, grafico_donut_gastos,
)

def VistaDashboard(db: Database, navegar) -> ft.Container:
    year     = datetime.now().year
    ingresos = db.ingresos_por_año(year)
    gastos   = db.gastos_por_año(year)
    res      = calcular_resumen(ingresos, gastos)

    #TARJETAS DEL DASHBOARD (INGRESOS, GASTOS Y AHORRO NETO)
    kpi_data = [
        ("Ingresos Totales",  formatear_moneda(res["total_ingresos"]), "Fuentes de ingreso",
         GRADIENTS[0], ft.Icons.TRENDING_UP),
        ("Gastos Totales",    formatear_moneda(res["total_gastos"]),   "Personales",
         GRADIENTS[1], ft.Icons.TRENDING_DOWN),
        ("Ahorro Neto",       formatear_moneda(res["beneficio"]),      "Ingresos – Gastos",
         GRADIENTS[2], ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED),
    ]
    kpis = ft.ResponsiveRow([
        ft.Container(content=tarjetas_informativas(t, v, s, ga, gb, icon=ic), col={"xs": 12, "md": 4})
        for t, v, s, (ga, gb), ic in kpi_data
    ], spacing=16)

    #GRAFICO DE EVOLUCION MENSUAL
    ing_mes  = ingresos_por_mes(ingresos)
    gast_mes = gastos_por_mes(gastos)

    line_b64 = grafico_mensual_lineas(ing_mes, gast_mes, MESES,
                                   width_px=1000, height_px=350)

    grafico = tarjeta(
        ft.Column([
            ft.Row([
                ft.Text("Evolución Mensual", size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"]),
                ft.Row([
                    ft.Container(width=10, height=10,
                                 bgcolor=COLORS["stat1"], border_radius=3),
                    ft.Text("Ingresos", size=11, color=COLORS["text_secondary"]),
                    ft.Container(width=10, height=10,
                                 bgcolor=COLORS["stat3"], border_radius=3),
                    ft.Text("Gastos", size=11, color=COLORS["text_secondary"]),
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Image(src=line_b64, height=240,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
    )

    #GRAFICO DE GASTOS POR CATEGORIA (DONUT)
    por_cat  = gastos_por_categoria(gastos)
    donut_b64 = grafico_donut_gastos(por_cat, CAT_LABELS,
                                    width_px=600, height_px=350)

    gastos_chart = tarjeta(
        ft.Column([
            ft.Text("Gastos por Categoría", size=15,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=donut_b64, height=240,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
    )

    #ULTIMOS INGRESOS
    ultimas = sorted(db.ingresos, key=lambda i: i.fecha, reverse=True)[:5]

    def fila_ingreso(i):
        nombre = i.origen if i.origen else "—"
        initials = "".join(w[0] for w in nombre.split()[:2]).upper() if nombre != "—" else "-"
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(initials, size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="white"),
                    width=36, height=36, border_radius=10,
                    bgcolor=COLORS["primary"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(i.concepto, size=13,
                            weight=ft.FontWeight.W_600,
                            color=COLORS["text_primary"]),
                    ft.Text(f"{nombre} · {i.fecha}", size=11,
                            color=COLORS["text_muted"]),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Text(formatear_moneda(i.total), size=13,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"]),
                    etiqueta("Cobrado" if i.estado == "cobrado" else "Pendiente",
                          "success" if i.estado == "cobrado" else "warning"),
                ], spacing=4,
                   horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=12),
            padding=ft.Padding.symmetric(vertical=10),
        )

    ingresos_list = tarjeta(
        ft.Column([
            ft.Row([
                ft.Text("Últimos Ingresos", size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"]),
                ft.TextButton("Ver todos →",
                              on_click=lambda e: navegar("ingresos")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(
                controls=[fila_ingreso(i) for i in ultimas] if ultimas else
                [ft.Text("No hay ingresos aún", size=13,
                         color=COLORS["text_muted"])],
                spacing=0,
            ),
        ], spacing=0),
        expand=True,
    )

    content = ft.Column([
        cabecera("Dashboard", f"Resumen general · {year}"),
        ft.Container(height=20),
        kpis,
        ft.Container(height=20),
        ft.ResponsiveRow([
            ft.Container(content=grafico, col={"xs": 12, "lg": 7}),
            ft.Container(content=gastos_chart, col={"xs": 12, "lg": 5})
        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=20),
        ingresos_list,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return vista_adaptable(content)