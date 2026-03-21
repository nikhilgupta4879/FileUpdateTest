"""
CanUDartMe — Flet entry point.
Runs on Web (browser), iOS, and Android from a single codebase.

  Web:      flet run --web app/main.py
  Desktop:  flet run app/main.py
  Mobile:   flet build apk / flet build ipa
"""
import flet as ft
from app.services.api_client import ApiClient
from app.pages.auth.login import build_login_page
from app.pages.auth.register import build_register_page
from app.pages.lobby.home import build_home_page
from app.pages.lobby.groups import build_groups_page
from app.pages.lobby.friends import build_friends_page
from app.pages.game.game_screen import build_game_page

# Shared API client (holds auth token in memory)
api = ApiClient()

# Runtime state (replace with proper state management as app grows)
_user_id: str = ""
_token: str = ""


async def main(page: ft.Page):
    page.title = "CanUDartMe"
    page.theme_mode = ft.ThemeMode.DARK
    page.adaptive = True   # adapts UI to iOS / Android / Web

    async def on_login_success():
        me = await api.get_me()
        global _user_id, _token
        _user_id = me["id"]
        _token = api._token
        page.go("/lobby")

    def on_join_session(session_id: str):
        page.go(f"/game/{session_id}")

    def on_session_created(session_id: str):
        page.go(f"/game/{session_id}")

    def route_change(e: ft.RouteChangeEvent):
        route = e.route
        page.views.clear()

        if route == "/register":
            page.views.append(build_register_page(page, api, on_login_success))
        elif route == "/lobby":
            page.views.append(build_home_page(page, api, on_join_session))
            page.views.append(
                ft.View("/lobby", controls=[
                    ft.NavigationBar(
                        destinations=[
                            ft.NavigationBarDestination(icon=ft.icons.HOME, label="Sessions"),
                            ft.NavigationBarDestination(icon=ft.icons.GROUP, label="Groups"),
                            ft.NavigationBarDestination(icon=ft.icons.PERSON_SEARCH, label="Friends"),
                        ],
                        on_change=lambda e: page.go(
                            ["/lobby", "/groups", "/friends"][e.control.selected_index]
                        ),
                    )
                ])
            )
        elif route == "/groups":
            page.views.append(build_groups_page(page, api, on_session_created))
        elif route == "/friends":
            page.views.append(build_friends_page(page, api, on_join_session))
        elif route.startswith("/game/"):
            sid = route.split("/game/")[1]
            page.views.append(build_game_page(page, api, sid, _user_id, _token))
        else:
            page.views.append(build_login_page(page, api, on_login_success))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top = page.views[-1]
        page.go(top.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")


ft.app(target=main, assets_dir="assets")
