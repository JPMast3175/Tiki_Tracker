"""Home view — premium hero DOTD card, stats, and can-make banner."""

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    suggestion_service = services["suggestion"]
    recipe_service     = services["recipe"]
    inventory_service  = services["inventory"]
    image_service      = services["image"]

    suggestion     = suggestion_service.get_drink_of_the_day()
    total_recipes  = recipe_service.count()
    in_stock_count = inventory_service.count_in_stock()
    makeable       = recipe_service.get_makeable()

    # ── Drink of the Day hero card ─────────────────────────────────────────
    def dotd_card() -> ft.Container:
        if suggestion is None:
            return T.card(
                ft.Column([
                    T.section_title("DRINK OF THE DAY"),
                    ft.Container(height=12),
                    ft.Text("Add some recipes to get started! 🌴",
                            color=T.TEXT_DIM, size=14),
                ])
            )

        dotd_img_src = image_service.get_image_src(suggestion.id)
        return ft.Container(
            bgcolor=T.SURFACE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=24, color="#33000000", offset=ft.Offset(0, 6)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(
                [
                    # ── Hero image area ──────────────────────────────
                    ft.Container(
                        height=220,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Stack(
                            [
                                # Gradient placeholder (hidden when image exists)
                                ft.Container(
                                    visible=not bool(dotd_img_src),
                                    expand=True,
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(-1, -1),
                                        end=ft.Alignment(1, 1),
                                        colors=["#0D3B0D", "#1E5C1E", "#0D2E0D"],
                                    ),
                                    content=ft.Stack(
                                        [
                                            ft.Container(
                                                gradient=ft.RadialGradient(
                                                    center=ft.Alignment(0, -0.2),
                                                    radius=0.75,
                                                    colors=["#254CAF50", "#00000000"],
                                                ),
                                                expand=True,
                                            ),
                                            ft.Column(
                                                [ft.Text("🌴 🍹 🌴", size=50,
                                                         text_align=ft.TextAlign.CENTER)],
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                expand=True,
                                            ),
                                        ]
                                    ),
                                ),
                                # Actual drink image
                                ft.Image(
                                    src=dotd_img_src or "",
                                    visible=bool(dotd_img_src),
                                    fit=ft.BoxFit.COVER,
                                    width=float("inf"),
                                    height=220,
                                    error_content=ft.Container(
                                        expand=True, bgcolor=T.SURFACE2),
                                ),
                                # "DRINK OF THE DAY" pill — top-left
                                ft.Container(
                                    content=ft.Text(
                                        "DRINK OF THE DAY",
                                        size=10,
                                        color=T.BG,
                                        weight=ft.FontWeight.BOLD,
                                        style=ft.TextStyle(letter_spacing=1.5),
                                    ),
                                    bgcolor=T.GOLD,
                                    border_radius=6,
                                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                    left=14, top=14,
                                ),
                                # Favorite heart — top-right (if favorited)
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.FAVORITE if suggestion.is_favorite
                                        else ft.Icons.FAVORITE_OUTLINE,
                                        color=T.FAV_COLOR if suggestion.is_favorite
                                        else "#80FFFFFF",
                                        size=20,
                                    ),
                                    right=14, top=14,
                                ),
                                # Bottom gradient fade
                                ft.Container(
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(0, 0),
                                        end=ft.Alignment(0, 1),
                                        colors=["#00000000", T.SURFACE],
                                    ),
                                    height=60,
                                    bottom=0,
                                    left=0, right=0,
                                ),
                            ]
                        ),
                    ),
                    # ── Card body ────────────────────────────────────
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(suggestion.name, size=24,
                                        weight=ft.FontWeight.BOLD, color=T.TEXT),
                                ft.Container(height=4),
                                ft.Row(
                                    [
                                        T.stars(suggestion.rating, size=15),
                                        ft.Container(width=8),
                                        T.difficulty_badge(suggestion.difficulty),
                                        ft.Container(width=6),
                                        T.meta_chip(ft.Icons.SCHEDULE, f"{suggestion.prep_time} min"),
                                    ],
                                    wrap=True, spacing=4,
                                ),
                                ft.Container(height=8),
                                ft.Text(
                                    (suggestion.description[:110] + "…")
                                    if len(suggestion.description) > 110
                                    else suggestion.description,
                                    size=13, color=T.TEXT_DIM,
                                ),
                                ft.Container(height=14),
                                ft.ElevatedButton(
                                    "View Recipe",
                                    icon=ft.Icons.ARROW_FORWARD,
                                    bgcolor=T.ACCENT,
                                    color="white",
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                                    ),
                                    on_click=lambda _: page.go(f"/recipe/{suggestion.id}"),
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=ft.Padding(left=18, right=18, top=14, bottom=18),
                    ),
                ],
                spacing=0,
            ),
        )

    # ── Stats row ──────────────────────────────────────────────────────────
    def stat_card(icon: str, value: str, label: str, route: str,
                  color: str = T.ACCENT) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=T.SURFACE,
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=12, color="#22000000", offset=ft.Offset(0, 3)),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            on_click=lambda _: page.go(route),
            ink=True,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=26),
                        bgcolor=T.SURFACE2,
                        border_radius=12,
                        padding=10,
                        width=48, height=48,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=10),
                    ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=T.TEXT),
                    ft.Text(label, size=11, color=T.TEXT_DIM),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    stats_row = ft.Row(
        [
            stat_card(ft.Icons.LOCAL_BAR, str(total_recipes), "Recipes", "/recipes"),
            stat_card(ft.Icons.INVENTORY_2, str(in_stock_count), "In Stock", "/inventory",
                      color=T.SUCCESS),
        ],
        spacing=12,
    )

    # ── Can make now banner ────────────────────────────────────────────────
    if makeable:
        names = ", ".join(r.name for r in makeable[:3])
        extra = f"  +{len(makeable)-3} more" if len(makeable) > 3 else ""
        make_banner = ft.Container(
            bgcolor=T.SURFACE,
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=12, color="#22000000", offset=ft.Offset(0, 3)),
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            on_click=lambda _: page.go("/recipes"),
            ink=True,
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=22),
                        bgcolor=T.SURFACE2,
                        border_radius=10,
                        padding=8,
                    ),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(
                                f"You can make {len(makeable)} drink{'s' if len(makeable)!=1 else ''}!",
                                size=14, weight=ft.FontWeight.BOLD, color=T.TEXT,
                            ),
                            ft.Text(names + extra, size=11, color=T.TEXT_DIM),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=T.TEXT_DIM, size=18),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
    else:
        make_banner = ft.Container(
            bgcolor=T.SURFACE,
            border_radius=14,
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY_2_OUTLINED,
                                        color=T.TEXT_DIM, size=22),
                        bgcolor=T.SURFACE2,
                        border_radius=10, padding=8,
                    ),
                    ft.Container(width=12),
                    ft.Text("Add inventory to see what you can make.",
                            size=13, color=T.TEXT_DIM, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    content = ft.ListView(
        [
            ft.Container(height=12),
            ft.Container(dotd_card(), padding=ft.Padding(left=16, right=16, top=0, bottom=0)),
            ft.Container(height=20),
            ft.Container(
                T.section_title("YOUR BAR"),
                padding=ft.Padding(left=20, right=16, top=0, bottom=8),
            ),
            ft.Container(
                content=stats_row,
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
            ),
            ft.Container(height=12),
            ft.Container(
                content=make_banner,
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
            ),
            ft.Container(height=24),
        ],
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
