"""Tiki-inspired premium color palette, gradients, and shared UI components."""

import flet as ft

# ── Color palette ──────────────────────────────────────────────────────────
BG          = "#120D07"   # Deep espresso background
SURFACE     = "#1E1509"   # Card / panel surface
SURFACE2    = "#2A1E0D"   # Slightly lighter surface
SURFACE3    = "#33250F"   # Hover / pressed surface
PRIMARY     = "#1E5C1E"   # Deep tropical green
PRIMARY_DARK= "#133913"   # Darker green (AppBar, hero)
PRIMARY_MID = "#2D6A2D"   # Mid green
GOLD        = "#C9A227"   # Rum-barrel gold
ACCENT      = "#D4861A"   # Warm amber
TEXT        = "#F0E2C8"   # Warm cream
TEXT_DIM    = "#9A7A55"   # Muted warm
TEXT_DARK   = "#5A4020"   # Very muted
DIVIDER     = "#2E2010"   # Subtle divider
STAR_ON     = "#FFD700"   # Active star
STAR_OFF    = "#3A2A10"   # Inactive star
SUCCESS     = "#4CAF50"   # In-stock
WARNING     = "#FF9800"   # Low stock
ERROR       = "#EF5350"   # Error / out-of-stock
FAV_COLOR   = "#E84545"   # Favorite red

# Gradient stop pairs
GRAD_HERO   = ["#0D3B0D", "#1A5C1A", "#0D2E0D"]
GRAD_CARD   = ["#1A5218", "#0E3410"]
GRAD_AMBER  = ["#8B4A00", "#3D1E00"]

SECONDARY   = "#8B6914"   # Bamboo / tan (legacy alias)

NAV_ROUTES  = ["/", "/recipes", "/inventory", "/favorites", "/settings"]


# ── Navigation ─────────────────────────────────────────────────────────────
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
        indicator_color="#C9A22730",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,       selected_icon=ft.Icons.HOME,        label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCAL_BAR_OUTLINED,  selected_icon=ft.Icons.LOCAL_BAR,   label="Recipes"),
            ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED,selected_icon=ft.Icons.INVENTORY_2, label="Inventory"),
            ft.NavigationBarDestination(icon=ft.Icons.FAVORITE_OUTLINE,    selected_icon=ft.Icons.FAVORITE,    label="Favorites"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED,   selected_icon=ft.Icons.SETTINGS,    label="Settings"),
        ],
        on_change=on_change,
    )


# ── Shared widgets ─────────────────────────────────────────────────────────
def card(content: ft.Control, padding: int = 16, radius: int = 14) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=radius,
        padding=padding,
        shadow=ft.BoxShadow(blur_radius=16, color="#22000000", offset=ft.Offset(0, 4)),
    )


def section_title(text: str) -> ft.Row:
    return ft.Row(
        [
            ft.Container(width=3, height=14, bgcolor=GOLD, border_radius=2),
            ft.Container(width=6),
            ft.Text(
                text,
                color=GOLD,
                size=11,
                weight=ft.FontWeight.BOLD,
                style=ft.TextStyle(letter_spacing=1.8),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def stars(rating: float, size: int = 16) -> ft.Row:
    filled = int(round(rating))
    icons = [
        ft.Icon(ft.Icons.STAR if i < filled else ft.Icons.STAR_OUTLINE,
                color=STAR_ON if i < filled else STAR_OFF, size=size)
        for i in range(5)
    ]
    return ft.Row(icons, spacing=0, tight=True)


def difficulty_badge(level: int) -> ft.Container:
    colors = {1: "#1B5E20", 2: "#388E3C", 3: "#F57F17", 4: "#E64A19", 5: "#B71C1C"}
    labels = {1: "Easy", 2: "Easy+", 3: "Medium", 4: "Hard", 5: "Expert"}
    return ft.Container(
        content=ft.Text(labels.get(level, "?"), size=10, color="white",
                        weight=ft.FontWeight.BOLD),
        bgcolor=colors.get(level, "#555"),
        border_radius=5,
        padding=ft.Padding(left=7, right=7, top=3, bottom=3),
    )


def hero_placeholder(height: int = 220, emoji: str = "🌴 🍹 🌴") -> ft.Container:
    """Full-width gradient hero used where a drink photo would appear."""
    return ft.Container(
        height=height,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=GRAD_HERO,
        ),
        content=ft.Stack(
            [
                # Subtle radial glow
                ft.Container(
                    gradient=ft.RadialGradient(
                        center=ft.Alignment(0, -0.2),
                        radius=0.8,
                        colors=["#204CAF50", "#00000000"],
                    ),
                    expand=True,
                ),
                # Centre content
                ft.Column(
                    [
                        ft.Text(emoji, size=44, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
            ]
        ),
    )


def card_hero(height: int = 150) -> ft.Container:
    """Compact gradient used inside recipe grid cards."""
    return ft.Container(
        height=height,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=GRAD_CARD,
        ),
        content=ft.Column(
            [ft.Icon(ft.Icons.LOCAL_BAR, color="#80C9A227", size=40)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )


def snack(page: ft.Page, message: str, error: bool = False) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="white"),
        bgcolor=ERROR if error else PRIMARY,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def meta_chip(icon: str, label: str) -> ft.Container:
    """Small info chip used in recipe meta rows."""
    return ft.Container(
        content=ft.Row(
            [ft.Icon(icon, size=13, color=TEXT_DIM),
             ft.Text(label, size=12, color=TEXT_DIM)],
            spacing=4,
            tight=True,
        ),
        bgcolor=SURFACE2,
        border_radius=8,
        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
    )
