import flet as ft

try:
    ft.OutlinedButton(text="Hola")
except Exception as e:
    print(f"Error 1: {e}")

try:
    ft.OutlinedButton("Hola")
except Exception as e:
    print(f"Error 2: {e}")

try:
    b = ft.OutlinedButton()
    b.text = "Hola"
except Exception as e:
    print(f"Error 3: {e}")
