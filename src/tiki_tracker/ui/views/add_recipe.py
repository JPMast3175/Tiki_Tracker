"""Add / Edit Recipe view — full form for custom recipes."""

import json
import flet as ft
from tiki_tracker.models.recipe import Recipe
from tiki_tracker.models.ingredient import CATEGORIES
from tiki_tracker.ui import theme as T

_DIFFICULTIES = ["1 - Easy", "2 - Easy+", "3 - Medium", "4 - Hard", "5 - Expert"]


def build(page: ft.Page, services: dict, recipe_id: int | None = None) -> ft.View:
    recipe_service = services["recipe"]
    inventory_service = services["inventory"]

    is_edit = recipe_id is not None
    existing: Recipe | None = recipe_service.get_by_id(recipe_id) if is_edit else None

    # ── Ingredient rows state ──────────────────────────────────────────────
    all_ingredients = inventory_service.get_all_ingredients()
    ing_options = [ft.dropdown.Option(key=str(i.id), text=i.name) for i in all_ingredients]

    ingredient_rows: list[dict] = []  # {dd, amount_tf, unit_tf, notes_tf, row_container}
    ing_col_ref = ft.Ref[ft.Column]()

    def make_ing_row(ingredient_id: str = "", amount: str = "", unit: str = "", notes: str = "") -> dict:
        dd = ft.Dropdown(
            options=ing_options,
            value=ingredient_id or None,
            label="Ingredient",
            label_style=ft.TextStyle(color=T.TEXT_DIM),
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
            expand=True,
        )
        amt_tf = ft.TextField(
            label="Amt", value=amount, label_style=ft.TextStyle(color=T.TEXT_DIM),
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, width=72,
        )
        unit_tf = ft.TextField(
            label="Unit", value=unit, label_style=ft.TextStyle(color=T.TEXT_DIM),
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, width=72,
        )
        notes_tf = ft.TextField(
            label="Notes", value=notes, label_style=ft.TextStyle(color=T.TEXT_DIM),
            bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
        )
        entry = {"dd": dd, "amt": amt_tf, "unit": unit_tf, "notes": notes_tf}

        def remove_row(_: ft.ControlEvent, e=entry) -> None:
            if e in ingredient_rows:
                ingredient_rows.remove(e)
            _rebuild_ing_col()

        entry["container"] = ft.Container(
            content=ft.Column([
                ft.Row([dd, amt_tf, unit_tf], spacing=8),
                ft.Row([notes_tf, ft.IconButton(
                    icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                    icon_color=T.ERROR, icon_size=20,
                    on_click=remove_row,
                )], spacing=8),
                ft.Divider(color=T.DIVIDER, height=1),
            ], spacing=6),
        )
        return entry

    def _rebuild_ing_col() -> None:
        if ing_col_ref.current:
            ing_col_ref.current.controls = [e["container"] for e in ingredient_rows]
            page.update()

    def add_ing_row(_: ft.ControlEvent) -> None:
        entry = make_ing_row()
        ingredient_rows.append(entry)
        _rebuild_ing_col()

    # ── Form fields ────────────────────────────────────────────────────────
    name_tf = ft.TextField(
        label="Recipe Name *", value=existing.name if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )
    desc_tf = ft.TextField(
        label="Description", value=existing.description if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
        multiline=True, min_lines=2, max_lines=4, expand=True,
    )
    instr_tf = ft.TextField(
        label="Instructions", value=existing.instructions if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
        multiline=True, min_lines=4, max_lines=10, expand=True,
    )
    garnish_tf = ft.TextField(
        label="Garnish", value=existing.garnish if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )
    glass_tf = ft.TextField(
        label="Glassware", value=existing.glassware if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )
    diff_dd = ft.Dropdown(
        label="Difficulty",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        options=[ft.dropdown.Option(d) for d in _DIFFICULTIES],
        value=_DIFFICULTIES[(existing.difficulty - 1) if existing else 2],
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )
    prep_tf = ft.TextField(
        label="Prep time (min)", value=str(existing.prep_time) if existing else "15",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY,
        keyboard_type=ft.KeyboardType.NUMBER, expand=True,
    )
    tags_tf = ft.TextField(
        label="Tags (comma-separated)",
        value=", ".join(existing.tags) if existing else "",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )

    # Pre-populate ingredient rows for edit mode
    if existing:
        for ri in existing.ingredients:
            entry = make_ing_row(str(ri.ingredient_id), ri.amount, ri.unit, ri.notes)
            ingredient_rows.append(entry)

    # ── New ingredient inline ──────────────────────────────────────────────
    new_ing_tf = ft.TextField(
        label="New ingredient name",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, expand=True,
    )
    new_cat_dd = ft.Dropdown(
        label="Category",
        label_style=ft.TextStyle(color=T.TEXT_DIM),
        options=[ft.dropdown.Option(c) for c in CATEGORIES],
        value="Other",
        bgcolor=T.SURFACE2, color=T.TEXT, border_color=T.SECONDARY, width=140,
    )

    def save_new_ingredient(_: ft.ControlEvent) -> None:
        name = (new_ing_tf.value or "").strip()
        if not name:
            return
        ing_id = inventory_service.create_ingredient(name, new_cat_dd.value or "Other")
        if ing_id:
            all_ingredients.append(type("Ing", (), {"id": ing_id, "name": name})())
            opt = ft.dropdown.Option(key=str(ing_id), text=name)
            for e in ingredient_rows:
                e["dd"].options.append(opt)
            new_ing_tf.value = ""
            T.snack(page, f'"{name}" added!')
            page.update()

    # ── Save ──────────────────────────────────────────────────────────────
    def on_save(_: ft.ControlEvent) -> None:
        name = (name_tf.value or "").strip()
        if not name:
            T.snack(page, "Recipe name is required.", error=True)
            return

        tags_raw = tags_tf.value or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

        diff_val = int((diff_dd.value or "3")[0])
        try:
            prep_val = int(prep_tf.value or "15")
        except ValueError:
            prep_val = 15

        recipe = Recipe(
            id=recipe_id or 0,
            name=name,
            description=desc_tf.value or "",
            instructions=instr_tf.value or "",
            garnish=garnish_tf.value or "",
            glassware=glass_tf.value or "",
            difficulty=diff_val,
            prep_time=prep_val,
            tags=tags,
            is_custom=True,
        )

        ing_list = []
        for e in ingredient_rows:
            if e["dd"].value:
                ing_list.append({
                    "ingredient_id": int(e["dd"].value),
                    "amount": e["amt"].value or "",
                    "unit": e["unit"].value or "",
                    "notes": e["notes"].value or "",
                })

        if is_edit:
            recipe_service.update(recipe, ing_list)
            T.snack(page, f'"{name}" updated!')
        else:
            recipe_service.create(recipe, ing_list)
            T.snack(page, f'"{name}" saved!')

        page.go("/recipes")

    save_btn = ft.ElevatedButton(
        "Save Recipe" if is_edit else "Create Recipe",
        icon=ft.Icons.SAVE,
        bgcolor=T.ACCENT, color="white",
        on_click=on_save,
        expand=True,
    )

    content = ft.ListView(
        [
            ft.Container(
                content=ft.Column(
                    [
                        T.section_title("RECIPE INFO"),
                        ft.Container(height=8),
                        name_tf,
                        desc_tf,
                        instr_tf,
                        ft.Container(height=8),
                        ft.Row([glass_tf, garnish_tf], spacing=12),
                        ft.Row([diff_dd, prep_tf], spacing=12),
                        tags_tf,
                        ft.Container(height=16),
                        ft.Divider(color=T.DIVIDER),
                        ft.Container(height=8),
                        T.section_title("INGREDIENTS"),
                        ft.Container(height=4),
                        ft.Column(ref=ing_col_ref, controls=[e["container"] for e in ingredient_rows], spacing=0),
                        ft.TextButton(
                            "Add Ingredient Row",
                            icon=ft.Icons.ADD,
                            style=ft.ButtonStyle(color=T.ACCENT),
                            on_click=add_ing_row,
                        ),
                        ft.Container(height=16),
                        ft.Divider(color=T.DIVIDER),
                        ft.Container(height=8),
                        T.section_title("CREATE NEW INGREDIENT"),
                        ft.Container(height=4),
                        ft.Row([new_ing_tf, new_cat_dd], spacing=8),
                        ft.TextButton(
                            "Save New Ingredient",
                            icon=ft.Icons.ADD_BOX,
                            style=ft.ButtonStyle(color=T.SECONDARY),
                            on_click=save_new_ingredient,
                        ),
                        ft.Container(height=20),
                        save_btn,
                        ft.Container(height=32),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            )
        ],
        expand=True,
        spacing=0,
    )

    title = "Edit Recipe" if is_edit else "New Recipe"
    return ft.View(
        route=f"/edit_recipe/{recipe_id}" if is_edit else "/add_recipe",
        controls=[content],
        appbar=ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=T.TEXT,
                on_click=lambda _: page.go("/recipes"),
            ),
            title=ft.Text(title, color=T.TEXT, size=18, weight=ft.FontWeight.BOLD),
            bgcolor=T.PRIMARY_DARK,
        ),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
