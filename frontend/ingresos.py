import flet as ft
from datetime import date, datetime
from backend.database import Database
from backend.logic import fmt
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary, btn_danger,
    badge, section_header, text_field, dropdown, snack, page_wrapper, divider
)

def IngresosView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year
    filtro_estado = {"val": "all"}
    editing_id = {"val": None}

    # ── Formulario (Dialog) ────────────────────────────────
    f_origen   = text_field("Fuente / Origen", "Nómina, Bizum, etc.")
    f_concepto = text_field("Concepto",   "Descripción del ingreso")
    f_fecha    = text_field("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    f_importe  = text_field("Importe", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    f_estado   = dropdown("Estado", [("pendiente","Pendiente"),("cobrado","Cobrado")], value="cobrado")

    list_col = ft.Column(spacing=0)
    page_ref = ft.Ref[ft.Page]()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Ingreso", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=520,
            content=ft.Column([
                ft.Row([f_origen, f_fecha], spacing=12),
                f_concepto,
                ft.Row([f_importe, f_estado], spacing=12),
            ], spacing=12, tight=True),
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_dlg(page):
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(e):
        dlg.open = False
        editing_id["val"] = None
        e.page.update()

    def guardar(e):
        page = e.page
        try:
            data = dict(
                origen=f_origen.value,
                concepto=f_concepto.value,
                fecha=f_fecha.value,
                importe=float(f_importe.value or 0),
                estado=f_estado.value,
            )
            if editing_id["val"]:
                db.update_ingreso(editing_id["val"], **data)
                snack(page, "Ingreso actualizado ✅")
            else:
                db.add_ingreso(**data)
                snack(page, "Ingreso creado ✅")
            dlg.open = False
            editing_id["val"] = None
            refresh(page)
        except Exception as ex:
            snack(page, f"Error: {ex}", ok=False)

    dlg.actions = [
        btn_secondary("Cancelar", on_click=close_dlg),
        btn_primary("Guardar", on_click=guardar),
    ]

    def refresh(page):
        render_list()
        page.update()

    # ── Tabla ──────────────────────────────────────────────
    def render_list():
        ings = [i for i in db.ingresos_by_year(year)
                 if filtro_estado["val"] == "all" or i.estado == filtro_estado["val"]]
        ings.sort(key=lambda x: x.fecha, reverse=True)

        list_col.controls.clear()

        # Cabecera
        def th(t, w=None):
            return ft.Container(
                content=ft.Text(t, size=11, weight=ft.FontWeight.W_600,
                                color=COLORS["text_muted"]),
                width=w,
            )

        list_col.controls.append(ft.Container(
            content=ft.Row([
                th("ORIGEN", 160), th("CONCEPTO", 200), th("FECHA", 100),
                th("IMPORTE", 100), th("ESTADO", 90), th("", 100),
            ], spacing=8),
            bgcolor="#F7F8FA", padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        ))

        if not ings:
            list_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("💰", size=40),
                    ft.Text("No hay ingresos", size=15, color=COLORS["text_muted"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment.CENTER,
                height=200,
            ))
        else:
            for idx, i in enumerate(ings):
                bg = "white" if idx % 2 == 0 else "#FAFAFA"

                def make_actions(iid):
                    def on_edit(e, iid=iid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para editar.", ok=False)
                            return
                        ing = db.get_ingreso(iid)
                        editing_id["val"] = iid
                        f_origen.value   = ing.origen
                        f_concepto.value = ing.concepto
                        f_fecha.value    = ing.fecha
                        f_importe.value  = str(ing.importe)
                        f_estado.value   = ing.estado
                        dlg.title        = ft.Text("Editar Ingreso", weight=ft.FontWeight.BOLD)
                        open_dlg(e.page)

                    def on_toggle(e, iid=iid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para modificar.", ok=False)
                            return
                        ing = db.get_ingreso(iid)
                        new_estado = "cobrado" if ing.estado == "pendiente" else "pendiente"
                        db.update_ingreso(iid, estado=new_estado)
                        snack(e.page, f"Marcado como {new_estado}")
                        refresh(e.page)

                    def on_delete(e, iid=iid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para borrar.", ok=False)
                            return
                        def confirm(ev):
                            db.delete_ingreso(iid)
                            ev.page.dialog.open = False
                            snack(ev.page, "Ingreso eliminado")
                            refresh(ev.page)
                        def cancel(ev):
                            ev.page.dialog.open = False
                            ev.page.update()
                        e.page.dialog = ft.AlertDialog(
                            title=ft.Text("¿Eliminar ingreso?"),
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
                        ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color=COLORS["success"],
                                      tooltip="Cambiar estado", on_click=on_toggle,
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
                        cell(i.origen, 160, bold=True, color=COLORS["primary"]),
                        cell(i.concepto, 200),
                        cell(i.fecha, 100, color=COLORS["text_secondary"]),
                        cell(fmt(i.importe), 100, bold=True),
                        ft.Container(
                            content=badge("Cobrado" if i.estado=="cobrado" else "Pendiente",
                                          "success" if i.estado=="cobrado" else "warning"),
                            width=90,
                        ),
                        make_actions(i.id),
                    ], spacing=8),
                    bgcolor=bg,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                )
                list_col.controls.append(row)

    render_list()

    # ── Filtros ────────────────────────────────────────────
    def make_tab(label, val):
        def on_click(e):
            filtro_estado["val"] = val
            render_list()
            e.page.update()
        return ft.TextButton(label, on_click=on_click,
                             style=ft.ButtonStyle(
                                 color=COLORS["primary"] if filtro_estado["val"]==val else COLORS["text_secondary"]
                             ))

    tabs = ft.Row([
        make_tab("Todos", "all"),
        make_tab("Cobrados", "cobrado"),
        make_tab("Pendientes", "pendiente"),
    ])

    def nuevo_ingreso(e):
        if getattr(e.page, "is_guest", False):
            snack(e.page, "Modo Invitado: Inicia sesión para añadir datos.", ok=False)
            return
        editing_id["val"] = None
        f_origen.value   = ""
        f_concepto.value = ""
        f_fecha.value    = str(date.today())
        f_importe.value  = ""
        f_estado.value   = "cobrado"
        dlg.title = ft.Text("Nuevo Ingreso", weight=ft.FontWeight.BOLD)
        open_dlg(e.page)

    content = ft.Column([
        ft.Row([
            section_header("Ingresos", "Gestiona todas tus fuentes de ingresos"),
            btn_primary("Nuevo Ingreso", on_click=nuevo_ingreso, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        tabs,
        ft.Container(height=8),
        card(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)