"""Application entry point — Flet page setup, routing, and service wiring."""

import flet as ft

from tiki_tracker.db.database import Database
from tiki_tracker.db.schema import create_tables
from tiki_tracker.db.seed_data import seed_database
from tiki_tracker.services.recipe_service import RecipeService
from tiki_tracker.services.inventory_service import InventoryService
from tiki_tracker.services.suggestion_service import SuggestionService
from tiki_tracker.services.qr_service import QRService
from tiki_tracker.services.export_service import ExportService
from tiki_tracker.ui import theme as T
from tiki_tracker.ui.views import home, recipes, recipe_detail, inventory, favorites, add_recipe, settings


_MAIN_ROUTES = {"/", "/recipes", "/inventory", "/favorites", "/settings"}


def main(page: ft.Page) -> None:
    # ── Database + services ────────────────────────────────────────────────
    db = Database()
    create_tables(db)
    seed_database(db)

    recipe_service = RecipeService(db)
    inventory_service = InventoryService(db)
    suggestion_service = SuggestionService(recipe_service, inventory_service)
    qr_service = QRService()
    export_service = ExportService(recipe_service, inventory_service)

    services = {
        "recipe": recipe_service,
        "inventory": inventory_service,
        "suggestion": suggestion_service,
        "qr": qr_service,
        "export": export_service,
    }

    # ── Page setup ─────────────────────────────────────────────────────────
    page.title = "Tiki Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = T.BG
    page.padding = 0
    page.window.min_width = 360
    page.window.min_height = 600

    # ── Routing ────────────────────────────────────────────────────────────
    def route_change(e: ft.RouteChangeEvent) -> None:
        route = page.route

        # Main-level routes: reset the view stack
        if route in _MAIN_ROUTES:
            page.views.clear()

        view: ft.View | None = None

        if route == "/":
            view = home.build(page, services)
        elif route == "/recipes":
            view = recipes.build(page, services)
        elif route == "/inventory":
            view = inventory.build(page, services)
        elif route == "/favorites":
            view = favorites.build(page, services)
        elif route == "/settings":
            view = settings.build(page, services, db)
        elif route.startswith("/recipe/"):
            try:
                rid = int(route.split("/")[-1])
                view = recipe_detail.build(page, services, rid)
            except (ValueError, IndexError):
                view = _not_found_view(page)
        elif route == "/add_recipe":
            view = add_recipe.build(page, services)
        elif route.startswith("/edit_recipe/"):
            try:
                rid = int(route.split("/")[-1])
                view = add_recipe.build(page, services, recipe_id=rid)
            except (ValueError, IndexError):
                view = _not_found_view(page)
        else:
            view = _not_found_view(page)

        if view is not None:
            page.views.append(view)
        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        if len(page.views) > 1:
            page.views.pop()
        top = page.views[-1] if page.views else None
        if top:
            page.go(top.route)
        else:
            page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route if page.route else "/")


def _not_found_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/404",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("404", size=64, weight=ft.FontWeight.BOLD, color=T.ACCENT),
                        ft.Text("Page not found", size=18, color=T.TEXT),
                        ft.ElevatedButton("Home", on_click=lambda _: page.go("/"),
                                          bgcolor=T.ACCENT, color="white"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
        bgcolor=T.BG,
    )
