"""JSON import/export and database backup utilities."""

import json
import shutil
from datetime import datetime
from pathlib import Path

from tiki_tracker.db.database import Database
from tiki_tracker.services.recipe_service import RecipeService
from tiki_tracker.services.inventory_service import InventoryService


def _exports_dir() -> Path:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    d = project_root / "exports"
    d.mkdir(exist_ok=True)
    return d


class ExportService:
    def __init__(self, recipe_service: RecipeService, inventory_service: InventoryService) -> None:
        self.recipe_service = recipe_service
        self.inventory_service = inventory_service

    # ── Export ─────────────────────────────────────────────────────────────

    def export_recipes_json(self, path: Path | None = None) -> Path:
        recipes = self.recipe_service.get_all()
        data = []
        for recipe in recipes:
            full = self.recipe_service.get_by_id(recipe.id)
            if full:
                data.append(full.to_dict())

        if path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = _exports_dir() / "recipes" / f"recipes_{ts}.json"
            path.parent.mkdir(exist_ok=True)

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def export_backup_json(self, db: Database, path: Path | None = None) -> Path:
        """Full data backup: recipes + inventory as JSON."""
        recipes = self.recipe_service.get_all()
        recipe_data = []
        for recipe in recipes:
            full = self.recipe_service.get_by_id(recipe.id)
            if full:
                recipe_data.append(full.to_dict())

        inventory = self.inventory_service.get_all_inventory()
        inv_data = [
            {
                "ingredient": item.ingredient_name,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "notes": item.notes,
                "in_stock": item.in_stock,
            }
            for item in inventory
        ]

        backup = {
            "version": 1,
            "exported_at": datetime.now().isoformat(),
            "recipes": recipe_data,
            "inventory": inv_data,
        }

        if path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = _exports_dir() / "backups" / f"backup_{ts}.json"
            path.parent.mkdir(exist_ok=True)

        path.write_text(json.dumps(backup, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def backup_database(self, db: Database) -> Path:
        """Copy the raw SQLite file to exports/backups/."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = _exports_dir() / "backups" / f"tiki_tracker_{ts}.db"
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(str(db.db_path), str(dest))
        return dest

    # ── Import ─────────────────────────────────────────────────────────────

    def import_recipes_json(self, path: Path) -> tuple[int, list[str]]:
        """
        Import recipes from a JSON file.
        Returns (imported_count, error_messages).
        """
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, list):
            data = data.get("recipes", [])

        imported = 0
        errors: list[str] = []

        for item in data:
            try:
                self._import_single_recipe(item)
                imported += 1
            except Exception as exc:
                errors.append(f"{item.get('name', '?')}: {exc}")

        return imported, errors

    def _import_single_recipe(self, data: dict) -> None:
        from tiki_tracker.models.recipe import Recipe

        recipe = Recipe(
            name=data["name"],
            description=data.get("description", ""),
            instructions=data.get("instructions", ""),
            garnish=data.get("garnish", ""),
            glassware=data.get("glassware", ""),
            image_url=data.get("image_url", ""),
            difficulty=data.get("difficulty", 3),
            prep_time=data.get("prep_time", 15),
            tags=data.get("tags", []),
            is_custom=True,
        )

        ingredient_rows: list[dict] = []
        for ing in data.get("ingredients", []):
            ing_name = ing.get("name", "").strip()
            if not ing_name:
                continue
            # Ensure ingredient exists
            row = self.inventory_service.db.fetchone(
                "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE", (ing_name,)
            )
            if row:
                ing_id = row["id"]
            else:
                ing_id = self.inventory_service.create_ingredient(ing_name, "Other")
            ingredient_rows.append(
                {
                    "ingredient_id": ing_id,
                    "amount": ing.get("amount", ""),
                    "unit": ing.get("unit", ""),
                    "notes": ing.get("notes", ""),
                }
            )

        self.recipe_service.create(recipe, ingredient_rows)
