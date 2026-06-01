import flet as ft
from datetime import datetime
from backend.database import Database
from backend.logic import formatear_moneda, gastos_por_categoria
from frontend.styles import (
    COLORS, CAT_LABELS, tarjeta, btn_primario, btn_secundario, btn_aviso,
    cabecera, notificacion, vista_adaptable
)

def VistaGastos(db: Database, navegar) -> ft.Container:
    """Crea toda la pantalla de Gastos, donde vemos la lista de lo que hemos gastado y el resumen de arriba."""
    year = datetime.now().year

    list_col = ft.Column(spacing=0)

    def dibujar_lista():
        """Dibuja la lista de gastos en forma de tabla"""
        gasts = sorted(db.gastos_por_año(year), key=lambda g: g.fecha, reverse=True)
        list_col.controls.clear()

        def th(t):
            """Crea una fila de encabezado de tabla"""
            return ft.Container(
                content=ft.Text(t, size=11, weight=ft.FontWeight.W_600, color=COLORS["text_muted"])
            )

        list_col.controls.append(ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(content=th("DESCRIPCIÓN"), col={"xs": 12, "md": 4}),
                ft.Container(content=th("CATEGORÍA"), col={"xs": 6, "md": 3}),
                ft.Container(content=th("FECHA"), col={"xs": 6, "md": 2}),
                ft.Container(content=th("IMPORTE"), col={"xs": 6, "md": 2}),
                ft.Container(content=th(""), col={"xs": 6, "md": 1}),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
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

                def accion(gid):
                    """Crea los pequeños botones de la derecha de cada gasto (el de editar y el de borrar)."""
                    def al_editar(e, gid=gid):
                        navegar("form_gasto", edit_id=gid)

                    def al_eliminar(e, gid=gid):
                            
                        dlg = ft.AlertDialog(
                            title=ft.Text("¿Eliminar gasto?"),
                            content=ft.Text("Esta acción no se puede deshacer.")
                        )
                        
                        def confirmar(ev):
                            db.eliminar_gasto(gid)
                            dlg.open = False
                            ev.page.update()
                            notificacion(ev.page, "Gasto eliminado")
                            dibujar_lista()
                            ev.page.update()
                            
                        def cancelar(ev):
                            dlg.open = False
                            ev.page.update()
                            
                        dlg.actions = [
                            ft.TextButton("Cancelar", on_click=cancelar),
                            ft.TextButton("Eliminar", on_click=confirmar, style=ft.ButtonStyle(color="red")),
                        ]
                        
                        e.page.overlay.append(dlg)
                        dlg.open = True
                        e.page.update()

                    return ft.Row([
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=COLORS["primary"],
                                      tooltip="Editar", on_click=al_editar,
                                      icon_size=18, width=32, height=32),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=COLORS["danger"],
                                      tooltip="Eliminar", on_click=al_eliminar,
                                      icon_size=18, width=32, height=32),
                    ], spacing=0)

                def celda(t, bold=False, color=None):
                    """Hace que todas las palabras de la tabla de gastos tengan el mismo tipo de letra y queden bonitas."""
                    return ft.Container(
                        content=ft.Text(str(t), size=13,
                                        weight=ft.FontWeight.W_600 if bold else ft.FontWeight.NORMAL,
                                        color=color or COLORS["text_primary"])
                    )

                row = ft.Container(
                    content=ft.ResponsiveRow([
                        ft.Container(content=celda(g.descripcion), col={"xs": 12, "md": 4}),
                        ft.Container(
                            content=ft.Container(
                                content=ft.Text(f"{ico} {lbl}", size=12),
                                bgcolor="#EFF6FF", border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            ),
                            col={"xs": 6, "md": 3},
                        ),
                        ft.Container(content=celda(g.fecha, color=COLORS["text_secondary"]), col={"xs": 6, "md": 2}),
                        ft.Container(content=celda(formatear_moneda(g.importe), bold=True), col={"xs": 6, "md": 2}),
                        ft.Container(content=accion(g.id), col={"xs": 6, "md": 1}),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=bg,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                )
                list_col.controls.append(row)

    dibujar_lista()

    #TARJETAS DE GASTOS POR CATEGORIAS ( ARRIBA DE LA PAGINA )
    por_cat = gastos_por_categoria(db.gastos_por_año(year))
    cat_cards = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text(CAT_LABELS.get(k, ("📦","Otros"))[0], size=22),
                    ft.Text(CAT_LABELS.get(k, ("📦","Otros"))[1], size=11,
                            color=COLORS["text_secondary"]),
                    ft.Text(formatear_moneda(v), size=15, weight=ft.FontWeight.BOLD,
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
        """Nos lleva a la pantalla para añadir un gasto nuevo."""
        navegar("form_gasto")

    content = ft.Column([
        ft.Row([
            cabecera("Gastos", "Controla tus gastos personales"),
            btn_primario("Nuevo Gasto", on_click=nuevo_gasto, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        cat_cards,
        ft.Container(height=16),
        tarjeta(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    return vista_adaptable(content)