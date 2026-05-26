"""Recipe model — a full tiki drink recipe with metadata."""

import json
import sqlite3
from dataclasses import dataclass, field

from tiki_tracker.models.ingredient import RecipeIngredient


@dataclass
class Recipe:
    id: int = 0
    name: str = ""
    description: str = ""
    instructions: str = ""
    garnish: str = ""
    glassware: str = ""
    image_path: str = ""
    image_url: str = ""
    difficulty: int = 3
    prep_time: int = 15
    rating: float = 0.0
    is_favorite: bool = False
    is_custom: bool = False
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    ingredients: list[RecipeIngredient] = field(default_factory=list)

    @property
    def difficulty_label(self) -> str:
        labels = {1: "Easy", 2: "Easy-Medium", 3: "Medium", 4: "Medium-Hard", 5: "Hard"}
        return labels.get(self.difficulty, "Medium")

    @property
    def star_display(self) -> str:
        filled = "★" * int(round(self.rating))
        empty = "☆" * (5 - int(round(self.rating)))
        return filled + empty

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "garnish": self.garnish,
            "glassware": self.glassware,
            "image_url": self.image_url,
            "difficulty": self.difficulty,
            "prep_time": self.prep_time,
            "rating": self.rating,
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "ingredients": [
                {
                    "name": ri.ingredient_name,
                    "amount": ri.amount,
                    "unit": ri.unit,
                    "notes": ri.notes,
                }
                for ri in self.ingredients
            ],
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Recipe":
        tags_raw = row["tags"] if row["tags"] else "[]"
        try:
            tags = json.loads(tags_raw)
        except (json.JSONDecodeError, TypeError):
            tags = []
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            instructions=row["instructions"],
            garnish=row["garnish"],
            glassware=row["glassware"],
            image_path=row["image_path"],
            image_url=row["image_url"],
            difficulty=row["difficulty"],
            prep_time=row["prep_time"],
            rating=float(row["rating"]),
            is_favorite=bool(row["is_favorite"]),
            is_custom=bool(row["is_custom"]),
            tags=tags,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
