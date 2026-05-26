"""Recipes list view — searchable, filterable grid of recipe cards."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    recipe_service = services["recipe"]

    search_query = ft.Ref[str]()
    _search_value = [""]

    def load_recipes(search: str = "") -> list:
        return recipe_service.get_all(search=search)

    def recipe_card(recipe) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    # Image area
                    ft.Container(
                        height=120,
                        bgcolor=T.PRIMARY_DARK,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10),
                        content=ft.Stack(
                            [
                                ft.Column(
                                    [
                                        ft.Icon(ft.Icons.LOCAL_BAR, color=T.ACCENT, size=36),
                                        ft.Text("🌴", size=18),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.FAVORITE if recipe.is_favorite else ft.Icons.FAVORITE_OUTLINE,
                                        color="#EF5350" if recipe.is_favorite else T.TEXT_DIM,
                                        size=18,
                                    ),
                                    right=8, top=8,
                                ),
                                ft.Container(
                                    content=T.difficulty_badge(recipe.difficulty),
                                    left=8, top=8,
                                ),
                            ],
                        ),
                    ),
                    # Card body
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    recipe.name,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=T.TEXT,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Row(
                                    [
                                        T.stars(recipe.rating, size=13),
                                        ft.Text(
                                            f"  {recipe.prep_time}m",
                                            size=11,
                                            color=T.TEXT_DIM,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                ft.Text(
                                    recipe.glassware or "—",
                                    size=11,
                                    color=T.TEXT_DIM,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
                    ),
                ],
                spacing=0,
            ),
            bgcolor=T.SURFACE,
            border_radius=10,
            on_click=lambda _, rid=recipe.id: page.go(f"/recipe/{rid}"),
            ink=True,
            animate=ft.animation.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    # ── Search bar ─────────────────────────────────────────────────────────
    grid_ref = ft.Ref[ft.GridView]()

    def on_search(e: ft.ControlEvent) -> None:
        _search_value[0] = e.control.value or ""
        refresh_grid()

    def refresh_grid() -> None:
        recipes = load_recipes(search=_search_value[0])
        if grid_ref.current:
            grid_ref.current.controls = [recipe_card(r) for r in recipes]
            if not recipes:
                grid_ref.current.controls = [
                    ft.Container(
                        ft.Text("No recipes found. Try a different search.", color=T.TEXT_DIM, size=14),
                        alignment=ft.alignment.center,
                        padding=40,
                        col={"xs": 12},
                    )
                ]
            page.update()

    search_field = ft.TextField(
        hint_text="Search recipes…",
        hint_style=ft.TextStyle(color=T.TEXT_DIM),
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=T.SURFACE,
        border_color=T.SECONDARY,
        focused_border_color=T.ACCENT,
        color=T.TEXT,
        border_radius=10,
        on_change=on_search,
        expand=True,
    )

    initial_recipes = load_recipes()

    grid = ft.GridView(
        ref=grid_ref,
        controls=[recipe_card(r) for r in initial_recipes],
        runs_count=2,
        max_extent=220,
        child_aspect_ratio=0.75,
        spacing=12,
        run_spacing=12,
        expand=True,
        padding=0,
    )

    if not initial_recipes:
        grid.controls = [
            ft.Container(
                ft.Text("No recipes yet. Add one with the + button!", color=T.TEXT_DIM, size=14),
                alignment=ft.alignment.center,
                padding=40,
            )
        ]

    content = ft.Column(
        [
            ft.Container(
                content=ft.Row([search_field]),
                padding=ft.padding.only(left=16, right=16, top=12, bottom=8),
            ),
            ft.Container(
                content=grid,
                padding=ft.padding.symmetric(horizontal=16),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route="/recipes",
        controls=[content],
        appbar=T.app_bar("Recipes", page),
        navigation_bar=T.nav_bar(1, page),
        bgcolor=T.BG,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=T.ACCENT,
            on_click=lambda _: page.go("/add_recipe"),
            tooltip="Add recipe",
        ),
        scroll=ft.ScrollMode.HIDDEN,
    )
