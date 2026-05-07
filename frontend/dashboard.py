import flet as ft
from backend.database import Database
from backend.logic import (
    fmt, calcular_resumen, ingresos_por_mes, gastos_por_mes
)
from frontend.styles import (
    COLORS, MESES, card, stat_card, section_header,
    divider, badge, page_wrapper
)

def DashboardView(db: Database, navigate) -> ft.Container:
    year = 2025
    facturas = db.facturas_by_year(year)
    gastos   = db.gastos_by_year(year)
    res      = calcular_resumen(facturas, gastos)

    # ── KPI Cards ──────────────────────────────────────────
    kpis = ft.Row([
        stat_card("Ingresos Totales",  fmt(res["total_ingresos"]), "Base imponible",      COLORS["stat1"], "💰"),
        stat_card("Gastos Totales",    fmt(res["total_gastos"]),   "Deducibles",           COLORS["stat2"], "📉"),
        stat_card("Beneficio Neto",    fmt(res["beneficio"]),      "Ingresos – Gastos",    COLORS["stat3"], "📈"),
        stat_card("IVA a Declarar",    fmt(res["iva_neto"]),       "Repercutido – Soportado", COLORS["stat4"], "🧾"),
    ], spacing=16)

    # ── Gráfico de barras mensual (ASCII/text simulado) ─────
    ing_mes  = ingresos_por_mes(facturas)
    gast_mes = gastos_por_mes(gastos)
    max_val  = max(max(ing_mes), max(gast_mes), 1)

    def bar_row(mes, ing, gas):
        def bar(val, color, width_total=120):
            w = int(val / max_val * width_total)
            return ft.Container(width=max(w, 2), height=12, bgcolor=color, border_radius=3)
        return ft.Column([
            ft.Text(mes, size=10, color=COLORS["text_muted"]),
            ft.Row([bar(ing, COLORS["stat1"]), ft.Text(fmt(ing), size=9, color=COLORS["text_secondary"])], spacing=4),
            ft.Row([bar(gas, COLORS["danger"]), ft.Text(fmt(gas), size=9, color=COLORS["text_secondary"])], spacing=4),
        ], spacing=2)

    chart_rows = ft.Column(
        [bar_row(MESES[i], ing_mes[i], gast_mes[i]) for i in range(12)],
        spacing=8, scroll=ft.ScrollMode.AUTO
    )

    grafico = card(
        ft.Column([
            ft.Row([
                ft.Text("Evolución Mensual", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=COLORS["stat1"], border_radius=3),
                    ft.Text("Ingresos", size=11, color=COLORS["text_secondary"]),
                    ft.Container(width=10, height=10, bgcolor=COLORS["danger"], border_radius=3),
                    ft.Text("Gastos", size=11, color=COLORS["text_secondary"]),
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            chart_rows,
        ], spacing=0),
        expand=True,
    )

    # ── Resumen Fiscal ─────────────────────────────────────
    def fiscal_row(label, value, color=COLORS["text_primary"]):
        return ft.Row([
            ft.Text(label, size=13, color=COLORS["text_secondary"], expand=True),
            ft.Text(value, size=13, weight=ft.FontWeight.BOLD, color=color),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    fiscal = card(
        ft.Column([
            ft.Text("Resumen Fiscal", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            fiscal_row("IVA Repercutido",    fmt(res["iva_repercutido"]),  COLORS["danger"]),
            divider(),
            fiscal_row("IVA Soportado",      fmt(res["iva_soportado"]),   COLORS["success"]),
            divider(),
            fiscal_row("IVA a Liquidar",     fmt(res["iva_neto"]),        COLORS["primary"]),
            divider(),
            fiscal_row("IRPF Retenido",      fmt(res["irpf_retenido"]),   COLORS["text_primary"]),
            divider(),
            fiscal_row("IRPF Est. (20%)",    fmt(res["irpf_estimado"]),   COLORS["stat3"]),
            divider(),
            fiscal_row("Facturas Pendientes",str(res["pendientes"]),       COLORS["warning_text"]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Text("Cuota SS estimada: 294 €/mes", size=12,
                                color=COLORS["danger"], weight=ft.FontWeight.W_500),
                bgcolor=COLORS["danger_bg"], border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            ),
        ], spacing=8),
        width=280,
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
                    content=ft.Text(initials, size=12, weight=ft.FontWeight.BOLD, color="white"),
                    width=36, height=36, border_radius=10,
                    bgcolor=COLORS["primary"],
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(f.numero, size=13, weight=ft.FontWeight.W_600, color=COLORS["text_primary"]),
                    ft.Text(f"{nombre} · {f.fecha}", size=11, color=COLORS["text_muted"]),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Text(fmt(f.total), size=13, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                    badge("Pagado" if f.estado=="pagado" else "Pendiente",
                          "success" if f.estado=="pagado" else "warning"),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=12, alignment=ft.MainAxisAlignment.START),
            padding=ft.Padding.symmetric(vertical=10),
        )

    facturas_list = card(
        ft.Column([
            ft.Row([
                ft.Text("Últimas Facturas", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                ft.TextButton("Ver todas →", on_click=lambda e: navigate("facturas")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(controls=[factura_row(f) for f in ultimas] if ultimas else
                      [ft.Text("No hay facturas aún", size=13, color=COLORS["text_muted"])],
                      spacing=0),
        ], spacing=0),
        expand=True,
    )

    content = ft.Column([
        section_header("Dashboard", "Resumen general de tu actividad"),
        ft.Container(height=20),
        kpis,
        ft.Container(height=20),
        ft.Row([grafico, fiscal], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=20),
        facturas_list,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)