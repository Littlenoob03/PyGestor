import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import (
    fmt, calcular_resumen, ingresos_por_mes, gastos_por_mes,
    gastos_por_categoria,
)
from frontend.styles import (
    COLORS, GRADIENTS, MESES, CAT_LABELS,
    gradient_stat_card, card, section_header,
    divider, badge, page_wrapper,
)
from frontend.charts import (
    line_chart_mensual, donut_chart_gastos,
)


def DashboardView(db: Database, navigate) -> ft.Container:
    year     = datetime.now().year
    facturas = db.facturas_by_year(year)
    gastos   = db.gastos_by_year(year)
    res      = calcular_resumen(facturas, gastos)

    # ── KPI Cards con gradiente ─────────────────────────────
    kpi_data = [
        ("Ingresos Totales",  fmt(res["total_ingresos"]), "Base imponible",
         GRADIENTS[0], ft.Icons.TRENDING_UP),
        ("Gastos Totales",    fmt(res["total_gastos"]),   "Deducibles",
         GRADIENTS[1], ft.Icons.TRENDING_DOWN),
        ("Beneficio Neto",    fmt(res["beneficio"]),      "Ingresos – Gastos",
         GRADIENTS[2], ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED),
        ("IVA a Declarar",    fmt(res["iva_neto"]),       "Repercutido – Soportado",
         GRADIENTS[3], ft.Icons.RECEIPT_OUTLINED),
    ]
    kpis = ft.Row([
        gradient_stat_card(t, v, s, ga, gb, icon=ic)
        for t, v, s, (ga, gb), ic in kpi_data
    ], spacing=16)

    # ── LineChart – Evolución mensual ──────────────────────
    ing_mes  = ingresos_por_mes(facturas)
    gast_mes = gastos_por_mes(gastos)

    line_b64 = line_chart_mensual(ing_mes, gast_mes, MESES,
                                   width_px=560, height_px=230)

    grafico = card(
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
            ft.Container(height=8),
            ft.Image(src=line_b64, width=560, height=230,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        expand=True,
    )

    # ── PieChart (donut) – Gastos por categoría ────────────
    por_cat  = gastos_por_categoria(gastos)
    donut_b64 = donut_chart_gastos(por_cat, CAT_LABELS,
                                    width_px=280, height_px=200)

    gastos_chart = card(
        ft.Column([
            ft.Text("Gastos por Categoría", size=15,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_primary"]),
            ft.Container(height=8),
            ft.Image(src=donut_b64, width=280, height=200,
                     fit=ft.BoxFit.CONTAIN),
        ], spacing=0),
        width=320,
    )

    # ── Resumen Fiscal ─────────────────────────────────────
    def fiscal_row(label, value, color=COLORS["text_primary"]):
        return ft.Row([
            ft.Text(label, size=13,
                    color=COLORS["text_secondary"], expand=True),
            ft.Text(value, size=13,
                    weight=ft.FontWeight.BOLD, color=color),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    fiscal = card(
        ft.Column([
            ft.Text("Resumen Fiscal", size=15,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_primary"]),
            ft.Container(height=12),
            fiscal_row("IVA Repercutido",
                       fmt(res["iva_repercutido"]), COLORS["danger"]),
            divider(),
            fiscal_row("IVA Soportado",
                       fmt(res["iva_soportado"]),   COLORS["success"]),
            divider(),
            fiscal_row("IVA a Liquidar",
                       fmt(res["iva_neto"]),         COLORS["primary"]),
            divider(),
            fiscal_row("IRPF Retenido",
                       fmt(res["irpf_retenido"]),    COLORS["text_primary"]),
            divider(),
            fiscal_row("IRPF Est. (20%)",
                       fmt(res["irpf_estimado"]),    COLORS["stat3"]),
            divider(),
            fiscal_row("Facturas Pendientes",
                       str(res["pendientes"]),       COLORS["warning_text"]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Text("Cuota SS est.: 294 €/mes", size=12,
                                color=COLORS["danger"],
                                weight=ft.FontWeight.W_500),
                bgcolor=COLORS["danger_bg"], border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            ),
        ], spacing=8),
        width=270,
    )

    # ── Últimas Facturas ───────────────────────────────────
    ultimas = sorted(db.facturas, key=lambda f: f.fecha, reverse=True)[:5]

    def factura_row(f):
        cl = db.get_cliente(f.cliente_id)
        nombre = cl.nombre if cl else "—"
        initials = "".join(w[0] for w in nombre.split()[:2]).upper()
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
                    ft.Text(f.numero, size=13,
                            weight=ft.FontWeight.W_600,
                            color=COLORS["text_primary"]),
                    ft.Text(f"{nombre} · {f.fecha}", size=11,
                            color=COLORS["text_muted"]),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Text(fmt(f.total), size=13,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"]),
                    badge("Pagado" if f.estado == "pagado" else "Pendiente",
                          "success" if f.estado == "pagado" else "warning"),
                ], spacing=4,
                   horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=12),
            padding=ft.Padding.symmetric(vertical=10),
        )

    facturas_list = card(
        ft.Column([
            ft.Row([
                ft.Text("Últimas Facturas", size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"]),
                ft.TextButton("Ver todas →",
                              on_click=lambda e: navigate("facturas")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(
                controls=[factura_row(f) for f in ultimas] if ultimas else
                [ft.Text("No hay facturas aún", size=13,
                         color=COLORS["text_muted"])],
                spacing=0,
            ),
        ], spacing=0),
        expand=True,
    )

    content = ft.Column([
        section_header("Dashboard", f"Resumen general · {year}"),
        ft.Container(height=20),
        kpis,
        ft.Container(height=20),
        ft.Row([grafico, gastos_chart, fiscal], spacing=16,
               vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=20),
        facturas_list,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)