"""Settings view — export, backup, import, and app info."""

from pathlib import Path
import flet as ft
from tiki_tracker.ui import theme as T


def build(page: ft.Page, services: dict, db) -> ft.View:
    export_service = services["export"]
    recipe_service = services["recipe"]

    def do_export_recipes(_: ft.ControlEvent) -> None:
        try:
            path = export_service.export_recipes_json()
            T.snack(page, f"Exported to {path.name}")
        except Exception as exc:
            T.snack(page, f"Export failed: {exc}", error=True)

    def do_backup_json(_: ft.ControlEvent) -> None:
        try:
            path = export_service.export_backup_json(db)
            T.snack(page, f"Backup saved: {path.name}")
        except Exception as exc:
            T.snack(page, f"Backup failed: {exc}", error=True)

    def do_backup_db(_: ft.ControlEvent) -> None:
        try:
            path = export_service.backup_database(db)
            T.snack(page, f"DB backup: {path.name}")
        except Exception as exc:
            T.snack(page, f"Backup failed: {exc}", error=True)

    # ── File picker for import ─────────────────────────────────────────────
    def on_file_picked(e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        try:
            path = Path(e.files[0].path)
            count, errors = export_service.import_recipes_json(path)
            msg = f"Imported {count} recipe{'s' if count != 1 else ''}"
            if errors:
                msg += f" ({len(errors)} skipped)"
            T.snack(page, msg, error=bool(errors))
        except Exception as exc:
            T.snack(page, f"Import failed: {exc}", error=True)

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def pick_import_file(_: ft.ControlEvent) -> None:
        file_picker.pick_files(
            dialog_title="Import Recipes JSON",
            allowed_extensions=["json"],
            allow_multiple=False,
        )

    def setting_tile(
        icon: str,
        title: str,
        subtitle: str,
        on_click,
        color: str = T.TEXT,
    ) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=T.ACCENT, size=24),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(title, size=15, color=color, weight=ft.FontWeight.W_500),
                            ft.Text(subtitle, size=12, color=T.TEXT_DIM),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=T.TEXT_DIM, size=20),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=T.SURFACE,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            on_click=on_click,
            ink=True,
        )

    db_path = str(db.db_path)
    total = recipe_service.count()

    content = ft.ListView(
        [
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCAL_BAR, color=T.ACCENT, size=48),
                        ft.Text("Tiki Tracker", size=20, weight=ft.FontWeight.BOLD, color=T.TEXT),
                        ft.Text("v1.0.0", size=12, color=T.TEXT_DIM),
                        ft.Text(f"{total} recipes in your library", size=12, color=T.TEXT_DIM),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=24),
            ),
            ft.Container(
                T.section_title("EXPORT"),
                padding=ft.padding.only(left=16, top=8, bottom=8),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        setting_tile(
                            ft.Icons.FILE_DOWNLOAD_OUTLINED,
                            "Export Recipes",
                            "Save all recipes as JSON",
                            do_export_recipes,
                        ),
                        ft.Container(height=8),
                        setting_tile(
                            ft.Icons.BACKUP_OUTLINED,
                            "Full Backup (JSON)",
                            "Backup recipes + inventory",
                            do_backup_json,
                        ),
                        ft.Container(height=8),
                        setting_tile(
                            ft.Icons.STORAGE_OUTLINED,
                            "Backup Database File",
                            "Copy tiki_tracker.db to backups/",
                            do_backup_db,
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(height=16),
            ft.Container(
                T.section_title("IMPORT"),
                padding=ft.padding.only(left=16, bottom=8),
            ),
            ft.Container(
                content=setting_tile(
                    ft.Icons.FILE_UPLOAD_OUTLINED,
                    "Import Recipes JSON",
                    "Load recipes from a JSON export file",
                    pick_import_file,
                ),
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(height=16),
            ft.Container(
                T.section_title("DATA"),
                padding=ft.padding.only(left=16, bottom=8),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        T.card(
                            ft.Column([
                                ft.Text("Database Location", size=13, color=T.TEXT_DIM),
                                ft.Container(height=4),
                                ft.Text(db_path, size=11, color=T.TEXT, selectable=True),
                            ], spacing=2)
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(height=32),
        ],
        expand=True,
        spacing=0,
    )

    return ft.View(
        route="/settings",
        controls=[content],
        appbar=T.app_bar("Settings", page),
        navigation_bar=T.nav_bar(4, page),
        bgcolor=T.BG,
        scroll=ft.ScrollMode.HIDDEN,
    )
