import flet as ft
from datetime import date, datetime
from backend.database import Database
from backend.logic import fmt, gastos_por_categoria
from frontend.styles import (
    COLORS, CAT_LABELS, card, btn_primary, btn_secondary, btn_danger,
    badge, section_header, text_field, dropdown, snack, page_wrapper
)

def GastosView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year
    editing_id = {"val": None}

    g_desc  = text_field("Descripción", "Descripción del gasto")
    g_fecha = text_field("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    g_base  = text_field("Base Imponible", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    g_iva   = dropdown("IVA %", [("21","21 %"),("10","10 %"),("4","4 %"),("0","0 %")], value="21")
    g_cat   = dropdown("Categoría", [
        ("oficina","🖊️ Oficina"), ("software","💻 Software"),
        ("marketing","📢 Marketing"), ("transporte","🚗 Transporte"),
        ("formacion","📚 Formación"), ("seguro","🛡️ Seguro"), ("otros","📦 Otros"),
    ], value="software")
    g_deducible = ft.Checkbox(label="Deducible fiscalmente", value=True)
    total_text = ft.Text("", size=13, color=COLORS["text_secondary"])

    def recalc(e=None):
        try:
            base = float(g_base.value or 0)
            iva  = base * float(g_iva.value or 0) / 100
            total_text.value = f"Total a pagar: {fmt(base + iva)}"
            total_text.update()
        except Exception:
            pass

    g_base.on_change = recalc
    g_iva.on_change  = recalc

    list_col = ft.Column(spacing=0)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Gasto", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=480,
            content=ft.Column([
                ft.Row([g_desc, g_fecha], spacing=12),
                ft.Row([g_base, g_iva, g_cat], spacing=12),
                g_deducible,
                ft.Container(
                    content=total_text,
                    bgcolor="#F0FDF4", border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                ),
            ], spacing=12, tight=True),
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dlg(e):
        dlg.open = False
        editing_id["val"] = None
        e.page.update()

    def guardar(e):
        page = e.page
        try:
            data = dict(
                descripcion=g_desc.value,
                categoria=g_cat.value,
                fecha=g_fecha.value,
                base=float(g_base.value or 0),
                iva_pct=float(g_iva.value or 21),
                deducible=g_deducible.value,
            )
            if editing_id["val"]:
                db.update_gasto(editing_id["val"], **data)
                snack(page, "Gasto actualizado ✅")
            else:
                db.add_gasto(**data)
                snack(page, "Gasto registrado ✅")
            dlg.open = False
            editing_id["val"] = None
            render_list()
            page.update()
        except Exception as ex:
            snack(page, f"Error: {ex}", ok=False)

    dlg.actions = [
        btn_secondary("Cancelar", on_click=close_dlg),
        btn_primary("Guardar", on_click=guardar),
    ]

    def render_list():
        gasts = sorted(db.gastos_by_year(year), key=lambda g: g.fecha, reverse=True)
        list_col.controls.clear()

        # Cabecera
        def th(t, w=None):
            return ft.Container(
                content=ft.Text(t, size=11, weight=ft.FontWeight.W_600, color=COLORS["text_muted"]),
                width=w,
            )

        list_col.controls.append(ft.Container(
            content=ft.Row([
                th("DESCRIPCIÓN", 180), th("CATEGORÍA", 120), th("FECHA", 100),
                th("BASE", 90), th("IVA", 80), th("TOTAL", 90),
                th("DEDUCIBLE", 90), th("", 80),
            ], spacing=8),
            bgcolor="#F7F8FA",
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        ))

        if not gasts:
            list_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("💸", size=40),
                    ft.Text("No hay gastos registrados", size=15, color=COLORS["text_muted"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment.CENTER, height=200,
            ))
        else:
            for idx, g in enumerate(gasts):
                bg = "white" if idx % 2 == 0 else "#FAFAFA"
                ico, lbl = CAT_LABELS.get(g.categoria, ("📦","Otros"))

                def make_actions(gid):
                    def on_edit(e, gid=gid):
                        ga = db.get_gasto(gid)
                        editing_id["val"] = gid
                        g_desc.value      = ga.descripcion
                        g_cat.value       = ga.categoria
                        g_fecha.value     = ga.fecha
                        g_base.value      = str(ga.base)
                        g_iva.value       = str(int(ga.iva_pct))
                        g_deducible.value = ga.deducible
                        dlg.title = ft.Text("Editar Gasto", weight=ft.FontWeight.BOLD)
                        recalc()
                        e.page.dialog = dlg
                        dlg.open = True
                        e.page.update()

                    def on_delete(e, gid=gid):
                        def confirm(ev):
                            db.delete_gasto(gid)
                            ev.page.dialog.open = False
                            snack(ev.page, "Gasto eliminado")
                            render_list()
                            ev.page.update()
                        def cancel(ev):
                            ev.page.dialog.open = False
                            ev.page.update()
                        e.page.dialog = ft.AlertDialog(
                            title=ft.Text("¿Eliminar gasto?"),
                            content=ft.Text("Esta acción no se puede deshacer."),
                            actions=[
                                btn_secondary("Cancelar", on_click=cancel),
                                btn_danger("Eliminar", on_click=confirm),
                            ],
                            open=True,
                        )
                        e.page.update()

                    return ft.Row([
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=COLORS["primary"],
                                      tooltip="Editar", on_click=on_edit,
                                      icon_size=18, width=32, height=32),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=COLORS["danger"],
                                      tooltip="Eliminar", on_click=on_delete,
                                      icon_size=18, width=32, height=32),
                    ], spacing=0)

                def cell(t, w=None, bold=False, color=None):
                    return ft.Container(
                        content=ft.Text(str(t), size=13,
                                        weight=ft.FontWeight.W_600 if bold else ft.FontWeight.NORMAL,
                                        color=color or COLORS["text_primary"]),
                        width=w,
                    )

                row = ft.Container(
                    content=ft.Row([
                        cell(g.descripcion, 180),
                        ft.Container(
                            content=ft.Text(f"{ico} {lbl}", size=12),
                            bgcolor="#EFF6FF", border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            width=120,
                        ),
                        cell(g.fecha, 100, color=COLORS["text_secondary"]),
                        cell(fmt(g.base),  90),
                        cell(fmt(g.iva),   80),
                        cell(fmt(g.total), 90, bold=True),
                        ft.Container(
                            content=badge("✓ Sí" if g.deducible else "✗ No",
                                          "success" if g.deducible else "danger"),
                            width=90,
                        ),
                        make_actions(g.id),
                    ], spacing=8),
                    bgcolor=bg,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                )
                list_col.controls.append(row)

    render_list()

    # ── Tarjetas resumen por categoría ─────────────────────
    por_cat = gastos_por_categoria(db.gastos_by_year(year))
    cat_cards = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text(CAT_LABELS.get(k, ("📦","Otros"))[0], size=22),
                    ft.Text(CAT_LABELS.get(k, ("📦","Otros"))[1], size=11,
                            color=COLORS["text_secondary"]),
                    ft.Text(fmt(v), size=15, weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"]),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="white",
                border_radius=14,
                padding=16,
                border=ft.border.all(1, COLORS["border"]),
                width=130,
                alignment=ft.Alignment.CENTER,
            )
            for k, v in por_cat.items()
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    def nuevo_gasto(e):
        editing_id["val"] = None
        g_desc.value  = ""
        g_fecha.value = str(date.today())
        g_base.value  = ""
        g_iva.value   = "21"
        g_cat.value   = "software"
        g_deducible.value = True
        total_text.value  = ""
        dlg.title = ft.Text("Nuevo Gasto", weight=ft.FontWeight.BOLD)
        e.page.dialog = dlg
        dlg.open = True
        e.page.update()

    content = ft.Column([
        ft.Row([
            section_header("Gastos", "Controla tus gastos deducibles"),
            btn_primary("Nuevo Gasto", on_click=nuevo_gasto, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        cat_cards,
        ft.Container(height=16),
        card(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)