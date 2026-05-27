"""Recipes list view — searchable grid of polished recipe cards."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    recipe_service = services["recipe"]
    image_service  = services["image"]
    _search_value  = [""]
    grid_ref       = ft.Ref[ft.GridView]()

    def load_recipes(search: str = ""):
        return recipe_service.get_all(search=search)

    def recipe_card(recipe) -> ft.Container:
        return ft.Container(
            bgcolor=T.SURFACE,
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=14, color="#28000000", offset=ft.Offset(0, 4)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda _, rid=recipe.id: page.go(f"/recipe/{rid}"),
            ink=True,
            content=ft.Column(
                [
                    # ── Image area ──────────────────────────────────
                    ft.Container(
                        height=148,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Stack(
                            [
                                # Gradient placeholder
                                ft.Container(
                                    visible=not bool(image_service.get_image_src(recipe.id)),
                                    expand=True,
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(-1, -1),
                                        end=ft.Alignment(1, 1),
                                        colors=["#1A5218", "#0E3410"],
                                    ),
                                    content=ft.Column(
                                        [ft.Icon(ft.Icons.LOCAL_BAR,
                                                 color="#80C9A227", size=44)],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                ),
                                # Actual image
                                ft.Image(
                                    src=image_service.get_image_src(recipe.id) or "",
                                    visible=bool(image_service.get_image_src(recipe.id)),
                                    fit=ft.BoxFit.COVER,
                                    width=float("inf"),
                                    height=148,
                                    error_content=ft.Container(
                                        expand=True, bgcolor=T.SURFACE2),
                                ),
                                # Difficulty badge — top-left
                                ft.Container(
                                    T.difficulty_badge(recipe.difficulty),
                                    left=8, top=8,
                                ),
                                # Favorite — top-right
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.FAVORITE if recipe.is_favorite
                                        else ft.Icons.FAVORITE_OUTLINE,
                                        color=T.FAV_COLOR if recipe.is_favorite
                                        else "#60FFFFFF",
                                        size=18,
                                    ),
                                    right=8, top=8,
                                ),
                                # Bottom gradient fade into card
                                ft.Container(
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(0, 0),
                                        end=ft.Alignment(0, 1),
                                        colors=["#00000000", T.SURFACE],
                                    ),
                                    height=48,
                                    bottom=0, left=0, right=0,
                                ),
                            ]
                        ),
                    ),
                    # ── Card info ───────────────────────────────────
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
                                ft.Container(height=4),
                                ft.Row(
                                    [
                                        T.stars(recipe.rating, size=12),
                                        ft.Container(expand=True),
                                        ft.Icon(ft.Icons.SCHEDULE,
                                                size=11, color=T.TEXT_DIM),
                                        ft.Text(f" {recipe.prep_time}m",
                                                size=11, color=T.TEXT_DIM),
                                    ],
                                ),
                                ft.Text(
                                    recipe.glassware or "",
                                    size=11,
                                    color=T.TEXT_DIM,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=ft.Padding(left=12, right=12, top=10, bottom=12),
                    ),
                ],
                spacing=0,
            ),
        )

    def on_search(e: ft.ControlEvent) -> None:
        _search_value[0] = e.control.value or ""
        recipes = load_recipes(search=_search_value[0])
        if grid_ref.current:
            grid_ref.current.controls = (
                [recipe_card(r) for r in recipes]
                if recipes else [_empty_grid_label()]
            )
            page.update()

    def _empty_grid_label() -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SEARCH_OFF, color=T.TEXT_DIM, size=48),
                    ft.Text("No recipes found.", color=T.TEXT_DIM, size=14),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment(0, 0),
            padding=40,
        )

    search_field = ft.TextField(
        hint_text="Search recipes…",
        hint_style=ft.TextStyle(color=T.TEXT_DIM),
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=T.SURFACE,
        border_color=T.SURFACE3,
        focused_border_color=T.GOLD,
        color=T.TEXT,
        cursor_color=T.GOLD,
        border_radius=12,
        on_change=on_search,
        expand=True,
    )

    initial_recipes = load_recipes()
    initial_controls = (
        [recipe_card(r) for r in initial_recipes]
        if initial_recipes else [_empty_grid_label()]
    )

    grid = ft.GridView(
        ref=grid_ref,
        controls=initial_controls,
        runs_count=2,
        max_extent=300,
        child_aspect_ratio=0.72,
        spacing=14,
        run_spacing=14,
        expand=True,
        padding=0,
    )

    content = ft.Column(
        [
            ft.Container(
                content=search_field,
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
            ),
            ft.Container(
                content=grid,
                padding=ft.Padding(left=16, right=16, top=0, bottom=16),
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
            tooltip="Add custom recipe",
        ),
        scroll=ft.ScrollMode.HIDDEN,
    )
