"""Inventory view — manage bar supplies with search, filter, and in-stock toggle."""

import flet as ft
from tiki_tracker.models.ingredient import CATEGORIES
from tiki_tracker.models.inventory import UNITS
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict) -> ft.View:
    inventory_service = services["inventory"]

    _search = [""]
    _category = ["All"]
    list_ref = ft.Ref[ft.ListView]()

    def load_items():
        return inventory_service.get_all_inventory(
            search=_search[0],
            category="" if _category[0] == "All" else _category[0],
        )

    def refresh_list() -> None:
        if list_ref.current:
            items = load_items()
            list_ref.current.controls = build_list_controls(items)
            page.update()

    def toggle_stock(inv_id: int, current: bool, switch: ft.Switch) -> None:
        new_val = not current
        inventory_service.toggle_stock(inv_id, new_val)
        switch.value = new_val
        page.update()

    def delete_item(inv_id: int) -> None:
        inventory_service.remove_from_inventory(inv_id)
        refresh_list()
        T.snack(page, "Item removed from inventory.")

    def build_list_controls(items) -> list[ft.Control]:
        if not items:
            return [
                ft.Container(
                    ft.Text("No inventory items found. Tap + to add some!", color=T.TEXT_DIM, size=14),
                    alignment=ft.Alignment(0, 0),
                    padding=40,
                )
            ]

        controls: list[ft.Control] = []
        current_cat = None
        for item in items:
            if item.category != current_cat:
                current_cat = item.category
                controls.append(
                    ft.Container(
                        ft.Text(current_cat.upper(), size=11, color=T.ACCENT,
                                weight=ft.FontWeight.BOLD,
                                style=ft.TextStyle(letter_spacing=1.2)),
                        padding=ft.Padding(left=4, right=0, top=12, bottom=4),
                    )
                )

            sw = ft.Switch(
                value=item.in_stock,
                active_color=T.SUCCESS,
                inactive_thumb_color=T.TEXT_DIM,
            )
            sw.on_change = lambda e, iid=item.id, cur=item.in_stock, s=sw: toggle_stock(iid, cur, s)

            tile = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(item.ingredient_name, color=T.TEXT, size=14,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        item.quantity_display if item.quantity else item.unit or "—",
                                        size=12, color=T.TEXT_DIM,
                                    ),
                                ],
                                spacing=2,
                            ),
                            expand=True,
                        ),
                        sw,
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=T.TEXT_DIM,
                            icon_size=18,
                            tooltip="Remove",
                            on_click=lambda _, iid=item.id: delete_item(iid),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=T.SURFACE,
                border_radius=10,
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            )
            controls.append(tile)

        return controls

    # ── Add-to-inventory dialog ────────────────────────────────────────────
    def show_add_dialog(_: ft.ControlEvent) -> None:
        all_ingredients = inventory_service.get_all_ingredients()
        existing_ids = {
            row.ingredient_id
            for row in inventory_service.get_all_inventory()
        }

        available = [i for i in all_ingredients if i.id not in existing_ids]

        ing_dd = ft.Dropdown(
            label="Ingredient",
            label_style=ft.TextStyle(color=T.TEXT_DIM),
            options=[ft.dropdown.Option(key=str(i.id), text=i.name) for i in available],
            bgcolor=T.SURFACE2,
            color=T.TEXT,
            border_color=T.SECONDARY,
            expand=True,
        )
        qty_field = ft.TextField(
            label="Quantity", label_style=ft.TextStyle(color=T.TEXT_DIM),
            value="", keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
            width=100,
        )
        unit_dd = ft.Dropdown(
            label="Unit",
            label_style=ft.TextStyle(color=T.TEXT_DIM),
            options=[ft.dropdown.Option(u) for u in UNITS],
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
            width=100,
        )
        new_ing_field = ft.TextField(
            label="Or add new ingredient…",
            label_style=ft.TextStyle(color=T.TEXT_DIM),
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
            expand=True,
        )
        cat_dd = ft.Dropdown(
            label="Category",
            label_style=ft.TextStyle(color=T.TEXT_DIM),
            options=[ft.dropdown.Option(c) for c in CATEGORIES],
            value="Other",
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
            expand=True,
        )

        def do_add(_: ft.ControlEvent) -> None:
            ing_id = None
            new_name = (new_ing_field.value or "").strip()
            if new_name:
                ing_id = inventory_service.create_ingredient(new_name, cat_dd.value or "Other")
            elif ing_dd.value:
                ing_id = int(ing_dd.value)

            if not ing_id:
                T.snack(page, "Please select or enter an ingredient.", error=True)
                return

            try:
                qty = float(qty_field.value) if qty_field.value else 0.0
            except ValueError:
                qty = 0.0

            inventory_service.add_to_inventory(
                ingredient_id=ing_id,
                quantity=qty,
                unit=unit_dd.value or "",
            )
            close_dlg(dlg)
            refresh_list()
            T.snack(page, "Added to inventory!")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add to Inventory", color=T.TEXT),
            bgcolor=T.SURFACE,
            content=ft.Column(
                [
                    ft.Text("Select existing:", size=12, color=T.TEXT_DIM),
                    ing_dd,
                    ft.Container(height=8),
                    ft.Row([qty_field, unit_dd], spacing=8),
                    ft.Divider(color=T.DIVIDER),
                    ft.Text("Or create new:", size=12, color=T.TEXT_DIM),
                    new_ing_field,
                    cat_dd,
                ],
                spacing=8,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dlg(dlg),
                              style=ft.ButtonStyle(color=T.TEXT_DIM)),
                ft.ElevatedButton("Add", on_click=do_add,
                                  bgcolor=T.ACCENT, color="white"),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dlg(dlg: ft.AlertDialog) -> None:
        dlg.open = False
        page.update()

    # ── Search / filter bar ────────────────────────────────────────────────
    def on_search(e: ft.ControlEvent) -> None:
        _search[0] = e.control.value or ""
        refresh_list()

    def on_cat_change(e: ft.ControlEvent) -> None:
        _category[0] = e.control.value or "All"
        refresh_list()

    search_field = ft.TextField(
        hint_text="Search inventory…",
        hint_style=ft.TextStyle(color=T.TEXT_DIM),
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=T.SURFACE, border_color=T.SECONDARY,
        focused_border_color=T.ACCENT, color=T.TEXT,
        border_radius=10, on_change=on_search, expand=True,
    )
    cat_filter = ft.Dropdown(
        value="All",
        options=[ft.dropdown.Option("All")] + [ft.dropdown.Option(c) for c in CATEGORIES],
        bgcolor=T.SURFACE, color=T.TEXT, border_color=T.SECONDARY,
        width=130, on_select=on_cat_change,
    )

    initial_items = load_items()
    item_list = ft.ListView(
        ref=list_ref,
        controls=build_list_controls(initial_items),
        spacing=6,
        expand=True,
        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
    )

    content = ft.Column(
        [
            ft.Container(
                content=ft.Row([search_field, ft.Container(width=8), cat_filter]),
                padding=ft.Padding(left=16, right=16, top=12, bottom=4),
            ),
            item_list,
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route="/inventory",
        controls=[content],
        appbar=T.app_bar("Inventory", page),
        navigation_bar=T.nav_bar(2, page),
        bgcolor=T.BG,
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=T.ACCENT,
            on_click=show_add_dialog,
            tooltip="Add to inventory",
        ),
        scroll=ft.ScrollMode.HIDDEN,
    )
