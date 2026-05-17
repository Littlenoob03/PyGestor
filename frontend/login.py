import flet as ft
from frontend.styles import COLORS, btn_primary, snack

def LoginView(db, on_login) -> ft.Container:
    
    is_register_mode = [False]
    
    # ── Inputs ─────────────────────────────────────────────────────────────
    username = ft.TextField(
        label="Usuario",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )
    
    password = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        on_submit=lambda e: handle_action(e),
    )
    
    password_confirm = ft.TextField(
        label="Repetir Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        visible=False,
        on_submit=lambda e: handle_action(e),
    )

    title_text = ft.Text("Inicia sesión para gestionar tu negocio", size=14, color=COLORS["text_secondary"])

    def handle_action(e):
        if not username.value or not password.value:
            snack(e.page, "Por favor, rellena todos los campos.", ok=False)
            return
            
        if is_register_mode[0]:
            if password.value != password_confirm.value:
                snack(e.page, "Las contraseñas no coinciden.", ok=False)
                return
            success = db.add_usuario(username.value, password.value)
            if success:
                snack(e.page, "Cuenta creada con éxito. Iniciando sesión...", ok=True)
                user = db.get_usuario(username.value, password.value)
                on_login(is_guest=False, user_id=user["id"] if user else None)
            else:
                snack(e.page, "Ese nombre de usuario ya existe.", ok=False)
        else:
            # Login
            user = db.get_usuario(username.value, password.value)
            if user:
                on_login(is_guest=False, user_id=user["id"])
            else:
                snack(e.page, "Usuario o contraseña incorrectos", ok=False)

    def toggle_mode(e):
        is_register_mode[0] = not is_register_mode[0]
        if is_register_mode[0]:
            title_text.value = "Crea una cuenta nueva"
            password_confirm.visible = True
            btn_action.content.controls[0].name = ft.Icons.PERSON_ADD_ALT_1
            btn_action.content.controls[1].value = "Crear Cuenta"
            btn_toggle.text = "Volver a Iniciar Sesión"
            btn_toggle.icon = ft.Icons.ARROW_BACK
        else:
            title_text.value = "Inicia sesión para gestionar tu negocio"
            password_confirm.visible = False
            btn_action.content.controls[0].name = ft.Icons.LOGIN
            btn_action.content.controls[1].value = "Iniciar Sesión"
            btn_toggle.text = "Registrarse"
            btn_toggle.icon = ft.Icons.PERSON_ADD_OUTLINED
        
        e.page.update()

    def handle_guest(e):
        on_login(is_guest=True, user_id=None)

    # ── Logo ───────────────────────────────────────────────────
    logo = ft.Container(
        content=ft.Column([
            ft.Image(src="Logo.png", width=120, height=120, fit=ft.BoxFit.CONTAIN),
            ft.Container(height=16),
            title_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        margin=ft.Margin(bottom=32, top=0, left=0, right=0)
    )

    btn_action = btn_primary("Iniciar Sesión", on_click=handle_action, icon=ft.Icons.LOGIN)
    
    btn_toggle = ft.OutlinedButton(
        "Registrarse",
        icon=ft.Icons.PERSON_ADD_OUTLINED,
        on_click=toggle_mode,
        style=ft.ButtonStyle(
            color=COLORS["primary"],
            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, COLORS["primary"]),
        )
    )

    # ── Tarjeta de Login ───────────────────────────────────────────────────
    card = ft.Container(
        content=ft.Column([
            logo,
            ft.Column([username, password, password_confirm], spacing=16),
            ft.Container(height=24),
            ft.Row([
                ft.Container(
                    content=btn_action,
                    expand=True,
                ),
            ]),
            ft.Container(height=8),
            ft.Row([
                ft.Container(
                    content=btn_toggle,
                    expand=True,
                ),
            ]),
            ft.Container(height=16),
            ft.Divider(color=COLORS["border"], height=1),
            ft.Container(height=8),
            ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=18, color=COLORS["text_secondary"]),
                    ft.Text("Entrar como invitado (solo lectura)", size=14, color=COLORS["text_secondary"]),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                on_click=handle_guest,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
        width=400,
        bgcolor="white",
        border_radius=24,
        padding=ft.Padding.all(40),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=40,
            color=ft.Colors.with_opacity(0.04, "black"),
            offset=ft.Offset(0, 10),
        ),
    )

    return ft.Container(
        content=card,
        expand=True,
        bgcolor=COLORS["bg"],
        alignment=ft.Alignment(0, 0), # Centrado absoluto
    )
