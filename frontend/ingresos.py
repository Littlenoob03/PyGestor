import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import fmt
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary, btn_danger,
    badge, section_header, snack, page_wrapper
)

def IngresosView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year
    filtro_estado = {"val": "all"}

    list_col = ft.Column(spacing=0)

    def refresh(page):
        render_list()
        page.update()

    #TABLA DE INGRESOS
    def render_list():
        ings = [i for i in db.ingresos_by_year(year)
                 if filtro_estado["val"] == "all" or i.estado == filtro_estado["val"]]
        ings.sort(key=lambda x: x.fecha, reverse=True)

        list_col.controls.clear()

        def th(t):
            return ft.Container(
                content=ft.Text(t, size=11, weight=ft.FontWeight.W_600,
                                color=COLORS["text_muted"])
            )

        list_col.controls.append(ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(content=th("ORIGEN"), col={"xs": 12, "md": 3}),
                ft.Container(content=th("CONCEPTO"), col={"xs": 12, "md": 4}),
                ft.Container(content=th("FECHA"), col={"xs": 6, "md": 2}),
                ft.Container(content=th("IMPORTE"), col={"xs": 6, "md": 2}),
                ft.Container(content=th("ESTADO"), col={"xs": 6, "md": 1}),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
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
                        navigate("form_ingreso", edit_id=iid)

                    def on_toggle(e, iid=iid):
                        ing = db.get_ingreso(iid)
                        new_estado = "cobrado" if ing.estado == "pendiente" else "pendiente"
                        db.update_ingreso(iid, estado=new_estado)
                        snack(e.page, f"Marcado como {new_estado}")
                        refresh(e.page)

                    def on_delete(e, iid=iid):
                        dlg = ft.AlertDialog(
                            title=ft.Text("¿Eliminar ingreso?"),
                            content=ft.Text("Esta acción no se puede deshacer.")
                        )
                        
                        def confirm(ev):
                            db.delete_ingreso(iid)
                            dlg.open = False
                            ev.page.update()  
                            snack(ev.page, "Ingreso eliminado")
                            render_list()     
                            ev.page.update()  
                            
                        def cancel(ev):
                            dlg.open = False
                            ev.page.update()
                            
                        dlg.actions = [
                            ft.TextButton("Cancelar", on_click=cancel),
                            ft.TextButton("Eliminar", on_click=confirm, style=ft.ButtonStyle(color="red")),
                        ]
                        
                        e.page.overlay.append(dlg)
                        dlg.open = True
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

                def cell(t, bold=False, color=None):
                    return ft.Container(
                        content=ft.Text(str(t), size=13,
                                        weight=ft.FontWeight.W_600 if bold else ft.FontWeight.NORMAL,
                                        color=color or COLORS["text_primary"])
                    )

                row = ft.Container(
                    content=ft.ResponsiveRow([
                        ft.Container(content=cell(i.origen, bold=True, color=COLORS["primary"]), col={"xs": 12, "md": 3}),
                        ft.Container(content=cell(i.concepto), col={"xs": 12, "md": 4}),
                        ft.Container(content=cell(i.fecha, color=COLORS["text_secondary"]), col={"xs": 6, "md": 2}),
                        ft.Container(content=cell(fmt(i.importe), bold=True), col={"xs": 6, "md": 2}),
                        ft.Container(
                            content=ft.Row([
                                badge("Cobrado" if i.estado == "cobrado" else "Pendiente",
                                      "success" if i.estado == "cobrado" else "warning"),
                                make_actions(i.id)
                            ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            col={"xs": 6, "md": 1}
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=bg,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                )
                list_col.controls.append(row)

    render_list()

    #FILTROS DE BUSQUEDA
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
        navigate("form_ingreso")

    content = ft.Column([
        ft.Row([
            section_header("Ingresos", "Gestiona tus fuentes de ingresos"),
            btn_primary("Nuevo Ingreso", on_click=nuevo_ingreso, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        tabs,
        ft.Container(height=8),
        card(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    return page_wrapper(content)