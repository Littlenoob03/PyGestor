import flet as ft
from backend.database import Database
from backend.logic import fmt
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary, btn_danger,
    section_header, text_field, snack, page_wrapper
)

AVATAR_COLORS = ["#6366F1","#10B981","#F59E0B","#EF4444","#14B8A6","#A855F7","#3B82F6"]

def ClientesView(db: Database, navigate) -> ft.Container:
    editing_id = {"val": None}

    c_nombre = text_field("Nombre / Empresa", "Nombre del cliente")
    c_nif    = text_field("NIF / CIF", "B12345678")
    c_email  = text_field("Email", "cliente@empresa.com", keyboard_type=ft.KeyboardType.EMAIL)
    c_tel    = text_field("Teléfono", "+34 600 000 000", keyboard_type=ft.KeyboardType.PHONE)
    c_dir    = text_field("Dirección", "Calle, número, ciudad")

    grid = ft.Row(wrap=True, spacing=16, run_spacing=16)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Cliente", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=440,
            content=ft.Column([
                ft.Row([c_nombre, c_nif], spacing=12),
                c_email,
                ft.Row([c_tel, c_dir], spacing=12),
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
                nombre=c_nombre.value,
                nif=c_nif.value,
                email=c_email.value,
                telefono=c_tel.value,
                direccion=c_dir.value,
            )
            if editing_id["val"]:
                db.update_cliente(editing_id["val"], **data)
                snack(page, "Cliente actualizado ✅")
            else:
                db.add_cliente(**data)
                snack(page, "Cliente añadido ✅")
            dlg.open = False
            editing_id["val"] = None
            render_grid()
            page.update()
        except Exception as ex:
            snack(page, f"Error: {ex}", ok=False)

    dlg.actions = [
        btn_secondary("Cancelar", on_click=close_dlg),
        btn_primary("Guardar", on_click=guardar),
    ]

    def render_grid():
        grid.controls.clear()
        if not db.clientes:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("👥", size=40),
                        ft.Text("No hay clientes", size=15, color=COLORS["text_muted"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment.CENTER, height=200, expand=True,
                )
            )
            return

        for c in db.clientes:
            facts = [f for f in db.facturas if f.cliente_id == c.id]
            total = sum(f.base for f in facts)
            initials = "".join(w[0] for w in c.nombre.split()[:2]).upper()
            color = AVATAR_COLORS[c.id % len(AVATAR_COLORS)]

            def make_card(cid, initials=initials, color=color, c=c, facts=facts, total=total):
                def on_edit(e):
                    editing_id["val"] = cid
                    ca = db.get_cliente(cid)
                    c_nombre.value = ca.nombre
                    c_nif.value    = ca.nif
                    c_email.value  = ca.email
                    c_tel.value    = ca.telefono
                    c_dir.value    = ca.direccion
                    dlg.title = ft.Text("Editar Cliente", weight=ft.FontWeight.BOLD)
                    e.page.dialog = dlg
                    dlg.open = True
                    e.page.update()

                def on_delete(e):
                    def confirm(ev):
                        db.delete_cliente(cid)
                        ev.page.dialog.open = False
                        snack(ev.page, "Cliente eliminado")
                        render_grid()
                        ev.page.update()
                    def cancel(ev):
                        ev.page.dialog.open = False
                        ev.page.update()
                    e.page.dialog = ft.AlertDialog(
                        title=ft.Text("¿Eliminar cliente?"),
                        content=ft.Text("Las facturas del cliente se conservarán."),
                        actions=[
                            btn_secondary("Cancelar", on_click=cancel),
                            btn_danger("Eliminar", on_click=confirm),
                        ],
                        open=True,
                    )
                    e.page.update()

                return ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(initials, size=16, weight=ft.FontWeight.BOLD, color="white"),
                                width=48, height=48, border_radius=14,
                                bgcolor=color, alignment=ft.Alignment.CENTER,
                            ),
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=COLORS["primary"],
                                              tooltip="Editar", on_click=on_edit, icon_size=18),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=COLORS["danger"],
                                              tooltip="Eliminar", on_click=on_delete, icon_size=18),
                            ], spacing=0),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(c.nombre, size=15, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                        ft.Text(f"NIF: {c.nif}", size=12, color=COLORS["text_muted"]),
                        ft.Container(height=4),
                        *([ft.Text(f"✉️  {c.email}",    size=12, color=COLORS["text_secondary"])] if c.email    else []),
                        *([ft.Text(f"📞 {c.telefono}", size=12, color=COLORS["text_secondary"])] if c.telefono else []),
                        *([ft.Text(f"📍 {c.direccion}",size=12, color=COLORS["text_secondary"])] if c.direccion else []),
                        ft.Container(height=8),
                        ft.Divider(color=COLORS["border"], height=1),
                        ft.Row([
                            ft.Text(f"{len(facts)} factura{'s' if len(facts)!=1 else ''}",
                                    size=12, color=COLORS["text_muted"]),
                            ft.Text(fmt(total), size=14, weight=ft.FontWeight.BOLD,
                                    color=COLORS["text_primary"]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=6),
                    bgcolor="white",
                    border_radius=16,
                    padding=20,
                    border=ft.border.all(1, COLORS["border"]),
                    width=280,
                    shadow=ft.BoxShadow(
                        spread_radius=0, blur_radius=8,
                        color=ft.Colors.with_opacity(0.06, "black"),
                        offset=ft.Offset(0, 2),
                    ),
                )

            grid.controls.append(make_card(c.id))

    render_grid()

    def nuevo_cliente(e):
        editing_id["val"] = None
        c_nombre.value = ""
        c_nif.value    = ""
        c_email.value  = ""
        c_tel.value    = ""
        c_dir.value    = ""
        dlg.title = ft.Text("Nuevo Cliente", weight=ft.FontWeight.BOLD)
        e.page.dialog = dlg
        dlg.open = True
        e.page.update()

    content = ft.Column([
        ft.Row([
            section_header("Clientes", "Base de datos de clientes"),
            btn_primary("Nuevo Cliente", on_click=nuevo_cliente, icon=ft.Icons.PERSON_ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=20),
        grid,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)