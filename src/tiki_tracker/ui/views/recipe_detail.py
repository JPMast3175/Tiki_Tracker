"""Recipe detail view — full recipe with rating, favorite, QR, and CRUD."""

import threading
from pathlib import Path

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict, recipe_id: int) -> ft.View:
    recipe_service = services["recipe"]
    qr_service = services["qr"]

    recipe = recipe_service.get_by_id(recipe_id)
    if recipe is None:
        return ft.View(
            route=f"/recipe/{recipe_id}",
            controls=[ft.Text("Recipe not found.", color=T.TEXT)],
            appbar=T.app_bar("Not Found", page),
            bgcolor=T.BG,
        )

    in_stock_ids = services["inventory"].get_in_stock_ingredient_ids()

    # ── Mutable state ──────────────────────────────────────────────────────
    fav_icon_ref = ft.Ref[ft.Icon]()
    star_row_ref = ft.Ref[ft.Row]()
    _rating = [recipe.rating]
    _is_fav = [recipe.is_favorite]

    def toggle_favorite(_: ft.ControlEvent) -> None:
        _is_fav[0] = not _is_fav[0]
        recipe_service.set_favorite(recipe_id, _is_fav[0])
        if fav_icon_ref.current:
            fav_icon_ref.current.name = ft.Icons.FAVORITE if _is_fav[0] else ft.Icons.FAVORITE_OUTLINE
            fav_icon_ref.current.color = "#EF5350" if _is_fav[0] else T.TEXT
            page.update()

    def set_rating(new_rating: float) -> None:
        _rating[0] = new_rating
        recipe_service.set_rating(recipe_id, new_rating)
        _rebuild_stars()

    def _rebuild_stars() -> None:
        if star_row_ref.current:
            star_row_ref.current.controls = _make_star_controls()
            page.update()

    def _make_star_controls() -> list[ft.Control]:
        controls = []
        filled = int(round(_rating[0]))
        for i in range(5):
            star_num = i + 1
            controls.append(
                ft.IconButton(
                    icon=ft.Icons.STAR if i < filled else ft.Icons.STAR_OUTLINE,
                    icon_color=T.STAR_ON if i < filled else T.STAR_OFF,
                    icon_size=28,
                    on_click=lambda _, n=star_num: set_rating(float(n)),
                    tooltip=f"{star_num} star{'s' if star_num != 1 else ''}",
                )
            )
        return controls

    # ── QR dialog ─────────────────────────────────────────────────────────
    def show_qr(_: ft.ControlEvent) -> None:
        if not qr_service.is_available():
            T.snack(page, "QR code library not available.", error=True)
            return

        qr_path = qr_service.generate_recipe_qr(recipe)
        if qr_path is None:
            T.snack(page, "Failed to generate QR code.", error=True)
            return

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Share: {recipe.name}", color=T.TEXT),
            content=ft.Column(
                [
                    ft.Image(src=str(qr_path), width=220, height=220, fit=ft.ImageFit.CONTAIN),
                    ft.Text("Scan to import recipe", size=12, color=T.TEXT_DIM,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            bgcolor=T.SURFACE,
            actions=[
                ft.TextButton("Close", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(color=T.ACCENT)),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_delete_confirm(_: ft.ControlEvent) -> None:
        def do_delete(_: ft.ControlEvent) -> None:
            close_dlg(dlg)
            recipe_service.delete(recipe_id)
            T.snack(page, f'"{recipe.name}" deleted.')
            page.go("/recipes")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Recipe?", color=T.TEXT),
            content=ft.Text(
                f'Delete "{recipe.name}"? This cannot be undone.',
                color=T.TEXT_DIM,
            ),
            bgcolor=T.SURFACE,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(color=T.TEXT_DIM)),
                ft.TextButton("Delete", on_click=do_delete, style=ft.ButtonStyle(color=T.ERROR)),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dlg(dlg: ft.AlertDialog) -> None:
        dlg.open = False
        page.update()

    # ── Ingredient list ────────────────────────────────────────────────────
    def ingredient_row(ri) -> ft.Row:
        have = ri.ingredient_id in in_stock_ids
        return ft.Row(
            [
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE if have else ft.Icons.RADIO_BUTTON_UNCHECKED,
                    color=T.SUCCESS if have else T.TEXT_DIM,
                    size=16,
                ),
                ft.Container(width=8),
                ft.Text(ri.display, color=T.TEXT if have else T.TEXT_DIM, size=14, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    ingredients_col = ft.Column(
        [ingredient_row(ri) for ri in recipe.ingredients],
        spacing=8,
    )

    # ── Actions bar ────────────────────────────────────────────────────────
    action_buttons = [
        ft.IconButton(
            icon=ft.Icons.FAVORITE if _is_fav[0] else ft.Icons.FAVORITE_OUTLINE,
            icon_color="#EF5350" if _is_fav[0] else T.TEXT,
            ref=fav_icon_ref,
            tooltip="Toggle favorite",
            on_click=toggle_favorite,
        ),
        ft.IconButton(
            icon=ft.Icons.QR_CODE,
            icon_color=T.TEXT,
            tooltip="Share via QR",
            on_click=show_qr,
        ),
    ]
    if recipe.is_custom:
        action_buttons += [
            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_color=T.TEXT,
                tooltip="Edit recipe",
                on_click=lambda _: page.go(f"/edit_recipe/{recipe_id}"),
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=T.ERROR,
                tooltip="Delete recipe",
                on_click=show_delete_confirm,
            ),
        ]

    # ── Tags ──────────────────────────────────────────────────────────────
    tags_row = ft.Row(
        [
            ft.Container(
                content=ft.Text(tag, size=11, color=T.SECONDARY, weight=ft.FontWeight.W_600),
                bgcolor=T.SURFACE2,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
            for tag in recipe.tags
        ],
        wrap=True,
        spacing=6,
    ) if recipe.tags else ft.Container()

    content = ft.ListView(
        [
            # Header image placeholder
            ft.Container(
                height=200,
                bgcolor=T.PRIMARY_DARK,
                border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCAL_BAR, color=T.ACCENT, size=64),
                        ft.Text("🌴🍹🌴", size=28),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            ft.Container(height=12),
            ft.Container(
                content=ft.Column(
                    [
                        # Name + actions
                        ft.Row(
                            [
                                ft.Text(recipe.name, size=24, weight=ft.FontWeight.BOLD,
                                        color=T.TEXT, expand=True),
                                ft.Row(action_buttons, spacing=0),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Container(height=4),
                        # Meta row
                        ft.Row(
                            [
                                T.difficulty_badge(recipe.difficulty),
                                ft.Text(f"🕐 {recipe.prep_time} min", size=12, color=T.TEXT_DIM),
                                ft.Text(f"🥂 {recipe.glassware}" if recipe.glassware else "", size=12, color=T.TEXT_DIM),
                            ],
                            spacing=10,
                            wrap=True,
                        ),
                        ft.Container(height=8),
                        # Rating
                        ft.Row(
                            [
                                ft.Text("Rate: ", size=13, color=T.TEXT_DIM),
                                ft.Row(ref=star_row_ref, controls=_make_star_controls(), spacing=0),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),
                        tags_row,
                        ft.Container(height=12),
                        ft.Divider(color=T.DIVIDER),
                        ft.Container(height=8),
                        # Description
                        T.section_title("ABOUT"),
                        ft.Container(height=6),
                        ft.Text(recipe.description, size=14, color=T.TEXT_DIM),
                        ft.Container(height=16),
                        # Ingredients
                        T.section_title("INGREDIENTS"),
                        ft.Container(height=6),
                        ingredients_col,
                        ft.Container(height=16),
                        # Instructions
                        T.section_title("INSTRUCTIONS"),
                        ft.Container(height=6),
                        ft.Text(recipe.instructions, size=14, color=T.TEXT, selectable=True),
                        ft.Container(height=16),
                        # Garnish
                        ft.Container(
                            content=ft.Column([
                                T.section_title("GARNISH"),
                                ft.Container(height=6),
                                ft.Text(recipe.garnish, size=14, color=T.TEXT_DIM),
                            ]),
                            visible=bool(recipe.garnish),
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(height=32),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route=f"/recipe/{recipe_id}",
        controls=[content],
        appbar=ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=T.TEXT,
                on_click=lambda _: page.go("/recipes"),
            ),
            title=ft.Text(recipe.name, color=T.TEXT, size=16,
                          overflow=ft.TextOverflow.ELLIPSIS),
            bgcolor=T.PRIMARY_DARK,
            center_title=False,
        ),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
