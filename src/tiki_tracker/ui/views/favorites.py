"""Favorites view — favorite drinks sorted by rating with polished cards."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    recipe_service = services["recipe"]

    favorites = sorted(
        recipe_service.get_all(favorites_only=True),
        key=lambda r: r.rating,
        reverse=True,
    )

    def fav_card(recipe) -> ft.Container:
        return ft.Container(
            bgcolor=T.SURFACE,
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=12, color="#22000000", offset=ft.Offset(0, 3)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda _, rid=recipe.id: page.go(f"/recipe/{rid}"),
            ink=True,
            content=ft.Row(
                [
                    # Gradient image strip
                    ft.Container(
                        width=80,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                            colors=["#1A5218", "#0E3410"],
                        ),
                        content=ft.Column(
                            [ft.Icon(ft.Icons.LOCAL_BAR, color="#80C9A227", size=30)],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    # Info
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=14, right=12, top=14, bottom=14),
                        content=ft.Column(
                            [
                                ft.Text(recipe.name, size=16,
                                        weight=ft.FontWeight.BOLD, color=T.TEXT,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Container(height=4),
                                ft.Row(
                                    [
                                        T.stars(recipe.rating, size=14),
                                        ft.Container(width=8),
                                        T.difficulty_badge(recipe.difficulty),
                                    ],
                                    spacing=0,
                                ),
                                ft.Container(height=4),
                                ft.Text(recipe.glassware or "", size=11,
                                        color=T.TEXT_DIM),
                            ],
                            spacing=0,
                        ),
                    ),
                    # Chevron
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHEVRON_RIGHT,
                                        color=T.TEXT_DIM, size=20),
                        padding=ft.Padding(left=0, right=14, top=0, bottom=0),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    if favorites:
        body_controls: list[ft.Control] = [
            ft.Container(height=12),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.FAVORITE, color=T.FAV_COLOR, size=16),
                        ft.Container(width=6),
                        ft.Text(
                            f"{len(favorites)} favorite drink{'s' if len(favorites)!=1 else ''}",
                            size=13, color=T.TEXT_DIM,
                        ),
                    ],
                ),
                padding=ft.Padding(left=20, right=16, top=0, bottom=8),
            ),
        ]
        for recipe in favorites:
            body_controls.append(
                ft.Container(
                    fav_card(recipe),
                    padding=ft.Padding(left=16, right=16, top=4, bottom=4),
                )
            )
        body_controls.append(ft.Container(height=24))
    else:
        body_controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.FAVORITE_OUTLINE,
                                            color=T.TEXT_DIM, size=64),
                            bgcolor=T.SURFACE,
                            border_radius=50,
                            padding=20,
                        ),
                        ft.Container(height=20),
                        ft.Text("No favorites yet!", size=20, color=T.TEXT,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=6),
                        ft.Text("Open a recipe and tap ❤️ to add it here.",
                                size=14, color=T.TEXT_DIM,
                                text_align=ft.TextAlign.CENTER),
                        ft.Container(height=24),
                        ft.ElevatedButton(
                            "Browse Recipes",
                            icon=ft.Icons.LOCAL_BAR,
                            bgcolor=T.ACCENT, color="white",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                            ),
                            on_click=lambda _: page.go("/recipes"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=40,
            )
        ]

    return ft.View(
        route="/favorites",
        controls=[ft.ListView(body_controls, expand=True, spacing=0)],
        appbar=T.app_bar("Favorites", page),
        navigation_bar=T.nav_bar(3, page),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
