"""CRUD operations for inventory and master ingredient list."""

from tiki_tracker.db.database import Database
from tiki_tracker.models.inventory import InventoryItem
from tiki_tracker.models.ingredient import Ingredient


class InventoryService:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ── Ingredients ────────────────────────────────────────────────────────

    def get_all_ingredients(self, search: str = "") -> list[Ingredient]:
        if search:
            rows = self.db.fetchall(
                "SELECT * FROM ingredients WHERE name LIKE ? ORDER BY category, name",
                (f"%{search}%",),
            )
        else:
            rows = self.db.fetchall("SELECT * FROM ingredients ORDER BY category, name")
        return [Ingredient.from_row(r) for r in rows]

    def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient | None:
        row = self.db.fetchone("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
        return Ingredient.from_row(row) if row else None

    def create_ingredient(self, name: str, category: str, description: str = "") -> int:
        return self.db.execute(
            "INSERT OR IGNORE INTO ingredients (name, category, description) VALUES (?, ?, ?)",
            (name.strip(), category, description),
        )

    def update_ingredient(self, ingredient: Ingredient) -> None:
        self.db.execute(
            "UPDATE ingredients SET name=?, category=?, description=? WHERE id=?",
            (ingredient.name, ingredient.category, ingredient.description, ingredient.id),
        )

    def delete_ingredient(self, ingredient_id: int) -> None:
        self.db.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))

    # ── Inventory ──────────────────────────────────────────────────────────

    def get_all_inventory(self, search: str = "", category: str = "") -> list[InventoryItem]:
        sql = """
            SELECT inv.*, i.name AS ingredient_name, i.category
            FROM inventory inv
            JOIN ingredients i ON i.id = inv.ingredient_id
            WHERE 1=1
        """
        params: list = []
        if search:
            sql += " AND i.name LIKE ?"
            params.append(f"%{search}%")
        if category and category != "All":
            sql += " AND i.category = ?"
            params.append(category)
        sql += " ORDER BY i.category, i.name"
        rows = self.db.fetchall(sql, tuple(params))
        return [InventoryItem.from_row(r) for r in rows]

    def get_in_stock_ingredient_ids(self) -> set[int]:
        rows = self.db.fetchall("SELECT ingredient_id FROM inventory WHERE in_stock = 1")
        return {r["ingredient_id"] for r in rows}

    def count_in_stock(self) -> int:
        row = self.db.fetchone("SELECT COUNT(*) as cnt FROM inventory WHERE in_stock = 1")
        return row["cnt"] if row else 0

    def add_to_inventory(
        self,
        ingredient_id: int,
        quantity: float = 0,
        unit: str = "",
        notes: str = "",
        in_stock: bool = True,
    ) -> int:
        return self.db.execute(
            """INSERT INTO inventory (ingredient_id, quantity, unit, notes, in_stock)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(ingredient_id) DO UPDATE SET
                 quantity=excluded.quantity, unit=excluded.unit,
                 notes=excluded.notes, in_stock=excluded.in_stock,
                 updated_at=CURRENT_TIMESTAMP""",
            (ingredient_id, quantity, unit, notes, 1 if in_stock else 0),
        )

    def update_inventory(self, item: InventoryItem) -> None:
        self.db.execute(
            """UPDATE inventory SET
               quantity=?, unit=?, notes=?, in_stock=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (item.quantity, item.unit, item.notes, 1 if item.in_stock else 0, item.id),
        )

    def toggle_stock(self, inventory_id: int, in_stock: bool) -> None:
        self.db.execute(
            "UPDATE inventory SET in_stock=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (1 if in_stock else 0, inventory_id),
        )

    def remove_from_inventory(self, inventory_id: int) -> None:
        self.db.execute("DELETE FROM inventory WHERE id = ?", (inventory_id,))

    def is_in_inventory(self, ingredient_id: int) -> bool:
        row = self.db.fetchone(
            "SELECT id FROM inventory WHERE ingredient_id = ?", (ingredient_id,)
        )
        return row is not None
