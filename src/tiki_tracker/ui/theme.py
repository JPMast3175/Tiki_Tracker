"""Tiki-inspired color palette and shared UI helpers."""

import flet as ft

# ── Color palette ──────────────────────────────────────────────────────────
BG = "#1A1209"           # Dark wood background
SURFACE = "#231A0B"      # Card / panel surface
SURFACE2 = "#2E2210"     # Slightly lighter surface
PRIMARY = "#2D6A2D"      # Deep tropical green
PRIMARY_DARK = "#1A4A1A" # Darker green (AppBar)
SECONDARY = "#8B6914"    # Bamboo / tan
ACCENT = "#D4861A"       # Warm amber highlight
TEXT = "#F5E6C8"         # Warm cream text
TEXT_DIM = "#A89070"     # Muted cream
DIVIDER = "#3A2A10"      # Subtle divider
STAR_ON = "#FFD700"      # Active star
STAR_OFF = "#4A3A20"     # Inactive star
SUCCESS = "#4CAF50"      # In-stock indicator
WARNING = "#FF9800"      # Low-stock indicator
ERROR = "#EF5350"        # Error / out-of-stock

NAV_ROUTES = ["/", "/recipes", "/inventory", "/favorites", "/settings"]


def app_bar(title: str, page: ft.Page, actions: list | None = None) -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title, color=TEXT, weight=ft.FontWeight.BOLD, size=18),
        bgcolor=PRIMARY_DARK,
        center_title=False,
        actions=actions or [],
    )


def nav_bar(selected: int, page: ft.Page) -> ft.NavigationBar:
    def on_change(e: ft.ControlEvent) -> None:
        page.go(NAV_ROUTES[e.control.selected_index])

    return ft.NavigationBar(
        selected_index=selected,
        bgcolor=SURFACE,
        indicator_color=ACCENT,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,     selected_icon=ft.Icons.HOME,     label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCAL_BAR_OUTLINED, selected_icon=ft.Icons.LOCAL_BAR, label="Recipes"),
            ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Inventory"),
            ft.NavigationBarDestination(icon=ft.Icons.FAVORITE_OUTLINE,  selected_icon=ft.Icons.FAVORITE,  label="Favorites"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_change,
    )


def card(content: ft.Control, padding: int = 16) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=12,
        padding=padding,
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, color=ACCENT, size=13, weight=ft.FontWeight.BOLD,
                   style=ft.TextStyle(letter_spacing=1.2))


def stars(rating: float, size: int = 18) -> ft.Row:
    filled = int(round(rating))
    icons = []
    for i in range(5):
        icons.append(
            ft.Icon(
                ft.Icons.STAR if i < filled else ft.Icons.STAR_OUTLINE,
                color=STAR_ON if i < filled else STAR_OFF,
                size=size,
            )
        )
    return ft.Row(icons, spacing=0, tight=True)


def difficulty_badge(level: int) -> ft.Container:
    colors = {1: "#2E7D32", 2: "#558B2F", 3: "#F9A825", 4: "#E65100", 5: "#B71C1C"}
    labels = {1: "Easy", 2: "Easy+", 3: "Medium", 4: "Hard", 5: "Expert"}
    return ft.Container(
        content=ft.Text(labels.get(level, "?"), size=11, color="white", weight=ft.FontWeight.BOLD),
        bgcolor=colors.get(level, "#666"),
        border_radius=6,
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
    )


def snack(page: ft.Page, message: str, error: bool = False) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="white"),
        bgcolor=ERROR if error else PRIMARY,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def recipe_placeholder() -> ft.Container:
    """Placeholder shown when no recipe image is available."""
    return ft.Container(
        height=160,
        bgcolor=PRIMARY_DARK,
        border_radius=10,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.LOCAL_BAR, color=ACCENT, size=48),
                ft.Text("🌴", size=24),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
    )
