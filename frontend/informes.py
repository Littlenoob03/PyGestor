import flet as ft
from backend.database import Database
from backend.logic import (
    fmt, ingresos_por_mes, gastos_por_mes,
    ingresos_por_cliente, gastos_por_categoria, calcular_trimestre
)
from frontend.styles import COLORS, CAT_LABELS, MESES, card, section_header, page_wrapper

def InformesView(db: Database, navigate) -> ft.Container:
    year = 2025
    facturas = db.facturas_by_year(year)
    gastos   = db.gastos_by_year(year)

    # ── Ingresos por cliente (barras horizontales) ─────────
    por_cliente = ingresos_por_cliente(facturas, db.clientes)
    max_cl = max(por_cliente.values(), default=1)

    def cliente_bar(nombre, valor):
        pct = valor / max_cl
        return ft.Column([
            ft.Row([
                ft.Text(nombre, size=12, color=COLORS["text_primary"],
                        expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(fmt(valor), size=12, weight=ft.FontWeight.BOLD,
                        color=COLORS["text_primary"]),
            ]),
            ft.Stack([
                ft.Container(height=8, border_radius=4, bgcolor="#EDE9FE", expand=True),
                ft.Container(height=8, border_radius=4, bgcolor=COLORS["stat1"],
                             width=max(int(pct * 340), 4)),
            ]),
        ], spacing=4)

    clientes_chart = card(
        ft.Column([
            ft.Text("Ingresos por Cliente", size=16,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            # Corrección aquí: Usamos una lista generada condicionalmente
            *( (cliente_bar(n, v) for n, v in sorted(por_cliente.items(), key=lambda x: -x[1])) 
               if por_cliente else [ft.Text("Sin datos", color=COLORS["text_muted"])] )
        ], spacing=10),
        expand=True,
    )

    # ── Gastos por categoría ───────────────────────────────
    por_cat = gastos_por_categoria(gastos)
    max_cat = max(por_cat.values(), default=1)
    cat_colors = ["#6366F1","#10B981","#F59E0B","#EF4444","#14B8A6","#A855F7","#3B82F6"]

    def cat_bar(k, v, idx):
        ico, lbl = CAT_LABELS.get(k, ("📦","Otros"))
        pct = v / max_cat
        return ft.Column([
            ft.Row([
                ft.Text(f"{ico} {lbl}", size=12, color=COLORS["text_primary"], expand=True),
                ft.Text(fmt(v), size=12, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ]),
            ft.Stack([
                ft.Container(height=8, border_radius=4, bgcolor="#F1F5F9", expand=True),
                ft.Container(height=8, border_radius=4, bgcolor=cat_colors[idx % len(cat_colors)],
                             width=max(int(pct * 340), 4)),
            ]),
        ], spacing=4)

    gastos_chart = card(
        ft.Column([
            ft.Text("Gastos por Categoría", size=16,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            # Corrección aquí: Usamos una lista generada condicionalmente
            *( (cat_bar(k, v, i) for i, (k, v) in enumerate(sorted(por_cat.items(), key=lambda x: -x[1]))) 
               if por_cat else [ft.Text("Sin datos", color=COLORS["text_muted"])] )
        ], spacing=10),
        expand=True,
    )

    # ── Comparativa trimestral ─────────────────────────────
    trimestres = []
    for t in [1, 2, 3, 4]:
        d = calcular_trimestre(facturas, gastos, t)
        trimestres.append(d)

    max_t = max((max(d["base_ingresos"], d["base_gastos"]) for d in trimestres), default=1)

    T_NAMES = ["T1", "T2", "T3", "T4"]

    def t_col(d, i):
        h_total = 140
        hi = int(d["base_ingresos"] / max_t * h_total)
        hg = int(d["base_gastos"]   / max_t * h_total)
        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Container(height=h_total - hi),
                    ft.Container(width=32, height=max(hi, 4), bgcolor=COLORS["stat1"], border_radius=ft.BorderRadius.only(top_left=4, top_right=4)),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Container(height=h_total - hg),
                    ft.Container(width=32, height=max(hg, 4), bgcolor=COLORS["danger"], border_radius=ft.BorderRadius.only(top_left=4, top_right=4)),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(T_NAMES[i], size=12, color=COLORS["text_secondary"],
                    text_align=ft.TextAlign.CENTER),
            ft.Text(fmt(d["beneficio"]), size=11, weight=ft.FontWeight.BOLD,
                    color=COLORS["success"] if d["beneficio"] >= 0 else COLORS["danger"],
                    text_align=ft.TextAlign.CENTER),
        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    trimestral_chart = card(
        ft.Column([
            ft.Row([
                ft.Text("Comparativa Trimestral", size=16,
                        weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=COLORS["stat1"], border_radius=3),
                    ft.Text("Ingresos", size=11, color=COLORS["text_secondary"]),
                    ft.Container(width=12, height=12, bgcolor=COLORS["danger"], border_radius=3),
                    ft.Text("Gastos", size=11, color=COLORS["text_secondary"]),
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=16),
            ft.Row(
                [t_col(d, i) for i, d in enumerate(trimestres)],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        ], spacing=0),
    )

    # ── Tabla de resumen anual ─────────────────────────────
    total_ingresos = sum(f.base for f in facturas)
    total_gastos_v = sum(g.base for g in gastos if g.deducible)
    beneficio_neto = total_ingresos - total_gastos_v
    tasa_beneficio = (beneficio_neto / total_ingresos * 100) if total_ingresos else 0

    resumen_anual = card(
        ft.Column([
            ft.Text(f"Resumen Anual {year}", size=16,
                    weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Container(height=12),
            ft.Row([
                _kpi_mini("Total Facturado",  fmt(total_ingresos), COLORS["stat1"]),
                _kpi_mini("Total Gastos",     fmt(total_gastos_v), COLORS["danger"]),
                _kpi_mini("Beneficio Neto",   fmt(beneficio_neto), COLORS["success"]),
                _kpi_mini("Margen",           f"{tasa_beneficio:.1f} %", COLORS["stat4"]),
                _kpi_mini("Nº Facturas",      str(len(facturas)),   COLORS["stat1"]),
                _kpi_mini("Nº Gastos",        str(len(gastos)),     COLORS["stat3"]),
            ], spacing=12),
        ], spacing=0),
    )

    content = ft.Column([
        section_header("Informes", "Análisis y estadísticas de tu actividad"),
        ft.Container(height=20),
        resumen_anual,
        ft.Container(height=16),
        ft.Row([clientes_chart, gastos_chart], spacing=20,
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
        bgcolor="#F8FAFC", border_radius=12, padding=16, expand=True,
        alignment=ft.Alignment.CENTER,
    )