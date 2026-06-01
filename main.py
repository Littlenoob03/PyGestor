import flet as ft
from frontend.dashboard import VistaDashboard
from frontend.ingresos import VistaIngresos
from frontend.gastos import VistaGastos
from frontend.informes import VistaInformes
from frontend.formulario_ingreso import VistaFormularioIngreso
from frontend.formulario_gasto import VistaFormularioGasto
from frontend.login import VistaLogin
from frontend.perfil import VistaPerfil
from backend.database import Database

def main(page: ft.Page):
    """
    Función principal que arranca la aplicación PyGestor.
    
    EXPLICACIÓN FUNCIONES DE FLET Y COLORS:
    1. ft.Page: Es la ventana de la aplicación. Nos permite poner un título, cambiar el color de fondo y actualizar lo que se ve.
    2. ft.Container: Es como una "caja" donde metemos cosas. Le podemos dar color de fondo, redondearle los bordes o hacerla más grande.
    3. ft.Column / ft.Row: Sirven para ordenar esas cajas. 'Column' las pone en lista de arriba a abajo, y 'Row' las pone en fila de izquierda a derecha.
    4. ft.Text / ft.Image / ft.Icon: Sirven para mostrar texto, fotos e iconos decorativos.
    5. COLORS: Aunque no es de Flet, es un diccionario propio donde guardamos nuestros colores favoritos para no tener que escribirlos todo el rato (ej: COLORS["primary"]).
    6. ft.app(): Es el motor que enciende la aplicación y la muestra en la pantalla de nuestro ordenador.
    """
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
    db.cuenta_admin()

    current_view = {"name": "dashboard"}
    content_area = ft.Container(expand=True)

    def navegar(view_name: str, **kwargs):
        """Se encarga de cambiar la pantalla que estamos viendo, borrando lo anterior y poniendo el nuevo contenido."""
        current_view["name"] = view_name
        cargar_vista(view_name, **kwargs)
        actualizar_menu(view_name)
        if page.width < 768 and 'sidebar_container' in locals() and sidebar_container.offset.x == 0:
            alternar_barra_lateral(None)
        page.update()

    def cargar_vista(view_name: str, **kwargs):
        """Prepara y dibuja la sección de la app que el usuario ha pedido ver."""
        views = {
            "dashboard": lambda: VistaDashboard(db, navegar),
            "ingresos":  lambda: VistaIngresos(db, navegar),
            "gastos":    lambda: VistaGastos(db, navegar),
            "informes":  lambda: VistaInformes(db, navegar),
            "form_ingreso": lambda: VistaFormularioIngreso(db, navegar, **kwargs),
            "form_gasto":   lambda: VistaFormularioGasto(db, navegar, **kwargs),
            "perfil":       lambda: VistaPerfil(db, navegar, actualizar_barra_lateral),
        }
        content_area.content = views.get(view_name, views["dashboard"])()
        page.update()

    #ICONOS CON MATERIAL DESING
    nav_items = [
        ("dashboard", ft.Icons.DASHBOARD_OUTLINED,         "Dashboard"),
        ("ingresos",  ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, "Ingresos"),
        ("gastos",    ft.Icons.PAYMENTS_OUTLINED,           "Gastos"),
        ("informes",  ft.Icons.BAR_CHART_OUTLINED,          "Informes"),
    ]

    nav_buttons = {}

    def boton_sidebar(key, icon, label):
        """Crea un botón para usarlo en el menú de la izquierda."""
        btn = ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=18, color="white"),
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color="white"),
            ], spacing=12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=13),
            border_radius=12,
            on_click=lambda e, k=key: navegar(k),
            ink=True,
            bgcolor=ft.Colors.with_opacity(0, "white"),
        )
        nav_buttons[key] = btn
        return btn

    def actualizar_menu(active: str):
        """Pinta el botón del menú de otro color para que sepamos en qué pantalla estamos."""
        for key, btn in nav_buttons.items():
            if key == active:
                btn.bgcolor = ft.Colors.with_opacity(0.18, "white")
                row = btn.content
                row.controls[0].color = "#A5B4FC"
            else:
                btn.bgcolor = ft.Colors.with_opacity(0, "white")
                row = btn.content
                row.controls[0].color = "white"
        page.update()

    #SIDEBAR
    sidebar = ft.Container(
        width=235,
        bgcolor="#0F1729",
        content=ft.Column([
            #LOGO
            ft.Container(
                content=ft.Image(src="banner.jpg", width=180, fit=ft.BoxFit.CONTAIN),
                padding=ft.Padding.symmetric(horizontal=20, vertical=20),
                alignment=ft.Alignment(-1, 0),
            ),
            ft.Divider(color=ft.Colors.with_opacity(0.15, "white"), height=1),
            ft.Container(height=8),
            #ETIQUETA DE SECCION
            ft.Container(
                content=ft.Text("MENÚ PRINCIPAL", size=10,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.with_opacity(0.45, "white")),
                padding=ft.Padding.symmetric(horizontal=20, vertical=4),
            ),
            ft.Container(height=4),
            #BOTONES DE REDIRECCION ( GASTOS, INGRESOS, INFORMES Y DASHBOARD)
            ft.Container(
                content=ft.Column([
                    boton_sidebar(k, i, l) for k, i, l in nav_items
                ], spacing=2),
                padding=ft.Padding.symmetric(horizontal=10),
            ),
            ft.Container(expand=True),
            ft.Divider(color=ft.Colors.with_opacity(0.15, "white"), height=1),
        ], spacing=0, expand=True),
    )

    sidebar_initials = ft.Text("US", size=13, weight=ft.FontWeight.BOLD, color="white")
    sidebar_avatar_container = ft.Container(
        content=sidebar_initials,
        width=36, height=36,
        bgcolor=ft.Colors.with_opacity(0.25, "white"),
        border_radius=18,
        alignment=ft.Alignment(0, 0),
    )
    sidebar_image = ft.Image(src="", width=36, height=36, fit=ft.BoxFit.COVER, border_radius=18, visible=False)
    
    sidebar_username = ft.Text("Usuario", size=13, weight=ft.FontWeight.W_500, color="white")
    sidebar_plan = ft.Text("Plan Personal", size=11, color="#A5B4FC")

    def actualizar_barra_lateral():
        """Actualiza el menú de la izquierda para mostrar nuestra foto y nombre si hemos iniciado sesión."""
        if not db.current_user_id:
            sidebar_initials.value = "?"
            sidebar_username.value = "Desconectado"
            sidebar_plan.value = "Sin cuenta"
            sidebar_avatar_container.visible = True
            sidebar_image.visible = False
        else:
            u = db.get_usser_by_id(db.current_user_id)
            if u:
                sidebar_username.value = u.get("username", "Usuario")
                sidebar_plan.value = u.get("plan", "Plan Personal")
                if u.get("foto"):
                    sidebar_image.src = f"imagenes/{u.get('foto')}"
                    sidebar_image.visible = True
                    sidebar_avatar_container.visible = False
                else:
                    sidebar_initials.value = sidebar_username.value[:2].upper()
                    sidebar_image.visible = False
                    sidebar_avatar_container.visible = True
        page.update()

    #INFO USUARIO
    ft_user_info = ft.Container(
        content=ft.Row([
            ft.Stack([sidebar_avatar_container, sidebar_image]),
            ft.Column([
                sidebar_username,
                sidebar_plan,
            ], spacing=0, expand=True),
            ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                icon_color=ft.Colors.with_opacity(0.7, "white"),
                items=[
                    ft.PopupMenuItem(content=ft.Text("Mi Perfil"), icon=ft.Icons.PERSON_OUTLINE, on_click=lambda _: navegar("perfil")),
                    ft.PopupMenuItem(content=ft.Text("Cerrar Sesión"), icon=ft.Icons.LOGOUT, on_click=lambda _: cerrar_sesion()),
                ]
            ),
        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.symmetric(horizontal=12, vertical=12),
    )

    sidebar.content.controls.append(ft_user_info)

    #SIDEBAR RESPONSIVE
    overlay_bg = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.4, "black"),
        expand=True,
        visible=False,
        on_click=lambda e: alternar_barra_lateral(e)
    )
    
    sidebar_container = ft.Container(
        content=sidebar,
        width=235,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(300, "decelerate"),
    )
    
    def alternar_barra_lateral(e):
        """Abre o cierra el menú de la izquierda cuando estamos en movil."""
        if sidebar_container.offset.x == -1:
            sidebar_container.offset.x = 0
            overlay_bg.visible = True
        else:
            sidebar_container.offset.x = -1
            overlay_bg.visible = False
        page.update()

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=alternar_barra_lateral, icon_color="black"),
        title=ft.Text("PyGestor", color="black", weight=ft.FontWeight.BOLD),
        bgcolor="white",
        visible=False,
    )

    sidebar_spacer = ft.Container(width=235, visible=True)

    #LAYOUT
    main_layout = ft.Stack([
        ft.Row([
            sidebar_spacer,
            ft.Container(
                content=content_area,
                expand=True,
                bgcolor="#F7F8FA",
            ),
        ], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
        overlay_bg,
        sidebar_container,
    ], expand=True)

    def redimensionar_pagina(e):
        """Detecta si la ventana del programa se hace grande o pequeña y ajusta el menú para que encaje bien."""
        if page.width < 768:
            sidebar_spacer.visible = False
            page.appbar.visible = True
            if not overlay_bg.visible:
                sidebar_container.offset.x = -1
        else:
            sidebar_spacer.visible = True
            page.appbar.visible = False
            sidebar_container.offset.x = 0
            overlay_bg.visible = False
        page.update()

    page.on_resize = redimensionar_pagina

    def iniciar_sesion(user_id: int):
        """Se ejecuta cuando introducimos bien el usuario y contraseña. Carga el menú principal y nos deja entrar."""
        db.current_user_id = user_id
        actualizar_barra_lateral()
        page.controls.clear()
        page.add(main_layout)
        navegar("dashboard")
        redimensionar_pagina(None)

    def cerrar_sesion():
        """Borra nuestra información temporal y nos devuelve a la pantalla para poner la contraseña."""
        db.current_user_id = None
        page.controls.clear()
        page.add(VistaLogin(db, iniciar_sesion))
        page.update()

    page.logout = cerrar_sesion

    #INICIALIZAR CON LOGIN
    page.add(VistaLogin(db, iniciar_sesion))


if __name__ == "__main__":
    # ft.app(target=main, assets_dir="assets") PARA ARRANCAR LA APP EN FORMATO APP EN VEZ DE NAVEGADOR
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER)