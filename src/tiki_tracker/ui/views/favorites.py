"""Favorites view — favorite drinks sorted by rating."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    recipe_service = services["recipe"]

    favorites = recipe_service.get_all(favorites_only=True)
    favorites.sort(key=lambda r: r.rating, reverse=True)

    def fav_card(recipe) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    # Left: placeholder image
                    ft.Container(
                        width=72,
                        height=72,
                        bgcolor=T.PRIMARY_DARK,
                        border_radius=10,
                        content=ft.Column(
                            [ft.Icon(ft.Icons.LOCAL_BAR, color=T.ACCENT, size=28)],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(recipe.name, size=16, weight=ft.FontWeight.BOLD, color=T.TEXT),
                            ft.Text(recipe.glassware or "—", size=12, color=T.TEXT_DIM),
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    T.stars(recipe.rating, size=15),
                                    ft.Container(width=6),
                                    T.difficulty_badge(recipe.difficulty),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=T.TEXT_DIM, size=14),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=T.SURFACE,
            border_radius=12,
            padding=12,
            on_click=lambda _, rid=recipe.id: page.go(f"/recipe/{rid}"),
            ink=True,
        )

    if favorites:
        controls: list[ft.Control] = [
            ft.Container(height=8),
            ft.Container(
                content=ft.Text(
                    f"❤️ {len(favorites)} favorite drink{'s' if len(favorites) != 1 else ''}",
                    size=13, color=T.TEXT_DIM,
                ),
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
            ),
            ft.Container(height=8),
        ] + [
            ft.Container(fav_card(r), padding=ft.Padding(left=16, right=16, top=4, bottom=4))
            for r in favorites
        ] + [ft.Container(height=24)]
    else:
        controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.FAVORITE_OUTLINE, color=T.TEXT_DIM, size=64),
                        ft.Container(height=16),
                        ft.Text("No favorites yet!", size=18, color=T.TEXT,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Open a recipe and tap ❤️ to add it here.",
                            size=14, color=T.TEXT_DIM, text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Browse Recipes",
                            icon=ft.Icons.LOCAL_BAR,
                            bgcolor=T.ACCENT, color="white",
                            on_click=lambda _: page.go("/recipes"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment(0, 0),
                padding=40,
                expand=True,
            )
        ]

    list_view = ft.ListView(controls=controls, expand=True, spacing=0)

    return ft.View(
        route="/favorites",
        controls=[list_view],
        appbar=T.app_bar("Favorites", page),
        navigation_bar=T.nav_bar(3, page),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
