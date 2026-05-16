import flet as ft
from datetime import date
from backend.database import Database
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary,
    section_header, text_field, dropdown, snack, page_wrapper
)

def FormularioIngresoView(db: Database, navigate, edit_id=None) -> ft.Container:
    
    # Referencias de los campos
    f_origen   = dropdown("Fuente / Origen", [
        ("Nómina", "💼 Nómina"),
        ("Bizum", "📱 Bizum"),
        ("Transferencia", "🏦 Transferencia"),
        ("Efectivo", "💵 Efectivo"),
        ("Venta", "🛍️ Venta"),
        ("Devolución", "🔄 Devolución"),
        ("Otros", "📦 Otros"),
    ], value="Nómina")
    f_concepto = text_field("Concepto", "Descripción del ingreso")
    f_fecha    = text_field("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    f_importe  = text_field("Importe", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    f_estado   = dropdown("Estado", [("pendiente","Pendiente"),("cobrado","Cobrado")], value="cobrado")

    is_edit = edit_id is not None

    if is_edit:
        ing = db.get_ingreso(edit_id)
        if ing:
            # Check if the existing value is one of our dropdown options, otherwise default to "Otros"
            valid_options = ["Nómina", "Bizum", "Transferencia", "Efectivo", "Venta", "Devolución", "Otros"]
            f_origen.value   = ing.origen if ing.origen in valid_options else "Otros"
            f_concepto.value = ing.concepto
            f_fecha.value    = ing.fecha
            f_importe.value  = str(ing.importe)
            f_estado.value   = ing.estado

    def guardar(e):
        page = e.page
        if getattr(page, "is_guest", False):
            snack(page, "Modo Invitado: Inicia sesión para guardar datos.", ok=False)
            if hasattr(page, "logout"):
                page.logout()
            return

        try:
            data = dict(
                origen=f_origen.value,
                concepto=f_concepto.value,
                fecha=f_fecha.value,
                importe=float(f_importe.value or 0),
                estado=f_estado.value,
            )
            if is_edit:
                db.update_ingreso(edit_id, **data)
                snack(page, "Ingreso actualizado ✅")
            else:
                db.add_ingreso(**data)
                snack(page, "Ingreso creado ✅")
            
            navigate("ingresos")
        except Exception as ex:
            snack(page, f"Error: {ex}", ok=False)

    def cancelar(e):
        navigate("ingresos")

    titulo = "Editar Ingreso" if is_edit else "Nuevo Ingreso"
    subtitulo = "Modifica los datos del ingreso" if is_edit else "Añade una nueva fuente de ingresos"

    form_content = ft.Column([
        ft.Row([f_origen, f_fecha], spacing=16),
        f_concepto,
        ft.Row([f_importe, f_estado], spacing=16),
        ft.Container(height=24),
        ft.Row([
            btn_secondary("Cancelar", on_click=cancelar),
            btn_primary("Guardar Ingreso", on_click=guardar, icon=ft.Icons.SAVE),
        ], alignment=ft.MainAxisAlignment.END, spacing=12),
    ], spacing=16)

    content = ft.Column([
        section_header(titulo, subtitulo),
        ft.Container(height=20),
        card(
            form_content,
            padding=32,
            radius=12
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    return page_wrapper(content)
