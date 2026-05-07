import flet as ft
from frontend.dashboard import DashboardView
from frontend.facturas import FacturasView
from frontend.gastos import GastosView
from frontend.clientes import ClientesView
from frontend.fiscal import FiscalView
from frontend.informes import InformesView
from backend.database import Database

def main(page: ft.Page):
    page.title = "GestorPro - Autónomos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#F8FAFC"
    
    # Configuración de ventana (Sintaxis moderna)
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

    # Estado de navegación
    current_view = {"name": "dashboard"}

    # Contenedor principal del contenido
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

    # ── NAV items ──────────────────────────────────────────
    nav_items = [
        ("dashboard", "📊", "Dashboard"),
        ("facturas",  "🧾", "Facturas"),
        ("gastos",    "💸", "Gastos"),
        ("clientes",  "👥", "Clientes"),
        ("fiscal",    "📋", "Fiscal / IVA"),
        ("informes",  "📈", "Informes"),
    ]

    nav_buttons = {}

    def make_nav_button(key, icon, label):
        btn = ft.Container(
            content=ft.Row([
                ft.Text(icon, size=18),
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color="white"),
            ], spacing=12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
            on_click=lambda e, k=key: navigate(k),
            ink=True,
            # CORRECCIÓN: ft.Colors (Mayúscula) y sintaxis de opacidad
            bgcolor=ft.Colors.with_opacity(0, "white"),
        )
        nav_buttons[key] = btn
        return btn

    def update_nav(active: str):
        for key, btn in nav_buttons.items():
            btn.bgcolor = (
                ft.Colors.with_opacity(0.2, "white")
                if key == active
                else ft.Colors.with_opacity(0, "white")
            )
        page.update()

    # ── Sidebar ────────────────────────────────────────────
    sidebar = ft.Container(
        width=230,
        bgcolor="#1E3A5F",
        content=ft.Column([
            # Logo
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("G", size=22, weight=ft.FontWeight.BOLD, color="white"),
                        width=42, height=42,
                        bgcolor=ft.Colors.with_opacity(0.25, "white"),
                        border_radius=12,
                        # CORRECCIÓN: alignment.center es un objeto, no un atributo dinámico
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("GestorPro", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("Autónomos", size=11, color="#93C5FD"),
                    ], spacing=0),
                ], spacing=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=24),
            ),
            ft.Divider(color=ft.Colors.with_opacity(0.2, "white"), height=1),
            ft.Container(height=8),
            # Nav buttons
            ft.Container(
                content=ft.Column([
                    make_nav_button(k, i, l) for k, i, l in nav_items
                ], spacing=4),
                padding=ft.Padding.symmetric(horizontal=12),
            ),
            ft.Container(expand=True),
            ft.Divider(color=ft.Colors.with_opacity(0.2, "white"), height=1),
            # User info
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("AU", size=13, weight=ft.FontWeight.BOLD, color="white"),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.3, "white"),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("Autónomo", size=13, weight=ft.FontWeight.W_500, color="white"),
                        ft.Text("Pro Plan", size=11, color="#93C5FD"),
                    ], spacing=0),
                ], spacing=10),
                padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            ),
        ], spacing=0, expand=True),
    )

    # ── Layout principal ───────────────────────────────────
    page.add(
        ft.Row([
            sidebar,
            ft.VerticalDivider(width=1, color="#E2E8F0"),
            ft.Container(
                content=content_area,
                expand=True,
                bgcolor="#F8FAFC",
            ),
        ], expand=True, spacing=0)
    )

    navigate("dashboard")

# CORRECCIÓN: Usar ft.app con target para mayor estabilidad en versiones recientes
if __name__ == "__main__":
    ft.app(target=main)