import flet as ft
from datetime import date
from backend.database import Database
from frontend.styles import (
    COLORS, tarjeta, btn_primario, btn_secundario,
    cabecera, campo_texto, desplegable, notificacion, vista_adaptable
)

def VistaFormularioGasto(db: Database, navegar, edit_id=None) -> ft.Container:
    """Crea la pantalla donde rellenamos los datos para apuntar un gasto nuevo o modificar uno que ya existe."""
    
    #CAMPOS DE GASTOS
    g_desc    = campo_texto("Descripción", "Descripción del gasto")
    g_fecha   = campo_texto("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    g_importe = campo_texto("Importe", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    g_cat     = desplegable("Categoría", [
        ("oficina","🖊️ Oficina"), ("software","💻 Software"),
        ("marketing","📢 Marketing"), ("transporte","🚗 Transporte"),
        ("formacion","📚 Formación"), ("seguro","🛡️ Seguro"), 
        ("alimentacion", "🛒 Alimentación"), ("ocio", "🍿 Ocio"),
        ("salud", "🏥 Salud"), ("vehiculo", "🚙 Vehículo"),
        ("otros","📦 Otros"),
    ], value="otros")

    is_edit = edit_id is not None

    if is_edit:
        ga = db.obtener_gasto(edit_id)
        if ga:
            g_desc.value      = ga.descripcion
            g_cat.value       = ga.categoria
            g_fecha.value     = ga.fecha
            g_importe.value   = str(ga.importe)

    def guardar(e):
        """Comprueba que todo esté bien y guarda el gasto en nuestro registro."""
        page = e.page

        try:
            data = dict(
                descripcion=g_desc.value,
                categoria=g_cat.value,
                fecha=g_fecha.value,
                importe=float(g_importe.value or 0),
            )
            if is_edit:
                db.actualizar_gasto(edit_id, **data)
                notificacion(page, "Gasto actualizado")
            else:
                db.añadir_gasto(**data)
                notificacion(page, "Gasto registrado")
            
            navegar("gastos")
        except Exception as ex:
            notificacion(page, f"Error: {ex}", ok=False)

    def cancelar(e):
        """Cierra esta pantalla y nos devuelve a la lista de gastos sin guardar nada."""
        navegar("gastos")

    titulo = "Editar Gasto" if is_edit else "Nuevo Gasto"
    subtitulo = "Modifica los datos del gasto" if is_edit else "Añade un nuevo gasto personal"

    form_content = ft.Column([
        ft.Row([g_desc, g_fecha], spacing=16),
        ft.Row([g_importe, g_cat], spacing=16),
        ft.Container(height=24),
        ft.Row([
            btn_secundario("Cancelar", on_click=cancelar),
            btn_primario("Guardar Gasto", on_click=guardar, icon=ft.Icons.SAVE),
        ], alignment=ft.MainAxisAlignment.END, spacing=12),
    ], spacing=16)

    content = ft.Column([
        cabecera(titulo, subtitulo),
        ft.Container(height=20),
        tarjeta(
            form_content,
            padding=32,
            radius=12
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    return vista_adaptable(content)
