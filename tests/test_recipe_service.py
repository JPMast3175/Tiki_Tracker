"""Tests for RecipeService CRUD and inventory matching."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import tempfile
import pytest

from tiki_tracker.db.database import Database
from tiki_tracker.db.schema import create_tables
from tiki_tracker.db.seed_data import seed_database
from tiki_tracker.models.recipe import Recipe
from tiki_tracker.services.recipe_service import RecipeService
from tiki_tracker.services.inventory_service import InventoryService


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        d = Database(db_path=Path(tmp) / "test.db")
        create_tables(d)
        yield d


@pytest.fixture
def recipe_service(db):
    return RecipeService(db)


@pytest.fixture
def inventory_service(db):
    return InventoryService(db)


@pytest.fixture
def seeded_db(db):
    seed_database(db)
    return db


def test_seed_creates_10_recipes(seeded_db):
    svc = RecipeService(seeded_db)
    assert svc.count() == 10


def test_create_and_get_recipe(recipe_service, inventory_service):
    # Ensure ingredient exists
    ing_id = inventory_service.create_ingredient("Test Rum", "Rum")
    assert ing_id

    recipe = Recipe(name="Test Cocktail", description="A test.", difficulty=2, prep_time=5)
    rid = recipe_service.create(recipe, [{"ingredient_id": ing_id, "amount": "2", "unit": "oz"}])
    assert rid > 0

    fetched = recipe_service.get_by_id(rid)
    assert fetched is not None
    assert fetched.name == "Test Cocktail"
    assert len(fetched.ingredients) == 1
    assert fetched.ingredients[0].ingredient_name == "Test Rum"
    assert fetched.ingredients[0].amount == "2"


def test_update_recipe(recipe_service, inventory_service):
    ing_id = inventory_service.create_ingredient("Old Rum", "Rum")
    new_id = inventory_service.create_ingredient("New Rum", "Rum")
    recipe = Recipe(name="Old Name")
    rid = recipe_service.create(recipe, [{"ingredient_id": ing_id, "amount": "1", "unit": "oz"}])

    updated = Recipe(id=rid, name="New Name", difficulty=4)
    recipe_service.update(updated, [{"ingredient_id": new_id, "amount": "2", "unit": "oz"}])

    fetched = recipe_service.get_by_id(rid)
    assert fetched.name == "New Name"
    assert fetched.difficulty == 4
    assert fetched.ingredients[0].ingredient_name == "New Rum"


def test_delete_recipe(recipe_service):
    rid = recipe_service.create(Recipe(name="Temp"), [])
    recipe_service.delete(rid)
    assert recipe_service.get_by_id(rid) is None


def test_favorite_toggle(recipe_service):
    rid = recipe_service.create(Recipe(name="Fav Test"), [])
    recipe_service.set_favorite(rid, True)
    assert recipe_service.get_by_id(rid).is_favorite is True

    recipe_service.set_favorite(rid, False)
    assert recipe_service.get_by_id(rid).is_favorite is False


def test_rating_clamped(recipe_service):
    rid = recipe_service.create(Recipe(name="Rating Test"), [])
    recipe_service.set_rating(rid, 7.0)
    assert recipe_service.get_by_id(rid).rating == 5.0

    recipe_service.set_rating(rid, -1.0)
    assert recipe_service.get_by_id(rid).rating == 0.0


def test_search_filter(recipe_service):
    recipe_service.create(Recipe(name="Zombie"), [])
    recipe_service.create(Recipe(name="Mai Tai"), [])

    results = recipe_service.get_all(search="zomb")
    assert len(results) == 1
    assert results[0].name == "Zombie"


def test_get_makeable(recipe_service, inventory_service):
    ing1 = inventory_service.create_ingredient("Rum Make", "Rum")
    ing2 = inventory_service.create_ingredient("Lime Make", "Citrus")
    ing3 = inventory_service.create_ingredient("Secret", "Spirits")

    rid = recipe_service.create(Recipe(name="Makeable"), [
        {"ingredient_id": ing1, "amount": "2", "unit": "oz"},
        {"ingredient_id": ing2, "amount": "1", "unit": "oz"},
    ])

    # Stock both — should be makeable
    inventory_service.add_to_inventory(ing1)
    inventory_service.add_to_inventory(ing2)

    makeable = recipe_service.get_makeable()
    assert any(r.id == rid for r in makeable)

    # Recipe requires ing3 which is not in stock
    recipe_service.create(Recipe(name="Not Makeable"), [
        {"ingredient_id": ing3, "amount": "1", "unit": "oz"},
    ])
    makeable_names = {r.name for r in recipe_service.get_makeable()}
    assert "Not Makeable" not in makeable_names


def test_recipe_to_dict(recipe_service, inventory_service):
    ing_id = inventory_service.create_ingredient("Rum Dict", "Rum")
    rid = recipe_service.create(
        Recipe(name="Dict Test", tags=["Classic", "Shaken"]),
        [{"ingredient_id": ing_id, "amount": "2", "unit": "oz", "notes": ""}],
    )
    recipe = recipe_service.get_by_id(rid)
    d = recipe.to_dict()
    assert d["name"] == "Dict Test"
    assert "Classic" in d["tags"]
    assert len(d["ingredients"]) == 1
    assert d["ingredients"][0]["name"] == "Rum Dict"
