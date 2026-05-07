"""
Paleta de colores, constantes de diseño y
helpers de componentes reutilizables para GestorPro.
"""
import flet as ft

# ── Colores ────────────────────────────────────────────────
COLORS = {
    "primary":        "#2563EB",
    "primary_dark":   "#1D4ED8",
    "sidebar_bg":     "#1E3A5F",
    "bg":             "#F8FAFC",
    "surface":        "#FFFFFF",
    "border":         "#E2E8F0",
    "text_primary":   "#1E293B",
    "text_secondary": "#64748B",
    "text_muted":     "#94A3B8",
    "success":        "#22C55E",
    "success_bg":     "#DCFCE7",
    "success_text":   "#166534",
    "danger":         "#EF4444",
    "danger_bg":      "#FEE2E2",
    "danger_text":    "#991B1B",
    "warning_bg":     "#FEF9C3",
    "warning_text":   "#854D0E",
    "info":           "#3B82F6",
    # Gradientes simulados (color principal de cada tarjeta stat)
    "stat1":  "#6366F1",
    "stat2":  "#10B981",
    "stat3":  "#F43F5E",
    "stat4":  "#06B6D4",
}

CAT_LABELS = {
    "oficina":    ("🖊️", "Oficina"),
    "software":   ("💻", "Software"),
    "marketing":  ("📢", "Marketing"),
    "transporte": ("🚗", "Transporte"),
    "formacion":  ("📚", "Formación"),
    "seguro":     ("🛡️", "Seguro"),
    "otros":      ("📦", "Otros"),
}

MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

# ── Helpers de componentes ─────────────────────────────────

def card(content, padding=20, radius=16, expand=False, width=None) -> ft.Container:
    """Tarjeta blanca con sombra suave."""
    return ft.Container(
        content=content,
        bgcolor=COLORS["surface"],
        border_radius=radius,
        padding=padding,
        border=ft.border.all(1, COLORS["border"]),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=8,
            color=ft.Colors.with_opacity(0.06, "black"),
            offset=ft.Offset(0, 2),
        ),
        expand=expand,
        width=width,
    )

def stat_card(title, value, subtitle, color, icon):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ft.Text(value, size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ft.Text(subtitle, size=11, color=ft.Colors.with_opacity(0.7, "white")),
        ], spacing=4),
        bgcolor=color,
        padding=ft.Padding.all(20),
        border_radius=ft.BorderRadius.all(12),
        # Usa el objeto Alignment con mayúscula
        alignment=ft.Alignment(0, 0) 
    )

def btn_primary(text, on_click=None, icon=None, width=None):
    # En lugar de usar text e icon como propiedades, creamos el contenido interno
    # Esto evita el conflicto de "icon must be specified together with content"
    inner_content = ft.Row(
        [
            ft.Icon(icon) if icon else ft.Container(),
            ft.Text(str(text), weight=ft.FontWeight.BOLD)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
        tight=True
    )

    btn = ft.ElevatedButton(
        content=inner_content, # Usamos content directamente
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    return btn

def btn_danger(text: str, on_click=None) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=COLORS["danger"],
            side=ft.BorderSide(1, COLORS["danger"]),
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

def btn_secondary(text, on_click=None, icon=None, width=None):
    btn = ft.OutlinedButton() # Constructor vacío
    btn.text = str(text)      # Asignación manual
    btn.on_click = on_click
    btn.icon = icon
    btn.width = width
    
    btn.style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8),
        color=ft.Colors.BLUE,
    )
    return btn

def badge(text: str, kind: str = "default") -> ft.Container:
    """kind: 'success' | 'danger' | 'warning' | 'info' | 'default'"""
    palettes = {
        "success": (COLORS["success_bg"],  COLORS["success_text"]),
        "danger":  (COLORS["danger_bg"],   COLORS["danger_text"]),
        "warning": (COLORS["warning_bg"],  COLORS["warning_text"]),
        "info":    ("#DBEAFE",             "#1E40AF"),
        "default": ("#F1F5F9",             COLORS["text_secondary"]),
    }
    bg, fg = palettes.get(kind, palettes["default"])
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=fg),
        bgcolor=bg, border_radius=8,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )

def section_header(title: str, subtitle: str = "") -> ft.Column:
    children = [ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=COLORS["text_primary"])]
    if subtitle:
        children.append(ft.Text(subtitle, size=13, color=COLORS["text_secondary"]))
    return ft.Column(children, spacing=2)

def divider() -> ft.Divider:
    return ft.Divider(color=COLORS["border"], height=1)

def text_field(label: str, hint: str = "", value: str = "",
               keyboard_type=ft.KeyboardType.TEXT,
               on_change=None, password=False, expand=False) -> ft.TextField:
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

def dropdown(label, options, value=None, on_change=None):
    # 1. Creamos el control básico con solo lo indispensable
    dd = ft.Dropdown(
        label=label,
        value=value,
        # Importante: Las opciones deben ser objetos ft.dropdown.Option
        options=[ft.dropdown.Option(key=str(k), text=str(t)) for k, t in options],
        # Usamos Mayúsculas para evitar los DeprecationWarnings
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=4),
        border_radius=ft.BorderRadius.all(8),
        focused_border_color=ft.Colors.BLUE,
    )
    
    # 2. Asignamos el evento después de la creación para evitar el TypeError en el __init__
    if on_change is not None:
        dd.on_change = on_change
        
    return dd

def snack(page: ft.Page, msg: str, ok: bool = True):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(msg, color="white"),
        bgcolor=COLORS["success"] if ok else COLORS["danger"],
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()

def page_wrapper(content) -> ft.Container:
    """Envuelve el contenido de una vista con scroll y padding."""
    return ft.Container(
        content=ft.Column(
            controls=[content] if not isinstance(content, list) else content,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        expand=True,
        padding=ft.Padding.all(28),
    )