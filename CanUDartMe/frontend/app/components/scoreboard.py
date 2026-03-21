import flet as ft


class Scoreboard(ft.UserControl):
    def __init__(self, players: list[dict]):
        super().__init__()
        self.players = players

    def build(self):
        return ft.Column(
            controls=[self._player_row(p) for p in self.players],
            spacing=4,
        )

    def _player_row(self, p: dict) -> ft.Control:
        strikes = p.get("strikes", 0)
        strike_icons = "".join(["❌" if i < strikes else "○" for i in range(3)])
        return ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    content=ft.Text(p["profile_name"][0].upper()),
                    bgcolor=ft.colors.BLUE_GREY_700 if not p.get("is_eliminated") else ft.colors.RED_900,
                    radius=18,
                ),
                ft.Column([
                    ft.Text(p["profile_name"], weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(strike_icons, size=11),
                ], spacing=0),
                ft.Container(expand=True),
                ft.Text(f"{p.get('score', 0)} pts", weight=ft.FontWeight.BOLD, size=16),
            ]),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
            opacity=0.5 if p.get("is_eliminated") else 1.0,
        )

    def update_players(self, players: list[dict]):
        self.players = players
        self.update()
