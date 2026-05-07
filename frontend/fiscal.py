import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import fmt, calcular_trimestre, calcular_cuota_autonomos
from frontend.styles import COLORS, card, section_header, page_wrapper, divider

T_NAMES    = ["T1 (Ene–Mar)", "T2 (Abr–Jun)", "T3 (Jul–Sep)", "T4 (Oct–Dic)"]
T_DEADLINE = ["20 Abril", "20 Julio", "20 Octubre", "30 Enero"]

def FiscalView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year
    facturas = db.facturas_by_year(year)
    gastos   = db.gastos_by_year(year)

    def row(label, value, color=None):
        return ft.Row([
            ft.Text(label, size=13, color=COLORS["text_secondary"], expand=True),
            ft.Text(value, size=13, weight=ft.FontWeight.BOLD,
                    color=color or COLORS["text_primary"]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # ── IVA Trimestral (Modelo 303) ────────────────────────
    def iva_card(t: int):
        d = calcular_trimestre(facturas, gastos, t)
        color = COLORS["danger"] if d["iva_neto"] > 0 else COLORS["success"]
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(T_NAMES[t-1], size=14, weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"]),
                    ft.Container(
                        content=ft.Text(f"Plazo: {T_DEADLINE[t-1]}", size=11,
                                        color=COLORS["text_muted"]),
                        bgcolor="#F1F5F9", border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                row("IVA Repercutido",  fmt(d["iva_rep"])),
                divider(),
                row("IVA Soportado",    fmt(d["iva_sop"])),
                divider(),
                row("A ingresar / Comp.", fmt(d["iva_neto"]), color),
            ], spacing=8),
            bgcolor="white",
            border_radius=14,
            padding=16,
            border=ft.border.all(1, COLORS["border"]),
        )

    iva_panel = card(
        ft.Column([
            ft.Text("Modelo 303 – IVA Trimestral", size=17,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            ft.Column([iva_card(t) for t in [1,2,3,4]], spacing=12),
        ], spacing=0),
        expand=True,
    )

    # ── IRPF Pagos Fraccionados (Modelo 130) ──────────────
    def irpf_card(t: int, acum: list):
        d = calcular_trimestre(facturas, gastos, t)
        pago = max(d["beneficio"] * 0.20 - d["irpf_retenido"] - acum[0], 0)
        if pago > 0:
            acum[0] += pago
        color = COLORS["danger"] if pago > 0 else COLORS["success"]
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(T_NAMES[t-1], size=14, weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"]),
                    ft.Container(
                        content=ft.Text(f"Plazo: {T_DEADLINE[t-1]}", size=11,
                                        color=COLORS["text_muted"]),
                        bgcolor="#F1F5F9", border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                row("Beneficio acumulado", fmt(d["beneficio"])),
                divider(),
                row("Retenciones practicadas", fmt(d["irpf_retenido"])),
                divider(),
                row("A pagar (20% s/ beneficio)", fmt(pago), color),
            ], spacing=8),
            bgcolor="white", border_radius=14, padding=16,
            border=ft.border.all(1, COLORS["border"]),
        )

    acum = [0.0]
    irpf_panel = card(
        ft.Column([
            ft.Text("Modelo 130 – IRPF Fraccionado", size=17,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            ft.Column([irpf_card(t, acum) for t in [1,2,3,4]], spacing=12),
            ft.Container(height=12),
            ft.Container(
                content=ft.Text(
                    "ℹ️  El modelo 130 corresponde al 20% del beneficio "
                    "(ingresos – gastos deducibles) menos las retenciones ya aplicadas.",
                    size=12, color="#1E40AF",
                ),
                bgcolor="#EFF6FF", border_radius=10,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            ),
        ], spacing=0),
        expand=True,
    )

    # ── Cuota Autónomos ────────────────────────────────────
    total_base   = sum(f.base for f in facturas)
    total_gastos = sum(g.base for g in gastos if g.deducible)
    rn_anual     = (total_base - total_gastos) * (1 - 0.07)
    rn_mensual   = rn_anual / 12
    tramo_desc, cuota_mes = calcular_cuota_autonomos(rn_mensual)

    cuota_panel = card(
        ft.Column([
            ft.Text("Cuota de Autónomos – Cotización por Ingresos Reales 2025",
                    size=17, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=16),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Rendimiento Neto Est.", size=12, color=COLORS["text_muted"]),
                        ft.Text(fmt(rn_mensual) + "/mes", size=18,
                                weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                    ], spacing=4),
                    bgcolor="#F8FAFC", border_radius=12, padding=16, expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Tramo de Cotización", size=12, color=COLORS["text_muted"]),
                        ft.Text(tramo_desc, size=14,
                                weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                    ], spacing=4),
                    bgcolor="#F8FAFC", border_radius=12, padding=16, expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Cuota Mensual", size=12, color=COLORS["text_muted"]),
                        ft.Text(fmt(cuota_mes), size=22,
                                weight=ft.FontWeight.BOLD, color=COLORS["danger"]),
                    ], spacing=4),
                    bgcolor="#FFF5F5", border_radius=12, padding=16, expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Cuota Anual Est.", size=12, color=COLORS["text_muted"]),
                        ft.Text(fmt(cuota_mes * 12), size=22,
                                weight=ft.FontWeight.BOLD, color=COLORS["danger"]),
                    ], spacing=4),
                    bgcolor="#FFF5F5", border_radius=12, padding=16, expand=True,
                ),
            ], spacing=12),
        ], spacing=0),
    )

    content = ft.Column([
        section_header("Fiscal / IVA", "Resumen para tus declaraciones trimestrales"),
        ft.Container(height=20),
        ft.Row([iva_panel, irpf_panel], spacing=20,
               vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Container(height=20),
        cuota_panel,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)