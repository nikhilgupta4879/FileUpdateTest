import flet as ft
from app.services.api_client import ApiClient


def build_register_page(page: ft.Page, api: ApiClient, on_success):
    profile_field = ft.TextField(label="Profile Name (visible to others)")
    email_field = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True)
    error_text = ft.Text(color=ft.colors.RED_400, visible=False)

    async def handle_register(e):
        error_text.visible = False
        try:
            resp = await api.register(profile_field.value, email_field.value, password_field.value)
            api.set_token(resp["access_token"])
            await on_success()
        except Exception as ex:
            error_text.value = f"Registration failed: {ex}"
            error_text.visible = True
        page.update()

    return ft.View(
        "/register",
        controls=[
            ft.AppBar(title=ft.Text("CanUDartMe — Register")),
            ft.Column(
                controls=[
                    ft.Text("Create Your Account", size=28, weight=ft.FontWeight.BOLD),
                    profile_field,
                    email_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton("Register", on_click=handle_register, width=300),
                    ft.TextButton("Already have an account? Login", on_click=lambda _: page.go("/login")),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        ],
    )
