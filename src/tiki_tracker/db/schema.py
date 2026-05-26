"""DDL — create all tables on first run; safe to call on every startup."""

from tiki_tracker.db.database import Database


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ingredients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    category    TEXT    NOT NULL DEFAULT 'Other',
    description TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS recipes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    description  TEXT    NOT NULL DEFAULT '',
    instructions TEXT    NOT NULL DEFAULT '',
    garnish      TEXT    NOT NULL DEFAULT '',
    glassware    TEXT    NOT NULL DEFAULT '',
    image_path   TEXT    NOT NULL DEFAULT '',
    image_url    TEXT    NOT NULL DEFAULT '',
    difficulty   INTEGER NOT NULL DEFAULT 3 CHECK(difficulty BETWEEN 1 AND 5),
    prep_time    INTEGER NOT NULL DEFAULT 15,
    rating       REAL    NOT NULL DEFAULT 0   CHECK(rating BETWEEN 0 AND 5),
    is_favorite  INTEGER NOT NULL DEFAULT 0,
    is_custom    INTEGER NOT NULL DEFAULT 0,
    tags         TEXT    NOT NULL DEFAULT '[]',
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id    INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    amount       TEXT    NOT NULL DEFAULT '',
    unit         TEXT    NOT NULL DEFAULT '',
    notes        TEXT    NOT NULL DEFAULT '',
    sort_order   INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (recipe_id)     REFERENCES recipes(id)     ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inventory (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL UNIQUE,
    quantity      REAL    NOT NULL DEFAULT 0,
    unit          TEXT    NOT NULL DEFAULT '',
    notes         TEXT    NOT NULL DEFAULT '',
    in_stock      INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe
    ON recipe_ingredients(recipe_id);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient
    ON recipe_ingredients(ingredient_id);

CREATE INDEX IF NOT EXISTS idx_inventory_ingredient
    ON inventory(ingredient_id);
"""

_CURRENT_VERSION = 1


def create_tables(db: Database) -> None:
    with db.connect() as conn:
        conn.executescript(_SCHEMA_SQL)
        row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
        if row is None:
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (_CURRENT_VERSION,))
