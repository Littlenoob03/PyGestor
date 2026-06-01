import flet as ft
from frontend.styles import COLORS, btn_primario, notificacion

def VistaLogin(db, on_login) -> ft.Container:
    """Crea la primera pantalla que vemos al abrir la aplicación, donde ponemos nuestra contraseña o nos registramos."""
    
    is_register_mode = [False]
    
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
    
    email = ft.TextField(
        label="Correo Electrónico",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        visible=False,
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
        on_submit=lambda e: validar_accion(e),
    )

    title_text = ft.Text("Inicia sesión para gestionar tu negocio", size=14, color=COLORS["text_secondary"])

    def validar_accion(e):
        """Comprueba que hayamos rellenado todo bien al darle al botón de entrar o de crear cuenta."""
        if not username.value or not password.value:
            notificacion(e.page, "Por favor, rellena todos los campos.", ok=False)
            return
            
        if is_register_mode[0]:
            if not email.value:
                notificacion(e.page, "Por favor, introduce un correo electrónico.", ok=False)
                return
            
            valid_domains = ["@gmail.com", "@hotmail.com", "@hotmail.es", "@yahoo.com", ".es", ".com"]
            if not any(d in email.value.lower() for d in valid_domains) or "@" not in email.value:
                notificacion(e.page, "Por favor, introduce un correo válido (ej: @gmail.com, @hotmail.com).", ok=False)
                return

            if len(password.value) < 8:
                notificacion(e.page, "La contraseña debe tener al menos 8 caracteres.", ok=False)
                return
            
            if not any(c.isupper() for c in password.value):
                notificacion(e.page, "La contraseña debe contener al menos una letra mayúscula.", ok=False)
                return

            if password.value != password_confirm.value:
                notificacion(e.page, "Las contraseñas no coinciden.", ok=False)
                return
                
            success = db.añadir_usuario(username.value, password.value, email.value)
            if success:
                notificacion(e.page, "Cuenta creada con éxito. Iniciando sesión...", ok=True)
                user = db.get_usser(username.value, password.value)
                on_login(user_id=user["id"] if user else None)
            else:
                notificacion(e.page, "Ese nombre de usuario ya existe.", ok=False)
        else:
            #LOGIN
            user = db.get_usser(username.value, password.value)
            if user:
                on_login(user_id=user["id"])
            else:
                notificacion(e.page, "Usuario o contraseña incorrectos", ok=False)

    def cambiar_login_registro(e):
        """Cambia la pantalla para que podamos elegir entre entrar a nuestra cuenta o crear una nueva, enseñando o escondiendo los huecos que hagan falta."""
        is_register_mode[0] = not is_register_mode[0]
        if is_register_mode[0]:
            title_text.value = "Crea una cuenta nueva"
            email.visible = True
            password_confirm.visible = True
            btn_action.content.controls[0].name = ft.Icons.PERSON_ADD_ALT_1
            btn_action.content.controls[1].value = "Crear Cuenta"
            btn_toggle.text = "Volver a Iniciar Sesión"
            btn_toggle.icon = ft.Icons.ARROW_BACK
        else:
            title_text.value = "Inicia sesión para gestionar tu negocio"
            email.visible = False
            password_confirm.visible = False
            btn_action.content.controls[0].name = ft.Icons.LOGIN
            btn_action.content.controls[1].value = "Iniciar Sesión"
            btn_toggle.text = "Registrarse"
            btn_toggle.icon = ft.Icons.PERSON_ADD_OUTLINED
        
        e.page.update()

    #LOGO 
    logo = ft.Container(
        content=ft.Column([
            ft.Image(src="Logo.png", width=120, height=120, fit=ft.BoxFit.CONTAIN),
            ft.Container(height=16),
            title_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        margin=ft.Margin(bottom=32, top=0, left=0, right=0)
    )

    btn_action = btn_primario("Iniciar Sesión", on_click=validar_accion, icon=ft.Icons.LOGIN)
    
    btn_toggle = ft.OutlinedButton(
        "Registrarse",
        icon=ft.Icons.PERSON_ADD_OUTLINED,
        on_click=cambiar_login_registro,
        style=ft.ButtonStyle(
            color=COLORS["primary"],
            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, COLORS["primary"]),
        )
    )

    #TARJETA DE LOGIN
    tarjeta = ft.Container(
        content=ft.Column([
            logo,
            ft.Column([username, email, password, password_confirm], spacing=16),
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
        content=tarjeta,
        expand=True,
        bgcolor=COLORS["bg"],
        alignment=ft.Alignment(0, 0),
    )
