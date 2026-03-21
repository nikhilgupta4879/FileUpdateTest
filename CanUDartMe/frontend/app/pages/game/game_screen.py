"""
Main game screen — adapts based on whether the current player is:
  - The THROWER: sees a list of active opponents to tap and throw a dart at
  - The TARGET:  sees the DartBoardWidget and must tap a region to catch
  - A SPECTATOR: sees the scoreboard and live action
"""
import asyncio
import flet as ft
from app.services.api_client import ApiClient
from app.services.websocket_client import GameWebSocketClient
from app.components.dart_board_widget import DartBoardWidget
from app.components.scoreboard import Scoreboard


class GameScreen(ft.UserControl):
    def __init__(self, page: ft.Page, api: ApiClient, session_id: str, user_id: str, token: str):
        super().__init__()
        self.page = page
        self.api = api
        self.session_id = session_id
        self.user_id = user_id

        self._players: list[dict] = []
        self._is_target = False
        self._travel_time = 2.0

        # Subcomponents
        self._scoreboard = Scoreboard([])
        self._dart_board = DartBoardWidget(on_catch=self._handle_catch, enabled=False)
        self._status_text = ft.Text("Waiting for game to start…", size=16)
        self._opponents_list = ft.ListView(spacing=8)
        self._round_text = ft.Text("Round 1 / 3", size=18, weight=ft.FontWeight.BOLD)

        # WebSocket
        self._ws = GameWebSocketClient(session_id, token, on_event=self._on_ws_event)

    def did_mount(self):
        asyncio.create_task(self._ws.connect())

    def will_unmount(self):
        asyncio.create_task(self._ws.disconnect())

    def build(self):
        return ft.Column([
            self._round_text,
            ft.Divider(),
            self._status_text,
            # Dart board (visible when this player is targeted)
            ft.Container(content=self._dart_board, alignment=ft.alignment.center, visible=False,
                         key="board_container"),
            # Opponents to throw at
            ft.Container(
                content=ft.Column([
                    ft.Text("Tap a player to throw your dart:", weight=ft.FontWeight.W_600),
                    self._opponents_list,
                ]),
                key="throw_container",
                visible=False,
            ),
            ft.Divider(),
            ft.Text("Scoreboard", weight=ft.FontWeight.BOLD),
            self._scoreboard,
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    # ------------------------------------------------------------------ #
    # WebSocket event handler                                               #
    # ------------------------------------------------------------------ #
    async def _on_ws_event(self, event: str, payload: dict):
        if event == "player_joined":
            self._status_text.value = f"🎯 {payload['profile_name']} joined!"

        elif event == "dart_thrown":
            self._travel_time = payload.get("travel_time", 2.0)
            thrower = payload["thrower_id"]
            target = payload["target_id"]

            if target == self.user_id:
                # This player is the target — activate board
                self._is_target = True
                self._status_text.value = "🎯 Incoming dart! TAP THE BOARD!"
                self._dart_board.set_enabled(True, self._travel_time)
                self._show_board(True)
            else:
                self._status_text.value = (
                    f"Dart in flight: {thrower[:6]}… → {target[:6]}…  ({self._travel_time}s)"
                )

        elif event in ("dart_caught", "dart_missed"):
            self._is_target = False
            self._dart_board.set_enabled(False)
            self._show_board(False)
            self._update_scoreboard(payload.get("scoreboard", []))
            msg = "✅ Caught!" if event == "dart_caught" else "💨 Missed!"
            pts = payload.get("points", 0)
            self._status_text.value = f"{msg}  +{pts} pts"

        elif event == "game_over":
            winner = next((p for p in payload.get("scoreboard", []) if p.get("is_winner")), None)
            self._status_text.value = f"🏆 Game Over! Winner: {winner['profile_name'] if winner else '?'}"
            self._update_scoreboard(payload.get("scoreboard", []))

        elif event == "player_left":
            self._status_text.value = f"Player {payload['user_id'][:8]} left."

        elif event == "error":
            self._status_text.value = f"⚠️ {payload.get('detail', 'Unknown error')}"

        self.update()

    async def _handle_catch(self, region: str):
        await self._ws.catch_dart(region)

    async def _handle_throw(self, target_id: str):
        await self._ws.throw_dart(target_id)

    def _update_scoreboard(self, players: list[dict]):
        self._players = players
        self._scoreboard.update_players(players)
        self._refresh_opponents()

    def _refresh_opponents(self):
        self._opponents_list.controls.clear()
        for p in self._players:
            if p["user_id"] == self.user_id or p.get("is_eliminated"):
                continue
            self._opponents_list.controls.append(
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.CircleAvatar(content=ft.Text(p["profile_name"][0].upper())),
                        ft.Text(p["profile_name"]),
                    ]),
                    on_click=lambda e, tid=p["user_id"]: asyncio.create_task(self._handle_throw(tid)),
                )
            )

    def _show_board(self, visible: bool):
        for c in self.controls:
            if hasattr(c, "key"):
                if c.key == "board_container":
                    c.visible = visible
                elif c.key == "throw_container":
                    c.visible = not visible


def build_game_page(page: ft.Page, api: ApiClient, session_id: str, user_id: str, token: str) -> ft.View:
    screen = GameScreen(page, api, session_id, user_id, token)
    return ft.View(
        f"/game/{session_id}",
        controls=[
            ft.AppBar(title=ft.Text("CanUDartMe — In Game"),
                      leading=ft.IconButton(ft.icons.EXIT_TO_APP, on_click=lambda _: page.go("/lobby"))),
            screen,
        ],
    )
