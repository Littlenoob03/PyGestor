import flet as ft
from datetime import date
from backend.database import Database
from frontend.styles import (
    COLORS, card, btn_primary, btn_secondary,
    section_header, text_field, dropdown, snack, page_wrapper
)

def FormularioGastoView(db: Database, navigate, edit_id=None) -> ft.Container:
    
    # Referencias de los campos
    g_desc    = text_field("Descripción", "Descripción del gasto")
    g_fecha   = text_field("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    g_importe = text_field("Importe", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    g_cat     = dropdown("Categoría", [
        ("oficina","🖊️ Oficina"), ("software","💻 Software"),
        ("marketing","📢 Marketing"), ("transporte","🚗 Transporte"),
        ("formacion","📚 Formación"), ("seguro","🛡️ Seguro"), 
        ("alimentacion", "🛒 Alimentación"), ("ocio", "🍿 Ocio"),
        ("salud", "🏥 Salud"), ("vehiculo", "🚙 Vehículo"),
        ("otros","📦 Otros"),
    ], value="otros")

    is_edit = edit_id is not None

    if is_edit:
        ga = db.get_gasto(edit_id)
        if ga:
            g_desc.value      = ga.descripcion
            g_cat.value       = ga.categoria
            g_fecha.value     = ga.fecha
            g_importe.value   = str(ga.importe)

    def guardar(e):
        page = e.page

        try:
            data = dict(
                descripcion=g_desc.value,
                categoria=g_cat.value,
                fecha=g_fecha.value,
                importe=float(g_importe.value or 0),
            )
            if is_edit:
                db.update_gasto(edit_id, **data)
                snack(page, "Gasto actualizado ✅")
            else:
                db.add_gasto(**data)
                snack(page, "Gasto registrado ✅")
            
            navigate("gastos")
        except Exception as ex:
            snack(page, f"Error: {ex}", ok=False)

    def cancelar(e):
        navigate("gastos")

    titulo = "Editar Gasto" if is_edit else "Nuevo Gasto"
    subtitulo = "Modifica los datos del gasto" if is_edit else "Añade un nuevo gasto personal"

    form_content = ft.Column([
        ft.Row([g_desc, g_fecha], spacing=16),
        ft.Row([g_importe, g_cat], spacing=16),
        ft.Container(height=24),
        ft.Row([
            btn_secondary("Cancelar", on_click=cancelar),
            btn_primary("Guardar Gasto", on_click=guardar, icon=ft.Icons.SAVE),
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
