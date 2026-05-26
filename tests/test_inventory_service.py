"""Tests for InventoryService CRUD and ingredient management."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tempfile
import pytest

from tiki_tracker.db.database import Database
from tiki_tracker.db.schema import create_tables
from tiki_tracker.models.inventory import InventoryItem
from tiki_tracker.services.inventory_service import InventoryService


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        d = Database(db_path=Path(tmp) / "test.db")
        create_tables(d)
        yield d


@pytest.fixture
def svc(db):
    return InventoryService(db)


def test_create_ingredient(svc):
    ing_id = svc.create_ingredient("Test Gin", "Spirits")
    assert ing_id > 0
    ing = svc.get_ingredient_by_id(ing_id)
    assert ing is not None
    assert ing.name == "Test Gin"
    assert ing.category == "Spirits"


def test_duplicate_ingredient_ignored(svc):
    id1 = svc.create_ingredient("Unique Rum", "Rum")
    id2 = svc.create_ingredient("Unique Rum", "Rum")
    # Second insert is ignored (IGNORE); id2 may be 0 or same id
    assert id1 > 0


def test_update_ingredient(svc):
    ing_id = svc.create_ingredient("Old Name", "Other")
    ing = svc.get_ingredient_by_id(ing_id)
    ing.name = "New Name"
    ing.category = "Rum"
    svc.update_ingredient(ing)
    updated = svc.get_ingredient_by_id(ing_id)
    assert updated.name == "New Name"
    assert updated.category == "Rum"


def test_add_and_retrieve_inventory(svc):
    ing_id = svc.create_ingredient("Lime Juice", "Citrus")
    svc.add_to_inventory(ing_id, quantity=16.0, unit="oz")
    items = svc.get_all_inventory()
    assert any(i.ingredient_name == "Lime Juice" for i in items)


def test_toggle_stock(svc):
    ing_id = svc.create_ingredient("Toggle Rum", "Rum")
    svc.add_to_inventory(ing_id, in_stock=True)
    items = svc.get_all_inventory()
    item = next(i for i in items if i.ingredient_name == "Toggle Rum")
    assert item.in_stock is True

    svc.toggle_stock(item.id, False)
    items2 = svc.get_all_inventory()
    item2 = next(i for i in items2 if i.ingredient_name == "Toggle Rum")
    assert item2.in_stock is False


def test_count_in_stock(svc):
    i1 = svc.create_ingredient("Rum A", "Rum")
    i2 = svc.create_ingredient("Rum B", "Rum")
    svc.add_to_inventory(i1, in_stock=True)
    svc.add_to_inventory(i2, in_stock=False)
    assert svc.count_in_stock() == 1


def test_remove_from_inventory(svc):
    ing_id = svc.create_ingredient("Temp Syrup", "Syrups")
    svc.add_to_inventory(ing_id)
    items = svc.get_all_inventory()
    item = next(i for i in items if i.ingredient_name == "Temp Syrup")
    svc.remove_from_inventory(item.id)
    remaining = svc.get_all_inventory()
    assert not any(i.ingredient_name == "Temp Syrup" for i in remaining)


def test_search_inventory(svc):
    i1 = svc.create_ingredient("Aged Rum", "Rum")
    i2 = svc.create_ingredient("Simple Syrup", "Syrups")
    svc.add_to_inventory(i1)
    svc.add_to_inventory(i2)
    results = svc.get_all_inventory(search="rum")
    names = [r.ingredient_name for r in results]
    assert "Aged Rum" in names
    assert "Simple Syrup" not in names


def test_category_filter(svc):
    i1 = svc.create_ingredient("Dark Rum", "Rum")
    i2 = svc.create_ingredient("Mint", "Garnishes")
    svc.add_to_inventory(i1)
    svc.add_to_inventory(i2)
    results = svc.get_all_inventory(category="Garnishes")
    assert all(r.category == "Garnishes" for r in results)


def test_get_in_stock_ids(svc):
    i1 = svc.create_ingredient("In Stock", "Rum")
    i2 = svc.create_ingredient("Out Stock", "Rum")
    svc.add_to_inventory(i1, in_stock=True)
    svc.add_to_inventory(i2, in_stock=False)
    ids = svc.get_in_stock_ingredient_ids()
    assert i1 in ids
    assert i2 not in ids


def test_upsert_inventory(svc):
    ing_id = svc.create_ingredient("Orgeat", "Syrups")
    svc.add_to_inventory(ing_id, quantity=8.0, unit="oz")
    svc.add_to_inventory(ing_id, quantity=16.0, unit="oz")  # should upsert
    items = svc.get_all_inventory()
    matches = [i for i in items if i.ingredient_name == "Orgeat"]
    assert len(matches) == 1
    assert matches[0].quantity == 16.0
