import flet as ft
from datetime import date, datetime
from backend.database import Database
from backend.logic import fmt
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary, btn_danger,
    badge, section_header, text_field, dropdown, snack, page_wrapper, divider
)

def FacturasView(db: Database, navigate) -> ft.Container:
    year = datetime.now().year
    filtro_estado = {"val": "all"}
    editing_id = {"val": None}

    # ── Formulario (Dialog) ────────────────────────────────
    f_numero   = text_field("Nº Factura", "FAC-2025-001")
    f_concepto = text_field("Concepto",   "Descripción del servicio")
    f_fecha    = text_field("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    f_base     = text_field("Base Imponible", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    f_iva      = dropdown("IVA %",  [("21","21 %"),("10","10 %"),("4","4 %"),("0","0 %")], value="21")
    f_irpf     = dropdown("IRPF %", [("15","15 %"),("7","7 % (nuevo)"),("0","0 %")], value="15")
    f_estado   = dropdown("Estado", [("pendiente","Pendiente"),("pagado","Pagado")], value="pendiente")
    f_cliente  = ft.Ref[ft.Dropdown]()

    totales_text = ft.Text("", size=13, color=COLORS["text_secondary"])

    def recalc(e=None):
        try:
            base  = float(f_base.value or 0)
            iva   = base * float(f_iva.value or 0) / 100
            irpf  = base * float(f_irpf.value or 0) / 100
            total = base + iva - irpf
            totales_text.value = (
                f"IVA: {fmt(iva)}   IRPF: -{fmt(irpf)}   "
                f"TOTAL: {fmt(total)}"
            )
            totales_text.update()
        except Exception:
            pass

    f_base.on_change = recalc
    f_iva.on_change  = recalc
    f_irpf.on_change = recalc

    def cliente_options():
        return [ft.dropdown.Option(str(c.id), c.nombre) for c in db.clientes]

    cliente_dd = ft.Dropdown(
        label="Cliente",
        options=cliente_options(),
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=4),
        ref=f_cliente,
    )

    list_col = ft.Column(spacing=0)
    page_ref = ft.Ref[ft.Page]()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nueva Factura", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=520,
            content=ft.Column([
                ft.Row([f_numero, f_fecha], spacing=12),
                cliente_dd,
                f_concepto,
                ft.Row([f_base, f_iva, f_irpf, f_estado], spacing=12),
                ft.Container(
                    content=totales_text,
                    bgcolor="#EFF6FF", border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                ),
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
                numero=f_numero.value,
                cliente_id=int(cliente_dd.value or 0),
                concepto=f_concepto.value,
                fecha=f_fecha.value,
                base=float(f_base.value or 0),
                iva_pct=float(f_iva.value or 21),
                irpf_pct=float(f_irpf.value or 15),
                estado=f_estado.value,
            )
            if editing_id["val"]:
                db.update_factura(editing_id["val"], **data)
                snack(page, "Factura actualizada ✅")
            else:
                db.add_factura(**data)
                snack(page, "Factura creada ✅")
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
        cliente_dd.options = cliente_options()
        render_list()
        page.update()

    # ── Tabla ──────────────────────────────────────────────
    def render_list():
        facts = [f for f in db.facturas_by_year(year)
                 if filtro_estado["val"] == "all" or f.estado == filtro_estado["val"]]
        facts.sort(key=lambda f: f.fecha, reverse=True)

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
                th("Nº FACTURA", 120), th("CLIENTE", 160), th("FECHA", 100),
                th("BASE", 90), th("IVA", 80), th("IRPF", 80),
                th("TOTAL", 100), th("ESTADO", 90), th("", 80),
            ], spacing=8),
            bgcolor="#F7F8FA", padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        ))

        if not facts:
            list_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("🧾", size=40),
                    ft.Text("No hay facturas", size=15, color=COLORS["text_muted"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment.CENTER,
                height=200,
            ))
        else:
            for idx, f in enumerate(facts):
                cl   = db.get_cliente(f.cliente_id)
                nombre = cl.nombre if cl else "—"
                bg   = "white" if idx % 2 == 0 else "#FAFAFA"

                def make_actions(fid):
                    def on_edit(e, fid=fid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para editar.", ok=False)
                            return
                        fa = db.get_factura(fid)
                        editing_id["val"] = fid
                        f_numero.value   = fa.numero
                        f_concepto.value = fa.concepto
                        f_fecha.value    = fa.fecha
                        f_base.value     = str(fa.base)
                        f_iva.value      = str(int(fa.iva_pct))
                        f_irpf.value     = str(int(fa.irpf_pct))
                        f_estado.value   = fa.estado
                        cliente_dd.value = str(fa.cliente_id)
                        dlg.title        = ft.Text("Editar Factura", weight=ft.FontWeight.BOLD)
                        recalc()
                        open_dlg(e.page)

                    def on_toggle(e, fid=fid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para modificar.", ok=False)
                            return
                        fa = db.get_factura(fid)
                        new_estado = "pagado" if fa.estado == "pendiente" else "pendiente"
                        db.update_factura(fid, estado=new_estado)
                        snack(e.page, f"Marcado como {new_estado}")
                        refresh(e.page)

                    def on_delete(e, fid=fid):
                        if getattr(e.page, "is_guest", False):
                            snack(e.page, "Modo Invitado: Inicia sesión para borrar.", ok=False)
                            return
                        def confirm(ev):
                            db.delete_factura(fid)
                            ev.page.dialog.open = False
                            snack(ev.page, "Factura eliminada")
                            refresh(ev.page)
                        def cancel(ev):
                            ev.page.dialog.open = False
                            ev.page.update()
                        e.page.dialog = ft.AlertDialog(
                            title=ft.Text("¿Eliminar factura?"),
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
                        cell(f.numero, 120, bold=True, color=COLORS["primary"]),
                        cell(nombre, 160),
                        cell(f.fecha, 100, color=COLORS["text_secondary"]),
                        cell(fmt(f.base), 90),
                        cell(fmt(f.iva),  80),
                        cell(f"-{fmt(f.irpf)}", 80, color=COLORS["danger"]),
                        cell(fmt(f.total), 100, bold=True),
                        ft.Container(
                            content=badge("Pagado" if f.estado=="pagado" else "Pendiente",
                                          "success" if f.estado=="pagado" else "warning"),
                            width=90,
                        ),
                        make_actions(f.id),
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
        make_tab("Todas", "all"),
        make_tab("Pagadas", "pagado"),
        make_tab("Pendientes", "pendiente"),
    ])

    def nueva_factura(e):
        if getattr(e.page, "is_guest", False):
            snack(e.page, "Modo Invitado: Inicia sesión para añadir datos.", ok=False)
            return
        editing_id["val"] = None
        f_numero.value  = f"FAC-{year}-{str(len(db.facturas)+1).zfill(3)}"
        f_concepto.value = ""
        f_fecha.value    = str(date.today())
        f_base.value     = ""
        f_iva.value      = "21"
        f_irpf.value     = "15"
        f_estado.value   = "pendiente"
        cliente_dd.value = None
        cliente_dd.options = cliente_options()
        dlg.title = ft.Text("Nueva Factura", weight=ft.FontWeight.BOLD)
        totales_text.value = ""
        open_dlg(e.page)

    content = ft.Column([
        ft.Row([
            section_header("Facturas", "Gestiona todas tus facturas emitidas"),
            btn_primary("Nueva Factura", on_click=nueva_factura, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=16),
        tabs,
        ft.Container(height=8),
        card(list_col, padding=0, radius=12),
    ], spacing=0, scroll=ft.ScrollMode.AUTO)

    return page_wrapper(content)