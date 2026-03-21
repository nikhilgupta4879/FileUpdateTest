"""
Portable dart board — displayed on the TARGET player's screen.
Three concentric circular tap zones: inner (30pts) / middle (20pts) / outer (10pts).
Player must tap within the travel time window.
"""
import flet as ft
from app.utils.constants import REGION_COLORS, REGION_POINTS


class DartBoardWidget(ft.UserControl):
    def __init__(self, on_catch, enabled: bool = False):
        super().__init__()
        self.on_catch = on_catch     # async callback(region: str)
        self.enabled = enabled
        self._countdown_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.RED)

    def build(self):
        def _make_zone(label: str, region: str, size: float):
            return ft.GestureDetector(
                content=ft.Container(
                    width=size, height=size,
                    border_radius=size / 2,
                    bgcolor=REGION_COLORS[region],
                    border=ft.border.all(3, ft.colors.WHITE),
                    content=ft.Text(
                        f"{label}\n{REGION_POINTS[region]}pts",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    alignment=ft.alignment.center,
                ),
                on_tap=lambda e, r=region: self._tapped(r),
            )

        return ft.Stack(
            controls=[
                _make_zone("OUTER", "outer", 220),
                ft.Container(
                    content=ft.Stack(controls=[
                        _make_zone("MIDDLE", "middle", 140),
                        ft.Container(
                            content=_make_zone("INNER", "inner", 70),
                            alignment=ft.alignment.center,
                        ),
                    ]),
                    alignment=ft.alignment.center,
                    width=220, height=220,
                ),
                ft.Container(
                    content=self._countdown_text,
                    alignment=ft.alignment.top_center,
                    top=0,
                ),
            ],
            width=220, height=240,
        )

    def _tapped(self, region: str):
        if self.enabled and self.on_catch:
            import asyncio
            asyncio.create_task(self.on_catch(region))

    def set_enabled(self, enabled: bool, countdown: float = 0):
        self.enabled = enabled
        self._countdown_text.value = f"⏱ {countdown:.1f}s" if enabled else ""
        self.update()
