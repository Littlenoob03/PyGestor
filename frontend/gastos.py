import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import fmt, gastos_por_categoria
from frontend.styles import (
    COLORS, CAT_LABELS, card, btn_primary, btn_secondary, btn_danger,
    section_header, snack, page_wrapper
)

def GastosView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year

    list_col = ft.Column(spacing=0)

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
                th("DESCRIPCIÓN", 220), th("CATEGORÍA", 140), th("FECHA", 100),
                th("IMPORTE", 100), th("", 80),
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
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para editar.", ok=False)
                            return
                        navigate("form_gasto", edit_id=gid)

                    def on_delete(e, gid=gid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para borrar.", ok=False)
                            return
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
                        cell(g.descripcion, 220),
                        ft.Container(
                            content=ft.Text(f"{ico} {lbl}", size=12),
                            bgcolor="#EFF6FF", border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            width=140,
                        ),
                        cell(g.fecha, 100, color=COLORS["text_secondary"]),
                        cell(fmt(g.importe), 100, bold=True),
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
        if getattr(e.page, "is_guest", False):
            snack(e.page, "Modo Invitado: Inicia sesión para añadir datos.", ok=False)
            return
        navigate("form_gasto")

    content = ft.Column([
        ft.Row([
            section_header("Gastos", "Controla tus gastos personales"),
            btn_primary("Nuevo Gasto", on_click=nuevo_gasto, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        cat_cards,
        ft.Container(height=16),
        card(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)