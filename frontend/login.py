import flet as ft
from frontend.styles import COLORS, btn_primary, snack

def LoginView(on_login) -> ft.Container:
    
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
        on_submit=lambda e: handle_login(e),
    )

    def handle_login(e):
        if username.value == "admin" and password.value == "admin":
            on_login(is_guest=False)
        else:
            snack(e.page, "Usuario o contraseña incorrectos", ok=False)

    def handle_guest(e):
        on_login(is_guest=True)

    # ── Logo Placeholder ───────────────────────────────────────────────────
    logo = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(ft.Icons.AUTO_GRAPH_ROUNDED, size=48, color="white"),
                width=80, height=80,
                bgcolor=COLORS["primary"],
                border_radius=20,
                alignment=ft.Alignment(0, 0),
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=15,
                    color=ft.Colors.with_opacity(0.4, COLORS["primary"]),
                    offset=ft.Offset(0, 8),
                ),
            ),
            ft.Container(height=8),
            ft.Text("PyGestor", size=28, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"]),
            ft.Text("Inicia sesión para gestionar tu negocio", size=14, color=COLORS["text_secondary"]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        margin=ft.Margin(bottom=32, top=0, left=0, right=0)
    )

    # ── Tarjeta de Login ───────────────────────────────────────────────────
    card = ft.Container(
        content=ft.Column([
            logo,
            ft.Column([username, password], spacing=16),
            ft.Container(height=24),
            ft.Row([
                ft.Container(
                    content=btn_primary("Iniciar Sesión", on_click=handle_login, icon=ft.Icons.LOGIN),
                    expand=True,
                ),
            ]),
            ft.Container(height=8),
            ft.Row([
                ft.Container(
                    content=ft.OutlinedButton(
                        "Registrarse",
                        icon=ft.Icons.PERSON_ADD_OUTLINED,
                        on_click=lambda e: snack(e.page, "Registro no implementado aún", ok=True),
                        style=ft.ButtonStyle(
                            color=COLORS["primary"],
                            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
                            shape=ft.RoundedRectangleBorder(radius=12),
                            side=ft.BorderSide(1, COLORS["primary"]),
                        )
                    ),
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
