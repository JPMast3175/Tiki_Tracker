"""CRUD operations for recipes and their ingredients."""

import json
from tiki_tracker.db.database import Database
from tiki_tracker.models.recipe import Recipe
from tiki_tracker.models.ingredient import RecipeIngredient


class RecipeService:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ── Queries ────────────────────────────────────────────────────────────

    def get_all(self, search: str = "", favorites_only: bool = False) -> list[Recipe]:
        sql = "SELECT * FROM recipes WHERE 1=1"
        params: list = []
        if search:
            sql += " AND name LIKE ?"
            params.append(f"%{search}%")
        if favorites_only:
            sql += " AND is_favorite = 1"
        sql += " ORDER BY name ASC"
        rows = self.db.fetchall(sql, tuple(params))
        return [Recipe.from_row(r) for r in rows]

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        row = self.db.fetchone("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        if row is None:
            return None
        recipe = Recipe.from_row(row)
        recipe.ingredients = self._get_ingredients(recipe_id)
        return recipe

    def _get_ingredients(self, recipe_id: int) -> list[RecipeIngredient]:
        rows = self.db.fetchall(
            """SELECT ri.*, i.name AS ingredient_name, i.category
               FROM recipe_ingredients ri
               JOIN ingredients i ON i.id = ri.ingredient_id
               WHERE ri.recipe_id = ?
               ORDER BY ri.sort_order""",
            (recipe_id,),
        )
        return [RecipeIngredient.from_row(r) for r in rows]

    def count(self) -> int:
        row = self.db.fetchone("SELECT COUNT(*) as cnt FROM recipes")
        return row["cnt"] if row else 0

    # ── Writes ─────────────────────────────────────────────────────────────

    def create(self, recipe: Recipe, ingredients: list[dict]) -> int:
        """Insert a new recipe; ingredients is list of {ingredient_id, amount, unit, notes}."""
        recipe_id = self.db.execute(
            """INSERT INTO recipes
               (name, description, instructions, garnish, glassware,
                image_path, image_url, difficulty, prep_time, tags, is_custom)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                recipe.name,
                recipe.description,
                recipe.instructions,
                recipe.garnish,
                recipe.glassware,
                recipe.image_path,
                recipe.image_url,
                recipe.difficulty,
                recipe.prep_time,
                json.dumps(recipe.tags),
            ),
        )
        self._save_ingredients(recipe_id, ingredients)
        return recipe_id

    def update(self, recipe: Recipe, ingredients: list[dict]) -> None:
        self.db.execute(
            """UPDATE recipes SET
               name=?, description=?, instructions=?, garnish=?, glassware=?,
               image_path=?, image_url=?, difficulty=?, prep_time=?, tags=?,
               updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (
                recipe.name,
                recipe.description,
                recipe.instructions,
                recipe.garnish,
                recipe.glassware,
                recipe.image_path,
                recipe.image_url,
                recipe.difficulty,
                recipe.prep_time,
                json.dumps(recipe.tags),
                recipe.id,
            ),
        )
        self.db.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe.id,))
        self._save_ingredients(recipe.id, ingredients)

    def delete(self, recipe_id: int) -> None:
        self.db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))

    def set_favorite(self, recipe_id: int, value: bool) -> None:
        self.db.execute(
            "UPDATE recipes SET is_favorite = ?, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
            (1 if value else 0, recipe_id),
        )

    def set_rating(self, recipe_id: int, rating: float) -> None:
        self.db.execute(
            "UPDATE recipes SET rating = ?, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
            (max(0.0, min(5.0, rating)), recipe_id),
        )

    def _save_ingredients(self, recipe_id: int, ingredients: list[dict]) -> None:
        for i, ing in enumerate(ingredients):
            self.db.execute(
                """INSERT INTO recipe_ingredients
                   (recipe_id, ingredient_id, amount, unit, notes, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    recipe_id,
                    ing["ingredient_id"],
                    ing.get("amount", ""),
                    ing.get("unit", ""),
                    ing.get("notes", ""),
                    i,
                ),
            )

    # ── Inventory match ────────────────────────────────────────────────────

    def get_makeable(self) -> list[Recipe]:
        """Return recipes whose non-garnish ingredients are all in stock."""
        in_stock_ids = {
            row["ingredient_id"]
            for row in self.db.fetchall(
                "SELECT ingredient_id FROM inventory WHERE in_stock = 1"
            )
        }
        all_recipes = self.get_all()
        makeable: list[Recipe] = []
        for recipe in all_recipes:
            recipe.ingredients = self._get_ingredients(recipe.id)
            garnish_cats = {"Garnishes"}
            needed = {
                ri.ingredient_id
                for ri in recipe.ingredients
                if ri.category not in garnish_cats
            }
            if needed and needed.issubset(in_stock_ids):
                makeable.append(recipe)
        return makeable
