import flet as ft
from frontend.dashboard import DashboardView
from frontend.facturas import FacturasView
from frontend.gastos import GastosView
from frontend.clientes import ClientesView
from frontend.fiscal import FiscalView
from frontend.informes import InformesView
from frontend.login import LoginView
from backend.database import Database

def main(page: ft.Page):
    page.title = "PyGestor - Autónomos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#F7F8FA"

    page.window_width = 1280
    page.window_height = 800
    page.window_min_width = 1100
    page.window_min_height = 700

    page.fonts = {
        "Inter": "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")

    db = Database()
    db.seed_demo_data()

    current_view = {"name": "dashboard"}
    content_area = ft.Container(expand=True)

    def navigate(view_name: str):
        current_view["name"] = view_name
        render_view(view_name)
        update_nav(view_name)
        page.update()

    def render_view(view_name: str):
        views = {
            "dashboard": lambda: DashboardView(db, navigate),
            "facturas":  lambda: FacturasView(db, navigate),
            "gastos":    lambda: GastosView(db, navigate),
            "clientes":  lambda: ClientesView(db, navigate),
            "fiscal":    lambda: FiscalView(db, navigate),
            "informes":  lambda: InformesView(db, navigate),
        }
        content_area.content = views.get(view_name, views["dashboard"])()
        page.update()

    # ── Nav items con iconos Material Design ───────────────
    nav_items = [
        ("dashboard", ft.Icons.DASHBOARD_OUTLINED,         "Dashboard"),
        ("facturas",  ft.Icons.RECEIPT_LONG_OUTLINED,      "Facturas"),
        ("gastos",    ft.Icons.PAYMENTS_OUTLINED,           "Gastos"),
        ("clientes",  ft.Icons.PEOPLE_OUTLINED,             "Clientes"),
        ("fiscal",    ft.Icons.ACCOUNT_BALANCE_OUTLINED,    "Fiscal / IVA"),
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
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("G", size=20, weight=ft.FontWeight.BOLD, color="white"),
                        width=42, height=42,
                        bgcolor=ft.Colors.with_opacity(0.22, "white"),
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("PyGestor", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("Autónomos", size=11, color="#A5B4FC"),
                    ], spacing=0),
                ], spacing=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=24),
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
                        content=ft.Text("AU", size=13, weight=ft.FontWeight.BOLD, color="white"),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.25, "white"),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("Autónomo", size=13, weight=ft.FontWeight.W_500, color="white"),
                        ft.Text("Pro Plan", size=11, color="#A5B4FC"),
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
    ], expand=True, spacing=0)

    def on_login(is_guest: bool):
        page.is_guest = is_guest
        page.controls.clear()
        page.add(main_layout)
        navigate("dashboard")

    def logout():
        page.is_guest = False
        page.controls.clear()
        page.add(LoginView(on_login))
        page.update()

    # Inicializar con Login
    page.add(LoginView(on_login))


if __name__ == "__main__":
    ft.app(target=main)