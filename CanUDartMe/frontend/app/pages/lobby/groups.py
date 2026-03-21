"""
Groups page — create, search, join groups and start a new session.
"""
import flet as ft
from app.services.api_client import ApiClient


def build_groups_page(page: ft.Page, api: ApiClient, on_session_created):
    search_field = ft.TextField(label="Search groups by name", expand=True)
    result_list = ft.ListView(expand=True, spacing=8, padding=12)
    new_group_field = ft.TextField(label="New group name", expand=True)

    async def search(e):
        result_list.controls.clear()
        try:
            groups = await api.search_groups(search_field.value)
            for g in groups:
                result_list.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(g["name"]),
                            subtitle=ft.Text(f"{g['member_count']} members"),
                            trailing=ft.Row([
                                ft.IconButton(
                                    ft.icons.STAR_BORDER,
                                    tooltip="Favorite",
                                    on_click=lambda e, gid=g["id"]: page.run_task(api.toggle_favorite, gid),
                                ),
                                ft.ElevatedButton(
                                    "Join",
                                    on_click=lambda e, gid=g["id"]: page.run_task(_join_group, gid),
                                ),
                            ]),
                        )
                    )
                )
        except Exception as ex:
            result_list.controls.append(ft.Text(f"Error: {ex}", color=ft.colors.RED))
        page.update()

    async def _join_group(group_id: str):
        try:
            await api.join_group(group_id)
            page.snack_bar = ft.SnackBar(ft.Text("Joined group!"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
        page.update()

    async def create_group(e):
        if not new_group_field.value.strip():
            return
        try:
            group = await api.create_group(new_group_field.value.strip())
            session = await api.create_session(group["id"])
            on_session_created(session["id"])
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    return ft.View(
        "/groups",
        controls=[
            ft.AppBar(title=ft.Text("Groups")),
            ft.Column([
                ft.Row([new_group_field,
                        ft.ElevatedButton("Create & Start", on_click=create_group)]),
                ft.Divider(),
                ft.Row([search_field,
                        ft.IconButton(ft.icons.SEARCH, on_click=search)]),
                result_list,
            ], expand=True, spacing=10, scroll=ft.ScrollMode.AUTO),
        ],
    )
