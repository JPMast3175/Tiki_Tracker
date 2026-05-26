"""Recipe detail view — full recipe with polished hero, ingredients, and actions."""

import traceback
from pathlib import Path

import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict, recipe_id: int) -> ft.View:
    recipe_service    = services["recipe"]
    qr_service        = services["qr"]
    inventory_service = services["inventory"]

    recipe = recipe_service.get_by_id(recipe_id)
    if recipe is None:
        return ft.View(
            route=f"/recipe/{recipe_id}",
            controls=[ft.Text("Recipe not found.", color=T.TEXT)],
            appbar=T.app_bar("Not Found", page),
            bgcolor=T.BG,
        )

    in_stock_ids = inventory_service.get_in_stock_ingredient_ids()

    # ── Mutable state ──────────────────────────────────────────────────────
    fav_icon_ref  = ft.Ref[ft.Icon]()
    star_row_ref  = ft.Ref[ft.Row]()
    _rating       = [recipe.rating]
    _is_fav       = [recipe.is_favorite]

    def toggle_favorite(_: ft.ControlEvent) -> None:
        _is_fav[0] = not _is_fav[0]
        recipe_service.set_favorite(recipe_id, _is_fav[0])
        if fav_icon_ref.current:
            fav_icon_ref.current.name  = ft.Icons.FAVORITE if _is_fav[0] else ft.Icons.FAVORITE_OUTLINE
            fav_icon_ref.current.color = T.FAV_COLOR if _is_fav[0] else T.TEXT
            page.update()

    def set_rating(n: float) -> None:
        _rating[0] = n
        recipe_service.set_rating(recipe_id, n)
        if star_row_ref.current:
            star_row_ref.current.controls = _star_controls()
            page.update()

    def _star_controls() -> list[ft.Control]:
        filled = int(round(_rating[0]))
        return [
            ft.IconButton(
                icon=ft.Icons.STAR if i < filled else ft.Icons.STAR_OUTLINE,
                icon_color=T.STAR_ON if i < filled else T.STAR_OFF,
                icon_size=28,
                on_click=lambda _, n=i+1: set_rating(float(n)),
                tooltip=f"{i+1} star{'s' if i else ''}",
            )
            for i in range(5)
        ]

    # ── Dialogs ────────────────────────────────────────────────────────────
    def close_dlg(dlg: ft.AlertDialog) -> None:
        dlg.open = False
        page.update()

    def show_qr(_: ft.ControlEvent) -> None:
        if not qr_service.is_available():
            T.snack(page, "QR library not installed.", error=True)
            return
        qr_path = qr_service.generate_recipe_qr(recipe)
        if not qr_path:
            T.snack(page, "QR generation failed.", error=True)
            return
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Share: {recipe.name}", color=T.TEXT),
            content=ft.Column(
                [
                    ft.Image(src=str(qr_path), width=220, height=220,
                             fit=ft.ImageFit.CONTAIN),
                    ft.Text("Scan to import this recipe", size=12,
                            color=T.TEXT_DIM, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True,
            ),
            bgcolor=T.SURFACE,
            actions=[ft.TextButton("Close", on_click=lambda _: close_dlg(dlg),
                                   style=ft.ButtonStyle(color=T.GOLD))],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_delete(_: ft.ControlEvent) -> None:
        def do_delete(_: ft.ControlEvent) -> None:
            close_dlg(dlg)
            recipe_service.delete(recipe_id)
            T.snack(page, f'"{recipe.name}" deleted.')
            page.go("/recipes")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Recipe?", color=T.TEXT),
            content=ft.Text(f'Remove "{recipe.name}" permanently?', color=T.TEXT_DIM),
            bgcolor=T.SURFACE,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dlg(dlg),
                              style=ft.ButtonStyle(color=T.TEXT_DIM)),
                ft.TextButton("Delete", on_click=do_delete,
                              style=ft.ButtonStyle(color=T.ERROR)),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # ── Ingredient rows ────────────────────────────────────────────────────
    def ing_row(ri) -> ft.Container:
        have = ri.ingredient_id in in_stock_ids
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=6, height=6,
                        bgcolor=T.SUCCESS if have else T.SURFACE3,
                        border_radius=3,
                    ),
                    ft.Container(width=10),
                    ft.Text(ri.display, color=T.TEXT if have else T.TEXT_DIM,
                            size=14, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=0, right=0, top=6, bottom=6),
        )

    # ── Tags ──────────────────────────────────────────────────────────────
    tags_row = ft.Row(
        [
            ft.Container(
                content=ft.Text(tag, size=11, color=T.GOLD,
                                weight=ft.FontWeight.W_600),
                bgcolor=T.SURFACE2,
                border_radius=8,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            )
            for tag in recipe.tags
        ],
        wrap=True, spacing=6,
    ) if recipe.tags else ft.Container()

    # ── Action buttons ─────────────────────────────────────────────────────
    def icon_action(icon, color, tip, fn) -> ft.Container:
        return ft.Container(
            content=ft.Icon(icon, color=color, size=22),
            bgcolor=T.SURFACE2,
            border_radius=10,
            padding=10,
            tooltip=tip,
            on_click=fn,
            ink=True,
        )

    actions = [
        icon_action(
            ft.Icons.FAVORITE if _is_fav[0] else ft.Icons.FAVORITE_OUTLINE,
            T.FAV_COLOR if _is_fav[0] else T.TEXT,
            "Toggle favorite",
            toggle_favorite,
        ),
        icon_action(ft.Icons.QR_CODE_2, T.TEXT, "Share via QR", show_qr),
    ]
    if recipe.is_custom:
        actions += [
            icon_action(ft.Icons.EDIT_OUTLINED, T.GOLD, "Edit recipe",
                        lambda _: page.go(f"/edit_recipe/{recipe_id}")),
            icon_action(ft.Icons.DELETE_OUTLINE, T.ERROR, "Delete recipe", show_delete),
        ]

    # Patch the fav icon ref onto the first action's icon
    fav_icon_ref  # kept for toggle_favorite to update directly on the container
    # We'll update via set_attribute instead — rebuild the icon inside toggle_favorite
    # using a simpler approach: rebuild the whole action row (see toggle_favorite above)

    content = ft.ListView(
        [
            # ── Hero ──────────────────────────────────────────────────────
            ft.Container(
                height=240,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#0D3B0D", "#1E5C1E", "#0A2A0A"],
                ),
                content=ft.Stack(
                    [
                        ft.Container(
                            gradient=ft.RadialGradient(
                                center=ft.Alignment(0, -0.1),
                                radius=0.8,
                                colors=["#254CAF50", "#00000000"],
                            ),
                            expand=True,
                        ),
                        ft.Column(
                            [ft.Text("🌴 🍹 🌴", size=56,
                                     text_align=ft.TextAlign.CENTER)],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        ),
                        # Bottom fade
                        ft.Container(
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment(0, 0),
                                end=ft.Alignment(0, 1),
                                colors=["#00000000", T.BG],
                            ),
                            height=80, bottom=0, left=0, right=0,
                        ),
                    ]
                ),
            ),
            # ── Body ──────────────────────────────────────────────────────
            ft.Container(
                content=ft.Column(
                    [
                        # Name + actions
                        ft.Row(
                            [
                                ft.Text(recipe.name, size=26,
                                        weight=ft.FontWeight.BOLD, color=T.TEXT,
                                        expand=True),
                                ft.Row(actions, spacing=8),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Container(height=8),
                        # Meta chips
                        ft.Row(
                            [
                                T.difficulty_badge(recipe.difficulty),
                                T.meta_chip(ft.Icons.SCHEDULE, f"{recipe.prep_time} min"),
                                T.meta_chip(ft.Icons.LOCAL_DRINK,
                                            recipe.glassware) if recipe.glassware else ft.Container(),
                            ],
                            spacing=8, wrap=True,
                        ),
                        ft.Container(height=10),
                        # Rating
                        ft.Row(
                            [
                                ft.Text("Your rating:", size=13, color=T.TEXT_DIM),
                                ft.Row(ref=star_row_ref, controls=_star_controls(), spacing=0),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=6),
                        tags_row,
                        ft.Container(height=16),
                        ft.Container(height=1, bgcolor=T.DIVIDER),
                        ft.Container(height=16),

                        # About
                        T.section_title("ABOUT"),
                        ft.Container(height=8),
                        ft.Text(recipe.description, size=14, color=T.TEXT_DIM),
                        ft.Container(height=20),

                        # Ingredients
                        T.section_title("INGREDIENTS"),
                        ft.Container(height=8),
                        ft.Column(
                            [ing_row(ri) for ri in recipe.ingredients],
                            spacing=0,
                        ),
                        ft.Container(height=20),

                        # Instructions
                        T.section_title("INSTRUCTIONS"),
                        ft.Container(height=8),
                        ft.Container(
                            content=ft.Text(recipe.instructions, size=14,
                                            color=T.TEXT, selectable=True),
                            bgcolor=T.SURFACE,
                            border_radius=12,
                            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
                        ),
                        ft.Container(height=16),

                        # Garnish
                        ft.Container(
                            visible=bool(recipe.garnish),
                            content=ft.Column(
                                [
                                    T.section_title("GARNISH"),
                                    ft.Container(height=8),
                                    ft.Text(recipe.garnish, size=14, color=T.TEXT_DIM),
                                ],
                            ),
                        ),
                        ft.Container(height=40),
                    ],
                    spacing=0,
                ),
                padding=ft.Padding(left=18, right=18, top=16, bottom=0),
            ),
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
                          overflow=ft.TextOverflow.ELLIPSIS,
                          weight=ft.FontWeight.W_600),
            bgcolor=T.PRIMARY_DARK,
        ),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
