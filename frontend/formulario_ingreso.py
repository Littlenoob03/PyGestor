import flet as ft
from datetime import date
from backend.database import Database
from frontend.styles import (
    COLORS, tarjeta, btn_primario, btn_secundario,
    cabecera, campo_texto, desplegable, notificacion, vista_adaptable
)

def VistaFormularioIngreso(db: Database, navegar, edit_id=None) -> ft.Container:
    """Crea la pantalla donde rellenamos los datos para apuntar un ingreso nuevo o modificar uno que ya existe."""
    
    #CAMPOS DE INGRESOS
    f_origen   = desplegable("Fuente / Origen", [
        ("Nómina", "💼 Nómina"),
        ("Bizum", "📱 Bizum"),
        ("Transferencia", "🏦 Transferencia"),
        ("Efectivo", "💵 Efectivo"),
        ("Venta", "🛍️ Venta"),
        ("Devolución", "🔄 Devolución"),
        ("Otros", "📦 Otros"),
    ], value="Nómina")
    f_concepto = campo_texto("Concepto", "Descripción del ingreso")
    f_fecha    = campo_texto("Fecha (YYYY-MM-DD)", str(date.today()), value=str(date.today()))
    f_importe  = campo_texto("Importe", "0.00", keyboard_type=ft.KeyboardType.NUMBER)
    f_estado   = desplegable("Estado", [("pendiente","Pendiente"),("cobrado","Cobrado")], value="cobrado")

    is_edit = edit_id is not None

    if is_edit:
        ing = db.obtener_ingreso(edit_id)
        if ing:
            valid_options = ["Nómina", "Bizum", "Transferencia", "Efectivo", "Venta", "Devolución", "Otros"]
            f_origen.value   = ing.origen if ing.origen in valid_options else "Otros"
            f_concepto.value = ing.concepto
            f_fecha.value    = ing.fecha
            f_importe.value  = str(ing.importe)
            f_estado.value   = ing.estado

    def guardar(e):
        """Comprueba que todo esté bien y guarda el ingreso en nuestro registro."""
        page = e.page
        try:
            data = dict(
                origen=f_origen.value,
                concepto=f_concepto.value,
                fecha=f_fecha.value,
                importe=float(f_importe.value or 0),
                estado=f_estado.value,
            )
            if is_edit:
                db.actualizar_ingreso(edit_id, **data)
                notificacion(page, "Ingreso actualizado")
            else:
                db.añadir_ingreso(**data)
                notificacion(page, "Ingreso creado")
            
            navegar("ingresos")
        except Exception as ex:
            notificacion(page, f"Error: {ex}", ok=False)

    def cancelar(e):
        """Cierra esta pantalla y nos devuelve a la lista de ingresos sin guardar nada."""
        navegar("ingresos")

    titulo = "Editar Ingreso" if is_edit else "Nuevo Ingreso"
    subtitulo = "Modifica los datos del ingreso" if is_edit else "Añade una nueva fuente de ingresos"

    form_content = ft.Column([
        ft.Row([f_origen, f_fecha], spacing=16),
        f_concepto,
        ft.Row([f_importe, f_estado], spacing=16),
        ft.Container(height=24),
        ft.Row([
            btn_secundario("Cancelar", on_click=cancelar),
            btn_primario("Guardar Ingreso", on_click=guardar, icon=ft.Icons.SAVE),
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
