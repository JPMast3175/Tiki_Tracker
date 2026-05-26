"""Ingredient model — represents a single bar ingredient in the master list."""

from dataclasses import dataclass, field
import sqlite3


CATEGORIES = [
    "Rum",
    "Spirits",
    "Liqueurs",
    "Citrus",
    "Juices",
    "Syrups",
    "Bitters",
    "Mixers",
    "Garnishes",
    "Glassware",
    "Other",
]


@dataclass
class Ingredient:
    id: int = 0
    name: str = ""
    category: str = "Other"
    description: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Ingredient":
        return cls(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            description=row["description"],
        )


@dataclass
class RecipeIngredient:
    """An ingredient within the context of a specific recipe."""

    id: int = 0
    recipe_id: int = 0
    ingredient_id: int = 0
    ingredient_name: str = ""
    category: str = ""
    amount: str = ""
    unit: str = ""
    notes: str = ""
    sort_order: int = 0

    @property
    def display(self) -> str:
        parts = [self.amount, self.unit, self.ingredient_name]
        result = " ".join(p for p in parts if p)
        if self.notes:
            result += f" ({self.notes})"
        return result

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "RecipeIngredient":
        keys = row.keys()
        return cls(
            id=row["id"],
            recipe_id=row["recipe_id"],
            ingredient_id=row["ingredient_id"],
            ingredient_name=row["ingredient_name"],
            category=row["category"] if "category" in keys else "",
            amount=row["amount"],
            unit=row["unit"],
            notes=row["notes"],
            sort_order=row["sort_order"],
        )
