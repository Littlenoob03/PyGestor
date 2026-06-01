import flet as ft

# COLORES
COLORS = {
    "primary":        "#1E1977",
    "primary_dark":   "#131054",
    "sidebar_bg":     "#0F1729",
    "bg":             "#F7F8FA",
    "surface":        "#FFFFFF",
    "border":         "#E5E7EB",
    "text_primary":   "#111827",
    "text_secondary": "#6B7280",
    "text_muted":     "#9CA3AF",
    "success":        "#059669",
    "success_bg":     "#D1FAE5",
    "success_text":   "#065F46",
    "danger":         "#DC2626",
    "danger_bg":      "#FEE2E2",
    "danger_text":    "#991B1B",
    "warning_bg":     "#FFFBEB",
    "warning_text":   "#92400E",
    "info":           "#1E1977",
    "stat1":  "#3B82F6",
    "stat2":  "#10B981",
    "stat3":  "#8B5CF6",
    "stat4":  "#F59E0B",
}

# COLORES DEGRADADOS O GRADIANTES
GRADIENTS = [
    ("#3B82F6", "#2563EB"),
    ("#8B5CF6", "#6D28D9"),
    ("#10B981", "#059669"),
    ("#F59E0B", "#D97706"),
]

# COLORES PARA GRAFICOS
CHART_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B",
    "#DC2626", "#14B8A6", "#8B5CF6",
    "#06B6D4", "#F97316",
]

CAT_LABELS = {
    "oficina":      ("🖊️", "Oficina"),
    "software":     ("💻", "Software"),
    "marketing":    ("📢", "Marketing"),
    "transporte":   ("🚗", "Transporte"),
    "formacion":    ("📚", "Formación"),
    "seguro":       ("🛡️", "Seguro"),
    "alimentacion": ("🛒", "Alimentación"),
    "ocio":         ("🍿", "Ocio"),
    "salud":        ("🏥", "Salud"),
    "vehiculo":     ("🚙", "Vehículo"),
    "otros":        ("📦", "Otros"),
}

MESES = ["Ene","Feb","Mar","Abr","May","Jun",
         "Jul","Ago","Sep","Oct","Nov","Dic"]


# HELPRES

def tarjeta(content, padding=20, radius=16, expand=False, width=None) -> ft.Container:
    """Crea un recuadro blanco con una pequeña sombra para que parezca que flota en la pantalla."""
    return ft.Container(
        content=content,
        bgcolor=COLORS["surface"],
        border_radius=radius,
        padding=padding,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=24,
            color=ft.Colors.with_opacity(0.07, "black"),
            offset=ft.Offset(0, 4),
        ),
        expand=expand,
        width=width,
    )

# COLORES DE LAS TARJETAS INFORMATIVAS
def tarjetas_informativas(title: str, value: str, subtitle: str,
                       grad_a: str, grad_b: str,
                       icon=None) -> ft.Container:
    """Crea las tarjetas de colores que vemos en la pantalla principal con los totales de ingresos y gastos."""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(title, size=12,
                            color=ft.Colors.with_opacity(0.85, "white"),
                            weight=ft.FontWeight.W_500),
                    ft.Text(value, size=26,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, size=11,
                            color=ft.Colors.with_opacity(0.7, "white")),
                ], spacing=5, expand=True),
                ft.Container(
                    content=ft.Icon(
                        icon or ft.Icons.SHOW_CHART,
                        color=ft.Colors.with_opacity(0.35, "white"),
                        size=32,
                    ),
                    width=52, height=52,
                    bgcolor=ft.Colors.with_opacity(0.18, "white"),
                    border_radius=14,
                    alignment=ft.Alignment(0, 0),
                ),
            ], spacing=12),
        ], spacing=0),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[grad_a, grad_b],
        ),
        padding=ft.Padding.all(20),
        border_radius=ft.BorderRadius.all(16),
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color=ft.Colors.with_opacity(0.28, grad_a),
            offset=ft.Offset(0, 6),
        ),
    )


def tarjeta_stat(title, value, subtitle, color, icon):
    """Crea una tarjeta de color básico apoyándose en las tarjetas de colores de arriba."""
    return tarjetas_informativas(title, value, subtitle, color, color)


