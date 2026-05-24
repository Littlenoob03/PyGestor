import flet as ft
import os
import shutil
from backend.database import Database
from frontend.styles import COLORS, btn_primary, card, section_header, text_field, page_wrapper, snack

def PerfilView(db: Database, navigate, refresh_sidebar) -> ft.Container:
    user_id = db.current_user_id
    if user_id is None:
        return ft.Container(content=ft.Text("Inicia sesión para ver tu perfil."))

    user = db.get_usuario_by_id(user_id)
    if not user:
        return ft.Container(content=ft.Text("Usuario no encontrado."))

    # Referencias
    f_username = text_field("Usuario", "Tu nombre de usuario", value=user.get("username", ""))
    f_password = text_field("Contraseña", "Tu contraseña", value=user.get("password", ""), password=True)
    f_email    = text_field("Email", "tu@email.com", value=user.get("email", ""))
    f_telefono = text_field("Teléfono", "123456789", value=user.get("telefono", ""))

    avatar_image = ft.Image(
        src=f"imagenes/{user.get('foto')}" if user.get("foto") else "",
        width=100,
        height=100,
        fit=ft.BoxFit.COVER,
        border_radius=50,
        visible=bool(user.get("foto"))
    )

    avatar_initials = ft.Container(
        content=ft.Text(user.get("username", "US")[:2].upper(), size=32, weight=ft.FontWeight.BOLD, color="white"),
        width=100, height=100,
        bgcolor=COLORS["primary"],
        border_radius=50,
        alignment=ft.Alignment(0, 0),
        visible=not bool(user.get("foto"))
    )

    def update_avatar_ui(foto_name):
        if foto_name:
            avatar_image.src = f"imagenes/{foto_name}"
            avatar_image.visible = True
            avatar_initials.visible = False
        else:
            avatar_image.visible = False
            avatar_initials.visible = True
        avatar_image.update()
        avatar_initials.update()

    f_foto = text_field("Nombre de la imagen", "ej: mi_foto.png", value=user.get("foto", ""))

    def guardar_foto_manual(e):
        foto_name = f_foto.value.strip()
        db.update_usuario(user_id, foto=foto_name)
        update_avatar_ui(foto_name)
        refresh_sidebar()
        dialog.open = False
        e.page.update()
        snack(e.page, "Foto de perfil actualizada ✅")

    def cerrar_dialog(e):
        dialog.open = False
        e.page.update()

    dialog = ft.AlertDialog(
        title=ft.Text("Cambiar Foto de Perfil"),
        content=ft.Column([
            ft.Text("El selector de archivos no es compatible con esta versión de la app. Coloca tu imagen en la carpeta 'assets/imagenes' y escribe aquí el nombre del archivo (ej: perfil.png).", size=13, color=COLORS["text_secondary"]),
            ft.Container(height=10),
            f_foto
        ], tight=True),
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=cerrar_dialog),
            btn_primary("Guardar", on_click=guardar_foto_manual)
        ]
    )

    def pick_photo(e):
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()

    def guardar(e):
        try:
            db.update_usuario(
                user_id,
                username=f_username.value,
                password=f_password.value,
                email=f_email.value,
                telefono=f_telefono.value
            )
            refresh_sidebar()
            snack(e.page, "Datos actualizados correctamente ✅")
        except Exception as ex:
            snack(e.page, f"Error al guardar: {ex}", ok=False)

    btn_upload = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.UPLOAD), ft.Text("Cambiar Foto")]), on_click=pick_photo)

    datos_personales = ft.Column([
        ft.Row([
            ft.Stack([avatar_initials, avatar_image]),
            ft.Column([btn_upload], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(height=30, color=COLORS["border"]),
        ft.Row([f_username, f_password], spacing=16),
        ft.Row([f_email, f_telefono], spacing=16),
        ft.Container(height=20),
        ft.Row([btn_primary("Guardar Cambios", on_click=guardar, icon=ft.Icons.SAVE)], alignment=ft.MainAxisAlignment.END)
    ], spacing=16)

    # ── Planes ────────────────────────────────────────────────
    current_plan = user.get("plan", "Plan Personal")

    def create_plan_card(title, price, features, is_active):
        active_color = COLORS["primary"] if is_active else COLORS["text_secondary"]
        bg_color = ft.Colors.with_opacity(0.05, COLORS["primary"]) if is_active else "white"
        
        return card(
            ft.Column([
                ft.Row([
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
                    ft.Container(
                        content=ft.Text("ACTIVO", size=10, weight=ft.FontWeight.BOLD, color="white"),
                        bgcolor=COLORS["primary"],
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        border_radius=10,
                        visible=is_active
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(price, size=24, weight=ft.FontWeight.BOLD, color=active_color),
                ft.Divider(height=20, color=COLORS["border"]),
                ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CHECK, size=16, color=COLORS["success"]), ft.Text(f, size=13)]) for f in features
                ], spacing=8),
                ft.Container(height=20),
                btn_primary("Plan Actual", width=200) if is_active else ft.OutlinedButton(content=ft.Text("Mejorar Plan"), width=200, disabled=True)
            ], spacing=10),
            padding=24, radius=12
        )

    planes = ft.Row([
        ft.Container(
            content=create_plan_card("Plan Personal", "Gratis", ["Gestión básica", "Hasta 100 registros", "Soporte comunitario"], current_plan == "Plan Personal"),
            expand=True
        ),
        ft.Container(
            content=create_plan_card("Plan Pro", "9.99€ / mes", ["Estadísticas avanzadas", "Registros ilimitados", "Soporte prioritario"], current_plan == "Plan Pro"),
            expand=True
        ),
        ft.Container(
            content=create_plan_card("Plan Deluxe", "19.99€ / mes", ["Exportación a PDF/Excel", "Modo multi-usuario", "Soporte 24/7", "Asesoría fiscal"], current_plan == "Plan Deluxe"),
            expand=True
        )
    ], spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)

    # ── Pestañas Customizadas ─────────────────────────────────
    active_tab = "datos"

    def set_tab(tab_name):
        nonlocal active_tab
        active_tab = tab_name
        
        btn_datos.style.color = COLORS["primary"] if active_tab == "datos" else COLORS["text_secondary"]
        btn_planes.style.color = COLORS["primary"] if active_tab == "planes" else COLORS["text_secondary"]
        
        tab_content.content = ft.Container(card(datos_personales, padding=32, radius=12), padding=ft.Padding.only(top=20)) if active_tab == "datos" else ft.Container(planes, padding=ft.Padding.only(top=20))
        tab_content.update()
        btn_datos.update()
        btn_planes.update()

    btn_datos = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.PERSON), ft.Text("Datos Personales")]),
        on_click=lambda _: set_tab("datos"),
        style=ft.ButtonStyle(color=COLORS["primary"])
    )
    btn_planes = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.STAR), ft.Text("Planes de Suscripción")]),
        on_click=lambda _: set_tab("planes"),
        style=ft.ButtonStyle(color=COLORS["text_secondary"])
    )

    tab_content = ft.Container(
        content=ft.Container(card(datos_personales, padding=32, radius=12), padding=ft.Padding.only(top=20))
    )

    tabs = ft.Column([
        ft.Row([btn_datos, btn_planes], spacing=10),
        ft.Divider(height=1, color=COLORS["border"]),
        tab_content
    ], spacing=0, expand=True)

    content = ft.Column([
        section_header("Mi Perfil", "Gestiona tus datos personales y tu plan de suscripción."),
        ft.Container(height=20),
        tabs
    ], expand=True)

    return page_wrapper(content)
