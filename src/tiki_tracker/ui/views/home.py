"""Home view — drink of the day, stats, and quick access."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    recipe_service = services["recipe"]
    suggestion_service = services["suggestion"]
    inventory_service = services["inventory"]

    suggestion = suggestion_service.get_drink_of_the_day()
    total_recipes = recipe_service.count()
    in_stock_count = inventory_service.count_in_stock()
    makeable = recipe_service.get_makeable()

    # ── Drink of the Day card ──────────────────────────────────────────────
    if suggestion:
        dotd_content = ft.Column(
            [
                T.section_title("DRINK OF THE DAY"),
                ft.Container(height=8),
                T.recipe_placeholder(),
                ft.Container(height=12),
                ft.Text(suggestion.name, size=22, weight=ft.FontWeight.BOLD, color=T.TEXT),
                ft.Text(
                    suggestion.description[:120] + "…" if len(suggestion.description) > 120 else suggestion.description,
                    size=13,
                    color=T.TEXT_DIM,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        T.stars(suggestion.rating),
                        ft.Container(width=8),
                        T.difficulty_badge(suggestion.difficulty),
                        ft.Container(width=8),
                        ft.Text(f"🕐 {suggestion.prep_time} min", size=12, color=T.TEXT_DIM),
                    ],
                    wrap=True,
                ),
                ft.Container(height=12),
                ft.ElevatedButton(
                    "View Recipe",
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=T.ACCENT,
                    color="white",
                    on_click=lambda _: page.go(f"/recipe/{suggestion.id}"),
                ),
            ],
            spacing=4,
        )
    else:
        dotd_content = ft.Column(
            [
                T.section_title("DRINK OF THE DAY"),
                ft.Container(height=16),
                ft.Text("Add some recipes to get started! 🌴", color=T.TEXT_DIM, size=14),
            ]
        )

    dotd_card = T.card(dotd_content, padding=20)

    # ── Quick stats ────────────────────────────────────────────────────────
    def stat_tile(icon: str, value: str, label: str, route: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, color=T.ACCENT, size=32),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=T.TEXT),
                    ft.Text(label, size=12, color=T.TEXT_DIM),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=T.SURFACE2,
            border_radius=12,
            padding=16,
            expand=True,
            on_click=lambda _: page.go(route),
            ink=True,
        )

    stats_row = ft.Row(
        [
            stat_tile(ft.Icons.LOCAL_BAR, str(total_recipes), "Recipes", "/recipes"),
            stat_tile(ft.Icons.INVENTORY_2, str(in_stock_count), "In Stock", "/inventory"),
        ],
        spacing=12,
    )

    # ── "Can make now" teaser ──────────────────────────────────────────────
    if makeable:
        names = ", ".join(r.name for r in makeable[:3])
        suffix = f" +{len(makeable) - 3} more" if len(makeable) > 3 else ""
        make_card = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=20),
                    ft.Container(width=8),
                    ft.Column(
                        [
                            ft.Text(
                                f"You can make {len(makeable)} drink{'s' if len(makeable) != 1 else ''}!",
                                size=14, weight=ft.FontWeight.BOLD, color=T.TEXT,
                            ),
                            ft.Text(names + suffix, size=12, color=T.TEXT_DIM),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=T.TEXT_DIM, size=14),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=T.SURFACE2,
            border_radius=12,
            padding=16,
            on_click=lambda _: page.go("/recipes"),
            ink=True,
        )
    else:
        make_card = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=T.TEXT_DIM, size=20),
                    ft.Container(width=8),
                    ft.Text(
                        "Add inventory items to see what you can make.",
                        size=13, color=T.TEXT_DIM,
                    ),
                ],
            ),
            bgcolor=T.SURFACE2,
            border_radius=12,
            padding=16,
        )

    content = ft.ListView(
        [
            ft.Container(height=4),
            dotd_card,
            ft.Container(height=16),
            T.section_title("YOUR BAR"),
            ft.Container(height=8),
            stats_row,
            ft.Container(height=12),
            make_card,
            ft.Container(height=24),
        ],
        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        spacing=0,
        expand=True,
    )

    return ft.View(
        route="/",
        controls=[content],
        appbar=T.app_bar("🌴 Tiki Tracker", page),
        navigation_bar=T.nav_bar(0, page),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