def btn_primario(text, on_click=None, icon=None, width=None):
    """Crea un botón normal, relleno de color y con el texto en blanco, ideal para la acción principal."""
    inner = ft.Row(
        [
            ft.Icon(icon, size=16, color="white") if icon else ft.Container(),
            ft.Text(str(text), weight=ft.FontWeight.BOLD, color="white"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
        tight=True,
    )
    return ft.ElevatedButton(
        content=inner,
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=COLORS["primary"],
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=0,
        ),
    )


def btn_aviso(text: str, on_click=None) -> ft.OutlinedButton:
    """Crea un botón rojo, usado para avisar de peligro, como cuando vas a borrar algo."""
    return ft.OutlinedButton(
        content=ft.Text(text),
        on_click=on_click,
        style=ft.ButtonStyle(
            color=COLORS["danger"],
            side=ft.BorderSide(1, COLORS["danger"]),
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )


def btn_secundario(text, on_click=None, icon=None, width=None):
    """Crea un botón transparente que solo tiene el borde de color, para acciones que no son la principal."""
    inner_controls = []
    if icon:
        inner_controls.append(ft.Icon(icon, size=16, color=COLORS["primary"]))
    inner_controls.append(ft.Text(str(text), weight=ft.FontWeight.BOLD, color=COLORS["primary"]))
    
    inner = ft.Row(
        inner_controls,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
        tight=True,
    )
    
    return ft.OutlinedButton(
        content=inner,
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            color=COLORS["primary"],
        )
    )


def etiqueta(text: str, kind: str = "default") -> ft.Container:
    """Crea un pequeñO check de color para marcar si algo está 'Cobrado' o 'Pendiente'."""
    palettes = {
        "success": (COLORS["success_bg"],  COLORS["success_text"]),
        "danger":  (COLORS["danger_bg"],   COLORS["danger_text"]),
        "warning": (COLORS["warning_bg"],  COLORS["warning_text"]),
        "info":    ("#DBEAFE",             "#1E40AF"),
        "default": ("#F7F8FA",             COLORS["text_secondary"]),
    }
    bg, fg = palettes.get(kind, palettes["default"])
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=fg),
        bgcolor=bg,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


def cabecera(title: str, subtitle: str = "") -> ft.Column:
    """Crea los títulos grandes que vemos al principio de cada pantalla."""
    children = [
        ft.Text(title, size=24, weight=ft.FontWeight.BOLD,
                color=COLORS["text_primary"]),
    ]
    if subtitle:
        children.append(ft.Text(subtitle, size=13, color=COLORS["text_secondary"]))
    return ft.Column(children, spacing=2)


def separador() -> ft.Divider:
    """Dibuja una fina línea horizontal gris para separar secciones visualmente."""
    return ft.Divider(color=COLORS["border"], height=1)


def campo_texto(label: str, hint: str = "", value: str = "",
               keyboard_type=ft.KeyboardType.TEXT,
               on_change=None, password=False, expand=False) -> ft.TextField:
    """Crea los recuadros donde escribimos texto en los formularios (como al añadir un gasto)."""
    return ft.TextField(
        label=label, hint_text=hint, value=value,
        keyboard_type=keyboard_type,
        password=password,
        expand=expand,
        on_change=on_change,
        border_radius=12,
        border_color=COLORS["border"],
        focused_border_color=COLORS["primary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text_secondary"], size=13),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
    )


def desplegable(label, options, value=None, on_change=None):
    """Crea una cajita donde puedes pinchar y se despliega una lista de opciones para elegir."""
    dd = ft.Dropdown(
        label=label,
        value=value,
        options=[ft.desplegable.Option(key=str(k), text=str(t)) for k, t in options],
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=4),
        border_radius=ft.BorderRadius.all(12),
        focused_border_color=ft.Colors.BLUE,
    )
    if on_change is not None:
        dd.on_change = on_change
    return dd


def notificacion(page: ft.Page, msg: str, ok: bool = True):
    """Muestra un pequeño aviso en la parte de abajo de la pantalla que desaparece solo (en verde si todo ha ido bien, rojo si hay error)."""
    sb = ft.SnackBar(
        content=ft.Text(msg, color="white"),
        bgcolor=COLORS["success"] if ok else COLORS["danger"],
        duration=3000,
        open=True,
    )
    page.overlay.append(sb)
    page.update()


def vista_adaptable(content) -> ft.Container:
    """Hace que el contenido de la pantalla se adapte al tamaño de la ventana y añade la barra para bajar si la página es muy larga."""
    return ft.Container(
        content=ft.Column(
            controls=[content] if not isinstance(content, list) else content,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        expand=True,
        padding=ft.Padding.all(28),
    )