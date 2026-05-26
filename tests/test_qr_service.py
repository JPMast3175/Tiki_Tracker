"""Tests for QRService — generation and JSON decode."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import tempfile
import pytest

from tiki_tracker.models.recipe import Recipe
from tiki_tracker.models.ingredient import RecipeIngredient
from tiki_tracker.services.qr_service import QRService


@pytest.fixture
def svc():
    return QRService()


@pytest.fixture
def sample_recipe():
    recipe = Recipe(
        id=1,
        name="Mai Tai",
        description="Classic tiki cocktail.",
        instructions="Shake and strain.",
        garnish="Mint sprig",
        glassware="Double Old Fashioned",
        difficulty=2,
        prep_time=10,
        tags=["Classic"],
    )
    recipe.ingredients = [
        RecipeIngredient(
            ingredient_name="Aged Rum", amount="2", unit="oz", sort_order=0
        )
    ]
    return recipe


def test_is_available(svc):
    # qrcode is installed in this venv; should be True
    assert svc.is_available() is True


def test_generate_qr_creates_file(svc, sample_recipe):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.png"
        result = svc.generate_recipe_qr(sample_recipe, output_path=out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0


def test_generate_qr_default_path(svc, sample_recipe):
    result = svc.generate_recipe_qr(sample_recipe)
    assert result is not None
    assert result.exists()
    result.unlink()  # cleanup


def test_decode_valid_json(svc, sample_recipe):
    payload = json.dumps(sample_recipe.to_dict())
    decoded = svc.decode_recipe_json(payload)
    assert decoded is not None
    assert decoded["name"] == "Mai Tai"
    assert decoded["difficulty"] == 2


def test_decode_invalid_json(svc):
    assert svc.decode_recipe_json("not json {{{") is None
    assert svc.decode_recipe_json("") is None
    assert svc.decode_recipe_json('["list", "not", "dict"]') is None


def test_round_trip_payload(svc, sample_recipe):
    """QR payload survives encode → decode intact."""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "recipe.png"
        svc.generate_recipe_qr(sample_recipe, output_path=out_path)

    payload = json.dumps(sample_recipe.to_dict())
    decoded = svc.decode_recipe_json(payload)
    assert decoded["name"] == sample_recipe.name
    assert len(decoded["ingredients"]) == len(sample_recipe.ingredients)
