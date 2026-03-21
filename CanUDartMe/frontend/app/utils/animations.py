"""
Animation helpers for dart throw and catch effects using Flet's animation API.
"""
import flet as ft
import asyncio


async def animate_dart_throw(
    page: ft.Page,
    dart_control: ft.Control,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    travel_time: float = 2.0,
):
    """
    Animates the dart image from thrower position to target position.
    Uses Flet's AnimatedPositioned or Transform.
    """
    dart_control.left = start_x
    dart_control.top = start_y
    page.update()

    dart_control.animate_position = ft.animation.Animation(
        int(travel_time * 1000), ft.AnimationCurve.EASE_IN_OUT
    )
    dart_control.left = end_x
    dart_control.top = end_y
    page.update()
    await asyncio.sleep(travel_time)


async def flash_hit(page: ft.Page, control: ft.Control, color: str = "#E53935"):
    """Brief color flash to indicate a dart hit."""
    original = control.bgcolor
    control.bgcolor = color
    page.update()
    await asyncio.sleep(0.3)
    control.bgcolor = original
    page.update()
