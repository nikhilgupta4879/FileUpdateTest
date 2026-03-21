"""
Friends page — find a player by profile name and see which session they're in.
"""
import flet as ft
from app.services.api_client import ApiClient


def build_friends_page(page: ft.Page, api: ApiClient, on_join_session):
    search_field = ft.TextField(label="Search by profile name", expand=True)
    result_card = ft.Card(visible=False)

    async def search(e):
        try:
            user = await api.find_friend(search_field.value.strip())
            result_card.content = ft.ListTile(
                leading=ft.CircleAvatar(content=ft.Text(user["profile_name"][0].upper())),
                title=ft.Text(user["profile_name"]),
                subtitle=ft.Text(f"Member since {user['created_at'][:10]}"),
                trailing=ft.ElevatedButton(
                    "Find & Join Session",
                    on_click=lambda e, uid=user["id"]: page.run_task(_join_friend_session, uid),
                ),
            )
            result_card.visible = True
        except Exception as ex:
            result_card.content = ft.ListTile(title=ft.Text(f"Not found: {ex}", color=ft.colors.RED))
            result_card.visible = True
        page.update()

    async def _join_friend_session(friend_id: str):
        """Find an active session where the friend is playing and join it."""
        try:
            sessions = await api.list_sessions()
            # TODO: filter sessions by friend_id presence (needs server-side endpoint)
            if sessions:
                on_join_session(sessions[0]["id"])
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Friend is not in any active session."))
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(str(ex)), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    return ft.View(
        "/friends",
        controls=[
            ft.AppBar(title=ft.Text("Find a Friend")),
            ft.Column([
                ft.Row([search_field, ft.IconButton(ft.icons.SEARCH, on_click=search)]),
                result_card,
            ], spacing=12, padding=16),
        ],
    )
