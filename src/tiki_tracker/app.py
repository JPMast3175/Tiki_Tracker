"""Application entry point — Flet page setup, routing, and service wiring."""

import logging
import traceback
from pathlib import Path

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


# ── Logging setup ──────────────────────────────────────────────────────────
_log_path = Path(__file__).resolve().parent.parent.parent.parent / "tiki_tracker.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(_log_path), mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("tiki_tracker")

_MAIN_ROUTES = {"/", "/recipes", "/inventory", "/favorites", "/settings"}


def _build_view(route: str, page: ft.Page, services: dict, db: Database) -> ft.View:
    log.debug("_build_view: %r", route)
    if route == "/":
        return home.build(page, services)
    if route == "/recipes":
        return recipes.build(page, services)
    if route == "/inventory":
        return inventory.build(page, services)
    if route == "/favorites":
        return favorites.build(page, services)
    if route == "/settings":
        return settings.build(page, services, db)
    if route.startswith("/recipe/"):
        rid = int(route.split("/")[-1])
        return recipe_detail.build(page, services, rid)
    if route == "/add_recipe":
        return add_recipe.build(page, services)
    if route.startswith("/edit_recipe/"):
        rid = int(route.split("/")[-1])
        return add_recipe.build(page, services, recipe_id=rid)
    raise ValueError(f"No view for route: {route!r}")


def _error_view(page: ft.Page, message: str) -> ft.View:
    log.error("Error view: %s", message[:200])
    return ft.View(
        route=page.route or "/",
        bgcolor=T.BG,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=T.ERROR, size=64),
                        ft.Text("Something went wrong", size=18, color=T.TEXT,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(message[:300], size=11, color=T.TEXT_DIM, selectable=True),
                        ft.Container(height=16),
                        ft.ElevatedButton("Go Home", bgcolor=T.ACCENT, color="white",
                                          on_click=lambda _: page.go("/")),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
            )
        ],
    )


def main(page: ft.Page) -> None:
    log.info("=== Tiki Tracker main() starting ===")
    log.info("Flet version: %s", ft.__version__)

    # ── Database ───────────────────────────────────────────────────────────
    try:
        db = Database()
        create_tables(db)
        seed_database(db)
        log.info("Database ready at: %s", db.db_path)
    except Exception:
        log.exception("Database init failed — cannot continue")
        raise

    recipe_service = RecipeService(db)
    inventory_service = InventoryService(db)
    services = {
        "recipe": recipe_service,
        "inventory": inventory_service,
        "suggestion": SuggestionService(recipe_service, inventory_service),
        "qr": QRService(),
        "export": ExportService(recipe_service, inventory_service),
    }

    # ── Page setup ─────────────────────────────────────────────────────────
    page.title = "Tiki Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = T.BG
    page.padding = 0
    try:
        page.window.min_width = 360
        page.window.min_height = 600
    except Exception:
        log.warning("window.min_size not supported on this platform")

    log.info("Page setup complete. page.route=%r", page.route)

    # ── Route handler ──────────────────────────────────────────────────────
    def route_change(e) -> None:
        route = page.route or "/"
        log.info("route_change -> %r  (views before: %d)", route, len(page.views))
        try:
            if route in _MAIN_ROUTES:
                page.views.clear()
            view = _build_view(route, page, services, db)
            page.views.append(view)
            log.info("view appended, stack now %d deep", len(page.views))
        except Exception:
            err = traceback.format_exc()
            log.error("route_change failed:\n%s", err)
            page.views.append(_error_view(page, err))
        page.update()
        log.info("page.update() called")

    def view_pop(e) -> None:
        log.info("view_pop (stack depth %d)", len(page.views))
        if len(page.views) > 1:
            page.views.pop()
        top = page.views[-1] if page.views else None
        page.go(top.route if top else "/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ── Initial render ─────────────────────────────────────────────────────
    # Render the home view directly — do NOT rely on page.go() firing
    # route_change on startup, which is unreliable in Flet 0.85 desktop mode.
    log.info("Rendering initial view directly (bypassing router event)")
    try:
        initial = _build_view("/", page, services, db)
        page.views.clear()
        page.views.append(initial)
        page.update()
        log.info("Initial view pushed and page.update() called — should be visible now")
    except Exception:
        err = traceback.format_exc()
        log.error("Initial view build failed:\n%s", err)
        page.views.append(_error_view(page, err))
        page.update()
