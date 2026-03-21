"""
Lobby home — shows all active game sessions.
Favorite-group sessions are pinned to the top (sorted server-side).
"""
import flet as ft
from app.services.api_client import ApiClient


def build_home_page(page: ft.Page, api: ApiClient, on_join_session):
    sessions_list = ft.ListView(expand=True, spacing=8, padding=12)
    status_text = ft.Text("Loading sessions…", italic=True)

    async def refresh(e=None):
        status_text.value = "Refreshing…"
        page.update()
        try:
            sessions = await api.list_sessions()
            sessions_list.controls.clear()
            if not sessions:
                sessions_list.controls.append(ft.Text("No active sessions. Start one from your group!"))
            for s in sessions:
                is_fav = s.get("is_favorite", False)
                sessions_list.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.STAR if is_fav else ft.icons.SPORTS_BASEBALL,
                                color=ft.colors.AMBER if is_fav else ft.colors.BLUE_GREY,
                            ),
                            title=ft.Text(s["group_name"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(
                                f"Players: {s['player_count']}/{s['max_players']}  •  "
                                f"Round {s['current_round']}  •  {s['status'].upper()}"
                            ),
                            trailing=ft.ElevatedButton(
                                "Join",
                                on_click=lambda e, sid=s["id"]: on_join_session(sid),
                                disabled=s["player_count"] >= s["max_players"],
                            ),
                        )
                    )
                )
            status_text.value = f"{len(sessions)} session(s) found."
        except Exception as ex:
            status_text.value = f"Error: {ex}"
        page.update()

    page.run_task(refresh)

    return ft.View(
        "/lobby",
        controls=[
            ft.AppBar(
                title=ft.Text("Live Sessions"),
                actions=[ft.IconButton(ft.icons.REFRESH, on_click=refresh)],
            ),
            status_text,
            sessions_list,
        ],
    )
