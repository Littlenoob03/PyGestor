import flet as ft
from frontend.dashboard import DashboardView
from frontend.ingresos import IngresosView
from frontend.gastos import GastosView
from frontend.informes import InformesView
from frontend.formulario_ingreso import FormularioIngresoView
from frontend.formulario_gasto import FormularioGastoView
from frontend.login import LoginView
from backend.database import Database

def main(page: ft.Page):
    page.title = "PyGestor"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#F7F8FA"

    page.window_width = 1280
    page.window_height = 800
    page.window_min_width = 1100
    page.window_min_height = 700
    page.window_icon = "Logo.png"

    page.fonts = {
        "Inter": "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")

    db = Database()
    db.seed_demo_data()

    current_view = {"name": "dashboard"}
    content_area = ft.Container(expand=True)

    def navigate(view_name: str, **kwargs):
        current_view["name"] = view_name
        render_view(view_name, **kwargs)
        update_nav(view_name)
        page.update()

    def render_view(view_name: str, **kwargs):
        views = {
            "dashboard": lambda: DashboardView(db, navigate),
            "ingresos":  lambda: IngresosView(db, navigate),
            "gastos":    lambda: GastosView(db, navigate),
            "informes":  lambda: InformesView(db, navigate),
            "form_ingreso": lambda: FormularioIngresoView(db, navigate, **kwargs),
            "form_gasto":   lambda: FormularioGastoView(db, navigate, **kwargs),
        }
        content_area.content = views.get(view_name, views["dashboard"])()
        page.update()

    # ── Nav items con iconos Material Design ───────────────
    nav_items = [
        ("dashboard", ft.Icons.DASHBOARD_OUTLINED,         "Dashboard"),
        ("ingresos",  ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, "Ingresos"),
        ("gastos",    ft.Icons.PAYMENTS_OUTLINED,           "Gastos"),
        ("informes",  ft.Icons.BAR_CHART_OUTLINED,          "Informes"),
    ]

    nav_buttons = {}

    def make_nav_button(key, icon, label):
        btn = ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=18, color="white"),
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color="white"),
            ], spacing=12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=13),
            border_radius=12,
            on_click=lambda e, k=key: navigate(k),
            ink=True,
            bgcolor=ft.Colors.with_opacity(0, "white"),
        )
        nav_buttons[key] = btn
        return btn

    def update_nav(active: str):
        for key, btn in nav_buttons.items():
            if key == active:
                btn.bgcolor = ft.Colors.with_opacity(0.18, "white")
                # Resaltar icono y texto en activo
                row = btn.content
                row.controls[0].color = "#A5B4FC"   # icono indigo claro
            else:
                btn.bgcolor = ft.Colors.with_opacity(0, "white")
                row = btn.content
                row.controls[0].color = "white"
        page.update()

    # ── Sidebar ────────────────────────────────────────────
    sidebar = ft.Container(
        width=235,
        bgcolor="#0F1729",
        content=ft.Column([
            # Logo
            ft.Container(
                content=ft.Image(src="banner.jpg", width=180, fit=ft.BoxFit.CONTAIN),
                padding=ft.Padding.symmetric(horizontal=20, vertical=20),
                alignment=ft.Alignment(-1, 0),
            ),
            ft.Divider(color=ft.Colors.with_opacity(0.15, "white"), height=1),
            ft.Container(height=8),
            # Etiqueta de sección
            ft.Container(
                content=ft.Text("MENÚ PRINCIPAL", size=10,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.with_opacity(0.45, "white")),
                padding=ft.Padding.symmetric(horizontal=20, vertical=4),
            ),
            ft.Container(height=4),
            # Nav buttons
            ft.Container(
                content=ft.Column([
                    make_nav_button(k, i, l) for k, i, l in nav_items
                ], spacing=2),
                padding=ft.Padding.symmetric(horizontal=10),
            ),
            ft.Container(expand=True),
            ft.Divider(color=ft.Colors.with_opacity(0.15, "white"), height=1),
            # User info
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("US", size=13, weight=ft.FontWeight.BOLD, color="white"),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.25, "white"),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("Usuario", size=13, weight=ft.FontWeight.W_500, color="white"),
                        ft.Text("Plan Personal", size=11, color="#A5B4FC"),
                    ], spacing=0, expand=True),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_color=ft.Colors.with_opacity(0.7, "white"),
                        items=[
                            ft.PopupMenuItem(content=ft.Text("Mi Perfil"), icon=ft.Icons.PERSON_OUTLINE),
                            ft.PopupMenuItem(content=ft.Text("Cerrar Sesión"), icon=ft.Icons.LOGOUT, on_click=lambda _: logout()),
                        ]
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding.symmetric(horizontal=12, vertical=12),
            ),
        ], spacing=0, expand=True),
    )

    # ── Layout principal ───────────────────────────────────
    main_layout = ft.Row([
        sidebar,
        ft.VerticalDivider(width=1, color="#E5E7EB"),
        ft.Container(
            content=content_area,
            expand=True,
            bgcolor="#F7F8FA",
        ),
    ], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)

    def on_login(is_guest: bool):
        page.is_guest = is_guest
        page.controls.clear()
        page.add(main_layout)
        navigate("dashboard")

    def logout():
        page.is_guest = False
        page.controls.clear()
        page.add(LoginView(db, on_login))
        page.update()

    # Inicializar con Login
    page.add(LoginView(db, on_login))


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets") 
    # view=ft.AppView.WEB_BROWSER)