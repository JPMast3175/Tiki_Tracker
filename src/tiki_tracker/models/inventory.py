"""Inventory model — a bar ingredient with quantity and stock status."""

import sqlite3
from dataclasses import dataclass


UNITS = ["oz", "ml", "bottle", "can", "jar", "bag", "piece", "dash", "drop", "tsp", "tbsp", "cup", "liter", ""]


@dataclass
class InventoryItem:
    id: int = 0
    ingredient_id: int = 0
    ingredient_name: str = ""
    category: str = ""
    quantity: float = 0.0
    unit: str = ""
    notes: str = ""
    in_stock: bool = True

    @property
    def quantity_display(self) -> str:
        if self.quantity == 0:
            return "—"
        qty = int(self.quantity) if self.quantity == int(self.quantity) else self.quantity
        return f"{qty} {self.unit}".strip()

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "InventoryItem":
        return cls(
            id=row["id"],
            ingredient_id=row["ingredient_id"],
            ingredient_name=row["ingredient_name"],
            category=row["category"],
            quantity=float(row["quantity"]),
            unit=row["unit"],
            notes=row["notes"],
            in_stock=bool(row["in_stock"]),
        )
